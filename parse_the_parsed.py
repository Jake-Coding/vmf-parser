import sys

from lark import *

the_tree : Tree
with open("./fgd_tree.txt", "r") as f:
    the_tree = eval(f.read())



def indent(s, level : int = 1):
    s = s.split('\n')
    s = [((level * 4) * ' ') + line for line in s]
    s = "\n".join(s)
    return s

class TransformToPyClass(visitors.Transformer):

    known_types : dict[str : type] = {
        "string" : str,
        "integer" : int,
        "float" : float,
        "boolean" : bool,
        "angle" : list[float],
        "color255" : list[float],
        "color1" : list[float],
        "vector" : list[float],
        "target_destination" : str,
        "target_name_or_class" : str,
        "target_source" : str,
    }


    discard = visitors.Discard

    @staticmethod
    def fix_str(string):

        fixed_ish =  string.strip().strip("'").strip('"')
        if fixed_ish in [":"]:
            return None
        return fixed_ish

    VECTOR = lambda arg1, arg2 : Token(arg2.type, [int(v) if float(v).is_integer() else float(v) for v in arg2.split(" ") ])
    COLOR = VECTOR
    ALPHANUM = fix_str
    VALIDNAME = fix_str
    STRING = fix_str
    PATH = fix_str
    PROPERTY = fix_str
    SIGNED_NUMBER = float
    BASECLASS = VALIDNAME
    ENTITY_PROPERTY_DESCRIPTION = STRING
    ENTITY_PROPERTY_STRING_NAME = STRING

    def __default_token__(self, token : Token):
        # print(token)
        return Token(token.type, TransformToPyClass.fix_str(token))


    @staticmethod
    def _get_entity_normal_property_data(entity_property: Tree):
        pass

    @staticmethod
    def _get_entity_flags_property_data(entity_property: Tree):
        pass

    @staticmethod
    def _get_entity_choices_property_data(entity_property: Tree):
        pass

    @staticmethod
    def _get_entity_io_property_data(entity_property: Tree):
        pass

    @staticmethod
    def _get_entity_non_io_property_data(entity_property : Tree):
        options = {
            "entity_property_normal" : TransformToPyClass._get_entity_normal_property_data,
            "entity_property_flags" : TransformToPyClass._get_entity_flags_property_data,
            "entity_property_choices" : TransformToPyClass._get_entity_choices_property_data,


        }
        property_type = entity_property.children[0].data

        return options[property_type](entity_property)

    @staticmethod
    def _make_property_doc(entity_property_data: dict):
        # return a docstring of the relevant property i.e. name: description = type (default= default), options = [options]
        pass

    @staticmethod
    def _make_property_getter(entity_property_data: dict):
        pass

    @staticmethod
    def _make_property_setter(entity_property_data: dict):
        # if readonly, return ""
        # if choices, make sure input is within choices
        pass

    @staticmethod
    def _make_property_angle_checker(entity_property_data: dict):
        # if entity_property is of type angle or angle_negative_pitch, create functions to see if its pointing up or down
        # else return ""
        pass


    def description(self, args):
        # print(args)
        fixed =  TransformToPyClass.fix_str(args[0])
        if fixed:
            return fixed
        return None


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
            i = 0
            while i < len(property_values):

                if isinstance(property_values[i], Token):
                    property_values[i] = f"{property_values[i].type} = {property_values[i].value}"

                i += 1

            property_values = [str(v) for v in property_values]

            return Token(property_name, ", ".join(property_values))
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
        # print(args)
        entity_name, entity_class = TransformToPyClass.make_entity_inner_class_str(args[2])
        class_name = args[0].replace("@", '')
        inheritance_sect = args[1]
        return f"class {entity_name}({class_name}, {inheritance_sect}\n{indent(entity_class)}\n" + "}"

    def inheritance_section(self, args):
        if not args:
            return ":\n"
        string_to_return = ""
        to_inherit : Token
        for to_inherit in args:
            if to_inherit.type == "base":
                to_inherit = to_inherit.replace("'", "")
                string_to_return += to_inherit.strip()
        string_to_return += "):\n"

        nonbase_inheritance_str = ""
        # print(args)
        for to_inherit in args:
            if to_inherit.type != "base":
                if to_inherit.type:
                    # print(to_inherit.value)
                    value = to_inherit.value

                    nonbase_inheritance_str += f"{to_inherit.type}({value})\n"
                    # print(nonbase_inheritance_str)
                else:
                    nonbase_inheritance_str += f"{to_inherit}\n"
        if nonbase_inheritance_str:
            string_to_return += indent(f"'''\nAdditional Requirements:\n{nonbase_inheritance_str}")
        else:
            string_to_return += indent("'''\n")
        return string_to_return

    @staticmethod
    def make_entity_inner_class_str(entity_tree : Tree) -> (str, str):
        # print(entity_tree)
        entity_name = list(entity_tree.scan_values(lambda v : isinstance(v, Token) and v.type == "ENTITY_NAME"))[0]
        # print(entity_name)



        entity_docstring = ""
        entity_init_section = ""
        entity_init_header = "def __init__(self, "
        entity_init_inner = ""
        entity_getters = ""
        entity_setters = ""
        entity_helpful_functions = ""

        # print(entity_tree)
        for n in entity_tree.find_data("description_section"):  # entity descriptions
            # print(n)
            if any(n.children):
                entity_docstring += n.children[0].strip() + "\n"

        inner_section : Tree = list(entity_tree.find_data("entity_inner_section"))[0]
        # print(inner_section)
        properties = inner_section.find_data("entity_property")

        for ent_property in properties:

            property_type = ent_property.children[0].data

        for ent_input in inner_section.find_data("entity_input"):
            pass

        for ent_output in inner_section.find_data("entity_output"):
            pass

        # print(entity_docstring)
        entity_docstring += "'''"
        entity_init_section = f"{entity_init_header}\n{indent(entity_init_inner)}"
        full_entity_inner = f"""{entity_docstring}\n{entity_init_section}\n\n{entity_getters}\n{entity_setters}\n{entity_helpful_functions}"""
        return entity_name, full_entity_inner









try:
    transformed = (TransformToPyClass().transform(the_tree))
    print(transformed.pretty())
except visitors.VisitError as e:
    raise e.orig_exc


