#!/usr/bin/env python2.7

import cairo
import collections
import math
import pango
import pangocairo
import optparse
import os
import random
import sys
import time
import pprint

import lib

Pad = collections.namedtuple('Pad', ['t', 'r', 'b', 'l'])

def color_of(r, g, b, a = None):
	vals = [x/255.0 for x in (r, g, b)]
	if a is None:
		return vals
	return vals + [a]

def create_seed():
	s = hex(int(time.time() * 1000))
	return s[2:]

def hexagon(context, cx, cy, r):
	a = r / 2.0
	b = r * math.sin(math.pi / 3.0)
	context.move_to(cx, cy + r)
	context.line_to(cx + b, cy + a)
	context.line_to(cx + b, cy - a)
	context.line_to(cx, cy - r)
	context.line_to(cx - b, cy - a)
	context.line_to(cx - b, cy + a)
	context.line_to(cx, cy + r)

def luminance(r, g, b):
	r /= 255.0
	g /= 255.0
	b /= 255.0
	return 0.2126 * r + 0.7152 * g + 0.0722 * b

# TODO(knorton): This is pretty junky, just as it says. We need to filter
# by minimal luminance.
def junk_colors(n, amin, amax, lum_min):
	dt = 255 / n

	all = []
	for r in range(n + 1):
		for g in range(n + 1):
			for b in range(n + 1):
				if luminance(r*dt, g*dt, b*dt) > lum_min:
					continue
				a = amin + random.random() * (amax - amin)
				all.append((r*dt, g*dt, b*dt, a))
	random.shuffle(all)
	return all

def main():
	parser = optparse.OptionParser()
	parser.add_option('--seed', default=create_seed(), dest='seed', help='')
	parser.add_option('--fmt', default='pdf', dest='fmt', help='')
	parser.add_option('--nx', default=10, dest='nx', help='')
	opts, args = parser.parse_args()

	print('seed = %s' % opts.seed)
	random.seed(opts.seed)

	w, h = 24 * 72, 36 * 72

	pad = Pad(h/16, h/16, h/16, h/16)

	surface = lib.create_surface(opts.fmt, os.path.basename(__file__), w, h)
	context = cairo.Context(surface)

	vw, vh = w - pad.l - pad.r, h - pad.t - pad.b

	nx = opts.nx

	dx = vw / float(nx)
	dy = dx / math.sin(math.pi / 3)
	ny = int(math.ceil(vh / dx))

	context.rectangle(0, 0, w, h)
	context.set_source_rgb(*color_of(0x33, 0x33, 0x33))
	context.fill()

	context.rectangle(pad.l, pad.t, w - pad.l - pad.r, h - pad.t - pad.b)
	context.set_source_rgb(*color_of(0xff, 0xff, 0xff))
	context.fill()

	context.rectangle(pad.l, pad.t, w - pad.l - pad.r, h - pad.t - pad.b)
	context.clip()


	idx = {}
	for i in range(0, nx):
		for j in range(0, ny):
			idx[(i, j)] = True

	colors = junk_colors(4, 0.1, 0.8, 0.5)[:10]


	a = float(nx * ny)

	while len(idx)/a > 0.15:
		x = random.randint(-2, nx + 2)
		y = random.randint(-2, ny + 2)
		r = random.randint(2, 3)
		for i in range(x, x + r):
			for j in range(y, y + r):
				if idx.has_key((i, j)):
					del idx[(i, j)]
		hexagon(context, pad.l + x * dx + dx/2.0, pad.t + y*dy + dy/2.0, r*dy - dy/2.0)
		context.set_source_rgba(*random.choice(colors))
		context.fill()

		hexagon(context, pad.l + x * dx + dx/2.0, pad.t + y*dy + dy/2.0, r*dy - dy/2.0)
		context.set_source_rgba(*color_of(0x00, 0x00, 0x00, 0.3))
		context.stroke()

	context.set_line_width(1.0)
	for x in range(1, nx):
		context.move_to(pad.l + x*dx, pad.t)
		context.line_to(pad.l + x*dx, h - pad.b)
		context.set_source_rgba(*color_of(0x99, 0x99, 0x99, 0.2))
		context.stroke()

	for y in range(1, ny):
		context.move_to(pad.l, pad.t + y*dy)
		context.line_to(w - pad.r, pad.t + y*dy)
		context.set_source_rgba(*color_of(0x99, 0x99, 0x99, 0.2))
		context.stroke()

	for i, color in enumerate(colors):
		print '%s %s %0.2f' % (color[:3], color_of(*color[:3]), luminance(*color[:3]))

		context.rectangle(pad.l + 10 + i * 20, pad.t + 20, 20, 20)
		context.set_source_rgb(*color[:3])
		context.fill()

		context.rectangle(pad.l + 10 + i * 20, pad.t + 20, 20, 20)
		context.set_source_rgb(*color_of(0x33, 0x33, 0x33))
		context.stroke()

	lib.commit(surface, os.path.basename(__file__) + '.png')


if __name__ == '__main__':
	sys.exit(main())