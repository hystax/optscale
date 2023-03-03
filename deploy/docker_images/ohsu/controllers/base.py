import logging
import threading

LOG = logging.getLogger(__name__)


class BaseController(object):

    def __init__(self, config=None):
        super().__init__()
        self.config = config

    @staticmethod
    def run_async(func, params):
        thr = threading.Thread(target=func, args=params)
        thr.start()
