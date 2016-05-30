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

debug_color = color_of(0xff0099)

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

class Mask(object):
	def __init__(self, w, h, draw):
		surface = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
		context = cairo.Context(surface)

		draw(context, w, h)

		self.surface = surface

	def pixel_at(self, x, y):
		surface = self.surface
		stride = surface.get_stride()
		data = surface.get_data()
		idx = y*surface.get_stride() + x
		return struct.unpack('B', data[idx])[0]

def draw_heart(context, w, h):
	context.translate(w/2.0, h/2.0)
	context.set_source_rgb(0, 0, 0)
	lib.parse_svg_path(HEART).scale(w/24.0, w/24.0).draw(context)
	context.fill()

def draw_text(context, w, h):
	context.translate(w/2.0, 5.0 * h/6.0)
	pctx = pangocairo.CairoContext(context)
	pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
	layout = pctx.create_layout()
	layout.set_font_description(
		pango.FontDescription('Acumin Pro Heavy 30'))
	layout.set_text('12')
	pctx.update_layout(layout)

	_, rect = layout.get_pixel_extents()
	context.translate(-rect[2]/2.0, -rect[3]/4.0)
	pctx.show_layout(layout)

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

def draw_debug_lines(context, pad, w, h, n=6):
	context.set_line_width(1.0)
	context.set_source_rgb(*debug_color)
	
	context.move_to(pad.l + w/2.0, pad.t)
	context.line_to(pad.l + w/2.0, pad.t + h)
	context.stroke()

	context.move_to(pad.l, pad.t + h/2.0)
	context.line_to(pad.l + w, pad.t + h/2.0)
	context.stroke()
	# dx = w/float(n)
	# context.set_line_width(1.0)
	# for i in range(1, n):
	# 	context.set_source_rgb(*debug_color)
	# 	context.move_to(pad.l + i*dx, pad.t)
	# 	context.line_to(pad.l + i*dx, pad.t + h)
	# 	context.stroke()

def main():
	parser = lib.create_options()
	parser.add_option('--size', default=10, dest='size', type='int',
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

	heart_mask = Mask(nx, ny, draw_heart)
	text_mask = Mask(nx, ny, draw_text)

	for j in range(ny):
		for i in range(nx):
			a = text_mask.pixel_at(i, j)
			if a > 128:
				# context.set_source_rgb(*color_of(0xb3351a))
				# context.set_source_rgb(*color_of(0xef826b))
				context.set_source_rgb(*color_of(0x999999))
				context.arc(
					pad.l + i*opts.size + opts.size/2.0,
					pad.t + j*opts.size + opts.size/2.0,
					opts.size * 0.25,
					0,
					2*math.pi)
				context.fill()
				continue

			a = heart_mask.pixel_at(i, j)
			if a > 128:
				context.set_source_rgb(*color_of(0xef4723))
				context.arc(
					pad.l + i*opts.size + opts.size/2.0,
					pad.t + j*opts.size + opts.size/2.0,
					opts.size * 0.3,
					0,
					2*math.pi)
				context.fill()
				continue

			context.set_source_rgb(*color_of(0x999999))
			context.arc(
				pad.l + i*opts.size + opts.size/2.0,
				pad.t + j*opts.size + opts.size/2.0,
				opts.size * 0.2,
				0,
				2*math.pi)
			context.fill()

	if opts.debug:
		draw_debug_lines(context, pad, vw, vh, 12)

	lib.commit(surface, os.path.basename(__file__) + '.png')

if __name__ == '__main__':
	sys.exit(main())