import traceback
def indent(s, level : int = 1):
    s = s.split('\n')
    # s = [((level * 4) * ' ') + line for line in s]
    s = ["\t" + line for line in s]
    s = "\n".join(s)
    return s


def fix_floats(value):
    v = value
    if type(value) == float:
        v = float(value)
        # print(v)
        if v.is_integer():
            v = int(v)
            # print(v)
    elif type(value) == list:
        i = 0
        while i < len(value):
            v[i] = fix_floats(v[i])
            i += 1

    return v

def convert_kv(kv):
    kv_key = list(kv.keys())[0]
    kv_value = kv[kv_key]
    if kv_key in ("uaxis", "vaxis"):
        inner = kv[kv_key]
        fixed = inner[0]
        fixed.append(inner[1])
        fixed = fix_floats(fixed)
        fixed = [str(v) for v in fixed]
        fixed_str = "[" + " ".join(fixed) +"]"+ " " + str(fix_floats(inner[2]))
        kv_value = fixed_str
    elif kv_key == "plane":
        fixed = ""
        f = fix_floats(kv_value)
        for p in f:
            fixed += "(" + " ".join([str(v) for v in p]) + ") "

        kv_value = fixed[:-1]
    elif kv_key == "points":
        string = ""
        for point in kv_value:
            point_fixed_str = " ".join([str(v) for v in fix_floats([point[0]] + point[1])])
            string += f"\"point\" \"{point_fixed_str}\"\n"
        return string[:-1]
    elif kv_key == "_3d":
        kv_key = "3d"
    elif kv_key in ("startposition", 'logicalpos', "look", "angle", "position") :
        kv_value = "[" + " ".join([str(v) for v in fix_floats(kv_value)]) + "]"
    elif type(kv_value) == list:
        kv_value = " ".join([str(v) for v in fix_floats(kv_value)])


    if type(kv_value) == bool:
        kv_value = 1 if kv_value == True else 0


    return f"\"{kv_key}\" \"{fix_floats(kv_value)}\" "

def convert_class(class_):
    string = class_["classtype"]
    string += "\n{\n"
    inner_string = ""
    for key in class_["kvs"]:

        if not class_["classtype"] == "connections":
            d = {key : class_["kvs"][key]}
            inner_string += convert_kv(d)
        else:
            d = {key : "".join([str(fix_floats(v)) for v in class_["kvs"][key][0]])}
            inner_string += convert_kv(d)
        inner_string += "\n"

    for c in class_["classes"]:
        inner_string += convert_class(c)
    string += indent(inner_string[:-1])
    string += "\n}\n"
    return string

# special cases: uaxis, vaxis, plane, point_data(points)


def py_to_vmf_str(vmf):
    first_level_classes = vmf["versioninfo"] + vmf["visgroups"] + vmf["viewsettings"] + vmf["world"] + vmf["entity"] + vmf["cameras"] + vmf["cordons"]
    string = ""
    for item in first_level_classes:
        string += convert_class(item)
    return string

if __name__=="__main__":
    vmf : dict
    s : str
    with open("./transformed_into_py_fix.txt") as f:
        s = f.read()
    try:
        vmf = eval(s)
    except Exception as e:
        print(traceback.format_exc().replace(" ", ""))
        print(e)
    vmf_str = py_to_vmf_str(vmf)
    # print(vmf_str)
    with open("./transformed_fixed_vmf.vmf", "w") as f:
        f.write(vmf_str)

    # import difflib
    # with open('transformed_fixed_vmf.vmf') as file_1, open('jump_cyskic_final_d.vmf') as file_2:
    #
    #     for line in difflib.unified_diff(file_1.readlines(), file_2.readlines()):
    #         print(line)
