# CVPL

CaWU's VMF Parser Library

Does what it says on the box. Valve Map Format be like

## Usage

```cmd
py make_mommy_mod.py
```

Behind the Scenes:

```python
import vmf


my_vmf = vmf.VMF('some_file_path_to_a.vmf')
my_vmf.tf2_to_momentum() # tf2 file -> momentum compatible file (hopefully). Plenty of other commands behind the scenes-- check out the files themselves. Hopefully self-documenting
# VMFElement is the main class used. VMF wraps it in an actual parsed file type of way. Access functions of VMFElement to actually do things tho
with open('some_file_path_to_a_momentum.vmf') as f:
    f.write(my_vmf.__str__())
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Also the code's pretty bad I don't expect anyone to want to even look at this. Please have a nice day <3.  

## License

[MIT](https://choosealicense.com/licenses/mit/)
