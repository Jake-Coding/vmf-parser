import pprint

def remove_ents(vmf, elems):
    for e in elems:
        vmf["entity"].remove(e)

def get_regens(vmf):
    return get_ents_by_classname(vmf, "func_regenerate") + get_ents_by_classname(vmf, "trigger_hurt")


def get_subclass_by_classtype(entity, classtype):
    for class_ in entity["classes"]:
        if class_["classtype"] == classtype:
            return class_
    return None

def get_empty_by_classname_and_part(vmf, classname = None, subclass_to_check = None): #class_to_check = connections usually
    ents = vmf["entity"]
    ent_list = []
    for ent in ents:
        if classname and ent["kvs"]["classname"] == classname:
            if subclass_to_check:
                if not get_subclass_by_classtype(ent, subclass_to_check)["kvs"] and not get_subclass_by_classtype(ent, subclass_to_check)["classes"]:
                    ent_list.append(ent)
            else:
                if not ents["classes"] and not ents["kvs"]:
                    ent_list.append(ent)

    return ent_list

def get_ents_by_classname(vmf, classname):
    ents = vmf["entity"]
    e = []
    for ent in ents:
        if ent["kvs"]["classname"] == classname:
            # print(ent)
            e.append(ent)
    return e






def remove_regen(vmf):
    ents_to_remove = []
    regens = get_regens(vmf)
    ents_to_remove += regens


    logic_timers = get_ents_by_classname(vmf, "logic_timer")
    for timer in logic_timers:
        # print(timer)
        conns = get_subclass_by_classtype(timer, "connections")

        if conns["kvs"].get("OnTimer"):
            ontimers = conns["kvs"]["OnTimer"]
            conns["kvs"]["OnTimer"] = list(filter(lambda conn_list : "health" not in conn_list[2], ontimers))
            if not conns["kvs"]["OnTimer"]:
                conns["kvs"].pop("OnTimer")


    ents_to_remove += get_empty_by_classname_and_part(vmf, "logic_timer", "connections")


    multiples = get_ents_by_classname(vmf, "trigger_multiple")
    for multi in multiples:
        # print(multi)
        conns = get_subclass_by_classtype(multi, "connections")
        if conns["kvs"].get("OnStartTouch"):
            ontimers = conns["kvs"]["OnStartTouch"]
            conns["kvs"]["OnStartTouch"] = list(filter(lambda conn_list : "health" not in conn_list[1], ontimers))
            if not conns["kvs"]["OnStartTouch"]:
                conns["kvs"].pop("OnStartTouch")

    ents_to_remove += get_empty_by_classname_and_part(vmf, "trigger_multiple", "connections")
    # for e in ents_to_remove:
        # print(e)
    remove_ents(vmf, ents_to_remove)
    # for e in ents_to_remove:
        # print(e in vmf["entity"])


def fix_downards_catapults(vmf):
    catapults = get_ents_by_classname(vmf, "trigger_catapult")
    for catapult in catapults:
        if not catapult["kvs"].get("launchtarget"):
            # print(catapult)
            direction = catapult["kvs"]["launchdirection"]
            d_to_norm = [float(d) % 360 for d in direction]
            if d_to_norm == [270, 0, 0]:
                catapult["kvs"]["playerspeed"] *= 1.5



def fix_multis(vmf, new_filternames_to_delete):
    ents_to_return_and_delete = []
    names_to_delete = []
    for filter_multi in get_ents_by_classname(vmf, "filter_multi"):
        is_and = not filter_multi["kvs"]["filtertype"]
        for num in range(10):
            filter_str: str = f"Filter{str(num + 1).zfill(2)}"  # Filter01, Filter02... Filter10
            if filter_multi["kvs"].get(filter_str) in new_filternames_to_delete:
                if is_and:
                    names_to_delete.append(filter_multi["kvs"]["targetname"])
                    ents_to_return_and_delete.append(filter_multi)
                    break
                else:
                    del filter_multi["kvs"][filter_str]

        if not is_and and not any([filter_multi["kvs"].get([ f"Filter{str(num + 1).zfill(2)}"] for num in range(10))]):
            names_to_delete.append(filter_multi["kvs"]["targetname"])
            ents_to_return_and_delete.append(filter_multi)
    return names_to_delete, ents_to_return_and_delete



