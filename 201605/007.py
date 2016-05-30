#!/usr/bin/env python2.7

import cairo
import collections
import math
import pango
import pangocairo
import noise
import optparse
import os
import random
import struct
import sys
import time
import pprint

import lib

from lib import color_of, Padding

HEART = """
	M 4.5,-6.5
	C 2.545,-6.5 0.67,-5.232 0,-3.5
	C -0.67,-5.232 -2.547,-6.5 -4.5,-6.5
	C -7.043,-6.5 -9,-4.568 -9,-2
	C -9,1.53 -5.207,4.257 0,9.5
	C 5.207,4.258 9,1.53 9,-2
	C 9,-4.568 7.043,-6.5 4.5,-6.5
	Z
	"""

class HeartMask(object):
	def __init__(self, w, h):
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
		context = cairo.Context(surface)

		context.rectangle(0, 0, w, h)
		context.set_source_rgb(1, 1, 1)
		context.fill()

		context.translate(w/2.0, h/2.0)
		context.set_source_rgb(0, 0, 0)
		lib.parse_svg_path(HEART).scale(w/24.0, w/24.0).draw(context)
		context.fill()

		self.surface = surface

	def pixel_at(self, x, y):
		surface = self.surface
		stride = surface.get_stride()
		data = surface.get_data()
		idx = y*surface.get_stride() + x*4
		return struct.unpack('I', data[idx:idx+4])[0]

def create_image_data(w, h):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
	context = cairo.Context(surface)
	

	lib.commit(surface, 'junk.png')

	return surface.get_data()

def luminance(r, g, b):
	r /= 255.0
	g /= 255.0
	b /= 255.0
	return 0.2126 * r + 0.7152 * g + 0.0722 * b

def rgb_of(p):
	r = (p >> 16) & 0xff
	g = (p >>  8) & 0xff
	b = p & 0xff
	return r, g, b

def draw_doodle_dah(context, x, y, vx, vy, r):
	v = (1 + noise.pnoise2(vx, vy, 1))/2.0
	a = 0.2+v*0.6
	context.set_source_rgba(*color_of(0xff0099, a=a))
	context.arc(x, y, r, 0, 2*math.pi)
	context.fill()

	context.set_source_rgb(*color_of(0x333333))
	context.arc(x, y, r, 0, 2*math.pi)
	context.stroke()

def draw_empty_spot(context, x, y, vx, vy, r):
	v = (1 + noise.pnoise2(vx, vy, 1))/2.0
	a = v*0.3
	context.set_source_rgba(*color_of(0x333333, a=0.1))
	context.arc(x, y, r, 0, 2*math.pi)
	context.fill()

	context.set_line_width(1.0)
	context.set_source_rgba(*color_of(0x333333, a=0.3))
	context.arc(x, y, r, 0, 2*math.pi)
	context.stroke()

def main():
	parser = lib.create_options()
	parser.add_option('--size', default=20, dest='size', type='int',
		help='')
	opts, args = parser.parse_args()

	w, h = 24 * 72, 36 * 72


	pad = Padding(w/16.0, w/16.0, w/16.0, w/16.0)

	vw = w - pad.l - pad.r
	vh = h - pad.t - pad.b

	surface = lib.create_surface(opts.fmt, os.path.basename(__file__), w, h)
	context = cairo.Context(surface)

	context.rectangle(0, 0, w, h)
	context.set_source_rgb(*color_of(0xffffff))
	context.fill()

	nx = int(math.ceil(vw / float(opts.size)))
	ny = int(math.ceil(vh / float(opts.size)))

	mask = HeartMask(nx, ny)

	for j in range(ny):
		for i in range(nx):
			r, g, b = rgb_of(mask.pixel_at(i, j))
			if luminance(r, g, b) < 0.5:
				draw_doodle_dah(context,
					pad.l + i*opts.size + opts.size/2.0,
					pad.t + j*opts.size + opts.size/2.0,
					i / 8.0,
					j / 8.0,
					opts.size*0.3)
			else:
				draw_empty_spot(context,
						pad.l + i*opts.size + opts.size/2.0,
						pad.t + j*opts.size + opts.size/2.0,
						i / 8.0,
						j / 8.0,
						opts.size*0.3)

			context.set_source_rgb(*color_of(0x333333))
			context.arc(
				pad.l + i*opts.size + opts.size/2.0,
				pad.t + j*opts.size + opts.size/2.0,
				opts.size * 0.1,
				0,
				2*math.pi)
			context.fill()


	lib.commit(surface, os.path.basename(__file__) + '.png')

if __name__ == '__main__':
	sys.exit(main())