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

Pt = collections.namedtuple('Pt', ['x', 'y'])

def color_of(r, g, b, a = None):
	vals = [x/255.0 for x in (r, g, b)]
	if a is None:
		return vals
	return vals + [a]

def create_seed():
	s = hex(int(time.time() * 1000))
	return s[2:]

def main():
	parser = optparse.OptionParser()
	parser.add_option('--seed', default=create_seed(), dest='seed', help='')
	parser.add_option('--fmt', default='pdf', dest='fmt', help='')
	parser.add_option('--nx', default=100, dest='nx', type='int', help='')
	opts, args = parser.parse_args()

	print('seed = %s' % opts.seed)	
	random.seed(opts.seed)

	w, h = 16 * 72, 10 * 72

	surface = lib.create_surface(opts.fmt, os.path.basename(__file__), w, h)
	context = cairo.Context(surface)

	context.rectangle(0, 0, w, h)
	context.set_source_rgb(1, 1, 1)
	context.fill()

	pad = w/16.0
	pa = Pt(pad, pad + (h - 2*pad) * random.random())
	pb = Pt(w - pad, pad + (h - 2*pad) * random.random())

	dx = pb.x - pa.x
	dy = pb.y - pa.y
	n = math.sqrt(dx*dx + dy*dy)
	m = dy / dx

	context.move_to(pa.x, pa.y)
	context.line_to(pb.x, pb.y)
	context.set_source_rgb(*color_of(0xaa, 0xaa, 0xaa))
	context.stroke()

	di = dx / opts.nx
	context.set_line_width(1.0)
	context.set_source_rgb(*color_of(0xee, 0xee, 0xee))
	for i in range(opts.nx + 1):
		context.move_to(pa.x + di*i, pad)
		context.line_to(pa.x + di*i, h - 2*pad)
		context.stroke()

	dj = 0.0
	r = 5

	pts = []
	for i in range(opts.nx + 1):
		x = di*i
		pts.append(Pt(pa.x + x, x*m + pa.y + r*noise.pnoise1(x/10.0, 1)))
		#pts.append(Pt(pa.x + x, x*m + pa.y + dj))
		#dj = max(min(dj + random.random()*r - r/2.0, r), -r)

	context.move_to(pts[0].x, pts[0].y)
	for i in range(1, len(pts)):
		# context.line_to(pts[i].x, pts[i].y)
		a = pts[i - 1]
		b = pts[i]
		context.curve_to(
			a.x + di/2.0, a.y,
			b.x - di/2.0, b.y,
			b.x, b.y)
	context.set_source_rgb(*color_of(0xff, 0x00, 0xff))
	context.stroke()


	lib.commit(surface, os.path.basename(__file__) + '.png')

if __name__ == '__main__':
	sys.exit(main())