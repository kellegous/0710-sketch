/// <reference path="signal.ts" />
interface Q {
  contains(e : any) : boolean;
  setAttr(k : string, v : string) : Q;
  setCss(k : string, v : string, p? : string) : Q;
  setCssTransform(xform:string) : Q;
  setHtml(v : string) : Q;
  setProp(k : string, v : any) : Q;
  setText(v : string) : Q;
  setVal(v : string) : Q;
  on(name : string, f : (e : Event) => void, capture? : boolean) : Q;
  off(name : string, f : (e : Event) => void, capture? : boolean) : Q;
  remove() : Q;
}

module Q {

export class Of1 implements Q {
  e : HTMLElement;

  constructor(node? : Node) {
    this.e = <HTMLElement>node;
  }

  set(e : HTMLElement) : Of1 {
    this.e = e;
    return this;
  }

  select1(sel : string) : Of1 {
    var e = this.e.querySelector(sel);
    return e ? new Of1(e) : null;
  }

  selectN(sel : string) : OfN {
    return new OfN(this.e.querySelectorAll(sel));
  }

  focus() : Of1 {
    this.e.focus();
    return this;
  }

  blur() : Of1 {
    this.e.blur();
    return this;
  }

  hasFocus() : boolean {
    return document.activeElement == this.e;
  }

  contains(q : any) : boolean {
    return contains(this.e, q instanceof Of1 ? q.e : q);
  }

  text() : string {
    return text(this.e);
  }

  html() : string {
    return html(this.e);
  }

  setHtml(v : string) : Of1 {
    setHtml(this.e, v);
    return this;
  }

  setText(v : string) : Of1 {
    setText(this.e, v);
    return this;
  }

  attr(k : string) : string {
    return attr(this.e, k);
  }

  setAttr(k : string, v : string) : Of1 {
    setAttr(this.e, k, v);
    return this;
  }

  prop(k : string) : any {
    return prop(this.e, k);
  }

  setProp(k : string, v : any) : Of1 {
    setProp(this.e, k, v);
    return this;
  }

  val() : string {
    return val(this.e);
  }

  setVal(v : string) : Of1 {
    setVal(this.e, v);
    return this;
  }

  css(k : string) : string {
    return css(this.e, k);
  }

  setCss(k : string, v : any, p? : string) : Of1 {
    setCss(this.e, k, v, p);
    return this;
  }

  setCssTransform(xform:string) : Of1 {
    setCssTransform(this.e, xform);
    return this;
  }

  on(name : string, f : (e : Event) => void, capture? : boolean) : Of1 {
    on(this.e, name, f, capture);
    return this;
  }

  off(name : string, f : (e : Event) => void, capture? : boolean) : Of1 {
    off(this.e, name, f, capture);
    return this;
  }

  children() : OfN {
    return new OfN(this.e.children);
  }

  parent() : Of1 {
    var p = this.e.parentElement;
    return p ? new Of1(p) : null;
  }

  remove() : Of1 {
    remove(this.e);
    return this;
  }

  hasClass(c : string) : boolean {
    return hasClass(this.e, c);
  }

  setClass(c : string) : Of1 {
    setClass(this.e, c);
    return this;
  }

  addClass(c : string) : Of1 {
    addClass(this.e, c);
    return this;
  }

  removeClass(c : string) : Of1 {
    removeClass(this.e, c);
    return this;
  }

  toggleClass(c : string) : Of1 {
    toggleClass(this.e, c);
    return this;
  }

  // TODO(jaime): Should probably make these typesafe.
  append(o : any) : Of1 {
    append(this.e, o);
    return this;
  }

  appendText(text: string) : Of1 {
    append(this.e, document.createTextNode(text));
    return this
  }

  appendTo(o : any) : Of1 {
    append(o, this.e);
    return this;
  }

  prepend(o : any) : Of1 {
    prepend(this.e, o);
    return this;
  }

  prependTo(o : any) : Of1 {
    prepend(o, this.e);
    return this;
  }

  bounds() : ClientRect {
    return this.e.getBoundingClientRect();
  }

  elem(): HTMLElement {
    return this.e;
  }

  offsetWidth(): number {
    return this.e.offsetWidth
  }

  offsetHeight(): number {
    return this.e.offsetHeight
  }

  offsetTop(): number {
    return this.e.offsetTop
  }
}

export class OfN implements Q {
  e : HTMLElement[];

