from lark import Lark, Tree, Token
import os

def parse_contract(file_path):
    grammar_path = os.path.join(os.path.dirname(__file__), "grammar.lark")
    with open(grammar_path, "r") as f:
        grammar = f.read()
    parser = Lark(grammar, parser='lalr')
    with open(file_path, "r") as f:
        tree = parser.parse(f.read())
    return transform_tree(tree)

def transform_tree(tree):
    if isinstance(tree, Tree):
        if tree.data == "start":
            return {
                "spec_version": transform_tree(tree.children[0]),
                "project": transform_tree(tree.children[1]),
                "input": transform_tree(tree.children[2]),
                "output": transform_tree(tree.children[3]),
                "implementation": transform_tree(tree.children[4])
            }
        elif tree.data == "spec_version":
            return str(tree.children[0])[1:-1]
        elif tree.data == "project_section":
            return {"name": str(tree.children[0])[1:-1], "version": str(tree.children[1])[1:-1]}
        elif tree.data in ("input_section", "output_section", "implementation_section"):
            return [transform_tree(child) for child in tree.children]
        elif tree.data == "source":
            return {"name": str(tree.children[0])}
        elif tree.data == "stage":
            result = {
                "name": str(tree.children[0]),
                "input": transform_tree(tree.children[1]),
                "output": transform_tree(tree.children[2]),
                "use": None,
                "schema": [],
                "require": [],
                "join": [],
                "filter": None,
                "deduplicate": None,
                "cast": [],
                "normalize": [],
                "enrich": []
            }
            remaining = list(tree.children[3:])
            while remaining:
                child = remaining.pop(0)
                if isinstance(child, Tree):
                    if child.data == "use_block":
                        result["use"] = transform_tree(child)
                    elif child.data == "schema_block":
                        result["schema"] = transform_tree(child)
                    elif child.data == "require_block":
                        result["require"] = transform_tree(child)
                    elif child.data == "join_block":
                        result["join"].append(transform_tree(child))
                    elif child.data == "filter_block":
                        result["filter"] = transform_tree(child.children[1])
                    elif child.data == "deduplicate_block":
                        result["deduplicate"] = transform_tree(child.children[1])
                    elif child.data == "cast_block":
                        result["cast"] = [transform_tree(c) for c in child.children if isinstance(c, Tree) and c.data == "cast_rule"]
                    elif child.data == "normalize_block":
                        result["normalize"] = [transform_tree(c) for c in child.children if isinstance(c, Tree) and c.data == "normalize_rule"]
                    elif child.data == "enrich_block":
                        result["enrich"] = [transform_tree(c) for c in child.children if isinstance(c, Tree) and c.data == "enrich_rule"]
            return result
        elif tree.data == "input_block":
            return str(tree.children[0])
        elif tree.data == "output_block":
            return str(tree.children[0])
        elif tree.data == "use_block":
            return str(tree.children[1])
        elif tree.data == "join_block":
            return {
                "target": str(tree.children[1]),
                "source": str(tree.children[3]),
                "on": str(tree.children[5])
            }
        elif tree.data == "schema_block":
            return [transform_tree(child) for child in tree.children]
        elif tree.data == "require_block":
            return [transform_tree(child) for child in tree.children]
        elif tree.data == "is_integer":
            return {"field": str(tree.children[0]), "operator": "is", "value": "integer"}
        elif tree.data == "is_float":
            return {"field": str(tree.children[0]), "operator": "is", "value": "float"}
        elif tree.data == "is_string":
            return {"field": str(tree.children[0]), "operator": "is", "value": "string"}
        elif tree.data == "compare_rule":
            op = str(tree.children[1])
            return {"field": str(tree.children[0]), "operator": op, "value": float(tree.children[2])}
        elif tree.data == "between_rule":
            return {"field": str(tree.children[0]), "operator": "between", "value": [int(tree.children[1]), int(tree.children[2])]}
        elif tree.data == "filter_condition":
            if len(tree.children) == 3:
                return {"field": str(tree.children[0]), "operator": str(tree.children[1]), "value": float(tree.children[2])}
            elif tree.children[1] == "between":
                return {"field": str(tree.children[0]), "operator": "between", "value": [int(tree.children[2]), int(tree.children[4])]}
            else:
                return {"field": str(tree.children[0]), "operator": str(tree.children[1]), "value": str(tree.children[2])[1:-1]}
        elif tree.data == "deduplicate_rule":
            return {"field": str(tree.children[0])}
        elif tree.data == "cast_rule":
            return {"field": str(tree.children[0]), "type": str(tree.children[1])}
        elif tree.data == "normalize_rule":
            return str(tree.children[0])
        elif tree.data == "enrich_rule":
            return str(tree.children[0])
        else:
            raise ValueError(f"Unknown tree data: {tree.data}")
    elif isinstance(tree, Token):
        return str(tree)
    return tree