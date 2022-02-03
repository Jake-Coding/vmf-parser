import vmf_element as ve
import vmf_property as vp
import typing
class VMF(ve.VMFElement):
    '''
    Parses the VMF file and creates the VMFElement objects.
    '''
    base_elements : list = ["versioninfo", "visgroups", "viewsettings", "world", "entity", "hidden", "cameras", "cordon", "cordons"]

    def __init__(self, vmf_path : str):
        '''
        Initializes the VMF object.
        '''
        self.vmf_path = vmf_path
        self.elements = {"versioninfo": None, "visgroups": None, "viewsettings": None, "world": None, "entities": [], "hidden": None, "cameras": None, "cordon": None, "cordons": None}
        self.parse()

    def parse_property(self, line : str) -> vp.VMFProperty:
        '''
        Parses a property line.
        :param line: The line to parse
        :type line: str
        :return: The parsed property
        :rtype: vp.VMFProperty
        '''
        line = line.strip()
        line = line.split(" ")
        rest_of_data = " ".join(line[1:])
        return vp.VMFProperty(line[0][1:-1], rest_of_data[1:-1])

    def parse_element(self, lines : typing.List[str], current_line : int) -> tuple([ve.VMFElement, int]): 
        '''
        Parses a VMF element.
        :param lines: The lines of the VMF file
        :type lines: typing.List[str]
        :param current_line: The current line to parse
        :type current_line: int
        :return: The parsed element and the next line to parse
        :rtype: tuple([ve.VMFElement, int])
        '''
        name = lines[current_line].strip() 

        current_line += 2 
        bracket_count = 1
        sub_elements = []
        i = current_line
        while i < len(lines):
            line = lines[i]
            line = line.strip()

            if len(line.split(" ")) > 1:
                sub_elements.append(self.parse_property(line))
            else:
                if line == "{":
                    bracket_count += 1
                elif line == "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        break
                else:
                    elem, i = self.parse_element(lines, i)
                    sub_elements.append(elem)
            i += 1
        return (ve.VMFElement(name, sub_elements), i)

    def parse(self) -> None:
        '''
        Parses the VMF file.

        '''

        with open(self.vmf_path, "r") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i]
            line = line.strip()
            if line in VMF.base_elements:
                if line == "entity":
                    entity, i = self.parse_element(lines, i)
                    self.elements["entities"].append(entity) 
                else:
                    # print(line)
                    # if (line == "visgroups"):
                        # print('guh')
                    self.elements[line], i = self.parse_element(lines, i)
                    # print(i)
            else:
                # print(line)
                i += 1

    def tf2_remove_class_attrs(self, class_n : int | str, all_except_one : bool = False) -> None:
        '''
        remove class tf filters and all entities that reference them
        Steps taken: 
        1. Remove all class_n only stuff. If all_except_one is True, instead remove all non-class_n stuff.
        2. filter_multi :))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))) im having a breakdown
            you can infinitely stack these fuckers, so we'll just do it for the first layer for now :)
            TODO: make it work for all layers

        :param class_n: The class number to remove. Can also be a string
        :type class_n: int | str
        :param all_except_one: If true, all entities except the one with the class number will be removed.
        :type all_except_one: bool
        :return: None
        :rtype: None
        '''
        classes = ["scout", "soldier", "pyro", "demoman", "heavy", "engineer", "medic", "sniper", "spy"]
        if type(class_n) == int:
            class_n = str(class_n)
        else:
            if class_n not in classes:
                raise ValueError("Invalid class number")
            else:
                class_n = classes.index(class_n) + 1

        # first loop to remove all filter_tf_class entities
        class_only_trigger_names : list[str]= [] 
        i : int = 0
        while (i < len(self.elements["entities"])):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("classname", "filter_tf_class") and entity.first_layer_has("targetname", None, False):
                if not all_except_one:
                    name = entity.get_subprops_by_name("targetname", False)[0].get_value()
                    if entity.first_layer_has("tfclass", f"{class_n}"): # 4 is demo. 2 is solly.
                        if not entity.first_layer_has("Negated", "1"):
                            class_only_trigger_names.append(name)
                            self.elements["entities"].remove(entity)
                            continue
                else:
                    if entity.first_layer_has("tfclass"):
                        name = entity.get_subprops_by_name("targetname", False)[0].get_value()
                        if not entity.first_layer_has("tfclass", f"{class_n}"): # 4 is demo. 2 is solly.
                            if not entity.first_layer_has("negated", "1"):
                                class_only_trigger_names.append(name)
                                self.elements["entities"].remove(entity)
                                continue

            i += 1

        # second loop to remove all entities that reference the filter_tf_class entities. Including the first layer of filter_multi

        names_to_remove : list[str] = [] # if a filter_multi is deleted, we need to remove all references to it. because of course we do
        i = 0
        while (i < len(self.elements["entities"])):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("filtername"):
                if (entity.get_subprops_by_name("filtername")[0].get_value() in class_only_trigger_names):
                    self.elements["entities"].remove(entity)
                    continue
            if entity.first_layer_has("classname", "filter_multi"):
                and_flag = False
                if entity.get_subprops_by_name("filtertype")[0].get_value() == "0":
                    and_flag = True

                for num in range(10):
                    if (entity.first_layer_has(f"Filter{num + 1}")):
                        if entity.get_subprops_by_name(f"Filter{num + 1}")[0].get_value() in class_only_trigger_names:
                            if and_flag:
                                filter_multi_name = str(entity)
                                names_to_remove.append(filter_multi_name) # add it to da list!!!

                                self.elements["entities"].remove(entity)
                                break
                            else:
                                entity.delete_prop(f"Filter{num + 1}")
                if not and_flag:
                    if not any([entity.first_layer_has(f"Filter{num + 1}") for num in range(10)]):
                        filter_multi_name = entity.get_subprops_by_name("targetname")[0].get_value()
                        self.elements["entities"].remove(entity)
                        continue
                                
            i += 1
        
        # third loop to remove all entities that have a filtername of a deleted filter_multi entity
        i = 0
        while (i < len(self.elements["entities"])):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("filtername"):
                if (entity.get_subprops_by_name("filtername")[0].get_value() in names_to_remove):
                    self.elements["entities"].remove(entity)
                    continue
            i += 1
    
    def tf2_simplify_class_attrs(self, class_n : int | str) -> None:
        '''
        remove tf_filter_class for the given class, and remove the filtername attribute from all entities. 
        TODO: make work for filter_multi rescursively

        :param class_n: The class number to remove. Can also be a string
        :type class_n: int | str
        :return: None
        :rtype: None
        '''
        classes = ["scout", "soldier", "pyro", "demoman", "heavy", "engineer", "medic", "sniper", "spy"]
        if type(class_n) == int:
            class_n = str(class_n)
        else:
            class_n = class_n.lower()
            if class_n not in classes:
                raise ValueError("Invalid class number")
            else:
                class_n = classes.index(class_n) + 1
        
        filter_entities_names : list[str] = []
        # first loop to remove all filter_tf_class entities for that class
        i : int = 0
        while (i < len(self.elements["entities"])):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("classname", "filter_tf_class"):
                # if entity.first_layer_has("tfclass", f"{class_n}") and entity.first_layer_has("negated", "0"): # not negated. 
                filter_entities_names.append(entity.get_subprops_by_name("targetname", False)[0].get_value())
                self.elements["entities"].remove(entity)
                continue

            i += 1
        

        # second loop to remove all filternames that reference the filter_tf_class entities
        i = 0
        while (i < len(self.elements["entities"])):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("filtername"):
                if entity.get_subprops_by_name("filtername")[0].get_value() in filter_entities_names:
                    # print(entity.get_subprops_by_name("filtername")[0].get_value()) 
                    entity.delete_prop("filtername") 

            if entity.first_layer_has("classname", "filter_multi"):
                for num in range(10):
                    if (entity.first_layer_has(f"Filter{str(num + 1).zfill(2)}")):
                        if entity.get_subprops_by_name(f"Filter{str(num + 1).zfill(2)}")[0].get_value() in filter_entities_names:
                            entity.delete_prop(f"Filter{str(num + 1).zfill(2)}")

                if not any([entity.first_layer_has(f"Filter{str(num + 1).zfill(2)}") for num in range(10)]):
                    self.elements["entities"].remove(entity)
                    continue

            i += 1
        

    def tf2_to_momentum(self, for_class_num : int | str) -> None:
        '''
        Converts the VMF to a hopefully working momentum map.
        Steps taken: 
        1. Remove all regen triggers
        1a. Remove func_regenerate
        1b. Remove trigger_hurt
        1c. Remove logic_timer based regen
        1d. Remove trigger_multiple based regen
        2. Change the flag for all buttons with OnPressed and not OnDamaged to instead trigger OnDamaged
        3. For all catapults without a launch target pointing straight up, multiply their velocity by 1.5. If any catapult has 0 playerSpeed, remove it instead

        :param for_class_num: The class number of the map to convert to. 2 is soldier, 4 is demo. 
        :type for_class_num: int | str
        :return: None
        :rtype: None

        
        '''

        i : int = 0
        while (i < len(self.elements["entities"])):
            entity = self.elements["entities"][i]

            if entity.first_layer_has("classname", "func_regenerate"):
                self.elements["entities"].remove(entity) # remove regen triggers
                continue

            elif entity.first_layer_has("classname", "trigger_hurt"):
                self.elements["entities"].remove(entity) # remove regen triggers
                continue

            elif entity.first_layer_has("classname", "logic_timer"):
                connections : ve.VMFElement = entity.get_subprops_by_name("connections")[0]
                if (connections and connections.first_layer_has("OnTimer", None, False)):
                    for timer in connections.get_subprops_by_name("OnTimer", False):
                        if "health" in timer.get_value().lower():
                            connections.delete_prop(timer.get_name(), timer.get_value()) # remove health tick regen
                    if len(connections.get_props()) == 0: # if the logic timer has no more properties, remove it
                        self.elements["entities"].remove(entity) 
                        continue
            
            elif entity.first_layer_has("classname", "trigger_multiple"):
                connections : ve.VMFElement = entity.get_subprops_by_name("connections")[0]
                if (connections and connections.first_layer_has("OnStartTouch", None, False)):
                    for trigger in connections.get_subprops_by_name("OnStartTouch", False):
                        if "health" in trigger.get_value().lower():
                            connections.delete_prop(trigger.get_name(), trigger.get_value()) # remove trigger_multiple health 900 regen
                    if len(connections.get_props()) == 0: # if the trigger_multiple has no more properties, remove it
                        self.elements["entities"].remove(entity)
                        continue

            elif entity.first_layer_has("classname", "func_button"):
                connections : ve.VMFElement = entity.get_subprops_by_name("connections")[0]
                if not connections.first_layer_has("OnDamaged", None, False): # if the button doesn't trigger onDamaged
                    for on_press in connections.get_subprops_by_name("OnPressed", None, False):
                        on_press.rename("OnDamaged") # rename all OnPressed to OnDamaged
            
            elif entity.first_layer_has("classname", "trigger_catapult"):
                direction : vp.VMFProperty = entity.get_subprops_by_name("launchDirection", False)[0]
                playerspeed : vp.VMFProperty = entity.get_subprops_by_name("playerspeed", False)[0]
                if not entity.first_layer_has("launchtarget"):
                    direction = direction.get_value()
                    direction = [float(d) for d in direction.split(" ")]
                    if (direction[0] % 360 == 270 and direction[1] % 360 == 0 and direction[2] % 360 == 0):
                        playerspeed.set_value(str(float(playerspeed.get_value()) * 1.5)) # multiply the velocity by 1.5
                # print(playerspeed) 
                if float(playerspeed.get_value()) == 0:
                    self.elements["entities"].remove(entity) # remove this
                    continue
            i += 1

            
        self.tf2_remove_class_attrs(for_class_num, True) # remove all other-class-specific attributes
        self.tf2_simplify_class_attrs(for_class_num) # remove all filters for this class, and all filternames for this class




        
    def __str__(self) -> str:
        '''
        Returns a string representation of the VMF.
        :return: The string representation of the VMF
        :rtype: str
        '''
        _str = ""
        for key in VMF.base_elements:
            if (key != "entity"):
                _str += str(self.elements[key]) + "\n" if self.elements[key] is not None else key + "\n{\n}\n"
            else:
                for entity in self.elements["entities"]:
                    _str += str(entity) + "\n"

        return _str


 