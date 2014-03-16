import numpy

class SlitProcessor:

    video = None

    def __init__(self, video):
        self.video = video

    def getSlitscan(self, slit_position, num_rows):
        slit_position = int(slit_position * self.video.getHeight())
        num_frames = self.video.getNumFrames()

        i = 0
        x1 = slit_position
        x2 = slit_position + num_rows
        final_image = numpy.zeros((num_frames*num_rows, self.video.getWidth(), 3), 'uint8')
        for image in self.video.yieldFrames():
            # the value of the slit from this frame
            slit = image[x1:x2, 0:1280, :]

            # where does the slit start in the output image?
            frame_index_start = num_rows*i
            # where does this slit end in the output image?
            frame_index_end = frame_index_start + num_rows

            final_image[frame_index_start:frame_index_end] = slit
            i += 1

        for i in xrange(3):
            final_image = numpy.rot90(final_image)
        return final_image

