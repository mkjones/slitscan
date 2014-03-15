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

        sub_image = image[row_index + num_rows, 0:1280, :]
        frame_index = num_rows*i
        final_image[frame_index:(frame_index+NUM_ROWS)] = sub_image
        i += 1

    for i in xrange(3):
        final_image = numpy.rot90(final_image)
    return final_image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert video to slitscan image.')
    parser.add_argument('-f', help='The filename to the video', metavar='filename', required=True)
    args = parser.parse_args()
    filename = args.f

    video = Video(filename)
    num_frames = video.getNumFrames()
    frames = video.yieldFrames()
    final_image = get_final_array(frames, NUM_ROWS, 400, num_frames)

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
    for row_index in xrange(720 - NUM_ROWS):
        print "processing row index %d" % row_index
        final_image = get_final_array(frames, NUM_ROWS, row_index, num_frames)
        name = filename.split('/')[-1]
        name = name.split('.')[0]
        name = '/Users/mkjones/slitscan/%s-%d-%03d.png' % (name, NUM_ROWS, row_index)
        Image.fromarray(final_image).save(name)
