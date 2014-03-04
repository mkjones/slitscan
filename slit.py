#!/usr/local/Cellar/python/2.7.3/bin/python

import subprocess as sp
import numpy
import pylab
import time
import sys
import re
import Image

# the file from which we read. Expected to be a video of
# width 1280px x 720px.
FILE_NAME = '/Users/mkjones/slitscan/walking2.MOV'

# How many rows should we take from each frame?
NUM_ROWS = 3

# Where (of the 720 rows) should we start pulling rows from?
ROW_INDEX = 350

def get_num_frames(filename):
    info_args = ('ffmpeg', '-i', filename, '-vcodec', 'copy',
                 '-f', 'null', '/dev/null')
    pipe = sp.Popen(info_args, stdin = sp.PIPE, stdout = sp.PIPE,
                    stderr = sp.PIPE)
    (stdout, stderr) = pipe.communicate()
    matches = re.search('frame= (\d+)', stderr)
    return int(matches.group(1))

def get_final_array(filename, num_rows, row_index, num_frames):

    args = [
        'ffmpeg',
        "-i",
        filename,
        "-f",
        "image2pipe",
        "-pix_fmt",
        "rgb24",
        "-vcodec",
        "rawvideo",
        "-"
        ]

    pipe = sp.Popen(args, stdin = sp.PIPE, stdout = sp.PIPE,
                    stderr = sp.PIPE)
    final_image = numpy.zeros((num_frames*num_rows, 1280,3), 'uint8')
    for i in xrange(num_frames):
        image_bytes = pipe.stdout.read(1280*720*3)
        image = numpy.fromstring(image_bytes, dtype='uint8').reshape((720, 1280, 3))
        x1 = row_index
        x2 = row_index + num_rows

        sub_image = image[row_index + num_rows, 0:1280, :]
        frame_index = num_rows*i
        final_image[frame_index:(frame_index+NUM_ROWS)] = sub_image

    return numpy.rot90(final_image)

if __name__ == '__main__':
    num_frames = get_num_frames(FILE_NAME)
    final_image = get_final_array(FILE_NAME, NUM_ROWS, ROW_INDEX, num_frames)
    Image.fromarray(final_image).save('/Users/mkjones/slitscan/out.jpg')
