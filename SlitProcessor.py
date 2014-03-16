import numpy
import Image
import time
from timedebug import debug

class SlitProcessor:

    video = None
    slitPosition = None
    numRows = None
    _lastTime = None

    def __init__(self, video, slit_position, num_rows):
        self.video = video
        self.slitPosition = slit_position
        self.numRows = num_rows
        debug("Constructed processor for %d" % slit_position)

    def _debug(self, event):
        now = time.time()
        diff = now - self._lastTime
        SlitProcessor._lastTime = now
        print "[%0.3f] %s" % (diff, event)

    def getAndSaveSlitscan(self):
        debug("getting image")
        image = self.getSlitscan()
        filename = self.getImageFilename()
        debug("writing to disk")
        Image.fromarray(image).save(filename)
        debug("done with slit_position %d" % self.slitPosition)
        return filename

    def getSlitscan(self):
        num_frames = self.video.getNumFrames()

        i = 0
        x1 = self.slitPosition
        x2 = self.slitPosition + self.numRows
        final_image = numpy.zeros((num_frames*self.numRows, self.video.getWidth(), 3), 'uint8')
        for image in self.video.getFrames():
            # the value of the slit from this frame
            slit = image[x1:x2, 0:1280, :]
            # where does the slit start in the output image?
            frame_index_start = self.numRows*i
            # where does this slit end in the output image?
            frame_index_end = frame_index_start + self.numRows

            final_image[frame_index_start:frame_index_end] = slit
            i += 1

        for i in xrange(3):
            final_image = numpy.rot90(final_image)
        return final_image

    def getImageFilename(self):
        filename = self.video.getFilename()
        filename_parts = filename.split('/')
        name = filename_parts[-1]
        name = name.split('.')[0]
        return '%s/%s-%d-%03d.png' % ('/'.join(filename_parts[0:-1]), name,
                                      self.numRows, self.slitPosition)
