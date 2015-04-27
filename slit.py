#!/usr/local/Cellar/python/2.7.6/bin/python

import subprocess as sp
import numpy
import re
from PIL import Image
from Video import VideoReader, MemoizedVideoReader, VideoWriter, ImageListVideoReader
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
    parser.add_argument('-m', metavar='mode', choices=('normal', 'video', 'average'), default='normal')
    parser.add_argument('-e', metavar='video_row_every', type=int, default=1,
                        help='Applicable only if we\'re in video mode.  We will generate a frame '
                        'every N rows.  If you have a large input video and want a small output '
                        'video, increase this from the default of 1.  For example, 10 will make a '
                        'frame from every 10th row of pixels.  1 will create every possible frame.')


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


    if args.m == 'video':
        video = MemoizedVideoReader(filename)
        out_filename = '%s.avi' % '.'.join(filename.split('.')[0:-1])
        writer = VideoWriter(out_filename)
        for slit_position in xrange(0, video.getHeight() - num_rows, args.e):
            print "processing slit position %d" % slit_position
            processor = SlitProcessor(video, slit_position, num_rows)
            image = processor.getSlitscan()
            writer.appendFrame(image)
        writer.done()

    elif args.m == 'normal':
        video = VideoReader(filename)
        slit_position = int(slit_position * video.getHeight())
        for slit_position in xrange(0, video.getHeight(), video.getHeight() / 6):
            processor = SlitProcessor(video, slit_position, num_rows)
            image_path = processor.getAndSaveSlitscan()
            print image_path

    elif args.m == 'average':
        video = VideoReader(filename)
        num_frames = video.getNumFrames()
        final_image = numpy.zeros((video.getHeight(), video.getWidth(), 3))
        num_frames = 0
        for im in video.getFrames():
            final_image += im
            num_frames += 1
        final_image = final_image / num_frames
        filename = '%s-avg.png' % (video.getBaseOutputName())
        Image.fromarray(final_image.astype('uint8')).save(filename)

