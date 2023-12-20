import random
import string


class DummyToken(object):

    def __init__(self, length=150):
        self.len = length

    def create(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits)
                       for _ in range(self.len))
