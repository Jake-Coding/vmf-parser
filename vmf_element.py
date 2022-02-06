from __future__ import annotations
import vmf_property
import typing


class VMFElement:
    """
    Represents an element of a .vmf file. Contains a name and a list of properties/elements.
    Example:
    solid
    {
        "thing" "value"
        "thing2" "value2"
        side
        {
            "more things" "and values"
            another_element
            {
                "it keeps going" "forever!!!"
            }
        }
        "can also have stuff here" "unfortunately"
    }
    :ivar element_name: The name of the element
    :type element_name: str
    :ivar items: The parts of the element. These can be VMFProperty objects or VMFElement objects.
    :type items: list
    """

    def __init__(self, element_name: str, items: list[vmf_property.VMFProperty | VMFElement] = None):
        self._element_name = element_name
        self._items = items

    def get_element_name(self) -> str:
        """
        Gets the name of this element.

        :return: The name of this element
        :rtype: str
        """
        return self._element_name

    def get_items(self) -> typing.List[vmf_property.VMFProperty | VMFElement]:
        """
        Returns a list of all items of this element.
        :return: A list of all items of this element
        :rtype: list
        """
        return self._items

    def set_element_name(self, new_name: str) -> None:
        """
        Renames this element.
        :param new_name: The new name of this element
        :type new_name: str
        :return: None
        :rtype: None
        """
        self._element_name = new_name

    def set_items(self, items: typing.List[vmf_property.VMFProperty | VMFElement]) -> None:
        """
        Sets the items of this element.
        :param items: The properties to set
        :type items: list
        :return: None
        :rtype: None
        """
        self._items = items

    def is_empty(self) -> bool:
        """
        Does what it says. Is len(properties) == 0
        :return: If this has no items in it
        :rtype: bool
        """
        return len(self._items) == 0

    def __eq__(self, other: VMFElement | str ):
        if type(other) == str:
            return self._element_name.lower() == other
        elif type(other) == type(self):
            return self.get_element_name().lower() == other.get_element_name().lower() and self.get_items() == other.get_items()

    def __iter__(self):
        return self

    def __next__(self):
        for item in self.get_items():
            if type(item) == vmf_property.VMFProperty:
                yield item
        raise StopIteration()

    def __getitem__(self, item_name : str) -> vmf_property.VMFProperty:
        for item in self.get_items():
            pass


    def matches(self, _name: str, _items: typing.List[vmf_property.VMFProperty | VMFElement] = None,
                case_sensitive_name: bool = False) -> bool:
        """
        :param _name: The name to check
        :type _name: str
        :param _items: The items to check
        :type _items: list
        :param case_sensitive_name: Whether the name should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: if this element matches the given parameters
        :rtype: bool
        """
        if case_sensitive_name:
            return self._element_name == _name and (_items is None or _items == self._items)
        return self._element_name.lower() == _name.lower() and (_items is None or _items == self._items)

    def first_layer_has(self, property_name: str, property_value: str = None,
                        case_sensitive_name: bool = False) -> bool:
        """
        Check if the element contains a property with the given name and (optional) given value.
        No sub-elements are checked.

        :param property_name: The name of the property to check
        :type property_name: str
        :param property_value: The value of the property, defaults to None. If None, will only check for existence.
        :type property_value: str, optional
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: if the property was found
        :rtype: bool
        """
        for p in self._items:
            if type(p) == vmf_property.VMFProperty and p.matches(property_name, property_value, case_sensitive_name):
                return True
        return False

    def add_property(self, prop: vmf_property.VMFProperty) -> bool:
        """
        Adds a property to the element.
        :param prop: The property to add
        :type prop: VMFProperty
        :return: if the property was added
        :rtype: bool
        """
        self._items.append(prop)
        return True

    def add_property_by_values(self, prop_name: str, new_value: str) -> bool:
        """
        Adds a property to the element.
        :param prop_name: The name of the property to add
        :type prop_name: str
        :param new_value: The value of the property to add
        :type new_value: str
        :return: if the property was added
        :rtype: bool
        """
        self._items.append(vmf_property.VMFProperty(prop_name, new_value))
        return True

    def modify_property_name(self, property_name: str, new_name: str, case_sensitive_name: bool = False) -> bool:
        """
        Modifies the name of a property.
        :param property_name: The name of the property to modify
        :type property_name: str
        :param new_name: The new name of the property
        :type new_name: str
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: if the name was found and modified
        :rtype: bool
        """
        for p in self._items:
            if type(p) == vmf_property.VMFProperty and (p.matches(property_name, None, case_sensitive_name)):
                p.rename(new_name)
                return True
            else:
                p.modify_property_name(property_name, new_name)
        return False

    def modify_property_value(self, property_name: str, new_value: str, case_sensitive_name: bool = False) -> bool:
        """
        Modifies the value of a property.
        :param property_name: The name of the property to modify
        :type property_name: str
        :param new_value: The new value of the property
        :type new_value: str
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: if the property was found and modified
        :rtype: bool
        """
        for p in self._items:
            if (type(p) == vmf_property.VMFProperty) and (p.matches(property_name, None, case_sensitive_name)):
                p.set_value(new_value)
                return True
            else:
                p.modify_property_value(property_name, new_value)
        return False

    def delete_property(self, property_name: str, property_value: str = None,
                        case_sensitive_name: bool = False) -> bool:
        """
        Deletes a property from the element.

        :param property_name: The name of the property to delete
        :type property_name: str
        :param property_value: The value of the property to delete, defaults to None. If None, will delete the first property with the given name.
        :type property_value: str, optional
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: if the property was found and deleted
        :rtpye: bool
        """
        for p in self._items:
            if type(p) == vmf_property.VMFProperty:
                if p.matches(property_name, property_value, case_sensitive_name):
                    self._items.remove(p)
                    return True
            else:
                p.delete_property(property_name)
        return False

    def get_subproperties_by_name(self, name: str, case_sensitive_name: bool = False) -> typing.List[
        vmf_property.VMFProperty]:
        """
        Returns a list of all properties with the given name.
        :param name: The name of the properties to return
        :type name: str
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: A list of all properties with the given name
        :rtype: list
        """
        matching_props: list[vmf_property.VMFProperty] = []
        for p in self._items:
            if type(p) == vmf_property.VMFProperty and p.matches(name, None, case_sensitive_name):
                matching_props.append(p)
        return matching_props

    def get_first_subproperty(self, name: str, case_sensitive_name: bool = False) -> vmf_property.VMFProperty:
        """
        Returns first subproperty if it exists. Otherwise None
        :param name: Name of the property to return
        :type name: str
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: The first property with the given name
        :rtype: list
        """
        if len(properties := self.get_subproperties_by_name(name, case_sensitive_name)) != 0:
            return properties[0]
        return None

    def get_subelements_by_name(self, name: str, case_sensitive_name: bool = False) -> typing.List[VMFElement]:
        """
        Returns a list of all elements with the given name
        :param name: Name of the element to return
        :type name: str
        :param case_sensitive_name: Whether the name of the element should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: A list of all elements with the given name
        :rtype: list
        """
        matching_elems: list[VMFElement] = []
        for e in self._items:
            if type(e) == VMFElement and e.matches(name, None, case_sensitive_name):
                matching_elems.append(e)
        return matching_elems

    def get_first_subelement(self, name: str, case_sensitive_name: bool = False) -> VMFElement:
        if len(elements := self.get_subelements_by_name(name, case_sensitive_name)) != 0:
            return elements[0]
        return None

    @staticmethod
    def _elem_str_helper(_item: VMFElement, indent: int) -> str:
        """
        Another helper for __str__

        :param _item: The item to print
        :type _item: VMFElement
        :param indent: indentation level
        :type indent: int
        :return: String representation of element
        :rtype: str
        """
        item_str: str = ""
        if len(_item.get_items()) > 0:
            for p in _item.get_items():
                if type(p) == VMFElement:
                    item_str += "\t" * indent + p.get_name()
                    item_str += "\n" + "\t" * indent + "{\n" + p._elem_str_helper(p, indent + 1)
                    item_str += "\t" * indent + "}\n"
                else:
                    item_str += "\t" * indent + f"{p}\n"

        return item_str

    def __str__(self) -> str:
        """
        Returns a string representation of the element as it would appear in a .vmf
        :return: The string representation of the element
        :rtype: str
        """

        return self._element_name + "\n{\n" + VMFElement._elem_str_helper(self, 1) + "\n}\n"
