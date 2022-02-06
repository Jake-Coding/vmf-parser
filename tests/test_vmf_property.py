from unittest import TestCase
from vmf_property import VMFProperty

class TestVMFProperty(TestCase):

    def test_get_name(self):
        property_test_case: VMFProperty = VMFProperty("hello", "1")
        self.assertEqual(property_test_case.get_name(), "hello")
        property_test_case = VMFProperty("", "1")
        self.assertEqual(property_test_case.get_name(), "")

    def test_get_value(self):
        self.fail()

    def test_set_name(self):
        self.fail()

    def test_set_value(self):
        self.fail()
