#import <Cocoa/Cocoa.h>
#include <getopt.h>
#include <memory>
#include <string>

#include "auto_ref.h"
#include "gr.h"
#include "status.h"

namespace {

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

uint8_t ToColorIndex(uint8_t r, uint8_t g, uint8_t b) {
  r >>= 6;
  g >>= 6;
  b >>= 6;
  return 0xc0 | (r<<4) | (g<<2) | b;
}

void FromColorIndex(float* r, float* g, float* b, uint8_t ix) {
  *r = ((ix & 0x30) << 2) / 255.0;
  *g = ((ix & 0x0c) << 4) / 255.0;
  *b = ((ix & 0x03) << 6) / 255.0;
}

Status Render(std::string& dst, std::string& src, int w, int h) {
  std::unique_ptr<uint8_t[]> pixels(new uint8_t[w*h*4]);
  Status did = LoadFileData(pixels.get(), src, w, h);
  if (!did.ok()) {
    return did;
  }

  int dy = 6;
  int dh = h / dy;

  std::unique_ptr<uint8_t[]> sample(new uint8_t[w*dh]);
  for (int j = 0; j < dh; j++) {
    for (int i = 0; i < w; i++) {
      uint64_t sr = 0, sg = 0, sb = 0;

      for (int k = 0; k < dy; k++) {
        int ix = ((k + j*dy)*w + i)*4;
        sr += pixels[ix];
        sg += pixels[ix+1];
        sb += pixels[ix+2];
      }

      sample[j*w + i] = ToColorIndex(sr/dy, sg/dy, sb/dy);
    }
  }

  AutoRef<CGContextRef> ctx = gr::NewContext(w, h);

  CGContextSetRGBFillColor(ctx, 1.0, 1.0, 1.0, 1.0);
  CGContextFillRect(ctx, CGRectMake(0, 0, w, h));

  CGContextScaleCTM(ctx, 1.0, -1.0);
  CGContextTranslateCTM(ctx, 0, -h);

  float r, g, b;
  for (int j = 0; j < dh; j++) {
    for (int i = 0; i < w; i++) {
      FromColorIndex(&r, &g, &b, sample[j*w + i]);
      CGContextSetRGBFillColor(ctx, r, g, b, 1.0);
      CGContextFillRect(ctx, CGRectMake(i, j*dy + 1, 1, dy - 2));
    }
  }

  return gr::ExportAsPng(ctx, dst);
}

void Panic(Status& did) {
  fprintf(stderr, "%s\n", did.what());
  exit(1);
}

void PrintUse(int argc, char* argv[]) {
  fprintf(stderr, "usage: %s src dst\n", argv[0]);
  exit(1);
}

void ParseArgs(int argc, char* argv[],
    std::string* src,
    std::string* dst) {

    int c = 0;
    while (true) {
      static struct option opts[] = {
        {0, 0, 0, 0}
      };

      int opt_index = 0;

      c = getopt_long(argc, argv, "", opts, &opt_index);

      if (c == -1) {
        break;
      }

      switch (c) {
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
  ParseArgs(argc, argv, &src, &dst);

  Status did = Render(dst, src, 1600, 600);
  if (!did.ok()) {
    Panic(did);
  }

  return 0;
}
