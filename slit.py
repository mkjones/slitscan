#!/usr/local/Cellar/python/2.7.3/bin/python

import subprocess as sp
import numpy
import pylab
import time
import matplotlib.pyplot as plt
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

info_args = ('ffmpeg', '-i', FILE_NAME, '-vcodec', 'copy',
             '-f', 'null', '/dev/null')
pipe = sp.Popen(info_args, stdin = sp.PIPE, stdout = sp.PIPE,
                stderr = sp.PIPE)
(stdout, stderr) = pipe.communicate()
matches = re.search('frame= (\d+)', stderr)
num_frames = int(matches.group(1))

args = [
    'ffmpeg',
    "-i",
    FILE_NAME,
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
final_image = numpy.zeros((num_frames*NUM_ROWS, 1280,3), 'uint8')
for i in xrange(num_frames):
    image_bytes = pipe.stdout.read(1280*720*3)
    image = numpy.fromstring(image_bytes, dtype='uint8').reshape((720, 1280, 3))
    x1 = ROW_INDEX
    x2 = ROW_INDEX + NUM_ROWS

    sub_image = image[ROW_INDEX + NUM_ROWS, 0:1280, :]
    frame_index = NUM_ROWS*i
    final_image[frame_index:(frame_index+NUM_ROWS)] = sub_image

Image.fromarray(numpy.rot90(final_image)).save('/Users/mkjones/out.jpg')
sys.exit()

plt.imshow(numpy.rot90(final_image))
plt.savefig('/Users/mkjones/figure.jpg')
