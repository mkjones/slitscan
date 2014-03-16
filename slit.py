#!/usr/local/Cellar/python/2.7.6/bin/python

import subprocess as sp
import numpy
import re
import Image
from Video import Video
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

    args = parser.parse_args()
    file = args.f
    filename = file.name
    num_rows = args.r
    slit_position = args.p

    if (slit_position < 0 or slit_position > 1):
        print >>sys.stderr, "Invalid slit position %0.2f.  Must be on [0, 1]." % slit_position
        parser.print_usage(sys.stderr)
        sys.exit(1)

    video = Video(filename)
    processor = SlitProcessor(video, slit_position, num_rows)
    image_path = processor.getAndSaveSlitscan()

    print image_path
    sys.exit()

    # only fetch the frames from ffmpeg once, and store them in memory
    frames = [x for x in frames]

    # for every slit in the original video, generate a slitscan image
    for row_index in xrange(0, 720 - num_rows, 4):
        print "processing row index %d" % row_index
        final_image = get_final_array(frames, num_rows, row_index, num_frames)
        name = filename.split('/')[-1]
        name = name.split('.')[0]
        name = '/Users/mkjones/slitscan/%s-%d-%03d.png' % (name, num_rows, row_index)
        Image.fromarray(final_image).save(name)
