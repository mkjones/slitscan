#!/usr/local/Cellar/python/2.7.3/bin/python

import subprocess as sp
import numpy
import re
import Image

# the file from which we read. Expected to be a video of
# width 1280px x 720px.
FILE_NAME = '/Users/mkjones/Movies/outside_work_for_slit.MP4'

# How many rows should we take from each frame?
NUM_ROWS = 1

# Where (of the 720 rows) should we start pulling rows from?
ROW_INDEX = 200

# True if your video has the "top" to the left
# False if it has the "top" to the right.
LEFT_IS_TOP = True

def get_num_frames(filename):
    info_args = ('ffmpeg', '-i', filename, '-vcodec', 'copy',
                 '-f', 'rawvideo', '-y', '/dev/null')
    pipe = sp.Popen(info_args, stdin = sp.PIPE, stdout = sp.PIPE,
                    stderr = sp.PIPE)
    (stdout, stderr) = pipe.communicate()
    matches = re.search('frame= *(\d+)', stderr)
    return int(matches.group(1))

def get_final_array(filename, num_rows, row_index, num_frames, top_is_left):

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
                    stderr = sp.PIPE, bufsize=1280*720*3)
    final_image = numpy.zeros((num_frames*num_rows, 1280,3), 'uint8')
    for i in xrange(num_frames):
        image_bytes = pipe.stdout.read(1280*720*3)
        image = numpy.fromstring(image_bytes, dtype='uint8').reshape((720, 1280, 3))
        if top_is_left:
            image = numpy.rot90(image)
            image = numpy.rot90(image)
        x1 = row_index
        x2 = row_index + num_rows

        sub_image = image[row_index + num_rows, 0:1280, :]
        frame_index = num_rows*i
        final_image[frame_index:(frame_index+NUM_ROWS)] = sub_image

    return numpy.rot90(final_image)

if __name__ == '__main__':
    num_frames = get_num_frames(FILE_NAME)
    final_image = get_final_array(FILE_NAME, NUM_ROWS, ROW_INDEX, num_frames, TOP_IS_LEFT)
    name = FILE_NAME.split('/')[-1]
    name = name.split('.')[0]
    name = '/Users/mkjones/slitscan/%s-%d-%d.png' % (name, NUM_ROWS, ROW_INDEX)
    Image.fromarray(final_image).save(name)
