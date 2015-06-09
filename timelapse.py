
import argparse
import numpy
from scipy import ndimage, misc
import sys

from Video import VideoReader, VideoWriter
from timedebug import debug

RESIZE_SIZE = 128

def get_diff(im1, im2):
    """ Gets the difference between two images.  Very dumb: just sums
    the absolute differences of all pixels."""
    diff = im1 - im2
    diff_abs = abs(diff)
    diff_flat = diff_abs.flat
    diff_sum = numpy.sum(diff_flat)
    return diff_sum

def gauss(frame):
    """ Grayscale and apply a gaussian blur to the given frame """
    frame = misc.imresize(frame, (RESIZE_SIZE, RESIZE_SIZE))
    frame = numpy.dot(frame, [0.299, 0.587, 0.144])
    frame = ndimage.filters.gaussian_filter(frame, 3)
    return frame

def find_most_similar(target, buf, iter):
    debug('finding most similar')
    target_int = gauss(target).astype(int)
    buf_gaus = [gauss(x) for x in buf]
    diffs = [get_diff(target_int, x.astype(int)) for x in buf_gaus]
    max_diff = float(max(diffs))
    diffs = [x / max_diff for x in diffs]
    debug('got diffs')

    argmin = numpy.argmin(diffs)
    debug('Picked frame %d of %d (distances from prev chosen frame: [%s]' %
          (argmin, len(buf), ', '.join([str(x) for x in diffs])))

    misc.imsave('/tmp/img-%d.jpg' % iter, target)
    for i in range(len(diffs)):
        misc.imsave('/tmp/img-%d-%d-%d-%0.2f.jpg' % (RESIZE_SIZE, iter, i, diffs[i]),
                    buf_gaus[i])
        i += 1
    return argmin


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a slightly smarter than navie timelapse')
    parser.add_argument('-s', metavar='speedup', type=int, default=8,
                        help='How many times should we speed up the video? e.g. 8 means 8 '
                        'times as fast.')
    parser.add_argument('-i', metavar='input_video', required=True, type=argparse.FileType(),
                        help='Path to the input video file')

    args = parser.parse_args()
    speedup = args.s
    input_filename = args.i.name

    reader = VideoReader(input_filename)
    debug('reader: %s' % reader)
    writer = VideoWriter('%s-%dx-%d.avi' % (reader.getBaseOutputName(), speedup, RESIZE_SIZE))

    buf = []
    last_frame = None

    i = -1
    for frame in reader.getFrames():
        i += 1
        # initialize the "last_frame" with the first frame of the video
        if last_frame == None:
            last_frame = frame
            continue

        # if we have a not-full buffer, just add this frame to it
        if len(buf) != speedup:
            buf.append(frame)
            continue

        # we have a full buffer!  pick the "best" frame from it and use that one
        debug('picking best frame from %d preceding frame %d' % (speedup, i))

        new_frame_idx = find_most_similar(last_frame, buf, i)
        new_frame = buf[new_frame_idx]
        writer.appendFrame(new_frame)
        last_frame = new_frame
        buf = []

    writer.done()