  constructor(e? : any) {
    if (e instanceof Array) {
      this.e = e.map((i) => {
        if (i instanceof Of1) {
          return i.e;
        }
        return i;
      });
    } else if (e instanceof NodeList || e instanceof HTMLCollection) {
      this.e = [];
      for (var i = 0, n = e.length; i < n; i++) {
        this.e.push(e[i]);
      }
    } else {
      this.e = [];
    }
  }

  selectN(sel : string) : OfN {
    var all = new OfN;
    this.eachQ((q) => {
      q.selectN(sel).e.forEach((e) => {
        all.push(e);
      });
    });
    return all;
  }

  empty() : boolean {
    return this.e.length == 0;
  }

  size() : number {
    return this.e.length;
  }

  contains(c : any) : boolean {
    var e = this.e;
    for (var i = 0, n = e.length; i < n; i++) {
      if (contains(e[i], c)) {
        return true;
      }
    }
    return false;
  }

  setHtml(v : string) : OfN {
    this.e.forEach((e) => {
      setHtml(e, v);
    });
    return this;
  }

  setText(v : string) : OfN {
    this.e.forEach((e) => {
      setText(e, v);
    });
    return this;
  }

  setAttr(k : string, v : string) : OfN {
    this.e.forEach((e) => {
      setAttr(e, k, v);
    });
    return this;
  }

  setProp(k : string, v : any) : OfN {
    this.e.forEach((e) => {
      setProp(e, k, v);
    });
    return this;
  }

  setVal(v : string) : OfN {
    this.e.forEach((e) => {
      setVal(e, v);
    });
    return this;
  }

  setCss(k : string, v : any, p? : string) : OfN {
    this.e.forEach((e) => {
      setCss(e, k, v, p);
    });
    return this;
  }

  setCssTransform(xform : string) : OfN {
    this.e.forEach((e) => {
      setCssTransform(e, xform);
    });
    return this;
  }

  on(name : string, f : (e : Event) => void, capture? : boolean) : OfN {
    this.e.forEach((e) => {
      on(e, name, f, capture);
    });
    return this;
  }

  off(name : string, f : (e : Event) => void, capture? : boolean) : OfN {
    this.e.forEach((e) => {
      off(e, name, f, capture);
    });
    return this;
  }


  remove() : OfN {
    this.e.forEach(remove);
    return this;
  }

  setClass(c : string) : OfN {
    this.e.forEach((e) => {
      setClass(e, c);
    });
    return this;
  }

  addClass(c : string) : OfN {
    this.e.forEach((e) => {
      addClass(e, c);
    });
    return this;
  }

  removeClass(c : string) : OfN {
    this.e.forEach((e) => {
      removeClass(e, c);
    });
    return this;
  }

  toggleClass(c : string) : OfN {
    this.e.forEach((e) => {
      toggleClass(e, c);
    });
    return this;
  }

  appendTo(o : any) : OfN {
    this.e.forEach((e) => {
      append(o, e);
    });
    return this;
  }

  prependTo(o : any) : OfN {
    this.e.forEach((e) => {
      prepend(o, e);
    });
    return this;
  }

  eachQ(f : (q : Of1, i : number) => void, q? : Of1) : OfN {
    if (!q) {
      q = new Of1;
    }

    this.e.forEach((e, i) => {
      q.set(e);
      f(q, i);
    });
    q.set(null);
    return this;
  }

  push(o : any) : OfN {
    this.e.push(o instanceof Of1 ? o.e : o);
    return this;
  }

