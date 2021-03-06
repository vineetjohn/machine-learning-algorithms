import abc


class Processor(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, options):
        self.options = options

    @abc.abstractmethod
    def process(self):
        pass
