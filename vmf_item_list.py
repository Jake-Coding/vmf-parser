from __future__ import annotations

import collections.abc
import typing

import vmf_element
import vmf_property


class _VMFItemListIterator(collections.abc.Iterator):
    def __init__(self, elem_list):
        self.index = 0
        self.elem_list = elem_list

    def __next__(self):
        if self.index < len(self.elem_list):
            result = self.elem_list.get_items()[self.index]
            self.index += 1
            return result
        raise StopIteration

T = typing.TypeVar("T")

class VMFItemList(collections.abc.Collection, typing.Generic[T]):

    def __init__(self, items : list[T] = None):
        assert T in (vmf_element.VMFElement, vmf_property.VMFProperty)
        self._items = []
        if items:
            self._items = items


    def get_items(self) -> list[T]:
        return self._items

    def set_items(self, elements : list[T]):
        self._items = elements


    def __len__(self):
        return len(self.get_items())


    def __getitem__(self, item : str | T) -> VMFItemList:
        matching_elements = []
        for elem in self.get_items():
            if elem == item:
                matching_elements.append(elem)
        if len(matching_elements) == 0:
            raise KeyError(item)
        return VMFItemList[T](matching_elements)


    def __iter__(self):
        return _VMFItemListIterator(self)


    def __contains__(self, item):
        return item in self.get_items()

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        for item_for_deletion in self[key]:
            del self[item_for_deletion][0]

    def append(self, item : T):
        self.get_items().append(item)

    def remove(self, item : T):
        self.get_items().remove(item)


def main():
    elems = VMFItemList([1,2,3,4,5])
    for elem in elems:
        print(elem)
    for elem2 in elems:
        print(elem2)

if __name__ == "__main__":
    main()

