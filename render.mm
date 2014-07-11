#import <Cocoa/Cocoa.h>
#include <curl/curl.h>
#include <memory>
#include <stdio.h>
#include <string>

#include "auto_ref.h"
#include "gr.h"
#include "math.h"
#include "status.h"

namespace {

void UrlForQuery(std::string* res, std::string& query) {
  res->assign("http://localhost:6488/flickr?q=");
  CURL* curl = curl_easy_init();
  char* q = curl_easy_escape(curl, query.c_str(), query.size());
  res->append(q);
  curl_free(q);
  curl_easy_cleanup(curl);
}

Status LoadQueryData(uint8_t* data, std::string& query, int dw, int dh) {
  std::string url;
  UrlForQuery(&url, query);

  AutoRef<CGImageRef> img;
  Status did = gr::LoadFromUrl(img.addr(), url);
  if (!did.ok()) {
    return did;
  }

  AutoRef<CGContextRef> ctx = gr::NewContext(data, dw, dh);

  gr::DrawCoveringImage(ctx, img);

  return NoErr();
}

void DrawThingy(
    CGContextRef ctx,
    CGPathDrawingMode mode,
    CGRect rect,
    float r0,
    float r1) {
  CGFloat minx = CGRectGetMinX(rect), midx = CGRectGetMidX(rect), maxx = CGRectGetMaxX(rect);
  CGFloat miny = CGRectGetMinY(rect), midy = CGRectGetMidY(rect), maxy = CGRectGetMaxY(rect);
  CGContextMoveToPoint(ctx, minx, midy);
  CGContextAddArcToPoint(ctx, minx, miny, midx, miny, r0);
  CGContextAddArcToPoint(ctx, maxx, miny, maxx, midy, r1);
  CGContextAddArcToPoint(ctx, maxx, maxy, midx, maxy, r0);
  CGContextAddArcToPoint(ctx, minx, maxy, minx, midy, r1);
  CGContextClosePath(ctx);
  CGContextDrawPath(ctx, mode);
}

}

int main(int argc, char* argv[]) {
  int grid = 20;
  int w = 1600;
  int h = 600;
  int dw = 1 + (w / grid);
  int dh = h / grid;

  AutoRef<CGContextRef> ctx = gr::NewContext(w, h);

  std::unique_ptr<uint8_t[]> pixels(new uint8_t[dw*dh*4]);
  std::string query("nude women");
  Status did = LoadQueryData(pixels.get(), query, dw, dh);
  if (!did.ok()) {
    fprintf(stderr, "%s\n", did.what());
    exit(1);
  }

  CGContextScaleCTM(ctx, 1.0, -1.0);
  CGContextTranslateCTM(ctx, 0, -h - 25);
  for (int i = 0, n = dw*dh; i < n; i++) {
    int o = i*4;
    float x = (i%dw)*grid;
    float y = (i/dw)*grid;

    float a = M_PI / 6;

    CGContextSaveGState(ctx);
    CGContextConcatCTM(ctx, CGAffineTransformMake(
        cos(a),
        sin(a),
        -sin(a),
        cos(a),
        x-x*cos(a)+y*sin(a),
        y-x*sin(a)-y*cos(a)));
    AutoRef<CGColorRef> c = CGColorCreateGenericRGB(0, 0, 0, 0.4);
    CGContextSetShadowWithColor(
      ctx,
      CGSizeMake(-4, 2),
      5.0,
      c);
    CGContextSetRGBStrokeColor(ctx, 0, 0, 0, 0.2);
    CGContextSetRGBFillColor(
      ctx,
      pixels[o+0] / 255.0,
      pixels[o+1] / 255.0,
      pixels[o+2] / 255.0,
      pixels[o+3] / 255.0);

    DrawThingy(
        ctx,
        kCGPathFillStroke,
        CGRectMake(x, y, grid*1.5, grid*1.5),
        4.0,
        1.0);
    CGContextRestoreGState(ctx);
  }

  std::string filename("dump.png");
  did = gr::ExportAsPng(ctx, filename);
  if (!did.ok()) {
    fprintf(stderr, "%s\n", did.what());
    exit(1);
  }

  return 0;
}