  qAt(index : number) : Of1 {
    return new Of1(this.e[index]);
  }
}

export var have1 = (n? : Node) => {
  return new Of1(n);
}

export var create1 = (t : string) : Of1 => {
  return new Of1(document.createElement(t));
}

export var haveN = (e? : any) => {
  return new OfN(e);
}

export var createN = (t : string, n : number) : OfN => {
  var q = new OfN;
  while (q.e.length < n) {
    q.push(create1(t));
  }
  return q;
}

export var select1 = (sel : string, t? : NodeSelector) : Of1 => {
  t = t || document;
  var r = t.querySelector(sel);
  return r ? new Of1(r) : null;
}

export var body = () : Of1 => {
  return new Of1(document.body);
}

export var head = () : Of1 => {
  return new Of1(document.head);
}

export var html = (e : HTMLElement) : string => {
  return e.innerHTML;
}

export var setHtml = (e : HTMLElement, v : string) => {
  e.innerHTML = v;
}

export var text = (e : HTMLElement) : string => {
  return e.textContent;
}

export var setText = (e : HTMLElement, v : string) => {
  e.textContent = v;
}

export var css = (e : HTMLElement, k : string) : string => {
  var lv = e.style.getPropertyValue(k);
  return lv ? lv : getComputedStyle(e).getPropertyValue(k);
}

export var setCss = (e : HTMLElement, k : string, v : any, p? : string) => {
  if (typeof v == 'number') {
    v = v + 'px';
  }
  e.style.setProperty(k, v, p || '');
}

export var setCssTransform = (e : HTMLElement, xform : string) => {
  e.style.setProperty('-webkit-transform', xform);
  e.style.setProperty('-moz-transform', xform);
  e.style.setProperty('-ms-transform', xform);
  e.style.setProperty('transform', xform);
}

export var prop = (e : HTMLElement, k : string) : any => {
  return e[k];
}

export var setProp = (e : HTMLElement, k : string, v : any) => {
  if (v ==null) {
    delete e[k];
  } else {
    e[k] = v;
  }
}

export var attr = (e : HTMLElement, k : string) : string => {
  return e.hasAttribute(k) ? e.getAttribute(k) : '';
}

export var setAttr = (e : HTMLElement, k : string, v : string) => {
  if (v == null) {
    e.removeAttribute(k);
  } else {
    e.setAttribute(k, v);
  }
}

export var contains = (e : HTMLElement, child : HTMLElement) : boolean => {
  return e.contains(child);
}

export var val = (e : HTMLElement) : string => {
  return e['value'];
}

export var setVal = (e : HTMLElement, v : string) => {
  e['value'] = v;
}

export var on = (e : HTMLElement, n : string, f : (e : Event) => void, capture? : boolean) => {
  e.addEventListener(n, f, !!capture);
}

export var off = (e : HTMLElement, n : string, f : (e : Event) => void, capture? : boolean) => {
  e.removeEventListener(n, f, !!capture);
}

export var hasClass = (e : HTMLElement, c : string) : boolean => {
  return e.classList.contains(c);
}

export var setClass = (e : HTMLElement, c : string) => {
  e.className = c;
}

export var addClass = (e : HTMLElement, c : string) => {
  e.classList.add(c);
}

export var removeClass = (e : HTMLElement, c : string) => {
  e.classList.remove(c);
}

export var toggleClass = (e : HTMLElement, c : string) => {
  e.classList.toggle(c);
}

export var remove = (e : HTMLElement) => {
  var p = e.parentElement;
  if (p) {
    p.removeChild(e);
  }
}

export var append = (e : any, o : any) => {
  var en : Node = (e instanceof Of1) ? e.e : e,
      on : Node = (o instanceof Of1) ? o.e : o;
  en.appendChild(on);
}

export var prepend = (e : any, o : any) => {
  var en : Node = (e instanceof Of1) ? e.e : e,
      on : Node = (o instanceof Of1) ? o.e : o;
  en.insertBefore(on, en);
}

var xhr = (url : string, verb : string, data : string, contentType : string,
    onWorked : (xhr : XMLHttpRequest) => void,
    onFucked : (xhr : XMLHttpRequest) => void) => {
  var xhr = new XMLHttpRequest;
  xhr.open(verb, url, true);
  if (contentType) {
    xhr.setRequestHeader('Content-Type', contentType);
  }
  xhr.onreadystatechange = () => {
    if (xhr.readyState != 4) {
      return;
    }

    if (xhr.status == 200) {
      onWorked(xhr);
    } else {
      onFucked(xhr);
    }
  };

  if (data) {
    xhr.send(data);
  } else {
    xhr.send();
  }
}

var deliverJson = (data : string, cb : (data : any) => void) => {
  var o = null;
  try {
    o = JSON.parse(data);
  } catch (e) {
    // invalid json, we'll deliver null.
  }
  cb(o);
}

export var getJson = (url : string, cb : (data : any) => void) => {
  xhr(url, 'GET', null, null,
    (xhr) => {
      deliverJson(xhr.responseText, cb);
    },
    (xhr) => {
      cb(null);
    });
}

export var postJson = (url : string, data : any, cb : (data : any) => void) => {
  xhr(url, 'POST', JSON.stringify(data), 'application/json',
    (xhr) => {
      deliverJson(xhr.responseText, cb);
    },
    (xhr) => {
      cb(null);
    });
}

}