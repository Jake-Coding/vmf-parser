from __future__ import annotations
class VMFProperty:
    """
    Represents a property in a vmf file. (i.e. "classname" "worldspawn"). It's a key value pair.
    :ivar name: The name of the property
    :type name: str
    :ivar value: The value of the property
    :type value: str
    """

    def __init__(self, name: str, value: str):
        """
        Initializes a new instance of the VMFProperty class. Self-explanatory.
        :param name: The name of the property
        :type name: str
        :param value: The value of the property
        :type value: str
        """
        self.name = name
        self.value = value

    def get_name(self) -> str:
        """
        get name of this property

        :return: name of this property
        :rtype: str
        """
        return self.name

    def get_value(self) -> str:
        """
        get value of this property

        :return: value of this property
        :rtype: str
        """
        return self.value

    def set_name(self, new_name: str) -> None:
        """
        Renames this property.
        :param new_name: The new name of this property
        :type new_name: str
        :return: None
        :rtype: None
        """
        self.name = new_name

    def set_value(self, new_value: str) -> None:
        """
        Modifies the value of a property
        :param new_value: The new value of the property
        :type new_value: str
        :return: None
        :rtype: None
        """
        self.value = new_value

    def __eq__(self, other: VMFProperty) -> bool:
        """
        Case-insensitive inequality between VMFProperties
        :param other: The object to compare this to
        :type other: VMFProperty
        :return: if the properties have the same name and value
        :rtype: bool
        """
        return type(self) == type(other) and self.name.lower() == other.get_name().lower() and self.value.lower() == other.get_value().lower()

    def __str__(self) -> str:
        """
        Returns a string representation of this property as it would appear in a .vmf
        :return: The string representation of this property
        :rtype: str
        """
        return f"\"{self.name}\" \"{self.value}\""


