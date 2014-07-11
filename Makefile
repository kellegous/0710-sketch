CFLAGS=-Wall
LDFLAGS=-framework Cocoa -lcurl

OBJS=gr.o render.o status.o util.o

ALL: render

%.o : %.mm %.h
	g++ $(CFLAGS) -c -o $@ $<

render : render.mm $(OBJS)
	g++ $(LDFLAGS) -o render $(OBJS)

clean:
	rm -f $(OBJS) render