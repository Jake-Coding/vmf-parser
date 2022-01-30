class VMFProperty:
    '''
    Represents a property in a vmf file. (i.e. "classname" "worldspawn"). It's a key value pair. I should probably make this a dictionary. Don't worry about it.
    :ivar name: The name of the property
    :type name: str
    :ivar value: The value of the property
    :type value: str
    '''
    def __init__(self, name: str, value: str):
        '''
        Initializes a new instance of the VMFProperty class. Self-explanatory.
        :param name: The name of the property
        :type name: str
        :param value: The value of the property
        :type value: str
        '''
        self.name = name
        self.value = value
    
    def __str__(self):
        '''
        Returns a string representation of this property as it would appear in a .vmf 
        :return: The string representation of this property
        :rtype: str
        '''
        return f"\"{self.name}\" \"{self.value}\""
    
    def set_value(self, new_value: str) -> None:
        '''
        Modifies the value of a property
        :param new_value: The new value of the property
        :type new_value: str
        :return: None
        :rtype: None
        '''
        self.value = new_value

    def get_value(self) -> str: 
        '''
        get value of this property

        :return: value of this property
        :rtype: str
        '''
        return self.value

    def get_name(self) -> str:
        '''
        get name of this property

        :return: name of this property
        :rtype: str
        '''
        return self.name

    def rename(self, new_name : str) -> None:
        '''
        Renames this property.
        :param new_name: The new name of this property
        :type new_name: str
        :return: None
        :rtype: None
        '''
        self.name = new_name
    
    def matches(self, name : str, value : str = None, case_sensitive_name : bool = True) -> bool:
        '''
        Checks if this property matches the given name and value.
        :param name: The name to check
        :type name: str
        :param value: The value to check, defaults to None. If None is selected, will return if the name matches.
        :type value: str, optional
        :param case_sensitive_name: Whether or not the name should be case sensitive, defaults to True.
        :type case_sensitive_name: bool, optional
        :return: if this property matches the given name and value
        :rtype: bool
        '''
        if (case_sensitive_name) {
            return self.name == name and (self.value == value or value is None)
        }
        return self.name.lower() == name.lower() and (self.value == value or value is None)