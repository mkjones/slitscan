
import argparse
import math
import numpy
from scipy import ndimage, misc
import sys

from Video import VideoReader, VideoWriter
from timedebug import debug

RESIZE_SIZE = 64
ADJUSTMENT_CONST = 4000000

analytics_file = file('/tmp/analytics', 'w')
accumulated_error = 0

def gauss(frame_data):
    """ Grayscale and apply a gaussian blur to the given frame """
    frame_data = misc.imresize(frame_data, (RESIZE_SIZE, RESIZE_SIZE))
    frame_data = numpy.dot(frame_data, [0.299, 0.587, 0.144])
    frame_data = ndimage.filters.gaussian_filter(frame_data, 3)
    return frame_data.astype(int)

def get_pixel_distance(frame1, frame2):
    """ Gets the difference between two freames.  Very dumb: just takes the
    root mean squared pixel difference of the downsampled gaussian-blurred
    version of the images."""

    diff = frame1.gauss_data - frame2.gauss_data
    flat = diff.flat
    sum_squares = numpy.dot(flat, flat)
    return math.sqrt(sum_squares)


class Frame:
    def __init__(self, data, idx):
        self.data = data
        self.idx = idx
        self.gauss_data = gauss(self.data)

    def __str__(self):
        return 'Frame w/ index: %d' % self.idx

    def get_raw_distance(self, target):
        return get_pixel_distance(target, self)

    def get_adjustment(self, target, speedup, median_raw):
        global accumulated_error
        desired_idx = target.idx + speedup + (0.25 * accumulated_error)
        error = float(abs(self.idx - desired_idx))
        error_pct = error / speedup

        return pow(error_pct, 3) * median_raw

        coeff = None
        if error_pct < 0.125:
            coeff = 1
        elif error_pct < 0.25:
            coeff = 1.25
        elif error_pct < 0.375:
            coeff = 1.5
        elif error_pct < 0.5:
            coeff = 2
        elif error_pct < 0.75:
            coeff = 4
        else:
            coeff = 8
        return coeff * ADJUSTMENT_CONST

        adjustment_factor = pow(error, 2) + 2
        return adjustment_factor

    def get_distance(self, target, speedup, median_raw):
        raw_distance = self.get_raw_distance(target)
        adjustment_factor = self.get_adjustment(target, speedup, median_raw)
        debug('frame %d has raw dist: %d, adj_dist: %d factor: %0.3f' % (
            self.idx,
            raw_distance,
            raw_distance + adjustment_factor,
            adjustment_factor))

        return adjustment_factor + raw_distance


def find_most_similar(target, buf, iter, speedup):
    global accumulated_error
    debug('finding most similar to %d' % target.idx)

    raw_distances = [x.get_raw_distance(target) for x in buf]
    analytics_file.write('raw_distance\t%s\n' % '\t'.join([str(x) for x in raw_distances]))
    median_raw = numpy.median(raw_distances)
    max_raw = float(max(raw_distances))
    analytics_file.write('norm_raw_distance\t%s\n' % '\t'.join([str(x/max_raw) for x in raw_distances]))

    distances = [x.get_distance(target, speedup, median_raw) for x in buf]
    analytics_file.write('adjusted_distance\t%s\n' % '\t'.join([str(x) for x in distances]))

    max_diff = float(max(distances))
    norm_distances = [x / max_diff for x in distances]
    analytics_file.write('norm_adj_distances\t%s\n' % '\t'.join([str(x) for x in norm_distances]))

    analytics_file.write('adjustments\t%s\n' % '\t'.join(
        [str(x.get_adjustment(target, speedup, median_raw)) for x in buf]))

    analytics_file.flush()
    debug('got diffs')



    argmin = numpy.argmin(norm_distances)
    debug('Picked frame %d (distances from prev chosen frame: \n[%s]\n[%s]' %
          (argmin,
           ', '.join([str(int(100*x)) for x in norm_distances]),
           ', '.join([str(int(100*x/float(max(raw_distances)))) for x in raw_distances])))

    misc.imsave('/tmp/img-%d.jpg' % iter, target.gauss_data)
    for i in range(len(buf)):
        misc.imsave('/tmp/img-%d-%d-%d-%0.2f.jpg' % (
            RESIZE_SIZE,
            iter,
            i,
            norm_distances[i]),
            buf[i].gauss_data)
        i += 1

    chosen_frame = buf[argmin]
    print('dist: %0.3f' % norm_distances[argmin])

    desired_idx = target.idx + speedup
    idx_error = desired_idx - chosen_frame.idx
    accumulated_error += idx_error
    print 'accum error: %d' % accumulated_error

    return chosen_frame


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
    writer = VideoWriter('%s-accum_error_25-%dx-%d.avi' % (reader.getBaseOutputName(), speedup, RESIZE_SIZE))

    buf = []
    last_frame = None

    idx = -1
    for frame in reader.getFrames():
        idx += 1
        frame = Frame(frame, idx)

        # initialize the "last_frame" with the first frame of the video
        if last_frame == None:
            last_frame = frame
            continue

        buf.append(frame)

        # if we have a not-full buffer, we're done
        if len(buf) != speedup * 2:
            continue

        # we have a full buffer!  pick the "best" frame from it and use that one
        debug('picking best frame from %d preceding frame %d' % (len(buf), idx))

        new_frame = find_most_similar(last_frame, buf, idx, speedup)
        writer.appendFrame(new_frame.data)
        last_frame = new_frame

        # keep only frames after the selected one in the buffer
        new_buf = []
        for i in range(len(buf)):
            if buf[i].idx > new_frame.idx:
                new_buf.append(buf[i])
        buf = new_buf

    writer.done()
