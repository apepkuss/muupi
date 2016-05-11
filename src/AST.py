import ast


class ASTTransformer(ast.NodeTransformer):

    def visit_BinOp(self, node):

        if node.op.__class__ is ast.Add:
            return ast.BinOp(left=node.left, op=ast.Sub(), right=node.right)
        return node

if __name__ == "__main__":
    tree = ast.parse("a * b")
    # ast.fix_missing_locations(tree)
    print ast.dump(tree)

    tree = ASTTransformer().visit(tree)
    # ast.fix_missing_locations(tree)
    print ast.dump(tree)
