package main

import (
  "bytes"
  "crypto/sha1"
  "encoding/hex"
  "encoding/json"
  "flag"
  "flickr"
  "fmt"
  "hash"
  "io"
  "os"
  "path/filepath"
)

type Config struct {
  Flickr struct {
    ApiKey string `json:"api-key"`
  } `json:"flickr"`
}

type HashWriter struct {
  w io.Writer
  d hash.Hash
}

func (w *HashWriter) Write(b []byte) (int, error) {
  if n, err := w.d.Write(b); err != nil {
    return n, err
  }

  return w.w.Write(b)
}

func (w *HashWriter) Sum(b []byte) []byte {
  return w.d.Sum(b)
}

func (w *HashWriter) SumAsString(b []byte) string {
  return hex.EncodeToString(w.d.Sum(b))
}

func NewSha1Writer(w io.Writer) *HashWriter {
  return &HashWriter{
    w: w,
    d: sha1.New(),
  }
}

func LoadConfig(cfg *Config, filename string) error {
  r, err := os.Open(filename)
  if err != nil {
    return err
  }
  defer r.Close()

  return json.NewDecoder(r).Decode(cfg)
}

func DownloadPhoto(dir string, photo *flickr.Photo) (string, error) {
  var buf bytes.Buffer
  hw := HashWriter{
    w: &buf,
    d: sha1.New(),
  }

  if _, err := photo.Download(&hw); err != nil {
    return "", err
  }

  fn := filepath.Join(dir, hw.SumAsString(nil)+".jpg")
  w, err := os.Create(fn)
  if err != nil {
    return "", err
  }
  defer w.Close()

  if _, err := io.Copy(w, &buf); err != nil {
    return "", err
  }

  return fn, nil
}

func main() {
  flagDest := flag.String("dest", "data", "")
  flagConf := flag.String("conf", "cfg.json", "")
  flag.Parse()

  var cfg Config
  if err := LoadConfig(&cfg, *flagConf); err != nil {
    panic(err)
  }

  if _, err := os.Stat(*flagDest); err != nil {
    if err := os.MkdirAll(*flagDest, os.ModePerm); err != nil {
      panic(err)
    }
  }

  api := flickr.New(cfg.Flickr.ApiKey)
  for _, query := range flag.Args() {
    photos, err := api.Search(query)
    if err != nil {
      panic(err)
    }

    for _, photo := range photos {
      name, err := DownloadPhoto(*flagDest, photo)
      if err != nil {
        panic(err)
      }
      fmt.Println(name)
    }
  }
}
