#!/usr/local/Cellar/python/2.7.6/bin/python

import subprocess as sp
import numpy
import re
import Image
from Video import Video
import argparse

# How many consecutive rows should we take from each frame?
# (Useful if a video does not have many frames and the output image
# ends up looking too horizontally squished)
NUM_ROWS = 2

# True if your video has the "top" to the left
# False if it has the "top" to the right.
TOP_IS_LEFT = True

def get_final_array(frames, num_rows, row_index, num_frames):
    i = 0
    final_image = numpy.zeros((num_frames*num_rows, 1280,3), 'uint8')
    for image in frames:
        x1 = row_index
        x2 = row_index + num_rows

        # the value of the slit from this frame
        slit = image[x1:x2, 0:1280, :]

        # where do we start
        frame_index_start = num_rows*i
        frame_index_end = frame_index_start + num_rows
        final_image[frame_index_start:frame_index_end] = slit
        i += 1

    for i in xrange(3):
        final_image = numpy.rot90(final_image)
    return final_image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert video to slitscan image.')
    parser.add_argument('-f', metavar='filename', required=True,
                        help='The filename to the video')
    parser.add_argument('-r', metavar='num_pixel_rows_per_frame', type=int, default=1,
                        help='How many consecutive rows of pixels should we take from '
                        'each frame? Increase if your image is too narrow. Anything '
                        'greater than 1 will make things look a bit jagged.')
    args = parser.parse_args()
    filename = args.f
    num_rows = args.r

    video = Video(filename)
    num_frames = video.getNumFrames()
    frames = video.yieldFrames()
    final_image = get_final_array(frames, num_rows, 400, num_frames)

    filename_parts = filename.split('/')
    name = filename_parts[-1]
    name = name.split('.')[0]
    image_path = '%s/%s.png' % ('/'.join(filename_parts[0:-1]), name)

    Image.fromarray(final_image).save(image_path)
    print 'saved in %s' % image_path
    import sys
    sys.exit()

    # only fetch the frames from ffmpeg once, and store them in memory
    frames = [x for x in frames]

    # for every slit in the original video, generate a slitscan image
    for row_index in xrange(720 - num_rows):
        print "processing row index %d" % row_index
        final_image = get_final_array(frames, NUM_ROWS, row_index, num_frames)
        name = filename.split('/')[-1]
        name = name.split('.')[0]
        name = '/Users/mkjones/slitscan/%s-%d-%03d.png' % (name, NUM_ROWS, row_index)
        Image.fromarray(final_image).save(name)
