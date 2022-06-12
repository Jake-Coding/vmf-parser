import sys
import pprint

from lark import *

the_tree : Tree
with open("./vmf_tree.txt", "r") as f:
    the_tree = eval(f.read())


class TransformVMF(visitors.Transformer):
    zero_depth_keys = {"name" : "name" ,
                       "classname" : "classname",
                       "color" : "color",
                      "position" : "position",
                      "angle" : "angle",
                      "id" : "id",
                      "material" : "material",
                      "rotation" : "rotation",
                      "uaxis" : "uaxis",
                      "vaxis" : "vaxis",
                      "lightmapscale" : "lightmapscale",
                      "smoothing_groups" : "smoothing_groups",
                      "numpts" : "numpts",
                      "spawnflags" : "spawnflags",
                      "origin" : "origin",
                      "editorversion" : "editorversion",
                      "editorbuild" : "editorbuild",
                      "mapversion" : "mapversion",
                      "formatversion" : "formatversion",
                      "prefab" : "prefab",
                      "visgroupid" : "visgroupid",
                      "bsnap" : "bSnapToGrid",
                        "bshow" : "bShowGrid",
                        "bshowl" : "bShowLogicalGrid",
                        "ngrid" : "nGridSpacing",
                        "bshowthree" : "bShow3DGrid",
                        "isthreed" : "3d",
                        "zoom" : "zoom",
                        "mins" : "mins",
                        "maxs" : "maxs",
                        "active" : "active",

                       }
    def remove_ending_quotes(self, string):
        return string[1:-1]
    VMF_SZ = lambda arg1, arg2 : arg2[1:-1]
    VMF_INT = int
    VMF_DEC = float
    VMF_BOOL = lambda arg1, arg2 : arg2 == "1"
    VMF_VERTEX = lambda arg1, arg2 : [float(v) for v in arg2.split(" ")]
    VMF_COLOR = lambda arg1, arg2 : [int(v) for v in arg2.split(" ")]
    CLASSNAME_WORLDSPAWN = lambda arg1, arg2 : {"classname" : "worldspawn"}

    @staticmethod
    def try_to_convert(arg : str):
        val = arg
        # try to convert arg into a valid data type. default to returning arg
        try: # is it an int??
            val = int(arg)
            return val
        except: # not an int ;-; # is it a float?
            try:
                val = float(val)
                return val
            except:
                try: # perhaps a color or int[]??
                    val = [int(v) for v in val.split(" ")]
                    return val
                except: # perhaps a float[]/vertex??
                    try:
                        val = [float(v) for v in val.split(" ")]
                        return val
                    except: # fuck it. return val
                        return val


    def __default_token__(self, token):
        print(token)
        return token.value



    def vmf_q(self, arg):
        return arg[0]
    def vmf_qint(self, arg):
        return self.vmf_q(arg)
    def vmf_qdec(self, arg):
        return self.vmf_q(arg)
    def vmf_qbool(self, arg):
        return self.vmf_q(arg)
    def vmf_qpvertex(self, arg):
        return self.vmf_q(arg)
    def vmf_pvertex(self, arg):
        return self.vmf_q(arg)
    def vmf_qcolor(self, arg):
        return self.vmf_q(arg)
    def vmf_qvertex(self, arg):
        return self.vmf_q(arg)

    def zero_depth_rule(self, key, data):
        # print(key)
        # print(data[0])
        return {key : data[0]}

    def default_helper(self, child, class_dict):
        if type(child) == dict:
            if child.get("type") == "class":
                class_dict["classes"].append(child)
            else:
                class_dict["kvs"] |= child
        elif type(child) == list:
            for c in child:
                class_dict |= self.default_helper(c, class_dict)
            # print(class_dict)
        else:
            print("something has gone horribly wrong")
            # print(type(child))
        return class_dict


    def __default__(self, data, children, meta):
        if data in TransformVMF.zero_depth_keys:
            return self.zero_depth_rule(TransformVMF.zero_depth_keys[data], children)

        # print(data.value)
        class_ = {"type": "class" , "classtype" : data.value, "kvs" : {}, "classes" : []}
        for child in children:
            if type(child) == dict:
                if child.get("type") == "class":
                    class_["classes"].append(child)
                else:
                    class_["kvs"] |= child
            elif type(child) == list:
                for c in child:
                    class_["kvs"] |= c

            # print(class_dict)
            else:
                print("something has gone horribly wrong")



        return class_

    def other_kv(self, data):
        value = data[1]
        value = TransformVMF.try_to_convert(value)
        return {data[0] : value}

    def uvaxis_inner(self, data):
        return data

    def plane(self, data):
        return {"plane" : data}

    def point(self, data):
        return {"point" : data}

    def point_data_inner(self, data):
        # print(data)
        v = [data[0]]
        points = []
        for p in data[1:]:
            points.append(p["point"])
        v.append({"points" : points})
        return v
        # return data


    def entity_inner(self, data):
        # print(data)

        return data

    def world_inner(self, data):
        return data

    def viewsettings_inner(self, data):
        return data

    def versioninfo_inner(self, data):
        return data

    def editor_inner(self, data):
        return data



    def viewname(self, data):

        class_ = {"type": "class" , "classtype" : f"v{data[0]}", "kvs" : {}, "classes" : []}
        return class_

    def section(self, data):
        return data[0]



    def entity(self, data):
        # print(data)
        return {"type":"class", "classtype": "entity", "kvs": data[0][0]["kvs"], "classes" : data[0][1]["classes"]}

    def world(self, data):

        return {"type":"class", "classtype":"world", "kvs": data[0][0]["kvs"], "classes" : data[0][1:]}


    def vmf(self, data):
        big_ol = {
            "versioninfo" : [],
            "visgroups" : [],
            "viewsettings" : [],
            "world" : [],
            "entity" : [],
            "cameras" : [],
            "cordons" : []
        }
        for datum in data:
            # print(datum)
            # print(datum["classtype"])
            big_ol[datum["classtype"]].append(datum)
            # print(datum)
        return big_ol









try:
    transformed = (TransformVMF().transform(the_tree))
    pp = pprint.PrettyPrinter(sort_dicts=False, indent=4, width=140)

    # print(transformed)
    with open("./transformed_into_py.txt", "w") as f:
        f.write(transformed.__repr__())
    with open("./transformed_pretty.txt", "w") as f:
        f.write(pp.pformat(transformed))
    for entity in transformed["entity"]:

        if entity["kvs"]["classname"] == "trigger_catapult":
            pass
            # pp.pprint(entity)
except visitors.VisitError as e:
    raise e.orig_exc