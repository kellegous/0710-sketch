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

import lib

Pad = collections.namedtuple('Pad', ['t', 'r', 'b', 'l'])

def random_walk(sigma):
	v = 0
	while True:
		yield v
		v += random.gauss(0, sigma)

def create_seed():
	s = hex(int(time.time() * 1000))
	return s[2:]

def color_of(r, g, b):
	return [x/255.0 for x in (r, g, b)]

def main():
	bg_color = color_of(0xef, 0x47, 0x23)
	fg_color = color_of(0x33, 0x33, 0x33)

	parser = optparse.OptionParser()
	parser.add_option('--seed', default=create_seed(), dest='seed', help='')
	parser.add_option('--fmt', default='pdf', dest='fmt', help='')
	opts, args = parser.parse_args()

	print('seed = %s' % opts.seed)
	random.seed(opts.seed)

	w, h = 24 * 72, 24 * 72

	pad = Pad(h/6, w/12, h/6, w/12)

	if opts.fmt == 'pdf':
		surface = cairo.PDFSurface(os.path.basename(__file__) + '.pdf', w, h)
	elif opts.fmt == 'svg':
		surface = cairo.SVGSurface(os.path.basename(__file__) + '.svg', w, h)
	else:
		raise Error('invalid format: %s' % opts.fmt)

	context = cairo.Context(surface)

	nx = 8
	dx = (w - pad.r - pad.l) / float(nx)

	context.rectangle(0, 0, w, h)
	context.set_source_rgb(*bg_color)
	context.fill()

	for x in range(nx + 1):
		context.set_line_width(2)
		context.move_to(pad.l + x*dx, 0)
		context.line_to(pad.l + x*dx, h)
		# context.set_source_rgb(*fg_color)
		context.set_source_rgba(0x33/255.0, 0x33/255.0, 0x33/255.0, 0.6)
		context.stroke()

	for x in range(nx):
		bx = x*dx + dx/2
		# generate a random number of points
		ny = random.randint(4, 10)

		dy = (h - pad.t - pad.b) / ny

		# create a random walk
		walk = random_walk(dx / 4.0)

		pts = [(bx + next(walk) + pad.l, y*dy + pad.t) for y in range(ny+1)]

		# draw the lines
		context.set_line_width(10)

		lx, ly = pts[0]
		context.move_to(lx, ly)
		for x, y in pts[1:]:
			my = (y - ly) * 0.75
			context.curve_to(
				lx, ly + my,
				x, y - my,
				x, y)
			lx, ly = x, y
		context.set_source_rgb(*fg_color)
		context.stroke()

		# highlight the verticies
		context.set_line_width(10)
		for pt in pts:
			context.arc(pt[0], pt[1], 24, 0, 2 * math.pi)
			context.set_source_rgb(*bg_color)
			context.fill()

			context.arc(pt[0], pt[1], 24, 0, 2 * math.pi)
			context.set_source_rgb(*fg_color)
			context.stroke()

			context.arc(pt[0], pt[1], 8, 0, 2 * math.pi)
			context.set_source_rgb(*fg_color)
			context.fill()

	lib.commit(surface, os.path.basename(__file__) + '.png')


if __name__ == '__main__':
	sys.exit(main())