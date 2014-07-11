#import <Cocoa/Cocoa.h>
#include <curl/curl.h>
#include <memory>
#include <stdio.h>
#include <string>

#include "auto_ref.h"
#include "gr.h"
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

};

int main(int argc, char* argv[]) {
  int grid = 50;
  int w = 1600;
  int h = 600;
  int dw = w / grid;
  int dh = h / grid;

  AutoRef<CGContextRef> ctx = gr::NewContext(w, h);

  std::unique_ptr<uint8_t[]> pixels(new uint8_t[dw*dh*4]);
  std::string query("lips");
  Status did = LoadQueryData(pixels.get(), query, dw, dh);
  if (!did.ok()) {
    fprintf(stderr, "%s\n", did.what());
    exit(1);
  }

  for (int i = 0, n = dw*dh; i < n; i++) {
    int o = i*4;
    int x = i%dw;
    int y = i/dw;

    CGContextSetRGBFillColor(
      ctx,
      pixels[o+0] / 255.0,
      pixels[o+1] / 255.0,
      pixels[o+2] / 255.0,
      pixels[o+3] / 255.0);
    CGContextFillRect(
      ctx,
      CGRectMake(x*grid, y*grid, grid, grid));
  }

  std::string filename("dump.png");
  did = gr::ExportAsPng(ctx, filename);
  if (!did.ok()) {
    fprintf(stderr, "%s\n", did.what());
    exit(1);
  }

  return 0;
}