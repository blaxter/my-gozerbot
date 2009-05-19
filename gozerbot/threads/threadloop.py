# gozerbot/threadloop.py
#
#

""" class to implement start/stoppable threads """

__copyright__ = 'this file is in the public domain'

from gozerbot.generic import rlog
from thr import start_new_thread
import Queue, time

class ThreadLoop(object):

    def __init__(self, name="", queue=None):
        self.name = name or 'idle'
        self.stopped = False
        self.running = False
        self.outs = []
        self.queue = queue or Queue.Queue()
        self.nowrunning = "none"

    def _loop(self):
        rlog(0, self.name, 'starting threadloop')
        self.running = True
        while not self.stopped:
            try:
                data = self.queue.get()
            except Queue.Empty:
                if self.stopped:
                    break
                time.sleep(0.1)
                continue
            if self.stopped:
                break
            if not data:
                break
            rlog(-1, self.name, 'running %s' % str(data))
            self.handle(*data)
        self.running = False
        rlog(0, self.name, 'stopping threadloop')

    def put(self, *data):
        self.queue.put_nowait(data)

    def start(self):
        if not self.running:
            start_new_thread(self._loop, ())

    def stop(self):
        self.stopped = True
        self.running = False
        self.queue.put(None)

    def handle(self, *args, **kwargs):
        """ overload this """
        pass

class RunnerLoop(ThreadLoop):

    def _loop(self):
        rlog(0, self.name, 'starting threadloop')
        self.running = True
        while not self.stopped:
            try:
                data = self.queue.get()
            except Queue.Empty:
                if self.stopped:
                    break
                time.sleep(0.1)
                continue
            if self.stopped:
                break
            if not data:
                break
            self.nowrunning = data[0]
            rlog(0, self.name, 'now running %s' % self.nowrunning)
            self.handle(*data)
        self.running = False
        rlog(0, self.name, 'stopping threadloop')
