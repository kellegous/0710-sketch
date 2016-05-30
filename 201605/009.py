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

def create_font_desc():
	desc = pango.FontDescription('Acumin Pro 288')
	desc.set_weight(pango.WEIGHT_HEAVY)
	desc.set_stretch(pango.STRETCH_NORMAL)
	return desc


def main():
	parser = lib.create_options()
	opts, args = parser.parse_args()

	w, h = 24 * 72, 36 * 72

	surface = lib.create_surface(opts.fmt, os.path.basename(__file__), w, h)
	context = cairo.Context(surface)

	context.set_source_rgb(1, 1, 1)
	context.rectangle(0, 0, w, h)
	context.fill()

	pctx = pangocairo.CairoContext(context)
	pctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

	layout = pctx.create_layout()
	layout.set_font_description(
		create_font_desc())
	layout.set_text('12')
	context.set_source_rgb(*color_of(0x0099ff))
	pctx.update_layout(layout)
	pctx.show_layout(layout)

	ink_rect, log_rect = layout.get_pixel_extents()
	context.rectangle(*ink_rect)
	context.set_source_rgba(*color_of(0x333333, a=0.5))
	context.stroke()

	context.rectangle(*log_rect)
	context.set_source_rgba(*color_of(0x333333, a=0.5))
	context.stroke()

	lib.commit(surface, os.path.basename(__file__) + '.png')

if __name__ == '__main__':
	sys.exit(main())