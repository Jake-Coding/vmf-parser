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

    def tf2_to_momentum(self) -> None:
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


 