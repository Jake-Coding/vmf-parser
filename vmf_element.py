from __future__ import annotations
import vmf_property as property
import typing


class VMFElement:
    """
    Represents an element of a .vmf file. Contains a name and a list of properties. Properties can be other elements as well.
    :ivar name: The name of the element
    :type name: str
    :ivar properties: The properties of the element. These can be VMFProperty objects or VMFElement objects.
    :type properties: list
    """

    def __init__(self, name: str, properties: typing.List[property.VMFProperty | VMFElement] = None):
        self.name = name
        self.properties = properties

    def first_layer_has(self, property_name: str, property_value: str = None,
                        case_sensitive_name: bool = False) -> bool:
        """
        Check if the element contains a property with the given name and (optional) given value. No sub-elements are checked.

        :param property_name: The name of the property to check
        :type property_name: str
        :param property_value: The value of the property, defaults to None. If None is selected, will only check if the property exists.
        :type property_value: str, optional
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: if the property was found
        :rtype: bool
        """
        for p in self.properties:
            if type(p) == property.VMFProperty and p.matches(property_name, property_value, case_sensitive_name):
                return True
        return False

    def is_empty(self) -> bool:
        return len(self.properties) == 0

    def for_all(self, func: typing.Callable) -> None:
        """
        Calls a function recursively on all properties of the element.
        :param func: The function to call
        :type func: typing.Callable
        :return: None
        :rtype: None
        """
        for p in self.properties:
            if type(p) == VMFElement:
                func(p)
                p.for_all(func)

    def delete_property(self, property_name: str, property_value: str = None,
                        case_sensitive_name: bool = False) -> bool:
        """
        Deletes a property from the element.

        :param property_name: The name of the property to delete
        :type property_name: str
        :param property_value: The value of the property to delete, defaults to None. If None is selected, will delete the first property with the given name.
        :type property_value: str, optional
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: if the property was found and deleted
        :rtpye: bool
        """
        for p in self.properties:
            if type(p) == property.VMFProperty:
                if p.matches(property_name, property_value, case_sensitive_name):
                    self.properties.remove(p)
                    return True
            else:
                p.delete_property(property_name)
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
        for p in self.properties:
            if (type(p) == property.VMFProperty) and (p.matches(property_name, None, case_sensitive_name)):
                p.set_value(new_value)
                return True
            else:
                p.modify_property_value(property_name, new_value)
        return False

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
        for p in self.properties:
            if type(p) == property.VMFProperty and (p.matches(property_name, None, case_sensitive_name)):
                p.rename(new_name)
                return True
            else:
                p.modify_property_name(property_name, new_name)
        return False

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
        self.properties.append(property.VMFProperty(prop_name, new_value))
        return True

    def add_property(self, prop: property.VMFProperty) -> bool:
        """
        Adds a property to the element.
        :param prop: The property to add
        :type prop: VMFProperty
        :return: if the property was added
        :rtype: bool
        """
        self.properties.append(prop)
        return True

    def rename(self, new_name: str) -> None:
        """
        Renames this element.
        :param new_name: The new name of this element
        :type new_name: str
        :return: None
        :rtype: None
        """
        self.name = new_name

    def get_name(self) -> str:
        """
        Gets the name of this element.

        :return: The name of this element
        :rtype: str
        """
        return self.name

    def get_properties(self) -> typing.List[property.VMFProperty | VMFElement]:
        """
        Returns a list of all properties of this element.
        :return: A list of all properties of this element
        :rtype: list
        """
        return self.properties

    def get_subproperties_by_name(self, name: str, case_sensitive_name: bool = False) -> typing.List[
        property.VMFProperty | VMFElement]:
        """
        Returns a list of all properties with the given name.
        :param name: The name of the properties to return
        :type name: str
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: A list of all properties with the given name
        :rtype: list
        """
        matching_props = []
        for p in self.properties:
            if p.matches(name, None, case_sensitive_name):
                matching_props.append(p)
        return matching_props

    def set_properties(self, properties: typing.List[property.VMFProperty | VMFElement]) -> None:
        """
        Sets the properties of this element.
        :param properties: The properties to set
        :type properties: list
        :return: None
        :rtype: None
        """
        self.properties = properties

    def matches(self, _name: str, _properties: typing.List[property.VMFProperty | VMFElement] = None,
                case_sensitive_name: bool = False) -> bool:
        """
        :param _name: The name to check
        :type _name: str
        :param _properties: The properties to check
        :type _properties: list
        :param case_sensitive_name: Whether the name should be case sensitive, defaults to False.
        :type case_sensitive_name: bool, optional
        :return: if this element matches the given parameters
        :rtype: bool
        """
        if case_sensitive_name:
            return self.name == _name and (_properties is None or _properties == self.properties)
        return self.name.lower() == _name.lower() and (_properties is None or _properties == self.properties)

    @staticmethod
    def elem_str_helper(_property: VMFElement, indent: int) -> str:
        """
        Another helper for __str__

        :param _property: The property to print
        :type _property: VMFElement
        :param indent: indentation level
        :type indent: int
        :return: String representation of element
        :rtype: str
        """
        property_str: str = ""
        if len(_property.get_properties()) > 0:
            for p in _property.get_properties():
                if type(p) == VMFElement:
                    property_str += "\t" * indent + p.get_name()
                    property_str += "\n" + "\t" * indent + "{\n" + p.elem_str_helper(p, indent + 1)
                    property_str += "\t" * indent + "}\n"
                else:
                    property_str += "\t" * indent + f"{p}\n"

        return property_str

    def __str__(self) -> str:
        """
        Returns a string representation of the element as it would appear in a .vmf
        :return: The string representation of the element
        :rtype: str
        """

        return self.name + "\n{\n" + VMFElement.elem_str_helper(self, 1) + "\n}\n"
