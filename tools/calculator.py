import ast
import operator

_ALLOWED = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod
}

def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large.")
        return _ALLOWED[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
        return _ALLOWED[type(node.op)](_evaluate(node.operand))
    raise ValueError("Only basic arithmetic expressions are accepted.")

def safe_calculate(expression: str):
    if not expression or len(expression) > 100:
        raise ValueError("A short arithmetic expression is required.")
    tree = ast.parse(expression, mode="eval")
    result = _evaluate(tree)
    if isinstance(result, complex):
        raise ValueError("Complex results are not supported.")
    return result
