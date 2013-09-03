import unittest
from itertools import izip, izip_longest, repeat, product

from src.python.orderedmultidict import itemlist

_unique = object()

class TestItemList(unittest.TestCase):

    def setUp(self):
        self.inits = [
            [],
            [(0,0)],
            [(0,0),(0,0),(None,None)],
            [(0,0),(1,1),(2,2)],
            [(True,False)],
            [(False,True)],
            [(object(),object()),(object(),object())],
            [(object,object)],
            [('p','pumps'),('d','dumps')]]
        self.appends = [(0,0), (1,1), (None,None), (True,False), (object(),object())]

    def test_init(self):
        for init in self.inits:
            il = itemlist(init)
            self.assertEquals(il.items(), init)

    def test_append(self):
        for init in self.inits:
            for key, value in self.appends:
                il = itemlist(init)
                oldsize = len(il)
                newnode = il.append(key, value)
                self.assertEquals(len(il), oldsize + 1)
                self.assertEquals(il[-1], newnode)

    def test_removenode(self):
        for init in self.inits:
            il = itemlist(init)
            for node, key, value in il:
                oldsize = len(il)
                self.assertTrue(node in il)
                self.assertEquals(il.removenode(node), il)
                self.assertEquals(len(il), oldsize - 1)
                self.assertFalse(node in il)

    def test_clear(self):
        for init in self.inits:
            il = itemlist(init)
            if len(init) > 0:
                self.assertTrue(il)
            else:
                self.assertFalse(il)
            self.assertEquals(len(init), len(il))
            self.assertEquals(il.clear(), il)
            self.assertFalse(il)

    def test_items_keys_values_iteritems_iterkeys_itervalues(self):
        for init in self.inits:
            il = itemlist(init)
            iterator = izip(izip(il.items(), il.keys(), il.values()),
                            izip(il.iteritems(), il.iterkeys(), il.itervalues()))
            for (item1,key1,value1), (item2,key2,value2) in iterator:
                self.assertEquals(item1, item2)
                self.assertEquals(key1, key2)
                self.assertEquals(value1, value2)

    def test_reverse(self):
        for init in self.inits:
            il = itemlist(init)
            items = il.items()
            items.reverse()
            self.assertEquals(il.reverse(), il)
            self.assertEquals(items, il.items())

    def test_len(self):
        for init in self.inits:
            il = itemlist(init)
            self.assertEquals(len(il), len(init))
            for key, value in self.appends:
                oldsize = len(il)
                il.append(key, value)
                self.assertEquals(len(il), oldsize + 1)

    def test_contains(self):
        for init in self.inits:
            il = itemlist(init)
            for node, key, value in il:
                self.assertTrue(node in il)
                self.assertTrue((key, value) in il)

            self.assertFalse(None in il)
            self.assertFalse(_unique in il)
            self.assertFalse((19283091823,102893091820) in il)

    def test_iter(self):
        for init in self.inits:
            il = itemlist(init)
            index = 0
            for node, key, value in il:
                self.assertTrue(node in il)
                self.assertTrue((key, value) in il)
                self.assertEquals(init[index][0], key)
                self.assertEquals(init[index][1], value)
                index += 1

    def test_delitem(self):
        for init in self.inits:
            for index in [0,-1]:
                il = itemlist(init)
                while il:
                    node = il[index]
                    self.assertTrue(node in il)
                    del il[index]
                    self.assertFalse(node in il)

    def test_nonzero(self):
        for init in self.inits:
            il = itemlist(init)
            if init:
                self.assertTrue(il)
                il.clear()
                self.assertFalse(il)
            else:
                self.assertFalse(il)
