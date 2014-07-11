/// <reference path="lib/q.ts" />

module app {

// var IMAGE = '/img/8293961091_cc7499e131_o.jpg';
var IMAGE = '/img/saf001014008051016.jpg',
    GRID = 15;

var ImageDataFor = (url : string,
    dw : number,
    dh : number,
    fn : (data : ImageData, ctx : CanvasRenderingContext2D) => void) => {
  var img = Q.create1('img')
    .setAttr('src', url)
    .on('load', (e : Event) => {
      var sw = img.prop('width'),
          sh = img.prop('height');

      var cvs = <HTMLCanvasElement>Q.create1('canvas')
        .setAttr('width', dw + 'px')
        .setAttr('height', dh + 'px')
        .elem();
      var ctx = cvs.getContext('2d'),
          dr = sw / sh,
          ir = dw / dh;
      if (dr / ir > 1) {
        // fit height
        var csw = sh * (dw / dh);
        ctx.drawImage(img.elem(), sw / 2 - csw / 2, 0, csw, sh, 0, 0, dw, dh);
      } else {
        // fit width
        var csh = sw * (dh / dw);
        ctx.drawImage(img.elem(), 0, sh / 2 - csh / 2, sw, csh, 0, 0, dw, dh);
      }

      fn(ctx.getImageData(0, 0, dw, dh), ctx);
    });
};

var ColorOf = (a : Uint8Array, i : number) => {
  i *= 4;
  return 'rgba('
    + a[i] + ','
    + a[i+1] + ','
    + a[i+2] + ','
    + (a[i+3]/255) + ')';
}

var GetUrl = (query : string) => {
  return '/flickr?q=' + encodeURIComponent(query) + '&v=' + Date.now();
}

var Render = (query : string, w : number, h : number) => {
  var dw = ((w / GRID) | 0),
      dh = ((h / GRID) | 0);

  var root = Q.select1('#root').setText('');

  ImageDataFor(GetUrl(query), dw, dh,
    (px : ImageData, ctx : CanvasRenderingContext2D) => {
      Q.createN('div', px.width * px.height)
        .addClass('divel')
        .eachQ((q, i) => {
          var x = (i % px.width) | 0,
              y = (i / px.width) | 0;

          q.setCss('position', 'absolute')
            .setCss('left', (x*GRID) + 'px')
            .setCss('top', (y*GRID - 30) + 'px')
            .setCss('width', ((GRID-2) * 1.5) + 'px')
            .setCss('height', ((GRID-2) * 1.5) + 'px')
            .setCss('border-top-right-radius', (GRID-2) + 'px')
            .setCss('border-bottom-left-radius', (GRID-2) + 'px')
            .setCss('background-color', ColorOf(px.data, i))
            .setCss('-webkit-transform', 'rotate(30deg)')
            .setCss('box-shadow', '-4px 2px 5px rgba(0, 0, 0, 0.4)')
            .setCss('border', '1px solid rgba(0,0,0,0.5)')
            .setCss('z-index', '' + i)

        })
        .appendTo(root);
    });
}

var elRoot = Q.select1('#root'),
    elQuery = Q.select1('#query')
      .on('keydown', (e : KeyboardEvent) => {
        if (e.keyCode == 13) {
          Render(elQuery.val(),
            elRoot.bounds().width,
            elRoot.bounds().height);
          e.preventDefault();
        }
      });

Render(elQuery.val(),
  elRoot.bounds().width,
  elRoot.bounds().height);

}