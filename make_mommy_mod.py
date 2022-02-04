import vmf as v
import os

user_in = input("Path to the map (vmf)\n> ")
user_in = os.path.abspath(user_in)
assert os.path.splitext(user_in)[1] == '.vmf'
try:
    vmf = v.VMF(user_in)
except Exception as e:
    print(e)
    exit()

for_class: str = input("What class is this for?\n> ")
classes = ["scout", "soldier", "pyro", "demoman", "heavy", "engineer", "medic", "sniper", "spy"]

for_class = for_class.lower()
class_num: int = 0
if for_class in ["demo", "d"]:
    for_class = "demoman"
if for_class == ["solly", "s"]:
    for_class = "soldier"

if for_class not in classes:
    raise ValueError("Invalid class")
else:
    class_num = classes.index(for_class) + 1


# print(class_num)
vmf.tf2_to_momentum(class_num)

out_path = list(os.path.split(user_in))
out_path[1] = out_path[1].replace(".vmf", "_momentum.vmf")
if out_path[1].startswith("jump_"):
    if class_num == 2:
        out_path[1] = out_path[1].replace("jump_", "rj_", 1)
    elif class_num == 4:
        out_path[1] = out_path[1].replace("jump_", "sj_", 1)
out_path = os.path.join(out_path[0], out_path[1])
print(out_path)

with open(out_path, "w") as f:
    f.write(vmf.__str__())

