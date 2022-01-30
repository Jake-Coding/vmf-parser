from __future__ import annotations
import vmf_property as prop
import typing

class VMFElement:
    '''
    Represents an element of a .vmf file. Contains a name and a list of properties. Properties can be other elements as well.
    :ivar name: The name of the element
    :type name: str
    :ivar props: The properties of the element. These can be VMFProperty objects or VMFElement objects.
    :type props: list
    '''
    def __init__(self, name: str, props : typing.List[prop.VMFProperty | VMFElement] = None):
        self.name = name
        self.props = props

    def first_layer_has(self, prop_name : str, prop_value : str = None) -> bool:
        '''
        Check if the element contains a property with the given name and (optional) given value. No sub-elements are checked.

        :param element: The element to check
        :type element: VMFElement
        :param prop_name: The name of the property to check
        :type prop_name: str
        :param prop_value: The value of the property, defaults to None. If None is selected, will only check if the property exists.
        :type prop_value: str, optional
        :return: if the property was found
        :rtype: bool
        '''
        for p in self.props:
            if type(p) == prop.VMFProperty and p.matches(prop_name, prop_value):
                return True
        return False
            
    def is_empty(self) -> bool:
        return len(self.props) == 0

    def __str__(self) -> str:
        '''
        Returns a string representation of the element as it would appear in a .vmf
        :return: The string representation of the element
        :rtype: str
        '''
        prop_str: str = "\n".join([f"\t{p}" for p in self.props])
        _str: str = self.name + "\n{\n" + prop_str + "\n}\n"
        return _str

    def for_all(self, func : typing.Callable) -> None:
        '''
        Calls a function recursively on all properties of the element.
        :param func: The function to call
        :type func: typing.Callable
        :return: None
        :rtype: None
        '''
        for p in self.props:
            if type(p) == VMFElement:
                func(p)
                p.for_all(func)

    def delete_prop(self, prop_name : str) -> bool:
        '''
        Deletes a property from the element.

        :param prop_name: The name of the property to delete
        :type prop_name: str
        :return: if the property was found and deleted
        :rtpye: bool
        '''
        for p in self.props:
            if type(p) == prop.VMFProperty and p.name == prop_name:
                self.props.remove(p)
                return True
            else:
                p.delete_prop(prop_name)
        return False
    
    def modify_prop_value(self, prop_name : str, new_value : str) -> bool:
        '''
        Modifies the value of a property.
        :param prop_name: The name of the property to modify
        :type prop_name: str
        :param new_value: The new value of the property
        :type new_value: str
        :return: if the property was found and modified
        :rtype: bool
        '''
        for p in self.props:
            if (type(p) == prop.VMFProperty) and (p.name == prop_name):
                p.set_value(new_value)
                return True
            else:
                p.modify_prop_value(prop_name, new_value)
        return False

    def modify_prop_name(self, prop_name : str, new_name : str) -> bool:
        '''
        Modifies the name of a property.
        :param prop_name: The name of the property to modify
        :type prop_name: str
        :param new_name: The new name of the property
        :type new_name: str
        :return: if the name  was found and modified
        :rtype: bool
        '''
        for p in self.props:
            if type(p) == prop.VMFProperty and p.name == prop_name:
                p.name = new_name
                return True
            else:
                p.modify_prop_name(prop_name, new_name)
        return False
    
    def add_prop_by_values(self, prop_name : str, new_value : str) -> bool:
        '''
        Adds a property to the element.
        :param prop_name: The name of the property to add
        :type prop_name: str
        :param new_value: The value of the property to add
        :type new_value: str
        :return: if the property was added
        :rtype: bool
        '''
        self.props.append(prop.VMFProperty(prop_name, new_value))
        return True
    
    def add_prop(self, prop : prop.VMFProperty) -> bool:
        '''
        Adds a property to the element.
        :param prop: The property to add
        :type prop: VMFProperty
        :return: if the property was added
        :rtype: bool
        '''
        self.props.append(prop)
        return True
    
    def rename(self, new_name : str) -> None:
        '''
        Renames this element.
        :param new_name: The new name of this element
        :type new_name: str
        :return: None
        :rtype: None
        '''
        self.name = new_name
    
    def get_props(self) -> typing.List[prop.VMFProperty | VMFElement]:
        '''
        Returns a list of all properties of this element.
        :return: A list of all properties of this element
        :rtype: list
        '''
        return self.props 
    
    def get_subprops_by_name(self, name : str) -> typing.List[prop.VMFProperty | VMFElement]:
        matching_props = []
        for p in self.props:
            if p.name == name:
                matching_props.append(p)
        return matching_props

    def set_props(self, props : typing.List[prop.VMFProperty | VMFElement]) -> None:
        '''
        Sets the properties of this element.
        :param props: The properties to set
        :type props: list
        :return: None
        :rtype: None
        '''
        self.props = props