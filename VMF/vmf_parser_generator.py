
import lark
def get_text(filename : str) ->str:
    text = ""
    with open(filename, "r") as f:
        text = f.read()
    return text
parser = lark.Lark(get_text("./vmf_parser_generator.lark"), start="vmf")

print(parser)
parsed = parser.parse(get_text("jump_cyskic_final_d.vmf"))
print(parsed)
print(parsed.pretty())
with open("./vmf_tree.txt", "w") as f:
    f.write(parsed.__repr__())
with open("./pretty_vmf_tree.txt", "w") as f:
    f.write(parsed.pretty())
