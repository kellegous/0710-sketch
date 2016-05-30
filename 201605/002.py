#!/usr/bin/env python2.7

import cairo
import math
import pango
import pangocairo
import os
import random
import sys

import lib

def random_walk(sigma):
	v = 0
	while True:
		yield v
		v += random.gauss(0, sigma)

def main():
	w, h = 1600, 600

	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
	context = cairo.Context(surface)

	nx = 25

	dx = w / nx

	print 'dx = %f' % dx
	context.rectangle(0, 0, w, h)
	context.set_source_rgb(0.1, 0.1, 0.1)
	context.fill()

	for x in range(nx):
		bx = x*dx + dx/2
		if (x & 1) == 1:
			context.move_to(bx, 0)
			context.line_to(bx, h)
			context.set_source_rgb(1, 1, 1)
			context.stroke()
		else:
			# generate a random number of points
			ny = random.randint(3, 10)
			# ny = int(math.pow(2, random.randint(1, 3)))
			dy = h / ny

			# create a random walk
			walk = random_walk(dx / 4.0)

			pts = [(bx + next(walk), y*dy) for y in range(ny+1)]

			# draw the lines
			context.set_line_width(4)

			lx, ly = pts[0]
			context.move_to(lx, ly)
			for x, y in pts[1:]:
				my = (y - ly) * 0.75
				context.curve_to(
					lx, ly + my,
					x, y - my,
					x, y)
				# context.line_to(x, y)
				lx, ly = x, y
			context.set_source_rgb(1, 1, 1)
			context.stroke()

			# highlight the verticies
			context.set_line_width(4)
			for pt in pts[1:-1]:
				context.arc(pt[0], pt[1], 8, 0, 2 * math.pi)
				context.set_source_rgb(0, 0, 0)
				context.fill()

				context.arc(pt[0], pt[1], 8, 0, 2 * math.pi)
				context.set_source_rgb(1, 1, 1)
				context.stroke()

	lib.commit(surface, os.path.basename(__file__) + '.png')


if __name__ == '__main__':
	sys.exit(main())