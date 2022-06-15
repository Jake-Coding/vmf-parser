from transform_parsed import TransformVMF
import lark
import to_mmod
import py_to_vmf
def get_parser(filename : str):
    parser_data : str
    with open(filename, "r") as f:
        parser_data = f.read()
    parser = lark.Lark(parser_data,
                       start="vmf",
                       parser="lalr",
                       )
    print(parser)
    return parser

if __name__ == "__main__":

    transformer = TransformVMF()
    parser = get_parser("vmf_parser_generator.lark")
    text : str
    with open("jump_cyskic_final_d.vmf", "r") as f:
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
    rj_map = to_mmod.to_mmod_rj(transformed)
    print("transformed to mmod")
    rj_vmf = py_to_vmf.py_to_vmf_str(rj_map)
    print("back to vmf string :)")
    with open("rj_cyskic_final_d.vmf", "w") as f:
        f.write(rj_vmf)
    print("written to file")

