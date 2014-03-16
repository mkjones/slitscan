import numpy
import Image

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
        Image.fromarray(image).save(filename)
        return filename

    def getSlitscan(self):
        slit_position = int(self.slitPosition * self.video.getHeight())
        num_frames = self.video.getNumFrames()

        i = 0
        x1 = slit_position
        x2 = slit_position + self.numRows
        final_image = numpy.zeros((num_frames*self.numRows, self.video.getWidth(), 3), 'uint8')
        for image in self.video.yieldFrames():
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
        return '%s/%s.png' % ('/'.join(filename_parts[0:-1]), name)
