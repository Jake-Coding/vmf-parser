import vmf as v

user_in = input("Path to the map (vmf)\n> ")

for_class = input("What class is this for?\n> ")

try:
    vmf = v.VMF(user_in)
except Exception as e:
    print(e)
    exit()

vmf.tf2_to_momentum(for_class)
out_path = user_in.replace(".vmf", "_momentum.vmf")
with open(out_path, "w") as f:
    f.write(vmf.__str__())

