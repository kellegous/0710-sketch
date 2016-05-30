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
import sys
import time
import pprint

import lib

Pad = collections.namedtuple('Pad', ['t', 'r', 'b', 'l'])

Pt = collections.namedtuple('Pt', ['x', 'y'])

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

class Sketcher(object):
	def __init__(self, r, f, n=200):
		self.r = r
		self.f = f
		self.n = n

	def draw(self, context, pa, pb):
		n = self.n

		dx = pb.x - pa.x
		dy = pb.y - pa.y
		m = dy / dx

		di = dx / float(n)

		r = self.r
		f = self.f
		dj = 0.0

		pts = []
		for i in range(n + 1):
			x = di*i
			pts.append(Pt(
				pa.x + x,
				pa.y + x*m + r*noise.pnoise2(i/f, (pa.y + x*m)/f, 1)))

		context.set_line_width(1.0)
		context.move_to(pa.x, pa.y)
		for i in range(1, len(pts)):
			a = pts[i - 1]
			b = pts[i]
			context.curve_to(
				a.x + di/2.0, a.y,
				b.x - di/2.0, b.y,
				b.x, b.y)
		context.stroke()

def color_of(r, g, b, a = None):
	vals = [x/255.0 for x in (r, g, b)]
	if a is None:
		return vals
	return vals + [a]

def create_seed():
	s = hex(int(time.time() * 1000))
	return s[2:]

def unit_normal(pa, pb):
	""" find a unit vector that is orthogonal to the line formed by pa and pb. """
	dx = pa.x - pb.x
	dy = pa.y - pb.y
	d = math.sqrt(dx*dx + dy*dy)
	return (-dy / d, dx / d)

def sketch_line(context, pa, pb, n=200):
	dx = pb.x - pa.x
	dy = pb.y - pa.y
	m = dy / dx

	di = dx / float(n)

	r = 5.0
	dj = 0.0

	pts = []
	for i in range(n + 1):
		x = di*i
		dj = max(min(dj + random.random()*r - r/2.0, r), -r)
		pts.append(Pt(pa.x + x, x*m + pa.y + dj))

	context.set_line_width(1.0)
	context.move_to(pa.x, pa.y)
	for i in range(1, len(pts)):
		a = pts[i - 1]
		b = pts[i]
		context.curve_to(
			a.x + di/2.0, a.y,
			b.x - di/2.0, b.y,
			b.x, b.y)
	context.stroke()

	# for i in range(n + 1):
	# 	x = di*i
	# 	dj = max(min(dj + random.random()*r - r/2.0, r), -r)
	# 	context.line_to(pa.x + x, x*m + pa.y + dj)
	# context.stroke()

def draw_line(context, pa, pb):
	dy = pb.y - pa.y
	dx = pb.x - pa.x
	m = dy / dx
	n = math.sqrt(dx*dx + dy*dy)
	context.move_to(pa.x, pa.y)
	context.line_to(pb.x, pb.y)
	context.stroke()

def draw_hatches(context, x, y, w, h, ny,
		color=[0, 0, 0, 1],
		draw_line=draw_line):
	ax = w * random.random()
	bx = w * random.random()

	v = unit_normal(Pt(ax, 0), Pt(bx, h))
	m = v[1] / v[0]

	dy = (h + abs(w*m)) / ny
	oy = max(w*m, 0)

	context.set_source_rgba(*color)
	for j in range(0, ny + 1):
		draw_line(context,
			Pt(x, y + dy*j - oy),
			Pt(x + w, y + w*m + dy*j - oy))

def main():
	parser = optparse.OptionParser()
	parser.add_option('--seed', default=create_seed(), dest='seed', help='')
	parser.add_option('--fmt', default='pdf', dest='fmt', help='')
	parser.add_option('--ny', default=250, dest='ny', type='int', help='')
	parser.add_option('--debug', default=False, action='store_true', help='')
	opts, args = parser.parse_args()

	print('seed = %s' % opts.seed)
	random.seed(opts.seed)

	debug_color = color_of(0x00, 0x99, 0xff)

	w, h = 24 * 72, 36 * 72

	pad = Pad(h/32, h/32, h/32, h/32)

	surface = lib.create_surface(opts.fmt, os.path.basename(__file__), w, h)
	context = cairo.Context(surface)

	vw, vh = w - pad.l - pad.r, h - pad.t - pad.b

	context.rectangle(0, 0, w, h)
	context.set_source_rgb(1.0, 1.0, 1.0)
	context.fill()

	bg_sketcher = Sketcher(5.0, 1.0, 300)
	context.save()
	context.rectangle(pad.l, pad.t, vw, vh)
	context.clip()
	draw_hatches(context,
		pad.l,
		pad.t,
		vw,
		vh,
		opts.ny,
		color_of(0x44, 0x44, 0x44, 1.0),
		bg_sketcher.draw)
	context.restore()

	scale = vw/24.0
	path = lib.parse_svg_path(HEART).scale(scale, scale)

	context.save()
	context.translate(w/2.0, h/2.0)
	path.draw(context)
	context.set_source_rgba(*color_of(0xff, 0xff, 0xff, 1.0))
	context.fill()

	context.set_line_width(10.0)
	path.draw(context)
	context.set_source_rgba(*color_of(0xff, 0xff, 0xff, 1.0))
	context.stroke()
	context.restore()

	context.save()
	context.translate(w/2.0, h/2.0)
	path.draw(context)
	context.clip()

	ht_sketcher = Sketcher(10.0, 1.0, 250)
	draw_hatches(context,
		-scale*10,
		-scale*10,
		scale*20,
		scale*20,
		int(opts.ny * 0.6),
		color_of(0xff, 0x00, 0x00, 1.0),
		ht_sketcher.draw)
	context.restore()

	# context.save()
	# context.set_line_width(8.0)
	# context.rectangle(pad.l, pad.t, vw, vh)
	# context.set_source_rgb(*color_of(0x33, 0x33, 0x33))
	# context.stroke()
	# context.restore()

	if opts.debug:
		context.move_to(w / 2.0, 0)
		context.line_to(w / 2.0, h)
		context.set_source_rgb(*debug_color)
		context.stroke()

		context.move_to(0, h / 2.0)
		context.line_to(w, h / 2.0)
		context.set_source_rgb(*debug_color)
		context.stroke()

	lib.commit(surface, os.path.basename(__file__) + '.png')

if __name__ == '__main__':
	sys.exit(main())