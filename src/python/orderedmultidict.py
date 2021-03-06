try:
    from collections import OrderedDict as odict
except ImportError:
    from ordereddict import OrderedDict as odict
from itertools import imap, izip, izip_longest, repeat, chain, izip_longest
from collections import namedtuple



_absent = object() # Marker that means no parameter was provided.

class itemnode(object):
    """
    Dictionary key:value items wrapped in a node to be members of itemlist, the
    doubly linked list defined below.
    """
    def __init__(self, prev=None, next=None, key=_absent, value=_absent):
        self.prev = prev
        self.next = next
        self.key = key
        self.value = value

class itemlist(object):
    """
    Doubly linked list of itemnodes.

    This class is used as the key:value item storage of orderedmultidict. Methods
    below were only added as needed for use with orderedmultidict, so some
    otherwise common list related methods may be missing.
    """
    def __init__(self, items=[]):
        self.root = itemnode()
        self.root.next = self.root.prev = self.root
        self.size = 0

        for key, value in items:
            self.append(key, value)

    def items(self):
        return [(key,value) for node, key, value in self]

    def append(self, key, value):
        tail = self.root.prev if self.root.prev is not self.root else self.root
        node = itemnode(tail, self.root, key=key, value=value)
        tail.next = node
        self.root.prev = node
        self.size += 1
        return node

    def removenode(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
        return self

    def clear(self):
        for node, key, value in self:
            self.removenode(node)
        return self

    def items(self):
        return list(self.iteritems())

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        for node, key, value in self:
            yield key, value

    def iterkeys(self):
        for node, key, value in self:
            yield key

    def itervalues(self):
        for node, key, value in self:
            yield value

    def reverse(self):
        for node, key, value in self:
            node.prev, node.next = node.next, node.prev
        self.root.prev, self.root.next = self.root.next, self.root.prev
        return self

    def __len__(self):
        return self.size

    def __iter__(self):
        current = self.root.next
        while current and current is not self.root:
            # Record current.next here in case current.next changes after the yield
            # and before we return for the next iteration. For example, methods like
            # reverse() will change current.next() before yield gets executed again.
            nextnode = current.next
            yield current, current.key, current.value
            current = nextnode

    def __contains__(self, item):
        """
        Params:
          item: Can either be a (key,value) tuple or an itemnode reference.
        """
        node = key = value = _absent
        if hasattr(item, '__len__') and callable(item.__len__):
            if len(item) == 2:
                key, value = item
            elif len(item) == 3:
                node, key, value = item
        else:
            node = item

        if node is not _absent or (key is not _absent and value is not _absent):
            for selfnode, selfkey, selfvalue in self:
                if ((node is _absent and key == selfkey and value == selfvalue) or
                    (node is not _absent and node == selfnode)):
                    return True
        return False

    def __getitem__(self, index):
        # Only support direct access to the first or last element, as this is all
        # orderedmultidict needs for now.
        if index == 0 and self.root.next is not self.root:
            return self.root.next
        elif index == -1 and self.root.prev is not self.root:
            return self.root.prev
        raise IndexError(index)

    def __delitem__(self, index):
        self.removenode(self[index])

    def __eq__(self, other):
        for (n1, key1, value1), (n2, key2, value2) in izip_longest(self, other):
            if key1 != key2 or value1 != value2:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.size > 0

    def __str__(self):
        return '[%s]' % self.items()

class omdict(object):
    """
    Ordered Multivalue Dictionary.

    A multivalue dictionary is a dictionary that can store multiple values per
    key. An ordered multivalue dictionary is a multivalue dictionary that retains
    the order of insertions and deletions.

    Internally, items are stored in a doubly linked list, self._items. A
    dictionary, self._map, is also maintained and stores an ordered list of linked
    list node references, one for each value associated with that key.

    Standard dict methods interact with the first value associated with a given
    key. This means that omdict retains method parity with dict, and a dict object
    can be replaced with an omdict object and all interaction will behave
    identically. All dict methods that retain parity with omdict are:

      get(), setdefault(), pop(), popitem(),
      clear(), copy(), update(), fromkeys(), len()
      __getitem__(), __setitem__(), __delitem__(), __contains__(),
      items(), keys(), values(), iteritems(), iterkeys(), itervalues(),

    Optional parameters have been added to some dict methods, but because the
    added parameters are optional, existing use remains unaffected. An optional
    <key> parameter has been added to these methods:

      items(), values(), iteritems(), itervalues()

    New methods have also been added to omdict. Methods with 'list' in their name
    interact with lists of values, and methods with 'all' in their name interact
    with all items in the dictionary, including multiple items with the same key.

    The new omdict methods are:

      load(), size(), reverse(),
      getlist(), add(), addlist(), set(), setlist(), setdefaultlist(),
      poplist(), popvalue(), popvalues(), popitem(), poplistitem(),
      allitems(), allkeys(), allvalues(), lists(), listitems(),
      iterallitems(), iterallkeys(), iterallvalues(), iterlists(), iterlistitems()

    Explanations and examples of the new methods above can be found in the
    function comments below and online at

      https://github.com/gruns/orderedmultidict

    Additional omdict information and documentation can also be found at the above
    url.
    """
    def __init__(self, mapping=[]):
        # Doubly linked list of itemnodes, each itemnode storing a key:value
        # item.
        self._items = itemlist()

        # Ordered dictionary of keys and itemnode references. Each itemnode
        # reference points to one of that keys values.
        self._map = odict()

        self.load(mapping)

    def load(self, mapping=[]):
        """
        Clear all existing key:value items and import all key:value items from
        <mapping>. If multiple values exist for the same key in <mapping>, they are
        all be imported.

        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.load([(4,4), (4,44), (5,5)])
          omd.allitems() == [(4,4), (4,44), (5,5)]

        Returns: <self>.
        """
        self.clear()
        self.updateall(mapping)
        return self

    def copy(self):
        return self.__class__(self._items)

    def clear(self):
        self._map.clear()
        self._items.clear()

    def size(self):
        """
        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.size() == 5

        Returns: Total number of items, including multiple items with the same key.
        """
        return len(self._items)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        return cls([(key, value) for key in iterable])

    def has_key(self, key):
        return key in self

    def update(self, *args, **kwargs):
        self._update_updateall(True, *args, **kwargs)

    def updateall(self, *args, **kwargs):
        """
        Update this dictionary with the items from <mapping>, replacing existing
        key:value items with shared keys before adding new key:value items.

        Example:
          omd = omdict([(1,1), (2,2)])
          omd.updateall([(2,'two'), (1,'one'), (2,222), (1,111)])
          omd.allitems() == [(1, 'one'), (2, 'two'), (2, 222), (1, 111)]

        Returns: <self>.
        """
        self._update_updateall(False, *args, **kwargs)
        return self

    def _update_updateall(self, replace_at_most_one, *args, **kwargs):
        # Bin the items in <args> and <kwargs> into <replacements> or
        # <leftovers>. Items in <replacements. are new values to replace old values
        # for a given key, and items in <leftovers> are new items to be added.
        replacements, leftovers = dict(), []
        for mapping in chain(args, [kwargs]):
            self._bin_update_items(self._items_iterator(mapping), replace_at_most_one,
                                   replacements, leftovers)

        # First, replace existing values for each key.
        for key, values in replacements.iteritems():
            self.setlist(key, values)
        # Then, add the leftover items to the end of the list of all items.
        for key, value in leftovers:
            self.add(key, value)

    def _bin_update_items(self, items, replace_at_most_one,
                              replacements, leftovers):
        """
        <replacements and <leftovers> are modified directly, ala pass by reference.
        """
        for key, value in items:
            # If there are existing items with key <key> that have yet to be marked
            # for replacement, mark that item's value to be replaced by <value> by
            # appending it to <replacements>.
            if key in self and key not in replacements:
                replacements[key] = [value]
            elif (key in self and not replace_at_most_one and
                  len(replacements[key]) < len(self.values(key))):
                replacements[key].append(value)
            else:
                if replace_at_most_one:
                    replacements[key] = [value]
                else:
                    leftovers.append((key, value))

    def _items_iterator(self, container):
        iterator = iter(container)
        if hasattr(container, 'iterallitems') and callable(container.iterallitems):
            iterator = container.iterallitems()
        elif hasattr(container, 'allitems') and callable(container.allitems):
            iterator = iter(container.allitems())
        elif hasattr(container, 'iteritems') and callable(container.iteritems):
            iterator = container.iteritems()
        elif hasattr(container, 'items') and callable(container.items):
            iterator = iter(container.items())
        return iterator

    def get(self, key, default=None):
        if key in self:
            return self._map[key][0].value
        return default

    def getlist(self, key, default=[]):
        """
        Returns: The list of values for <key> if <key> is in the dictionary, else
        <default>. If <default> is not provided, an empty list is returned.
        """
        if key in self:
            return [node.value for node in self._map[key]]
        return default

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self.add(key, default)
        return default

    def setdefaultlist(self, key, defaultlist=[None]):
        """
        Similar to setdefault() except <defaultlist> is a list of values to set for
        <key>. If <key> already exists, its existing list of values is returned.

        If <key> isn't a key and <defaultlist> is an empty list, [], no values are
        added for <key> and <key> will not be added as a key.

        Returns: List of <key>'s values if <key> exists in the dictionary, otherwise
        <default>.
        """
        if key in self:
            return self.getlist(key)
        self.addlist(key, defaultlist)
        return defaultlist

    def add(self, key, value=None):
        """
        Add <value> to the list of values for <key>. If <key> is not in the
        dictionary, then <value> is added as the sole value for <key>.

        Example:
          omd = omdict()
          omd.add(1, 1)  # omd.allitems() == [(1,1)]
          omd.add(1, 11) # omd.allitems() == [(1,1), (1,11)]
          omd.add(2, 2)  # omd.allitems() == [(1,1), (1,11), (2,2)]

        Returns: <self>.
        """
        self._map.setdefault(key, [])
        node = self._items.append(key, value)
        self._map[key].append(node)
        return self

    def addlist(self, key, valuelist=[]):
        """
        Add the values in <valuelist> to the list of values for <key>. If <key> is
        not in the dictionary, the values in <valuelist> become the values for
        <key>.

        Example:
          omd = omdict([(1,1)])
          omd.addlist(1, [11, 111])
          omd.allitems() == [(1, 1), (1, 11), (1, 111)]
          omd.addlist(2, [2])
          omd.allitems() == [(1, 1), (1, 11), (1, 111), (2, 2)]

        Returns: <self>.
        """
        for value in valuelist:
            self.add(key, value)
        return self

    def set(self, key, value=None):
        """
        Sets <key>'s value to <value>. Identical in function to __setitem__().

        Returns: <self>.
        """
        self[key] = value
        return self

    def setlist(self, key, values):
        """
        Sets <key>'s list of values to <values>. Existing items with key <key> are
        first replaced with new values from <values>. Any remaining old items that
        haven't been replaced with new values are deleted, and any new values from
        <values> that don't have corresponding items with <key> to replace are
        appended to the end of the list of all items.

        If values is an empty list, [], <key> is deleted, equivalent in action to
        del self[<key>].

        Example:
          omd = omdict([(1,1), (2,2)])
          omd.setlist(1, [11, 111])
          omd.allitems() == [(1,11), (2,2), (1,111)]

          omd = omdict([(1,1), (1,11), (2,2), (1,111)])
          omd.setlist(1, [None])
          omd.allitems() == [(1,None), (2,2)]

          omd = omdict([(1,1), (1,11), (2,2), (1,111)])
          omd.setlist(1, [])
          omd.allitems() == [(2,2)]

        Returns: <self>.
        """
        if not values and key in self:
            self.pop(key)
        else:
            it = izip_longest(list(self._map.get(key, [])), values, fillvalue=_absent)
            for node, value in it:
                if node is not _absent and value is not _absent:
                    node.value = value
                elif node is _absent:
                    self.add(key, value)
                elif value is _absent:
                    self._map[key].remove(node)
                    self._items.removenode(node)
        return self

    def removevalues(self, key, values):
        """
        Removes all <values> from the values of <key>. If <key> has no remaining
        values after removevalues(), the key is popped.

        Example:
          omd = omdict([(1, 1), (1, 11), (1, 1), (1, 111)])
          omd.removevalues(1, [1, 111])
          omd.allitems() == [(1, 11)]

        Returns: <self>.
        """
        self.setlist(key, [v for v in self.getlist(key) if v not in values])
        return self

    def pop(self, key, default=_absent):
        if key in self:
            return self.poplist(key)[0]
        elif key not in self._map and default is not _absent:
            return default
        raise KeyError(key)

    def poplist(self, key, default=_absent):
        """
        If <key> is in the dictionary, pop it and return its list of values. If
        <key> is not in the dictionary, return <default>. KeyError is raised if
        <default> is not provided and <key> is not in the dictionary.

        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.poplist(1) == [1, 11, 111]
          omd.allitems() == [(2,2), (3,3)]
          omd.poplist(2) == [2]
          omd.allitems() == [(3,3)]

        Raises: KeyError if <key> isn't in the dictionary and <default> isn't
          provided.
        Returns: List of <key>'s values.
        """
        if key in self:
            values = self.getlist(key)
            del self._map[key]
            for node, nodekey, nodevalue in self._items:
                if nodekey == key:
                    self._items.removenode(node)
            return values
        elif key not in self._map and default is not _absent:
            return default
        raise KeyError(key)

    def popvalue(self, key, value=_absent, default=_absent, last=True):
        """
        If <value> is provided, pops the first or last (key,value) item in the
        dictionary if <key> is in the dictionary.

        If <value> is not provided, pops the first or last value for <key> if <key>
        is in the dictionary.

        If <key> no longer has any values after a popvalue() call, <key> is removed
        from the dictionary. If <key> isn't in the dictionary and <default> was
        provided, return default. KeyError is raised if <default> is not provided
        and <key> is not in the dictionary. ValueError is raised if <value> is
        provided but isn't a value for <key>.

        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3), (2,22)])
          omd.popvalue(1) == 111
          omd.allitems() == [(1,11), (1,111), (2,2), (3,3), (2,22)]
          omd.popvalue(1, last=False) == 1
          omd.allitems() == [(1,11), (2,2), (3,3), (2,22)]
          omd.popvalue(2, 2) == 2
          omd.allitems() == [(1,11), (3,3), (2,22)]
          omd.popvalue(1, 11) == 11
          omd.allitems() == [(3,3), (2,22)]
          omd.popvalue('not a key', default='sup') == 'sup'

        Params:
          last: Boolean whether to return <key>'s first value (<last> is False) or
            last value (<last> is True).
        Raises:
          KeyError if <key> isn't in the dictionary and <default> isn't
            provided.
          ValueError if <value> isn't a value for <key>.
        Returns: The first or last of <key>'s values.
        """
        def pop_node_with_index(key, index):
            node = self._map[key].pop(index)
            if not self._map[key]:
                del self._map[key]
            self._items.removenode(node)
            return node

        if key in self:
            if value is not _absent:
                if last:
                    pos = self.values(key)[::-1].index(value)
                else:
                    pos = self.values(key).index(value)
                if pos == -1:
                    raise ValueError(value)
                else:
                    index = (len(self.values(key)) - 1 - pos) if last else pos
                    return pop_node_with_index(key, index).value
            else:
                return pop_node_with_index(key, -1 if last else 0).value
        elif key not in self._map and default is not _absent:
            return default
        raise KeyError(key)

    def popitem(self, fromall=False, last=True):
        """
        Pop and return a key:value item.

        If <fromall> is False, items()[0] is popped if <last> is False or
        items()[-1] is popped if <last> is True. All remaining items with the same
        key are removed.

        If <fromall> is True, allitems()[0] is popped if <last> is False or
        allitems()[-1] is popped if <last> is True. Any remaining items with the
        same key remain.

        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.popitem() == (3,3)
          omd.popitem(fromall=False, last=False) == (1,1)
          omd.popitem(fromall=False, last=False) == (2,2)

          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.popitem(fromall=True, last=False) == (1,1)
          omd.popitem(fromall=True, last=False) == (1,11)
          omd.popitem(fromall=True, last=True) == (3,3)
          omd.popitem(fromall=True, last=False) == (1,111)

        Params:
          fromall: Whether to pop an item from items() (<fromall> is True) or
            allitems() (<fromall> is False).
          last: Boolean whether to pop the first item or last item of items() or
            allitems().
        Raises: KeyError if the dictionary is empty.
        Returns: The first or last item from item() or allitem().
        """
        if not self._items:
            raise KeyError('popitem(): %s is empty' % self.__class__.__name__)

        if fromall:
            node = self._items[-1 if last else 0]
            key, value = node.key, node.value
            return key, self.popvalue(key, last=last)
        else:
            key = self._map.keys()[-1 if last else 0]
            return key, self.pop(key)

    def poplistitem(self, last=True):
        """
        Pop and return a key:valuelist item comprised of a key and that key's list
        of values. If <last> is False, a key:valuelist item comprised of keys()[0]
        and its list of values is popped and returned. If <last> is True, a
        key:valuelist item comprised of keys()[-1] and its list of values is popped
        and returned.

        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.poplistitem(last=True) == (3,[3])
          omd.poplistitem(last=False) == (1,[1,11,111])

        Params:
          last: Boolean whether to pop the first or last key and its associated list
            of values.
        Raises: KeyError if the dictionary is empty.
        Returns: A two-tuple comprised of the first or last key and its associated
          list of values.
        """
        if not self._items:
            raise KeyError('poplistitem(): %s is empty' % self.__class__.__name__)

        key = self.keys()[-1 if last else 0]
        return key, self.poplist(key)

    def items(self, key=_absent):
        """
        Raises: KeyError if <key> is provided and not in the dictionary.
        Returns: List created from iteritems(<key>). Only items with key <key> are
          returned if <key> is provided and is a dictionary key.
        """
        return list(self.iteritems(key))

    def keys(self):
        return list(self.iterkeys())

    def values(self, key=_absent):
        """
        Raises: KeyError if <key> is provided and not in the dictionary.
        Returns: List created from itervalues(<key>).If <key> is provided and is a
          dictionary key, only values of items with key <key> are returned.
        """
        if key is not _absent and key in self._map:
            return self.getlist(key)
        return list(self.itervalues())

    def lists(self):
        """
        Returns: List created from iterlists().
        """
        return list(self.iterlists())

    def listitems(self):
        """
        Returns: List created from iterlistitems().
        """
        return list(self.iterlistitems())

    def iteritems(self, key=_absent):
        """
        Parity with dict.iteritems() except the optional <key> parameter has been
        added. If <key> is provided, only items with the provided key are iterated
        over. KeyError is raised if <key> is provided and not in the dictionary.

        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.iteritems(1) -> (1,1) -> (1,11) -> (1,111)
          omd.iteritems() -> (1,1) -> (1,11) -> (1,111) -> (2,2) -> (3,3)

        Raises: KeyError if <key> is provided and not in the dictionary.
        Returns: An iterator over the items() of the dictionary, or only items with
          the key <key> if <key> is provided.
        """
        if key is not _absent:
            if key in self:
                return iter([(node.key,node.value) for node in self._map[key]])
            raise KeyError(key)
        return iter([(key,nodes[0].value) for (key,nodes) in self._map.iteritems()])

    def iterkeys(self):
        return self._map.iterkeys()

    def itervalues(self, key=_absent):
        """
        Parity with dict.itervalues() except the optional <key> parameter has been
        added. If <key> is provided, only values from items with the provided key
        are iterated over. KeyError is raised if <key> is provided and not in the
        dictionary.

        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.itervalues(1) -> 1 -> 11 -> 111
          omd.itervalues() -> 1 -> 11 -> 111 -> 2 -> 3

        Raises: KeyError if <key> is provided and isn't in the dictionary.
        Returns: An iterator over the values() of the dictionary, or only the values
          of key <key> if <key> is provided.
        """
        if key is not _absent:
            if key in self:
                return iter([node.value for node in self._map[key]])
            raise KeyError(key)
        return iter([nodes[0].value for nodes in self._map.itervalues()])

    def allitems(self, key=_absent):
        '''
        Raises: KeyError if <key> is provided and not in the dictionary.
        Returns: List created from iterallitems(<key>).
        '''
        return list(self.iterallitems(key))

    def allkeys(self):
        '''
        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.allkeys() == [1,1,1,2,3]

        Returns: List created from iterallkeys().
        '''
        return list(self.iterallkeys())

    def allvalues(self, key=_absent):
        '''
        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.allvalues() == [1,11,111,2,3]
          omd.allvalues(1) == [1,11,111]

        Raises: KeyError if <key> is provided and not in the dictionary.
        Returns: List created from iterallvalues(<key>).
        '''
        return list(self.iterallvalues(key))

    def iterallitems(self, key=_absent):
        '''
        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.iterallitems() == (1,1) -> (1,11) -> (1,111) -> (2,2) -> (3,3)
          omd.iterallitems(1) == (1,1) -> (1,11) -> (1,111)

        Raises: KeyError if <key> is provided and not in the dictionary.
        Returns: An iterator over every item in the diciontary. If <key> is
          provided, only items with the key <key> are iterated over.
        '''
        if key is not _absent:
            return self.iteritems(key) # Raises KeyError if <key> is not in self._map.
        return self._items.iteritems()

    def iterallkeys(self):
        '''
        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.iterallkeys() == 1 -> 1 -> 1 -> 2 -> 3

        Returns: An iterator over the keys of every item in the dictionary.
        '''
        return self._items.iterkeys()

    def iterallvalues(self, key=_absent):
        '''
        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.iterallvalues() == 1 -> 11 -> 111 -> 2 -> 3

        Returns: An iterator over the values of every item in the dictionary.
        '''
        if key is not _absent:
            if key in self:
                return iter(self.getlist(key))
            raise KeyError(key)
        return self._items.itervalues()

    def iterlists(self):
        '''
        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.iterlists() -> [1,11,111] -> [2] -> [3]

        Returns: An iterator over the list comprised of the lists of values for each
        key.
        '''
        return imap(lambda key: self.getlist(key), self)

    def iterlistitems(self):
        """
        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.iterlistitems() -> (1,[1,11,111]) -> (2,[2]) -> (3,[3])

        Returns: An iterator over the list of key:valuelist items.
        """
        return imap(lambda key: (key, self.getlist(key)), self)

    def reverse(self):
        """
        Reverse the order of all items in the dictionary.

        Example:
          omd = omdict([(1,1), (1,11), (1,111), (2,2), (3,3)])
          omd.reverse()
          omd.allitems() == [(3,3), (2,2), (1,111), (1,11), (1,1)]

        Returns: <self>.
        """
        for key in self._map.iterkeys():
            self._map[key].reverse()
        self._items.reverse()
        return self

    def __eq__(self, other):
        if hasattr(other, 'iterallitems') and callable(other.iterallitems):
            myiter, otheriter = self.iterallitems(), other.iterallitems()
            for item1, item2 in izip_longest(myiter, otheriter, fillvalue=_absent):
                if item1 != item2 or item1 is _absent or item2 is _absent:
                    return False
        elif not hasattr(other, '__len__') or not hasattr(other, 'iteritems'):
            return False
        # Ignore order so we can compare ordered omdicts with unordered dicts.
        else:
            if len(self) != len(other):
                return False
            for key, value in other.iteritems():
                if self.get(key, _absent) != value:
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self._map)

    def __iter__(self):
        for key in self.iterkeys():
            yield key

    def __contains__(self, key):
        return key in self._map

    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.setlist(key, [value])

    def __delitem__(self, key):
        return self.pop(key)

    def __nonzero__(self):
        return bool(self._map)

    def __str__(self):
        return '{%s}' % ', '.join(map(lambda p: '%r: %r'%(p[0], p[1]),
                                      self.iterallitems()))

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.allitems())
