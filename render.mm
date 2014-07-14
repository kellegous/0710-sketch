#import <Cocoa/Cocoa.h>
#include <getopt.h>
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
Status Render(std::string& dst, std::string& src, int grid, bool lighten) {
  int w = 1600;
  int h = 600;
  int dw = 1 + (w / grid);
  int dh = 1 + (h / grid);

  AutoRef<CGContextRef> ctx = gr::NewContext(w, h);

  std::unique_ptr<uint8_t[]> pixels(new uint8_t[dw*dh*4]);
  Status did = LoadFileData(pixels.get(), src, dw, dh);
  if (!did.ok()) {
    return did;
  }

  CGContextSetRGBFillColor(ctx, 1.0, 1.0, 1.0, 1.0);
  CGContextFillRect(ctx, CGRectMake(0, 0, w, h));

  CGContextScaleCTM(ctx, 1.0, -1.0);
  CGContextTranslateCTM(ctx, 0, -h - grid);
  for (int i = 0, n = dw*dh; i < n; i++) {
    int o = i*4;
    float x = (i%dw)*grid;
    float y = (i/dw)*grid;

    float t = M_PI / 6;

    CGContextSaveGState(ctx);
    CGContextConcatCTM(ctx, CGAffineTransformMake(
        cos(t),
        sin(t),
        -sin(t),
        cos(t),
        x-x*cos(t)+y*sin(t),
        y-x*sin(t)-y*cos(t)));
    AutoRef<CGColorRef> c = CGColorCreateGenericRGB(0, 0, 0, 0.4);
    CGContextSetShadowWithColor(
      ctx,
      CGSizeMake(-4, 2),
      2.0,
      c);
    CGContextSetRGBStrokeColor(ctx, 0, 0, 0, 0.2);
    float r = pixels[o+0] / 255.0,
          g = pixels[o+1] / 255.0,
          b = pixels[o+2] / 255.0,
          a = pixels[o+3] / 255.0;

    float f = 0.25;
    if (lighten) {
      r = r + (1.0-r)*f;
      g = g + (1.0-g)*f;
      b = b + (1.0-b)*f;
    }

    CGContextSetRGBFillColor(ctx, r, g, b, a);

    DrawThingy(
        ctx,
        kCGPathFillStroke,
        CGRectMake(x, y, grid*1.5, grid*1.5),
        5.0,
        1.0);
    CGContextRestoreGState(ctx);
  }

  // return gr::ExportAsJpg(ctx, dst, 0.6);
  return gr::ExportAsPng(ctx, dst);
}

void PrintUse(int argc, char* argv[]) {
  fprintf(stderr, "usage: %s src dst\n", argv[0]);
  exit(1);
}

void Panic(Status& did) {
  fprintf(stderr, "%s\n", did.what());
  exit(1);
}

bool ParseIntArg(const char* arg, int* v) {
  std::string s(arg);
  Status did = util::ParseInt(s, 10, v);
  return did.ok();
}

void ParseArgs(int argc, char* argv[],
    std::string* src,
    std::string* dst,
    int* grid,
    bool* lighten) {
  int c = 0;
  while (true) {
    static struct option opts[] = {
      { "grid-size", required_argument, 0, 'g' },
      { "lighten",   no_argument,       0, 'l' },
      { 0, 0, 0, 0 }
    };

    int opt_index = 0;

    c = getopt_long(argc, argv, "", opts, &opt_index);

    if (c == -1) {
      break;
    }

    switch (c) {
    case 'g':
      if (!ParseIntArg(optarg, grid)) {
        fprintf(stderr, "invalid --grid-size option\n");
        PrintUse(argc, argv);
      }
      break;
    case 'l':
      *lighten = true;
      break;
    case '?':
    default:
      PrintUse(argc, argv);
    }
  }

  if (argc - optind != 2) {
    PrintUse(argc, argv);
  }

  src->assign(argv[optind]);
  dst->assign(argv[optind+1]);
}

} // anonymous

int main(int argc, char* argv[]) {
  std::string src, dst;
  int grid = 40;
  bool lighten = false;
  ParseArgs(argc, argv, &src, &dst, &grid, &lighten);

  Status did = Render(dst, src, grid, lighten);
  if (!did.ok()) {
    Panic(did);
  }

  return 0;
}