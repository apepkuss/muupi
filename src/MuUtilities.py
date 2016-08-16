import imp
import importlib
import os
import codegen
import time
import config
import traceback

from MuOperators import *
from MuTester import *
from copy import deepcopy
from difflib import *

class MuUtilities(object):

    @classmethod
    def load_module(cls, module_fullname, module_path=None):
        """
        Load a single module by full module name
        """
        module = None
        try:
            names = module_fullname.split('.')
            pkg_path = module_path
            for i in xrange(len(names)):
                if names[i] not in sys.modules:
                    if i == 0:
                        f, filename, data = imp.find_module(names[i], [pkg_path])
                    else:
                        f, filename, data = imp.find_module(names[i], pkg_path)
                    if i == len(names)-1:
                        name, ext = os.path.splitext(filename)
                        if os.path.exists(name + '.pyc'):
                            os.remove(name + '.pyc')

                    module = imp.load_module(names[i], f, filename, data)
                    if i < len(names)-1:
                        pkg_path = module.__path__
        except ImportError:
            print "ImportError: faild to import " + module_fullname
            traceback.print_exc(file=sys.stdout)
        assert module is not None
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
    def make_diff(cls, node1, node2, operator_name):
        """
        Compare the original source code and mutant.
        :param node1:
        :param node2:
        :return:
        """
        if not os.path.isdir('output'):
            os.mkdir(os.path.curdir + '/output')
        dest_dir = os.path.curdir + '/output'

        # write the original code to a file
        original_code = codegen.to_source(node1)
        filename = operator_name + "_original_" + ".py"
        path = os.path.join(dest_dir, filename)
        cls.write_to_file(path, original_code)

        # write the mutated code to a file
        mutated_code = codegen.to_source(node2)
        filename = operator_name + "_mutant_" + ".py"
        path = os.path.join(dest_dir, filename)
        cls.write_to_file(path, mutated_code)

        # write the diff result to a file
        d = Differ()
        res = ''.join(list(d.compare(original_code, mutated_code)))
        filename = operator_name + "_diff_" + ".py"
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

    @classmethod
    def save_change(cls, orignal, mutated):
        config.changes.append((orignal, mutated))








