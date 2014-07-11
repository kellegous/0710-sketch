CFLAGS=-Wall
LDFLAGS=-framework Cocoa -lcurl

OBJS=gr.o render.o status.o util.o
DEPS=src/github.com/kellegous/pork src/github.com/kellegous/lilcache
SRCS=$(shell find src -name *.go)
GOPATH=$(shell pwd)

ALL: sample render

%.o : %.mm %.h
	g++ $(CFLAGS) -c -o $@ $<

status.o : status.cc status.h
	g++ $(CFLAGS) -c -o $@ $<

render : render.mm $(OBJS)
	g++ $(LDFLAGS) -o render $(OBJS)

sample : $(SRCS) $(DEPS)
	GOPATH=$(GOPATH) go build -o sample src/sample/main.go

src/github.com/kellegous/pork:
	./bin/get-deps

src/github.com/kellegous/lilcache:
	./bin/get-deps

clean:
	rm -f $(OBJS) render sample
