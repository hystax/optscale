import random
import string


class DummyToken(object):

    def __init__(self, len=150):
        self.len = len

    def create(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits)
                       for _ in range(self.len))
