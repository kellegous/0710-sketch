#!/usr/bin/env python2.7

import glob
import optparse
import os
import subprocess
import sys

def main():
  base = os.path.dirname(__file__)

  parser = optparse.OptionParser()
  parser.add_option('--grid-sizes',
      dest='sizes',
      default='10,12,15,20',
      help='')
  opts, args = parser.parse_args()
  sizes = [int(x.strip()) for x in opts.sizes.split(',')]

  for dir in args:
    for src in glob.glob("%s/*.jpg" % dir):
      for size in sizes:
        dst = "%s_%d.png" % (src[:-4], size)
        if os.path.exists(dst):
          continue
        print '%s (%d)' % (src, size)
        if subprocess.call([
            os.path.join(base, 'render'),
            '--grid-size=%d' % size,
            src,
            dst]) != 0:
          return 1

if __name__ == '__main__':
  sys.exit(main())