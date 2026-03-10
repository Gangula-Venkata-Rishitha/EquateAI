"""Serialize AST to JSON-serializable dict."""
from app.agents.base import ASTNode


def ast_to_dict(node: ASTNode | None) -> dict | None:
    if node is None:
        return None
    d: dict = {"type": node.type}
    if node.value is not None:
        d["value"] = node.value
    if node.left is not None:
        d["left"] = ast_to_dict(node.left)
    if node.right is not None:
        d["right"] = ast_to_dict(node.right)
    if node.children:
        d["children"] = [ast_to_dict(c) for c in node.children]
    return d
