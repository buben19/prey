from __future__ import unicode_literals
from python.orderedmultidict import omdict

# TODO: move these tool into utils package
class ObjectMultiplier(object):
    """
    multiple object instances by integer
    """

    __objects = None

    def __init__(self):
        self.__objects = {}

    def __iter__(self):
        for o in self.__objects:
            for i in range(self.__objects[o]):
                yield o

    def add(self, obj, count):
        """
        add object and its multiplier
        """
        if not obj in self.__objects:
            self.__objects[obj] = 0
        self.__objects[obj] += count

    def __len__(self):
        l = 0
        for o in self.__objects:
            l += self.__objects[o]
        return l

    def __repr__(self):
        tmp = []
        for o in self.__objects:
            tmp.append(str(self.__objects[o]) + ' * ' + repr(o))
        return '<' + ', '.join(tmp) + '>'

class Counter(object):

    count = None

    def __init__(self, count):
        self.count = count

    def decrement(self):
        if self.count > 0:
            self.count -= 1
        else:
            raise ValueError, "counter should'n reach negative number"

    def increment(self):
        self.count += 1

    def add(self, count):
        self.count += count

    def isZero(self):
        return not self.count > 0

