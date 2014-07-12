#import <Cocoa/Cocoa.h>
#include <memory>
#include <stdio.h>
#include <string>
#include <vector>

#include "auto_ref.h"
#include "gr.h"
#include "math.h"
#include "status.h"
#include "util.h"

namespace {

//
Status LoadFileData(uint8_t* data, std::string& src, int dw, int dh) {
  AutoRef<CGImageRef> img;
  Status did = gr::LoadFromFile(img.addr(), src);
  if (!did.ok()) {
    return did;
  }

  AutoRef<CGContextRef> ctx = gr::NewContext(data, dw, dh);
  gr::DrawCoveringImage(ctx, img);
  return NoErr();
}

//
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

//
Status Render(std::string& dst, std::string& src) {
  int grid = 20;
  int w = 1600;
  int h = 600;
  int dw = 1 + (w / grid);
  int dh = h / grid;

  AutoRef<CGContextRef> ctx = gr::NewContext(w, h);

  std::unique_ptr<uint8_t[]> pixels(new uint8_t[dw*dh*4]);
  Status did = LoadFileData(pixels.get(), src, dw, dh);
  if (!did.ok()) {
    return did;
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
        10.0,
        1.0);
    CGContextRestoreGState(ctx);
  }

  return gr::ExportAsPng(ctx, dst);
}

void PrintUse(int argc, char* argv[]) {
  fprintf(stderr, "usage: %s srcs... dst", argv[0]);
  exit(1);
}

void Panic(Status& did) {
  fprintf(stderr, "%s\n", did.what());
  exit(1);
}

} // anonymous

int main(int argc, char* argv[]) {
  if (argc < 3) {
    PrintUse(argc, argv);
  }

  std::string dstRoot(argv[argc-1]);

  for (int i = 1, n = argc-1; i < n; i++) {
    std::string src(argv[i]);
    src.append("/*.jpg");

    std::vector<std::string> files;
    Status did = util::Glob(src.c_str(), &files);
    if (!did.ok()) {
      Panic(did);
    }

    for (int j = 0, m = files.size(); j < m; j++) {
      std::string dst(dstRoot);

      std::string base;
      util::Basename(&base, files[j]);
      util::PathJoin(&dst, base);

      printf("%s\n", base.c_str());
      did = Render(dst, files[j]);
      if (!did.ok()) {
        Panic(did);
      }
    }
  }

  return 0;
}