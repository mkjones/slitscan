import time

last_time = time.time()

class Debugger:
    instance = None

    lastTime = None

    @staticmethod
    def get():
        if Debugger.instance is None:
            Debugger.instance = Debugger()
        return Debugger.instance

    def __init__(self):
        self.lastTime = time.time()

    def debug(self, message):
        now = time.time()
        diff = now - self.lastTime
        self.lastTime = now
        print "[%0.3f] %s" % (diff, message)


def debug(message):
    Debugger.get().debug(message)
