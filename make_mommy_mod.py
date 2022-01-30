user_in = input("Path to the map (vmf)\n> ")
try:
    vmf = VMF(user_in)
catch Exception as e:
    print(e)
    exit()

vmf.tf2_to_momentum()
out_path = user_in.replace(".vmf", "_momentum.vmf")
with open(out_path, "w") as f:
    f.write(vmf.__str__())
