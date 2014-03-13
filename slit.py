#!/usr/local/Cellar/python/2.7.6/bin/python

import subprocess as sp
import numpy
import re
import Image

# the file from which we read. Expected to be a video of
# size 1280px x 720px.
FILE_NAME = '/Users/mkjones/Movies/spinning_in_chair.mov'
FILE_NAME = '/Users/mkjones/Movies/outside_work_for_slit.MP4'

# How many rows should we take from each frame?
NUM_ROWS = 1

# True if your video has the "top" to the left
# False if it has the "top" to the right.
TOP_IS_LEFT = True

def get_num_frames(filename):
    info_args = ('ffmpeg', '-i', filename, '-vcodec', 'copy',
                 '-f', 'rawvideo', '-y', '/dev/null')
    pipe = sp.Popen(info_args, stdin = sp.PIPE, stdout = sp.PIPE,
                    stderr = sp.PIPE)
    (stdout, stderr) = pipe.communicate()
    matches = re.search('frame= *(\d+)', stderr)
    return int(matches.group(1))

def yield_frames(filename, num_frames, top_is_left):
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

    for i in xrange(num_frames):
        image_bytes = pipe.stdout.read(1280*720*3)
        image = numpy.fromstring(image_bytes, dtype='uint8').reshape((720, 1280, 3))
        if top_is_left:
            image = numpy.rot90(image)
            image = numpy.rot90(image)
        yield image

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

    return final_image
    return numpy.rot90(final_image)

if __name__ == '__main__':
    num_frames = get_num_frames(FILE_NAME)
    frames = yield_frames(FILE_NAME, num_frames, TOP_IS_LEFT)

    # only fetch the frames from ffmpeg once, and store them in memory
    frames = [x for x in frames]

    # for every slit in the original video, generate a slitscan image
    for row_index in xrange(720 - NUM_ROWS):
        print "processing row index %d" % row_index
        final_image = get_final_array(frames, NUM_ROWS, row_index, num_frames)
        name = FILE_NAME.split('/')[-1]
        name = name.split('.')[0]
        name = '/Users/mkjones/slitscan/%s-%d-%03d.png' % (name, NUM_ROWS, row_index)
        Image.fromarray(final_image).save(name)
