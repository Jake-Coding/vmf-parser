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
                       parser="earley"
                       )
    print(parser)
    return parser

if __name__ == "__main__":
    parser = get_parser("vmf_parser_generator.lark")
    text : str
    with open("jump_cyskic_final_d.vmf", "r") as f:
        text = f.read()
    print("text read")
    parsed = parser.parse(text)
    print("text parsed")
    transformer = TransformVMF()
    transformed = transformer.transform(parsed)
    print("parsed transformed")
    rj_map = to_mmod.to_mmod_rj(transformed)
    print("transformed to mmod")
    rj_vmf = py_to_vmf.py_to_vmf_str(rj_map)
    print("back to vmf string :)")
    print(rj_vmf)

