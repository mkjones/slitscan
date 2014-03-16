import re
import subprocess
import numpy
import Image

class VideoReader:
    filename = ''
    numFrames = None
    width = None
    height = None

    def __init__(self, filename):
        self.filename = filename

    def getFilename(self):
        return self.filename

    def getNumFrames(self):
        if self.numFrames is None:
            self._populateMetadata()

        return self.numFrames

    def getWidth(self):
        if self.width is None:
            self._populateMetadata()
        return self.width

    def getHeight(self):
        if self.height is None:
            self._populateMetadata()
        return self.height

    def _populateMetadata(self):
        info_args = ('ffmpeg', '-i', self.filename, '-vcodec', 'copy',
                     '-f', 'rawvideo', '-y', '/dev/null')
        pipe = subprocess.Popen(info_args,
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE)
        (stdout, stderr) = pipe.communicate()
        matches = re.search('frame= *(\d+)', stderr)
        self.numFrames = int(matches.group(1))

        matches = re.search(' (\d+)x(\d+),? ', stderr)
        self.width = int(matches.group(1))
        self.height = int(matches.group(2))

    def getFrames(self):
        args = [
            "ffmpeg",
            "-i",
            self.filename,
            "-f",
            "image2pipe",
            "-pix_fmt",
            "rgb24",
            "-vcodec",
            "rawvideo",
            "-"
        ]

        buffer_size = self.getWidth() * self.getHeight() * 3
        pipe = subprocess.Popen(args, stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE, bufsize=buffer_size)

        for i in xrange(self.getNumFrames()):
            image_bytes = pipe.stdout.read(buffer_size)
            image = numpy.fromstring(image_bytes, dtype='uint8').reshape(
                (self.getHeight(), self.getWidth(), 3))

            yield self._rotateSourceImageForOutput(image)

    def _rotateSourceImageForOutput(self, image):
        return image

# Same as Video, except the video frames are memoized so you only need to parse
# the video file once.  Trades off faster speed for more (O(n)) memory usage.
class MemoizedVideoReader(VideoReader):
    memoizedFrames = None

    def getFrames(self):
        if self.memoizedFrames is None:
            self.memoizedFrames = [x for x in VideoReader.getFrames(self)]
        return self.memoizedFrames

class VideoWriter:

    filename = None
    pipe = None

    def __init__(self, filename):
        self.filename = filename
        self._initSubprocess()

    def _initSubprocess(self):
        args = [
            "ffmpeg",
            "-y",
            "-f",
            "image2pipe",
            "-vcodec",
            "png",
            "-r",
            "24",
            "-i",
            "-",
            "-c",
            "libx264",
            self.filename
        ]

        self.pipe = subprocess.Popen(args, stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)

    def appendFrame(self, raw_frame):
        Image.fromarray(raw_frame).save(self.pipe.stdin, 'PNG')

    def done(self):
        self.pipe.stdin.close()
        self.pipe.wait()


if __name__ == '__main__':
    v = Video('/Users/mkjones/Pictures/sunset_timelapse/large.avi')
    print 'num frames: %d' % (v.getNumFrames())
    print 'dims: %d x %d' % (v.getWidth(), v.getHeight())
    print 'again: %d' % (v.getNumFrames())
