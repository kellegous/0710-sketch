package flickr

import (
  "encoding/json"
  "fmt"
  "io"
  "net/http"
  "net/url"
)

const baseUrl = "https://api.flickr.com/services/rest/"

type Api struct {
  key string
}

type Photo struct {
  Id     string
  Title  string
  Farm   int
  Server string
  Secret string
}

func (p *Photo) Url() string {
  return fmt.Sprintf("http://farm%d.staticflickr.com/%s/%s_%s_%s.jpg",
    p.Farm,
    p.Server,
    p.Id,
    p.Secret,
    "b")
}

func (p *Photo) Download(w io.Writer) (int64, error) {
  r, err := http.Get(p.Url())
  if err != nil {
    return 0, err
  }
  defer r.Body.Close()

  return io.Copy(w, r.Body)
}

func New(key string) *Api {
  return &Api{
    key: key,
  }
}

func (a *Api) Search(query string) ([]*Photo, error) {
  r, err := http.Get(fmt.Sprintf("%s?%s", baseUrl,
    url.Values{
      "api_key":        {a.key},
      "method":         {"flickr.photos.search"},
      "format":         {"json"},
      "nojsoncallback": {"1"},
      "text":           {query},
      "sort":           {"interestingness-desc"},
      "license":        {"1,2"},
    }.Encode()))
  if err != nil {
    return nil, err
  }

  defer r.Body.Close()

  var s struct {
    Message string
    Photos  struct {
      Photo []*Photo
    }
  }

  if err := json.NewDecoder(r.Body).Decode(&s); err != nil {
    return nil, err
  }

  if r.StatusCode != 200 {
    if s.Message == "" {
      return nil, fmt.Errorf("status: %d", r.StatusCode)
    }
    return nil, fmt.Errorf("%s", s.Message)
  }

  return s.Photos.Photo, nil
}
