from __future__ import annotations
from vmf_property import VMFProperty
from vmf_item_list import VMFItemList


class VMFElement:
    """
    Represents an element of a .vmf file. Contains a name and a list of properties/elements.
    Example:
    solid
    {
        "thing" "value"
        "thing" "value2" // NON-UNIQUE KEYS
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
    """

    def __init__(self, element_name: str, elements: VMFItemList[VMFElement] = None, properties: VMFItemList[VMFProperty] = None):
        self._element_name = element_name
        self._elements = elements
        self._properties = properties

    def get_element_name(self) -> str:
        """
        Gets the name of this element.

        :return: The name of this element
        :rtype: str
        """
        return self._element_name

    def get_elements(self) -> VMFItemList[VMFElement]:
        return self._elements

    def get_properties(self) -> VMFItemList[VMFProperty]:
        """
        Returns a list of all properties of this element.
        :return:
        """
        return self._properties


    def set_element_name(self, new_name: str) -> None:
        """
        Renames this element.
        :param new_name: The new name of this element
        :type new_name: str
        :return: None
        :rtype: None
        """
        self._element_name = new_name


    def set_elements(self, elements: VMFItemList[VMFElement]) -> None:
        self._elements = elements

    def set_properties(self, properties: VMFItemList[VMFProperty]) -> None:
        self._properties = properties

    def has_properties(self) -> bool:
        return len(self.get_properties()) == 0


    def __eq__(self, other: VMFElement | str ) -> bool:
        if type(other) == str:
            return self._element_name.lower() == other.lower()
        elif type(other) == type(self):
            return self.get_element_name().lower() == other.get_element_name().lower() and self.get_elements() == other.get_elements() and self.get_properties() == other.get_properties()
        return False



    def __len__(self):
        return len(self.get_properties()) + len(self.get_elements())

    def __getitem__(self, item : str | VMFProperty) -> VMFItemList[VMFProperty]:
        return self.get_properties()[item]

    # def __setitem__(self, item_name : str, item_value) -> None:
    #     self[item_name].set_value(item_value)

    def __delitem__(self, item : str | VMFProperty) -> None:
        del self.get_properties()[item]


    def __contains__(self, other : VMFProperty | str):
        return other in self.get_elements() or other in self.get_properties()

    def is_empty(self) -> bool:
        """
        Does what it says.
        :return: If this has no items in it
        :rtype: bool
        """
        return len(self) == 0

    def add_property(self, property_: VMFProperty) -> None:
        """
        Adds a property to the element.
        :param property_: The property to add
        :type property_: VMFProperty
        """
        self._properties.append(property_)

    def add_property_by_values(self, property_name: str, property_value: str) -> None:
        """
        Adds a property to the element.
        :param property_name: The name of the property to add
        :type property_name: str
        :param property_value: The value of the property to add
        :type property_value: str
        """
        self._properties.append(VMFProperty(property_name, property_value))

    def modify_property_names(self, property_name: str, new_name: str) -> None:
        """
        Modifies the name of a property.
        :param property_name: The name of the property to modify
        :type property_name: str
        :param new_name: The new name of the property
        :type new_name: str
        """
        for p in self[property_name]:
            p.set_name(new_name)

    def modify_property_values(self, property_name: str, new_values : str | list[str]) -> None:
        """
        Modifies the value of a property.
        :param property_name: The name of the property to modify
        :type property_name: str
        :param new_values: The new value of the property. A string will be applied to all values of the property on the first layer
        :type new_values: str | list
        """
        properties_to_change : VMFItemList[VMFProperty] = self[property_name]
        if type(new_values) == list:
            if len(new_values) != len(properties_to_change):
                raise ValueError(f"length of values does not match length of self[{property_name}]")
        i : int = 0
        for p in properties_to_change:
            if type(new_values) == list:
                p.set_value(new_values[i])
                i += 1
            else:
                p.set_value(new_values)



    def get_subelements_by_name(self, name: str) -> VMFItemList[VMFElement]:
        """
        Returns a list of all elements with the given name
        :param name: Name of the element to return
        :type name: str
        :return: A list of all elements with the given name
        :rtype: list
        """
        return self.get_elements()[name]


    @staticmethod
    def elem_str_helper(_item: VMFElement, indent: int) -> str:
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
        if len(_item) > 0:
            for p in _item.get_elements():
                item_str += "\t" * indent + p.get_name()
                item_str += "\n" + "\t" * indent + "{\n" + p.elem_str_helper(p, indent + 1)
                item_str += "\t" * indent + "}\n"

            for p in _item.get_properties():
                item_str += "\t" * indent + f"{p}\n"

        return item_str

    def __str__(self) -> str:
        """
        Returns a string representation of the element as it would appear in a .vmf
        :return: The string representation of the element
        :rtype: str
        """

        return self._element_name + "\n{\n" + VMFElement.elem_str_helper(self, 1) + "\n}\n"
