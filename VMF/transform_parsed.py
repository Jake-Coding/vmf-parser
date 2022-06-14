import pprint

from lark import *



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
                        "isthreed" : "_3d",
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
    VALIDNAME = str

    @staticmethod
    def try_to_convert(arg : str):

        val = arg
        if arg.startswith("(") and arg.endswith(")"):
            val = arg[1:-1]
        if arg.startswith("[") and arg.endswith("]"):
            val = arg[1:-1]
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
                        return val.lower()


    def __default_token__(self, token):
        # print(token)
        return token.value.lower()




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



    def __default__(self, data, children, meta):
        if data in TransformVMF.zero_depth_keys:
            return self.zero_depth_rule(TransformVMF.zero_depth_keys[data], children)

        # print(data.value)
        class_ = {"type": "class" , "classtype" : data.value.lower(), "kvs" : {}, "classes" : []}
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
                raise Exception("oops")



        return class_

    def other_kv(self, data):
        value = data[1]
        value = TransformVMF.try_to_convert(value)
        return {data[0].lower() : value}

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

    def connections(self, data):
        class_ = {"type": "class" , "classtype" : "connections", "kvs" : {}, "classes" : []}
        for conn in data:
            conn_name = list(conn.keys())[0]
            if conn_name in class_["kvs"]:
                class_["kvs"][conn_name].append(conn[conn_name])
            else:
                class_["kvs"][conn_name] = [conn[conn_name]]

        return class_
        # print(data[1])

    def connection(self, data):
        # print(data)
        return {data[0] : data[1]}

    def vmf_sz_rule(self, data):
        # print(data)
        return data[0]

    def connection_value(self, data):
        return data

    def ent_name_or_class(self, data):
        # print(data[0])
        return data[0]

    def input(self, data):
        # print(data)
        return data[0]

    def delay(self, data):
        # print(data)
        return data[0]

    def num_times_fire(self, data):
        return data[0]

    def override(self, data):
        if data:
            return data[0]
        return None

    def validname(self, data):
        # print(data)
        return data[0]





    def entity_inner(self, data):
        # print(data)

        return data

    def world_inner(self, data):
        return data

    def viewsettings_inner(self, data):
        c = {"type" : "class", "classtype" : "viewsettings", "kvs" :{}, "classes" : []}
        for d in data:
            if d.get("type") == "class":
                c["classes"].append(d)
            else:
                c["kvs"] |= d
        return c

    def viewsettings_kvs(self, data):
        return data[0]

    def view(self, data):
        c = data[0]
        for d in data[1:]:
            if d.get("type") == "class":
                c["classes"].append(d)
            else:
                c["kvs"] |= d
        return c


    def viewsettings(self, data):
        return data[0]

    def versioninfo_inner(self, data):
        return data

    def editor_inner(self, data):
        return data

    def dispinfo_inner(self, data):
        c = {"type" : "class", "classtype" : "dispinfo", "kvs" :{}, "classes" : []}
        for d in data:
            if d.get("type") == "class":
                c["classes"].append(d)
            else:
                c["kvs"] |= d
        return c

    def dispinfo(self, data):
        return data[0]


    def other_class(self, data):
        c = {"type": "class", "classtype" : data[0], "kvs" : {}, "classes" : []}

        for d in data[1:]:
            if d.get("type") == "class":
                c["classes"].append(d)
            else:
                c["kvs"] |= d
        return c


    def viewname(self, data):

        class_ = {"type": "class" , "classtype" : f"v{data[0]}", "kvs" : {}, "classes" : []}
        return class_

    def section(self, data):
        return data[0]



    def entity(self, data):
        # print(data)
        kvs = {}
        classes = []
        for d in data[0]:
            kvs |= d["kvs"]
            classes += (d["classes"])

        # print(kvs)
        return {"type":"class", "classtype": "entity", "kvs": kvs, "classes" : classes}

    def entity_kvs(self, data):
        kvs = {}
        for d in data:
            kvs |= d
        return {"kvs": kvs, "classes": {}}

    def entity_nonkvs(self, data):
        classes = []
        for d in data:
            classes.append(d)
        return {"kvs": {}, "classes": classes}
        # print(data)


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









if __name__ == "__main__":

    the_tree: Tree
    with open("./vmf_tree.txt", "r") as f:
        the_tree = eval(f.read())
    try:
        transformed = (TransformVMF().transform(the_tree))
        pp = pprint.PrettyPrinter(sort_dicts=False, indent=4, width=140)

        # print(transformed)
        with open("./transformed_into_py.txt", "w") as f:
            f.write(transformed.__repr__())
        with open("./transformed_pretty.txt", "w") as f:
            f.write(pp.pformat(transformed))
        # for entity in transformed["entity"]:
        #
        #     if entity["kvs"]["classname"] == "trigger_catapult":
        #         pass
                # pp.pprint(entity)
    except visitors.VisitError as e:
        raise e.orig_exc