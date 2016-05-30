#!/usr/bin/env python2.7

import cairo
import math
import pango
import pangocairo
import os
import sys

import lib

def dist(ax, ay, bx, by):
	dx = bx - ax
	dy = by - ay
	return math.sqrt(dx*dx + dy*dy)

def main():
	w, h = 1600, 600

	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
	context = cairo.Context(surface)

	context.rectangle(0, 0, w, h)
	context.set_source_rgb(1, 1, 1)
	context.fill()

	size = 20 

	nx, ny = w / size, h / size

	cx = w/2.0
	cy = h/2.0

	for y in range(ny + 1):
		for x in range(nx + 1):
			px = x*size + size/2
			py = y*size + size/2

			dx, dy = 0, 0

			d = dist(cx, cy, px, py)
			if d < 200:
				dx = 20 * (px - cx) / d
				dy = 20 * (py - cy) / d

			context.arc(px + dx, py + dy, 0.6 * size/2, 0, 2*math.pi)
			context.set_source_rgb(0, 0.6, 0.9)
			context.fill()

			context.arc(px + dx, py + dy, 0.6 * size/2, 0, 2*math.pi)
			context.set_source_rgb(0.5, 0.5, 0.5)
			context.stroke()

	lib.commit(surface, 'test.png')

	return 0

if __name__ == '__main__':
	sys.exit(main())