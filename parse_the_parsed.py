import sys

import lark.visitors
from lark import *

the_tree : Tree = None
with open("./fgd_tree.txt", "r") as f:
    the_tree = eval(f.read())




class TransformToPyClass(visitors.Transformer):
    discard = visitors.Discard

    VECTOR = str
    COLOR = VECTOR
    ALPHANUM = str
    VALIDNAME = str
    STRING = str
    PATH = str
    PROPERTY = str
    SIGNED_NUMBER = float
    BASECLASS = VALIDNAME




    # def __default_token__(self, token):
    #     # print(help(token))
    #     super(TransformToPyClass, self).__default_token__(token)
    #
    def element(self, args):
        if not args:
            return self.discard
        return args[0]
    def WS(self, string): return self.discard # i do not care about whitespace
    #
    def mapsize(self, args): return self.discard # i do not care about mapsize
    #
    def autovisgroup(self, args): return self.discard # i do not care about visgroups
    #
    def class_property(self, args):
        # print(args)
        if isinstance(args[0], Tree):
            property_name = args[0].data
            property_values = [v for v in args[0].children if v is not None]
            # print(property_name)
            # print(property_values)

            return Token(property_name, str(property_values)[1:-1])
        else:
            # print(args[0].value)
            return Token(None, args[0].value)

    def class_property_ws(self, args):
        return args[0]

    def inheritance_section_ws(self, args):
        return args[0]

    def fgd_class(self, args):
        if not args:
            return self.discard
        # print(args[2])
        entity_name, entity_class = TransformToPyClass.make_entity_class_str(args[2])
        class_name = args[0].replace("@", '')
        return f"class {entity_name}({class_name}, {args[1]}{entity_class}"

    def inheritance_section(self, args):
        if not args:
            return ":\n"
        string_to_return = ""
        to_inherit : Token
        for to_inherit in args:
            if to_inherit.type == "base":
                to_inherit = to_inherit.replace("'", "")
                string_to_return += to_inherit
        string_to_return += "):\n"
        string_to_return += "'''\nThis class also needs:\n"
        for to_inherit in args:
            if to_inherit.type != "base":
                if to_inherit.type:
                    string_to_return += f"{to_inherit.type}({to_inherit.value})\n"
                else:
                    string_to_return += f"{to_inherit}\n"
        string_to_return += "'''\n"
        string_to_return = string_to_return.replace("\n", "\n\t")
        return string_to_return

    @staticmethod
    def make_entity_class_str(entity_tree : Tree) -> (str, str):
        return "SomeClassname", "there should be a full class definition here :)\n\n\n\n\n\n\n"
        # return (entity_name, entity_class)


try:
    transformed = (TransformToPyClass().transform(the_tree))
    print(transformed.pretty())
except visitors.VisitError as e:
    raise e.orig_exc


