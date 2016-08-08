import imp
import importlib
import os
import codegen
import time

from MuOperators import *
from MuTester import *
from copy import deepcopy
from difflib import *

import traceback

class MuUtilities(object):

    @classmethod
    def load_module(cls, module_fullname, module_path):
        """
        Load a single module by full module name
        """
        module = None
        # if module_path[-3:] == ".py":
        #     module_path = module_path.replace(".py", ".pyc")
        try:
            if os.path.exists(module_path[:len(module_path)-3] + '.pyc'):
                os.remove(module_path[:len(module_path)-3] + '.pyc')
            # module = imp.load_source(module_fullname, module_path)
            module = importlib.import_module(module_fullname)
        except ImportError:
            print "ImportError: faild to import " + module_fullname + " from " + module_path
            traceback.print_exc(file=sys.stdout)
        return module

    @classmethod
    def load_single_class(cls, full_class_string):
        """
        Loading dynamically a class with importlib is easy,
        first you have to actually load the module with import_module,
        and finally you can retrieve the class with getattr.
        """
        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]

        module = importlib.import_module(module_path)

        # Finally, we retrieve the Class
        return getattr(module, class_str)

    @classmethod
    def make_diff(cls, node1, node2):
        """
        Compare the original source code and mutant.
        :param node1:
        :param node2:
        :return:
        """
        if not os.path.isdir('output'):
            os.mkdir(os.path.curdir + '/output')
        dest_dir = os.path.curdir + '/output'

        timestamp = int(round(time.time() * 1000))

        # write the original code to a file
        original_code = codegen.to_source(node1)
        filename = str(timestamp) + "_original" + ".py"
        path = os.path.join(dest_dir, filename)
        cls.write_to_file(path, original_code)

        # write the mutated code to a file
        mutated_code = codegen.to_source(node2)
        filename = str(timestamp) + "_mutant" + ".py"
        path = os.path.join(dest_dir, filename)
        cls.write_to_file(path, mutated_code)

        # write the diff result to a file
        d = Differ()
        res = ''.join(list(d.compare(original_code, mutated_code)))
        filename = str(timestamp) + "_diff_result" + ".txt"
        path = os.path.join(dest_dir, filename)
        cls.write_to_file(path, res)

    @classmethod
    def write_to_file(cls, filename, text):
        with open(filename, 'w') as sourcefile:
            sourcefile.write(text)

    @classmethod
    def print_ast(cls, tree):
        """
        Print out a specified abstract syntax tree.
        :param tree: abstract syntax tree to print
        """
        # print out the mutated tree
        code = codegen.to_source(tree)
        print code








