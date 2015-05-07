import numpy
from PIL import Image
import time
from timedebug import debug

class SlitProcessor:

    video = None
    slitPosition = None
    numRows = None

    def __init__(self, video, slit_position, num_rows):
        self.video = video
        self.slitPosition = slit_position
        self.numRows = num_rows

    def getAndSaveSlitscan(self):
        image = self.getSlitscan()
        filename = self.getImageFilename()
        debug("writing to disk")
        Image.fromarray(image).save(filename)
        debug("done with slit_position %d" % self.slitPosition)
        return filename

    def getSlitscan(self):
        num_frames = self.video.getNumFrames()
        if num_frames > 10000:
            num_frames = 10000
        debug("generating slitscan for %d frames" % num_frames)
        i = 0
        x1 = self.slitPosition
        x2 = self.slitPosition + self.numRows
        final_image = numpy.zeros((num_frames*self.numRows, self.video.getWidth(), 3), 'uint8')

        for im in self.video.getFrames():
            if i % 1000 == 0:
                debug("starting frame %d" % i)
            if i > num_frames:
                break
            # the value of the slit from this frame
            slit = im[x1:x2, :, :]

            # where does the slit start in the output image?
            frame_index_start = self.numRows*i
            # where does this slit end in the output image?
            frame_index_end = frame_index_start + self.numRows

            final_image[frame_index_start:frame_index_end] = slit
            i += 1

        for i in xrange(1):
            final_image = numpy.rot90(final_image)
        return final_image

    def getImageFilename(self):
        base = self.video.getBaseOutputName()
        return '%s-%d-%d.png' % (base, self.numRows, self.slitPosition)

