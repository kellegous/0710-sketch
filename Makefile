CFLAGS=-Wall
LDFLAGS=-framework Cocoa -lcurl

OBJS=gr.o shingle.o status.o util.o
GOPATH=$(shell pwd)
PROGS=shingle furlr

ALL: $(PROGS)

%.o : %.mm %.h
	g++ $(CFLAGS) -c -o $@ $<

status.o : status.cc status.h
	g++ $(CFLAGS) -c -o $@ $<

shingle: shingle.o $(OBJS)
	g++ $(LDFLAGS) -o $@ $(OBJS)

furlr : $(shell find src -name *.go)
	GOPATH=$(GOPATH) go build -o furlr src/furlr/main.go

clean:
	rm -f $(OBJS) $(PROGS)
