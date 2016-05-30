
import base64
import cairo
import collections
import optparse
import random
import StringIO
import svg.path
import time

Pt = collections.namedtuple('Pt', ['x', 'y'])

Rect = collections.namedtuple('Rect', ['x', 'y', 'w', 'h'])

Padding = collections.namedtuple('Padding', ['t', 'r', 'b', 'l'])

class Path(object):
	def __init__(self, path):
		self.path = path

	def translate(self, dx, dy):
		dv = complex(dx, dy)
		for seg in self.path:
			seg.start += dv
			seg.end += dv
			if isinstance(seg, svg.path.CubicBezier):
				seg.control1 += dv
				seg.control2 += dv
			elif isinstance(seg, svg.path.QuadraticBezier):
				seg.control += dv
		return self

	def scale(self, sx, sy):
		for seg in self.path:
			seg.start = complex(seg.start.real * sx, seg.start.imag * sy)
			seg.end = complex(seg.end.real * sx, seg.end.imag * sy)
			if isinstance(seg, svg.path.CubicBezier):
				seg.control1 = complex(seg.control1.real * sx, seg.control1.imag * sy)
				seg.control2 = complex(seg.control2.real * sx, seg.control2.imag * sy)
			elif isinstance(seg, svg.path.QuadraticBezier):
				seg.control = complex(seg.control.real * sx, seg.control.imag * sy)
		return self

	def draw(self, context):
		path = self.path
		if len(path) == 0:
			return self

		first = path[0].start
		context.move_to(first.real, first.imag)

		for seg in self.path:
			# TODO(knorton): for now assume the segment is smooth from
			# the previous/current point.
			if isinstance(seg, svg.path.CubicBezier):
				ctrl1 = seg.control1
				ctrl2 = seg.control2
				point = seg.end
				context.curve_to(
					ctrl1.real, ctrl1.imag,
					ctrl2.real, ctrl2.imag,
					point.real, point.imag)
			elif isinstance(seg, svg.path.QuadraticBezier):
				raise Exception('not implemented: %s' % seg)
			elif isinstance(seg, svg.path.Arc):
				raise Exception('not implemented: %s' % seg)
			elif isinstance(seg, svg.path.Line):
				pt = seg.end
				context.line_to(pt.real, pt.imag)

def parse_svg_path(path):
	return Path(svg.path.parse_path(path))

def color_of(r, g=None, b=None, a = None):
	if g is None and b is None:
		c = r
		r = (c >> 16) & 0xff
		g = (c >> 8) & 0xff
		b = c & 0xff
		if a is None:
			a = (c >> 24) & 0xff
			if a == 0:
				a = None
	vals = [x/255.0 for x in (r, g, b)]
	if a is None:
		return vals

	return vals + [a]


class Options(object):
	def __init__(self, parser):
		self.parser = parser

	def add_option(self, name, **kwargs):
		self.parser.add_option(name, **kwargs)
		return self

	def parse_args(self):
		opts, args = self.parser.parse_args()
		print 'seed = %s' % opts.seed
		random.seed(opts.seed)
		return opts, args

def create_options():
	def create_seed():
		s = hex(int(time.time() * 1000))
		return s[2:]
	parser = optparse.OptionParser()
	parser.add_option('--seed', default=create_seed(), dest='seed',
		help='magic seed')
	parser.add_option('--fmt', default='pdf', dest='fmt',
		help='the file format [svg or pdf]')
	parser.add_option('--debug', default=False, action='store_true',
		help='debug mode')
	return Options(parser)

def create_surface(fmt, basename, w, h):
	if fmt == 'pdf':
		return cairo.PDFSurface(basename + '.pdf', w, h)

	if fmt == 'svg':
		return cairo.SVGSurface(basename + '.svg', w, h)

	return cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)

def commit(surface, filename):
	buf = StringIO.StringIO()

	surface.write_to_png(buf)

	with open(filename, 'w') as w:
		w.write(buf.getvalue())

	data = base64.b64encode(buf.getvalue())
	name = base64.b64encode(filename)
	print "\033]1337;File=%s;size=%d;inline=1:%s\a" % (name, len(data), data)
