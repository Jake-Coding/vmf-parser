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
        if len(fixed_ish.split(" ")) > 2:
            try:
                return [int(v) if float(v).is_integer() else float(v) for v in fixed_ish.split(" ")]
            except:
                return fixed_ish
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
    READONLY = STRING

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


    @staticmethod
    def _get_entity_name(entity_tree : Tree) -> Token:
        return list(entity_tree.scan_values(lambda v : isinstance(v, Token) and v.type == "ENTITY_NAME"))[0]


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

    def get_class_by_name(self, class_name: str, classes ):
        for fgd_class_ in classes:
            if fgd_class_[2].children[0] == class_name:
                return fgd_class_
        return None

    def fgd(self, big_tree : list):
        # print(big_tree)

        fgd_class_ : list
        fgd_classes = [v for v in big_tree if v[0].type == "CLASS_IDENTIFIER"]


        def extract_nested_values(it):
            if isinstance(it, list):
                for sub_it in it:
                    yield (sub_it)
            elif isinstance(it, dict):
                for value in it.values():
                    yield from extract_nested_values(value)


        for fgd_class_ in fgd_classes:

            needed_properties = {"for_super": [], "unique":[]}
            inheritance = fgd_class_[1]
            ent : Tree
            ent = fgd_class_[2]
            ent_desc = list(ent.find_data("description_section"))[0].children[0]
            ent_name = TransformToPyClass._get_entity_name(ent)
            # print(ent_desc)
            big_properties_dict = self._get_properties(fgd_class_, fgd_classes)
                    # MAKE RECURSIVELY INHERIT
            needed_properties["unique"] = big_properties_dict["props"]

            b = big_properties_dict
            b["props"] = []

            needed_properties["for_super"] = list(extract_nested_values(b))

            # print(needed_properties)
            docstring = self._make_docstring(ent_desc, inheritance, needed_properties)
            # print(docstring)

            init_string = self._make_init(needed_properties)
            # print(init_string)

            getters = self._make_getters(needed_properties)
            # print(getters)

            setters = self._make_setters(needed_properties)


    def _make_setters(self, needed_properties : dict):
        setters = []
        for p in needed_properties["unique"]:
            setters.append(self._make_setter(p))
        return "\n\n".join(setters)

    def _make_setter(self, property_ : dict):
        return "this settin"
        pass #TODO this shit

    def _make_getters(self, needed_properties : dict):
        # inherit super getters from parent
        getters = []
        for p in needed_properties["unique"]:
            getters.append(self._make_getter(p))
        return "\n\n".join(getters)

    def _make_getter(self, property_ : dict):
        string = f"def get_{property_['name']}():"
        if property_.get('recommended_type'):
            string += f" -> {property_['recommended_type'].__name__}"
        string += "\n"
        string += indent(f"return self.{property_['name']}")

        return string + "\n"





    def _make_init(self, needed_properties : dict):
        signature = self._make_init_signature(needed_properties)
        # print(signature)
        super_call = []
        for p in needed_properties["for_super"]:
            super_call.append(p["name"])

        unique_property_inits = []
        for p in needed_properties["unique"]:
            property_starting_string = f"self.{p['name']} = {p['name']}\n"
            if p.get('default'):
                property_starting_string += f"if {p['name']} is None:\n\tself.{p['name']} = {p['default']}\n"

            unique_property_inits.append(property_starting_string)

        super_call = ", ".join(super_call)
        unique_property_inits = "\n".join(unique_property_inits)
        super_call = f"super({super_call})\n"
        final_str = f"def __init__({signature}):\n" + indent(f"\n{super_call}" + unique_property_inits)

        return final_str





    def _make_init_signature(self, needed_properties : dict):
        signs = ["self "]
        for p in needed_properties["for_super"]:
            hinted_name = self._make_type_hinted_property_var_name(p)
            hinted_name += "= None"
            signs.append(hinted_name)

        for p in needed_properties["unique"]:
            hinted_name = self._make_type_hinted_property_var_name(p)
            hinted_name += "= None"
            signs.append(hinted_name)
        return ",\n\t".join(signs)

    def _make_type_hinted_property_var_name(self, property_ : dict) -> str:
        if property_.get("recommended_type"):
            return f"{property_['name']} : {property_['recommended_type'].__name__} "
        return property_['name'] + " "

    def _make_docstring(self, ent_desc : str = None, inheritance : dict = None, needed_properties : dict = None):
        string = "'''\n"
        # print(ent_desc)
        if ent_desc:
            string += ent_desc
            string += "\n\n"
        if inheritance["nonbase"]:
            string += "This class needs addition class properties to function in-game, including\n"
            for nb_inheritance in inheritance["nonbase"]:
                string += nb_inheritance
                string += "\n"
        string += "This class also may need additional properties as defined by its base(class) inheritances\n\n"
        if needed_properties and needed_properties.get("unique"):
            string += "UNIQUE PROPERTIES"
            for unique_needed_property in needed_properties["unique"]:
                # print(unique_needed_property)
                property_string = ""
                if unique_needed_property["readonly"]:
                    property_string += "READONLY "
                property_string += self._make_type_hinted_property_var_name(unique_needed_property)
                property_string += f"({unique_needed_property['type']}) | "
                if unique_needed_property.get("str_name"):
                    property_string += f"{unique_needed_property['str_name']}"
                if unique_needed_property.get("default"):
                    property_string += f"\n\tDEFAULT: {unique_needed_property['default']}"
                if unique_needed_property.get("description"):
                    property_string += f"\n\t{unique_needed_property['description']}"

                if unique_needed_property['type'] == "choices":
                    property_string += "\n\tCHOICES\n"
                    for choice in unique_needed_property["choices"]:
                        property_string += "\t\t" + str(choice) + "\n"

                elif unique_needed_property['type'] == "flags":
                    property_string += "\n\tFLAGS\n"
                    flag : dict
                    for flag in unique_needed_property["flags"]:
                        property_string += f"\t\t{int(list(flag.keys())[0])} : {list(flag.values())[0][1]}\n\t\t\t{list(flag.values())[0][0]}\n"

                string += f"\n{property_string}\n"

        string += "\n'''\n"
        return string









            # print(ent_name)


    def _get_properties(self, class_ : list, classes):
        property_dict = {"super_props" : {},
                         "props" : []
                         }
        if class_[1]["base"]:
            for parentclass in class_[1]["base"]:
                parent_properties = self._get_properties(self.get_class_by_name(parentclass, classes), classes)
                property_dict["super_props"] |= parent_properties


        for prop in (class_[2].find_data("entity_property")):
            property_dict["props"].append(prop.children[0])

        return property_dict


    def fgd_class(self, args):
        if not args:
            return self.discard
        return args

    def inheritance_section(self, args):
        if not args:
            return {"base": None, "nonbase":None}
        to_inherit : Token
        base_inherits = []
        for to_inherit in args:
            if to_inherit.type == "base":
                for individual_to_inherit in to_inherit.split(","):
                    individual_to_inherit = individual_to_inherit.replace("'", "")
                    base_inherits.append(individual_to_inherit.strip())

        nonbase_inherits = []
        for to_inherit in args:
            if to_inherit.type != "base":
                if to_inherit.type:
                    # print(to_inherit.value)
                    value = to_inherit.value

                    nonbase_inherits.append(f"{to_inherit.type}({value})")
                    # print(nonbase_inheritance_str)
                else:
                    nonbase_inherits.append(f"{to_inherit}")

        return {"base" : base_inherits, "nonbase" : nonbase_inherits}

    @staticmethod
    def make_entity_inner_class(entity_tree : Tree, inheritance : dict[str : list]) -> (str, str):
        # print(inheritance)
        # print(entity_tree)
        entity_name = list(entity_tree.scan_values(lambda v : isinstance(v, Token) and v.type == "ENTITY_NAME"))[0]
        # print(entity_name)



        entity_docstring = ""
        entity_init_section = ""
        entity_init_header = ""
        entity_init_inner = ""
        entity_getters = ""
        entity_setters = ""
        entity_helpful_functions = ""

        # print(entity_tree)
        for n in entity_tree.find_data("description_section"):  # entity descriptions
            # print(n)
            if any(n.children):
                entity_docstring += n.children[0].strip() + "\n"

        if inheritance["nonbase"]:
            entity_docstring += "Additional Requirements:\n"
            entity_docstring += "\n".join(inheritance["nonbase"])

        if inheritance["base"]:
            for base_to_inherit_from in inheritance["base"]:
                entity_init_header += "" # Gotta grab stuff for super


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
        entity_init_section = f"{entity_init_header}\n{indent(entity_init_inner)}"
        full_entity_inner = f"""{entity_docstring}\n{entity_init_section}\n\n{entity_getters}\n{entity_setters}\n{entity_helpful_functions}"""
        return {
            "name": entity_name,
            "docstring" : entity_docstring,
            "init" : {"header" : entity_init_header, "inner" : entity_init_inner},
            "getters" : entity_getters,
            "setters" : entity_setters,
            "helpful_funcs" : entity_helpful_functions
        }

    def entity_property_name_and_type(self, args):
        # print(args)
        return {"name" : args[0],
                "type" : args[1],
                "recommended_type" : TransformToPyClass.known_types.get(args[1]),
                "readonly" : bool(args[2])
                }

    def entity_property_normal(self, args):
        # print(args[1])
        ent_specifc_data = {
            "str_name" : args[1],
            "default" : args[2],
            "description" : args[3],
        }
        # print(args[2])
        return args[0] | ent_specifc_data

    def entity_input(self, args):
        # print(args)
        return args[0] | {"description" : args[1]}

    def entity_output(self, args):
        return args[0] | {"description" : args[1]}

    def entity_property_choices(self, args):
        choice_dict = {"choices": []}
        choices : list = args[1:]
        choice : Tree
        for choice in choices:
            choice_dict["choices"].append({choice.children[0] : choice.children[1]})
        return args[0] | choice_dict

    def entity_property_flags(self, args):
        flag_dict = {"flags" : []}
        flags = args[1:]
        flag : Tree
        for flag in flags:
            flag_dict["flags"].append({flag.children[0] : [flag.children[1], bool(int(flag.children[2]))]}) # flagname : flag_description (on/off)
        return args[0] | flag_dict








try:
    transformed = (TransformToPyClass().transform(the_tree))
    # print(transformed.pretty())
except visitors.VisitError as e:
    raise e.orig_exc


