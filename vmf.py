import vmf_element as ve
import vmf_property as vp
import typing


class VMF:
    """
    Representation of a full VMF file.
    """
    base_elements: list[str] = ["versioninfo", "visgroups", "viewsettings", "world", "entity", "hidden", "cameras",
                                "cordon", "cordons"]

    textures_to_change: dict[str, dict[str, str]] = {
        # {entity name (lowercase) : {old_texture (UPPERCASE) : new_texture}}
        "trigger_catapult": {"TOOLS/TOOLSTRIGGER": "TOOLS/TRIGGER_CATAPULT"},
        "func_nogrenades": {"TOOLS/TOOLSTRIGGER": "TOOLS/TRIGGER_NOGRENADES"},
        "trigger_teleport": {"TOOLS/TOOLSTRIGGER": "TOOLS/TRIGGER_TELEPORT"},

    }

    def __init__(self, *, vmf_path: str = None, vmf_elements: dict = None):
        """
        Initializes the VMF object.
        :param vmf_path: the path to a file to parse
        :type vmf_path: str
        :param vmf_elements: a pre-existing dict resembling a VMF class
        :type vmf_elements: dict
        """

        # no VMF should have more than these elements
        self.elements = {"versioninfo": None, "visgroups": None, "viewsettings": None, "world": None, "entities": [],
                         "hidden": None, "cameras": None, "cordon": None, "cordons": None}

        if vmf_path is not None:
            self._parse(vmf_path)
        else:
            self.elements = vmf_elements

    @staticmethod
    def _parse_property(line: str) -> vp.VMFProperty:
        """
        Parses a property line.
        :param line: The line to parse
        :type line: str
        :return: The parsed property
        :rtype: vp.VMFProperty
        """
        line = line.strip()
        line = line.split(" ")
        rest_of_data = " ".join(line[1:])
        return vp.VMFProperty(line[0][1:-1], rest_of_data[1:-1])  # slice to ignore the " chars that wrap the property

    def _parse_element(self, lines: typing.List[str], current_line: int) -> tuple[ve.VMFElement, int]:
        """
        Parses a VMF element. Helper function for parse()
        Assumes formatting as:
        thing
        {
            "key" "value"
            "key" "value"
            other_thing
            {
                "key" "value"
            }
            "key" "value"
        }
            I haven't seen a VMF without this format so far, so hopefully this should be robust enough.

        :param lines: The lines of the VMF file
        :type lines: typing.List[str]
        :param current_line: The current line to parse
        :type current_line: int
        :return: The parsed element and the next line to parse
        :rtype: tuple([ve.VMFElement, int])
        """

        name = lines[current_line].strip()

        current_line += 2
        bracket_count = 1
        sub_elements = []
        i = current_line
        while i < len(lines):
            line = lines[i]
            line = line.strip()

            if len(line.split(" ")) > 1:  # the only lines with spaces in the middle are properties
                sub_elements.append(VMF._parse_property(line))
            else:
                if line == "{":
                    bracket_count += 1
                elif line == "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        break
                else:
                    elem, i = self._parse_element(lines, i)
                    sub_elements.append(elem)
            i += 1
        return ve.VMFElement(name, sub_elements), i

    def _parse(self, vmf_path: str) -> None:
        """
        Parses the VMF file. See parse_element() for assumed formatting.

        """

        with open(vmf_path, "r") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i]
            line = line.strip()
            if line in VMF.base_elements:
                if line == "entity":
                    entity, i = self._parse_element(lines, i)
                    self.elements["entities"].append(entity)
                else:
                    self.elements[line], i = self._parse_element(lines, i)
            else:
                i += 1

    @staticmethod
    def change_texture_to_momentum(entity: ve.VMFElement) -> None:
        """
        Changes the textures of the entity to the correct ones for Momentum.
        :param entity: The entity to change the textures of
        :type entity: ve.VMFElement
        :return: None
        :rtype: None
        """
        if entity.first_layer_has("solid"):
            ent_type: str = entity.get_first_subproperty("classname").get_value().lower()
            if ent_type in VMF.textures_to_change:
                solids: list[ve.VMFElement] = entity.get_subelements_by_name("solid")
                for solid in solids:
                    for side in solid.get_subelements_by_name("side"):
                        side_mat: vp.VMFProperty = side.get_first_subproperty("material")
                        if side_mat.get_value().upper() in VMF.textures_to_change[ent_type]:  # uppercase to match VMF
                            side_mat.set_value(VMF.textures_to_change[ent_type][side_mat.get_value()])

    def _tf2_simplify_class_attrs(self) -> None:
        """
        remove all tf_filter_class , and remove the filtername attribute from all entities.
        Probably only use this after tf2_remove_class_attrs
        TODO: make work for filter_multi recursively

        :return: None
        :rtype: None
        """

        filter_entities_names: list[str] = []
        # first loop to remove all filter_tf_class entities
        i: int = 0
        while i < len(self.elements["entities"]):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("classname", "filter_tf_class"):
                filter_entities_names.append(entity.get_first_subproperty("targetname").get_value())
                self.elements["entities"].remove(entity)
                continue
            i += 1

        # second loop to remove all filternames that reference the filter_tf_class entities
        i = 0
        while i < len(self.elements["entities"]):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("filtername"):
                # make sure we only remove class filters
                if entity.get_first_subproperty("filtername").get_value() in filter_entities_names:
                    entity.delete_property("filtername")

            if entity.first_layer_has("classname", "filter_multi"):
                for num in range(10):
                    filter_str: str = f"Filter{str(num + 1).zfill(2)}"
                    if entity.first_layer_has(filter_str):
                        if entity.get_first_subproperty(filter_str).get_value() in filter_entities_names:
                            entity.delete_property(filter_str)

                if not any([entity.first_layer_has(f"Filter{str(num + 1).zfill(2)}") for num in range(10)]):
                    # delete empty filter_multi
                    self.elements["entities"].remove(entity)
                    continue

            i += 1

    def _tf2_remove_class_attrs(self, class_n: int, all_except_one: bool = False) -> None:
        """
        remove class tf filters and all entities that reference them
        Steps taken:
        1. Remove all class_n only stuff. If all_except_one is True, instead remove all non-class_n stuff.
        2. filter_multi :))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))) im having a breakdown
            you can infinitely stack these fuckers, so we'll just do it for the first layer for now :)
            TODO: make it work for all layers

        :param class_n: The class number to remove. 2 = Soldier, 4 = Demo
        :type class_n: int
        :param all_except_one: If true, all entities except the one with the class number will be removed.
        :type all_except_one: bool
        :return: None
        :rtype: None
        """

        # first loop to remove all filter_tf_class entities
        class_only_trigger_names: list[str] = []
        i: int = 0
        while i < len(self.elements["entities"]):
            entity: ve.VMFElement = self.elements["entities"][i]

            if entity.first_layer_has("classname", "filter_tf_class") and entity.first_layer_has("targetname"):
                if not all_except_one:
                    name = entity.get_first_subproperty("targetname").get_value()
                    if entity.first_layer_has("tfclass", f"{class_n}"):  # 4 is demo. 2 is solly.
                        if entity.first_layer_has("Negated", "0"):  # not negated
                            class_only_trigger_names.append(name)
                            self.elements["entities"].remove(entity)
                            continue
                else:
                    if entity.first_layer_has("tfclass"):
                        name = entity.get_first_subproperty("targetname").get_value()
                        if not entity.first_layer_has("tfclass", f"{class_n}"):  # 4 is demo. 2 is solly.
                            if entity.first_layer_has("negated", "0"):
                                class_only_trigger_names.append(name)
                                # print(name)
                                self.elements["entities"].remove(entity)
                                continue
                        elif entity.first_layer_has("tfclass", f"{class_n}"):
                            if entity.first_layer_has("negated", "1"):
                                class_only_trigger_names.append(name)
                                self.elements["entities"].remove(entity)
                                continue

            i += 1

        # second loop to remove all entities and layer 1 of filter_multi that reference the filter_tf_class
        # if a filter_multi is deleted, we need to remove all filtername references to it
        names_to_remove: list[str] = []
        i = 0
        while i < len(self.elements["entities"]):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("filtername"):
                if entity.get_first_subproperty("filtername").get_value() in class_only_trigger_names:
                    self.elements["entities"].remove(entity)
                    continue
            if entity.first_layer_has("classname", "filter_multi"):
                deleted_flag: bool = False
                and_flag = False  # filter_multi can have AND (0) or OR (1) as an operator.
                if entity.get_first_subproperty("filtertype").get_value() == "0":
                    and_flag = True

                for num in range(10):
                    filter_str: str = f"Filter{str(num + 1).zfill(2)}"  # Filter01, Filter02... Filter10
                    if entity.first_layer_has(filter_str):
                        if entity.get_first_subproperty(filter_str).get_value() in class_only_trigger_names:
                            if and_flag:  # delete any AND filter_multi with a non-this-class filter
                                filter_multi_name = str(entity.get_first_subproperty("targetname").get_value())
                                names_to_remove.append(filter_multi_name)
                                self.elements["entities"].remove(entity)
                                deleted_flag = True
                                break
                            else:  # for OR filter_multi, just delete the filter that references class
                                entity.delete_property(filter_str)
                if not and_flag:  # delete OR filter_multi if there's nothing left in them
                    if not any([entity.first_layer_has(f"Filter{str(num + 1).zfill(2)}") for num in range(10)]):
                        self.elements["entities"].remove(entity)
                        continue
                if deleted_flag:
                    continue
            i += 1

        # third loop to remove all entities that have a filtername of a deleted AND filter_multi entity.
        i = 0
        while i < len(self.elements["entities"]):
            entity = self.elements["entities"][i]
            if entity.first_layer_has("filtername"):
                if entity.get_first_subproperty("filtername").get_value() in names_to_remove:
                    self.elements["entities"].remove(entity)
                    continue
            i += 1

        self._tf2_simplify_class_attrs()

    def tf2_to_momentum(self, for_class_num: int | str) -> None:
        """
        Converts the VMF to a hopefully working momentum map.
        Steps taken:
        1. Change tool textures to momentum tool textures, if applicable
        2. Remove all regen triggers
        2a. Remove func_regenerate
        2b. Remove trigger_hurt
        2c. Remove logic_timer based regen
        2d. Remove trigger_multiple based regen
        3. Change the flag for all buttons with OnPressed and not OnDamaged to instead trigger OnDamaged
        4. For all catapults without a launch target pointing straight up, multiply their velocity by 1.5.
            If any catapult has 0 playerSpeed, remove it instead


        :param for_class_num: The class number of the map to convert to. 2 is soldier, 4 is demo.
        :type for_class_num: int | str
        :return: None
        :rtype: None


        """

        i: int = 0
        while i < len(self.elements["entities"]):
            entity: ve.VMFElement = self.elements["entities"][i]

            VMF.change_texture_to_momentum(entity)  # change tool textures to momentum tool textures, if applicable

            if entity.first_layer_has("classname", "func_regenerate"):
                self.elements["entities"].remove(entity)  # remove regen triggers
                continue

            elif entity.first_layer_has("classname", "trigger_hurt"):
                self.elements["entities"].remove(entity)  # remove regen triggers
                continue

            elif entity.first_layer_has("classname", "logic_timer"):
                connections: ve.VMFElement = entity.get_first_subelement("connections")
                if connections and connections.first_layer_has("OnTimer"):
                    for timer in connections.get_subproperties_by_name("OnTimer"):
                        if "health" in timer.get_value().lower():  # sethealth and addhealth both have health :)
                            connections.delete_property(timer.get_name(), timer.get_value())  # remove health tick regen
                    if len(connections.get_items()) == 0:  # if the logic timer has no more properties, remove it
                        self.elements["entities"].remove(entity)
                        continue

            elif entity.first_layer_has("classname", "trigger_multiple"):
                connections: ve.VMFElement = entity.get_first_subelement("connections")
                if connections and connections.first_layer_has("OnStartTouch", None, False):
                    for trigger in connections.get_subproperties_by_name("OnStartTouch"):
                        if "health" in trigger.get_value().lower():
                            connections.delete_property(trigger.get_name(),
                                                        trigger.get_value())  # remove trigger_multiple health 900 regen
                    if connections.is_empty():  # if the trigger_multiple's connections has no properties, remove it
                        self.elements["entities"].remove(entity)
                        continue

            # TODO- inquire to big mmod if this will need to be changed
            elif entity.first_layer_has("classname", "func_button"):
                connections: ve.VMFElement = entity.get_first_subelement("connections")
                if not connections.first_layer_has("OnDamaged"):  # if the button doesn't trigger onDamaged
                    for on_press in connections.get_subproperties_by_name("OnPressed"):
                        on_press.rename("OnDamaged")  # rename all OnPressed to OnDamaged

            elif entity.first_layer_has("classname", "trigger_catapult"):
                direction: vp.VMFProperty = entity.get_first_subproperty("launchDirection")
                player_speed: vp.VMFProperty = entity.get_first_subproperty("playerspeed")
                if not entity.first_layer_has("launchtarget"):
                    dir_value: str = direction.get_value()
                    dir_values: list[float] = [float(d) for d in dir_value.split(" ")]
                    if dir_values[0] % 360 == 270 and dir_values[1] % 360 == 0 and dir_values[2] % 360 == 0:
                        player_speed.set_value(
                            str(float(player_speed.get_value()) * 1.5)
                        )  # multiply the velocity by 1.5
                if float(player_speed.get_value()) == 0:
                    self.elements["entities"].remove(entity)  # remove if catapult with no player velocity
                    # WARNING: Will break physics catapults if they have 0 player vel
                    continue
            i += 1

        self._tf2_remove_class_attrs(for_class_num, all_except_one=True)  # remove all other-class-specific attributes

    def __str__(self) -> str:
        """
        Returns a string representation of the VMF.
        :return: The string representation of the VMF
        :rtype: str
        """
        _str = ""
        for key in VMF.base_elements:
            if key != "entity":
                _str += str(self.elements[key]) + "\n" if self.elements[key] is not None else key + "\n{\n}\n"
            else:
                for entity in self.elements["entities"]:
                    _str += str(entity) + "\n"

        return _str
