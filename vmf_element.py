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

    def first_layer_has(self, prop_name : str, prop_value : str = None, case_sensitive_name : bool = True) -> bool:
        '''
        Check if the element contains a property with the given name and (optional) given value. No sub-elements are checked.

        :param element: The element to check
        :type element: VMFElement
        :param prop_name: The name of the property to check
        :type prop_name: str
        :param prop_value: The value of the property, defaults to None. If None is selected, will only check if the property exists.
        :type prop_value: str, optional
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to True.
        :type case_sensitive_name: bool, optional
        :return: if the property was found
        :rtype: bool
        '''
        for p in self.props:
            if type(p) == prop.VMFProperty and p.matches(prop_name, prop_value, case_sensitive_name):
                return True
        return False
            
    def is_empty(self) -> bool:
        return len(self.props) == 0

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

    def delete_prop(self, prop_name : str, prop_value : str = None, case_sensitive_name : bool = True) -> bool:
        '''
        Deletes a property from the element.

        :param prop_name: The name of the property to delete
        :type prop_name: str
        :param prop_value: The value of the property to delete, defaults to None. If None is selected, will delete the first property with the given name.
        :type prop_value: str, optional
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to True.
        :type case_sensitive_name: bool, optional
        :return: if the property was found and deleted
        :rtpye: bool
        '''
        for p in self.props:
            if type(p) == prop.VMFProperty and p.matches(prop_name, prop_value, case_sensitive_name):
                self.props.remove(p)
                return True
            else:
                p.delete_prop(prop_name)
        return False
    
    def modify_prop_value(self, prop_name : str, new_value : str, case_sensitive_name : bool = True) -> bool:
        '''
        Modifies the value of a property.
        :param prop_name: The name of the property to modify
        :type prop_name: str
        :param new_value: The new value of the property
        :type new_value: str
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to True.
        :type case_sensitive_name: bool, optional
        :return: if the property was found and modified
        :rtype: bool
        '''
        for p in self.props:
            if (type(p) == prop.VMFProperty) and (p.matches(prop_name, None, case_sensitive_name)):
                p.set_value(new_value)
                return True
            else:
                p.modify_prop_value(prop_name, new_value)
        return False

    def modify_prop_name(self, prop_name : str, new_name : str, case_sensitive_name : bool = True) -> bool:
        '''
        Modifies the name of a property.
        :param prop_name: The name of the property to modify
        :type prop_name: str
        :param new_name: The new name of the property
        :type new_name: str
        :param case_sensitive_name: Whether the name of the property should be case sensitive, defaults to True.
        :type case_sensitive_name: bool, optional
        :return: if the name was found and modified
        :rtype: bool
        '''
        for p in self.props:
            if type(p) == prop.VMFProperty and (p.matches(prop_name, None, case_sensitive_name)):
                p.rename(new_name)
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
    
    def get_name(self) -> str:
        '''
        Gets the name of this element.

        :return: The name of this element
        :rtype: str
        '''
        return self.name

    def get_props(self) -> typing.List[prop.VMFProperty | VMFElement]:
        '''
        Returns a list of all properties of this element.
        :return: A list of all properties of this element
        :rtype: list
        '''
        return self.props 
    
    def get_subprops_by_name(self, name : str, case_sensitive_name : bool = True) -> typing.List[prop.VMFProperty | VMFElement]:
        matching_props = []
        for p in self.props:
            if p.matches(name, None, case_sensitive_name):
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
    
    def matches(self, _name : str, _props : typing.List[prop.VMFProperty | VMFElement] = None, case_sensitive_name : bool = True) -> bool:
        '''
        :param _name: The name to check
        :type _name: str
        :param _props: The properties to check
        :type _props: list
        :param case_sensitive_name: Whether the name should be case sensitive, defaults to True.
        :type case_sensitive_name: bool, optional
        :return: if this element matches the given parameters
        :rtype: bool
        '''
        if (case_sensitive_name):
            return self.name == _name and (_props == None or _props == self.props)
        return self.name.lower() == _name.lower() and (_props == None or _props == self.props)

    def elem_str_helper(self, prop : VMFElement, indent : int) -> str:
        '''
        Another helper for __str__

        :param indent: indentation level
        :type indent: int
        :return: String representation of element
        :rtype: str
        '''
        prop_str : str = ""
        if len(prop.get_props()) > 0:
            for p in prop.get_props():
                if type(p) == VMFElement:
                    prop_str += "\t"*indent + p.get_name() + "\n" + "\t" * indent + "{\n" + p.elem_str_helper(p, indent+1) + "\t" * indent + "}\n"
                else:
                    prop_str += "\t"*indent + f"{p}\n"

        

        return prop_str

    def __str__(self) -> str:
        '''
        Returns a string representation of the element as it would appear in a .vmf
        :return: The string representation of the element
        :rtype: str
        '''
        
        return self.name + "\n{\n" + self.elem_str_helper(self, 1) + "\n}\n"