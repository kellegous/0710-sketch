#!/usr/bin/env python2.7

import glob
import optparse
import os
import subprocess
import sys

def main():
  base = os.path.dirname(__file__)

  parser = optparse.OptionParser()
  parser.add_option('--grid-size',
      type='int',
      dest='grid',
      default=20,
      help='')
  opts, args = parser.parse_args()
  for dir in args:
    for src in glob.glob("%s/*.jpg" % dir):
      dst = src[:-4] + '.png'
      print src
      if subprocess.call([
          os.path.join(base, 'render'),
          '--grid-size=%d' % opts.grid,
          src,
          dst]) != 0:
        return 1

if __name__ == '__main__':
  sys.exit(main())