from transform_parsed import TransformVMF
import lark
import to_mmod
import py_to_vmf
from os.path import exists

def get_parser(filename : str):
    parser_data : str
    with open(filename, "r") as f:
        parser_data = f.read()
    parser = lark.Lark(parser_data,
                       start="vmf",
                       parser="lalr",
                       )
    return parser

if __name__ == "__main__":


    filename = input("VMF File to Transform\n> ")

    while not exists(filename):
        print("Invalid File")
        filename = input("VMF File to Transform\n> ")

    classes = {"s" : 2, "d" : 4}
    classnum_str = input("Class (s/d)\n> ")
    classnum_str = classnum_str.lower()
    while classnum_str not in ("s", "d"):
        print("Valid classes are s (soldier) or d (demo). Please type s or d.")
        classnum_str = input("Class (s/d)\n> ")
        classnum_str = classnum_str.lower()

    classnum = classes[classnum_str]


    transformer = TransformVMF()
    parser = get_parser("vmf_parser_generator.lark")
    text : str
    with open(filename, "r") as f:
        text = f.read()
    print("text read")

    parsed : lark.Tree
    try:
        parsed = parser.parse(text)
    except lark.exceptions.UnexpectedToken as e:
        print(e)
        print(e.get_context(text, 40))

    print("text parsed")
    transformed = transformer.transform(parsed)
    print("parsed transformed")
    mm_map = to_mmod.to_mmod_by_classnum(transformed, classnum)
    print("transformed to mmod")
    mm_vmf = py_to_vmf.py_to_vmf_str(mm_map)
    print("back to vmf string :)")
    new_filename = filename.removesuffix(".vmf")
    if new_filename.startswith("jump_"):
        new_filename = new_filename[5:]
        if classnum == 2:
            new_filename = "rj_" + new_filename
        elif classnum == 4:
            new_filename = "sj_" + new_filename
        else:
            new_filename = "mm_" + new_filename
    else:
        new_filename += "_momentum"

    new_filename += ".vmf"

    with open(new_filename, "w") as f:
        f.write(mm_vmf)
    print("written to file " + new_filename)

