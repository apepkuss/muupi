import ast

# specify if some changes happened on the original module
mutated = False

# indicates if a mutated node needs recovery
recovering = False

# save node info before and after mutation happens
changes = []

# for SDM operator
nodes_to_remove = set()
nodes_to_potential = set()

# save all mutated nodes
node_pairs = {}
visited_nodes = set()
current_mutated_node = None

# save parent-child relations
parent_dict = {}

# save the number of output files
counter = 0

# list of arithmetic operators for AOR, ASR
arithmetic_operators = [ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv]

comparison_operators = [ast.Eq, ast.NotEq, ast.Lt, ast.Gt, ast.LtE, ast.GtE]


