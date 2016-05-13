import importlib
import ast


class ModuleLoader(object):

    @classmethod
    def load_modules(cls, full_module_names):
        """
        Load multiple modules by full module names
        """
        modules = []
        for name in full_module_names:
            module = cls.load_single_module(name)
            if module:
                modules.append(module)
        return modules

    @classmethod
    def load_single_module(cls, full_module_name):
        """
        Load a single module by full module name
        """
        module = None
        try:
            module = importlib.import_module(full_module_name)
        except ImportError:
            pass
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


class AST(ast.NodeTransformer):
    class_nodes = []
    function_nodes = []

    @classmethod
    def build_ast(cls, module):
        """
        Build an abstract syntax tree from a source file
        """
        with open(module.__file__) as module_file:
            cls.root = ast.parse(module_file.read(), module_file.name)
        return cls.root

    @classmethod
    def parse_ast(cls):
        """
        Parse an existing ast tree for some interesting nodes
        """
        if cls.root is None:
            return
        cls.dfs_ast(cls.root)

    @classmethod
    def dfs_ast(cls, node):
        if node is None: return
        if node.body == []: return

        for node in node.body:
            if node.__class__ is ast.ClassDef:
                # get all class nodes
                AST.class_nodes.append((node.name, node))
                cls.dfs_ast(node)
            elif node.__class__ is ast.FunctionDef:
                # get all function nodes
                AST.function_nodes.append((node.name, node))
                cls.dfs_ast(node)
            else:
                pass

    def visit_BinOp(self, node):

        if node.op.__class__ is ast.Add:
            return ast.BinOp(left=node.left, op=ast.Sub(), right=node.right)
        return node


if __name__ == "__main__":
    tree = ast.parse("a * b")
    # ast.fix_missing_locations(tree)
    print ast.dump(tree)

    tree = AST().visit(tree)
    # ast.fix_missing_locations(tree)
    print ast.dump(tree)
