
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

def find_most_similar(target, buf, iter, last_frame_idx, speedup):
    debug('finding most similar')
    target_int = gauss(target).astype(int)
    buf_gaus = [(x[0], gauss(x[1])) for x in buf]
    diffs = [(x[0], get_diff(target_int, x[1].astype(int))) for x in buf_gaus]
    adjusted_diffs = []
    for i in range(len(diffs)):
        (frame_idx, raw_diff) = diffs[i]
        distance = abs(frame_idx - last_frame_idx - speedup)
        distance_cost = (distance * distance) + 1
        adjusted_diffs.append((frame_idx, distance_cost * raw_diff))

    max_diff = float(max([x[1] for x in adjusted_diffs]))
    normalized_adjusted_diffs = [(x[0], x[1] / max_diff) for x in adjusted_diffs]
    debug('got diffs')

    argmin = numpy.argmin([x[1] for x in adjusted_diffs])
    debug('Picked frame %d of %d (distances from prev chosen frame: [%s]' %
          (argmin, len(buf), ', '.join([str(x) for x in normalized_adjusted_diffs])))

    misc.imsave('/tmp/img-%d.jpg' % iter, target)
    for i in range(len(diffs)):
        misc.imsave('/tmp/img-%d-%d-%d-%0.2f.jpg' % (RESIZE_SIZE, iter, i, normalized_adjusted_diffs[i][1]),
                    buf_gaus[i][1])
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
    writer = VideoWriter('%s-t2-%dx-%d.avi' % (reader.getBaseOutputName(), speedup, RESIZE_SIZE))

    buf = []
    last_frame = None
    last_frame_idx = None

    i = -1
    for frame in reader.getFrames():
        i += 1
        # initialize the "last_frame" with the first frame of the video
        if last_frame == None:
            last_frame = frame
            last_frame_idx = 0
            continue

        buf.append((i, frame))

        # if we have a not-full buffer, we're done
        if len(buf) != speedup:
            continue

        # we have a full buffer!  pick the "best" frame from it and use that one
        debug('picking best frame from %d preceding frame %d' % (len(buf), i))

        new_frame_idx = find_most_similar(last_frame, buf, i, last_frame_idx, speedup)
        new_frame = buf[new_frame_idx][1]
        writer.appendFrame(new_frame)
        last_frame = new_frame
        last_frame_idx = buf[new_frame_idx][0]
        buf = buf[new_frame_idx:]

    writer.done()
