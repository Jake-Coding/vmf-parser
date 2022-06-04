
import lark
def get_text(filename : str) ->str:
    text = ""
    with open(filename, "r") as f:
        text = f.read()
    return text
parser = lark.Lark(get_text("./parser_generator.lark"), start="fgd")

print(parser)
parsed = parser.parse(get_text("./not_an_fgd.fgd"))
with open("fgd_tree.txt", "w") as f:
    f.write(parsed.__repr__())
