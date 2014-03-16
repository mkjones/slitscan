#!/usr/local/Cellar/python/2.7.6/bin/python

import subprocess as sp
import numpy
import re
import Image
from Video import VideoReader, MemoizedVideoReader, VideoWriter
from SlitProcessor import SlitProcessor
import argparse
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert video to slitscan image.')
    parser.add_argument('-f', metavar='filename', required=True, type=argparse.FileType(),
                        help='The filename to the video')
    parser.add_argument('-r', metavar='num_pixel_rows_per_frame', type=int, default=1,
                        help='How many consecutive rows of pixels should we take from '
                        'each frame? Increase if your image is too narrow. Anything '
                        'greater than 1 will make things look a bit jagged.')
    parser.add_argument('-p', metavar='slit_position', type=float, default=0.5,
                        help="Where in the frame is the slit?  Should be a decimal from "
                        "[0, 1] representing the percent offset from the left of the frame.")
    parser.add_argument('-v', action="store_true",
                        help="Make a video, instead of just a single frame.")

    args = parser.parse_args()
    file = args.f
    filename = file.name
    num_rows = args.r
    slit_position = args.p

    if num_rows < 0:
        print >>sys.stderr, "Must use at least one row (got %d)" % num_rows
        parser.print_usage(sys.stderr)
        sys.exit(1)

    if (slit_position < 0 or slit_position > 1):
        print >>sys.stderr, "Invalid slit position %0.2f.  Must be on [0, 1]." % slit_position
        parser.print_usage(sys.stderr)
        sys.exit(1)

    make_video = args.v
    if make_video:
        video = MemoizedVideoReader(filename)
        out_filename = '%s.avi' % '.'.join(filename.split('.')[0:-1])
        writer = VideoWriter(out_filename)
        for slit_position in xrange(0, 720 - num_rows, 1):
            print "processing slit position %d" % slit_position
            processor = SlitProcessor(video, slit_position, num_rows)
            image = processor.getSlitscan()
            writer.appendFrame(image)
        writer.done()

    else:
        video = MemoizedVideoReader(filename)
        # slit_position = int(slit_position * video.getHeight())
        for slit_position in xrange(0, video.getHeight(), 90):
            processor = SlitProcessor(video, slit_position, num_rows)
            image_path = processor.getAndSaveSlitscan()
            print image_path
