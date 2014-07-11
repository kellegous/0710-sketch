package main

import (
  "encoding/json"
  "flag"
  "flickr"
  "github.com/kellegous/lilcache"
  "github.com/kellegous/pork"
  "log"
  "math/rand"
  "net/http"
  "os"
  "path/filepath"
  "runtime"
)

type Config struct {
  Flickr struct {
    ApiKey string `json:"api-key"`
  } `json:"flickr"`
}

func projRoot() (string, error) {
  _, file, _, _ := runtime.Caller(0)
  return filepath.Abs(filepath.Join(filepath.Dir(file), "..", ".."))
}

func fromCache(cache *lilcache.Cache, key string) []*flickr.Photo {
  v, _ := cache.Get(key)
  if v == nil {
    return nil
  }

  return v.([]*flickr.Photo)
}

func setup(r pork.Router, root string, cfg *Config) {
  cache := lilcache.New(100)

  r.RespondWith("/", pork.Content(pork.NewConfig(pork.None),
    http.Dir(filepath.Join(root, "pub"))))

  r.RespondWithFunc("/flickr", func(w pork.ResponseWriter, r *http.Request) {
    q := r.FormValue("q")
    if q == "" {
      q = "legs"
    }

    var err error
    imgs := fromCache(cache, q)
    if imgs == nil {
      imgs, err = flickr.New(cfg.Flickr.ApiKey).Search(q)
      if err != nil {
        panic(err)
      }
      cache.Put(q, imgs)
    }

    if len(imgs) == 0 {
      http.NotFound(w, r)
      return
    }

    img := imgs[rand.Intn(len(imgs))]

    log.Print(img.Url())
    w.Header().Set("Content-Type", "image/jpeg")
    if _, err := img.Download(w); err != nil {
      panic(err)
    }
  })
}

func LoadConfig(cfg *Config, filename string) error {
  r, err := os.Open(filename)
  if err != nil {
    return err
  }
  defer r.Close()

  return json.NewDecoder(r).Decode(cfg)
}

func ConfigPath(root, path string) string {
  if path != "" {
    return path
  }
  return filepath.Join(root, "cfg.json")
}

func main() {
  flagAddr := flag.String("addr", ":6488", "Address to which we should bind")
  flagConf := flag.String("conf", "", "A config file")
  flag.Parse()

  root, err := projRoot()
  if err != nil {
    panic(err)
  }

  var cfg Config

  if err := LoadConfig(&cfg, ConfigPath(root, *flagConf)); err != nil {
    panic(err)
  }

  r := pork.NewRouter(func(status int, r *http.Request) {
    log.Printf("%d :: %s", status, r.URL.Path)
  }, nil, nil)

  setup(r, root, &cfg)

  log.Printf("addr=%s", *flagAddr)
  if err := http.ListenAndServe(*flagAddr, r); err != nil {
    panic(err)
  }
}