def make_filters_for_classnum(vmf, classnum):
    names_of_non_class_filters = []
    ents_to_remove = []
    for ent in get_ents_by_classname(vmf, "filter_tf_class"):
        if ent["kvs"].get("targetname"):
            if ent["kvs"]["tfclass"] != classnum and ent["kvs"].get("negated") in (0, "allow entities that match criteria"):
                names_of_non_class_filters.append(ent["kvs"]["targetname"])
                ents_to_remove.append(ent)
            elif ent["kvs"]["tfclass"] == classnum and ent["kvs"].get("negated"):
                names_of_non_class_filters.append(ent["kvs"]["targetname"])
                ents_to_remove.append(ent)


    pre_l = len(names_of_non_class_filters)
    m = fix_multis(vmf, names_of_non_class_filters)
    names_of_non_class_filters = []
    names_of_non_class_filters += m[0]
    ents_to_remove += m[1]
    l = len(names_of_non_class_filters)

    remove_ents(vmf, ents_to_remove)
    ents_to_remove = []
    while pre_l != l:
        pre_l = len(names_of_non_class_filters)
        m = fix_multis(vmf, m[0])
        names_of_non_class_filters = []
        names_of_non_class_filters += m[0]
        ents_to_remove += m[1]
        l = len(names_of_non_class_filters)
        # print("piss and shit we loopin")

        remove_ents(vmf, ents_to_remove)
        ents_to_remove = []


    for ent in vmf["entity"]:
        if ent["kvs"].get("filtername"):
            if ent["kvs"]["filtername"] in names_of_non_class_filters:
                ents_to_remove.append(ent)


    names_of_class_filters = []
    for ent in get_ents_by_classname(vmf, "filter_tf_class"):
        if ent["kvs"].get("targetname"):
            if ent["kvs"]["tfclass"] == 2 and  ent["kvs"].get("negated") in (0, "allow entities that match criteria"):
                names_of_class_filters.append(ent["kvs"]["targetname"])
                ents_to_remove.append(ent)
            elif ent["kvs"]["tfclass"] != 2 and ent["kvs"].get("negated"):
                names_of_class_filters.append(ent["kvs"]["targetname"])
                ents_to_remove.append(ent)

    for ent in vmf["entity"]:
        if ent["kvs"].get("filtername"):
            # print(ent)

            if ent["kvs"]["filtername"] in names_of_class_filters:
                del ent["kvs"]["filtername"]
    pre_l = len(names_of_class_filters)
    m = fix_multis(vmf, names_of_class_filters)
    names_of_class_filters = []
    names_of_class_filters += m[0]
    ents_to_remove += m[1]
    l = len(names_of_class_filters)
    for ent in vmf["entity"]:
        if ent["kvs"].get("filtername"):
            # print(ent)

            if ent["kvs"]["filtername"] in names_of_class_filters:
                del ent["kvs"]["filtername"]

    remove_ents(vmf, ents_to_remove)
    ents_to_remove = []
    while pre_l != l:
        pre_l = len(names_of_class_filters)
        m = fix_multis(vmf, m[0])
        names_of_class_filters = []
        names_of_class_filters += m[0]
        ents_to_remove += m[1]
        l = len(names_of_class_filters)

        for ent in vmf["entity"]:
            if ent["kvs"].get("filtername"):
                if ent["kvs"]["filtername"] in names_of_class_filters:
                    del ent["kvs"]["filtername"]

        remove_ents(vmf, ents_to_remove)
        ents_to_remove = []




def get_world_solids(vmf):
    l = []
    for s in vmf["world"][0]["classes"]:
        if s["classtype"] == "solid":
            l.append(s)
    return l

class TextureChange:
    def __init__(self, texture_from, texture_to, classnames = None, world_solids = False):
        self.texture_from = texture_from
        self.texture_to = texture_to
        self.classnames = []
        if classnames:
            self.classnames = classnames
        self.apply_to_world_solids = world_solids

    def change(self, vmf):
        if self.apply_to_world_solids:
            for solid in get_world_solids(vmf):
                for sub in solid["classes"]:
                    if sub["classtype"] == "side":
                        if sub["kvs"]["material"] == self.texture_from:
                            sub["kvs"]["material"] = self.texture_to
        for classname in self.classnames:
            for c in get_ents_by_classname(vmf, classname):
                for sub in c["classes"]:
                    if sub["classtype"] == "solid":
                        for s in sub["classes"]:
                            if s["classtype"] == "side":
                                if s["kvs"]["material"] == self.texture_from:
                                    s["kvs"]["material"] = self.texture_to



def to_mmod_rj(vmf):
    remove_regen(vmf)
    make_filters_for_classnum(vmf, 2)
    fix_downards_catapults(vmf)
    return vmf

if __name__== "__main__":
    vmf: dict
    with open("./transformed_into_py.txt", "r") as f:
        vmf = eval(f.read())
    fixed = to_mmod_rj(vmf)
    with open("./transformed_into_py_fix.txt", "w") as f:
        f.write(fixed.__repr__())

    # pp = pprint.PrettyPrinter(sort_dicts=False, indent=4, width=140)
    # with open("./transformed_into_py_fix_pretty.txt", "w") as f:
    #     f.write(pp.pformat(fixed))
    #
    # a : dict
    # with open("./transformed_into_py_fix.txt", "r") as f:
    #     a = eval(f.read())
    # b : dict
    # with open("./transformed_into_py.txt", "r") as f:
    #     b = eval(f.read())
    # print(a == b)



