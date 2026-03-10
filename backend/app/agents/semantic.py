"""Semantic Analysis Agent - determines variable roles (defined, used, undefined)."""
from app.agents.base import ParsedEquation, ASTNode, VariableInfo, SemanticEquation


def _collect_vars(node: ASTNode | None) -> set[str]:
    """Collect all variable names from AST."""
    out: set[str] = set()
    if node is None:
        return out
    if node.type == "VAR":
        if node.value:
            out.add(node.value)
        return out
    if node.type in ("BINARY", "UNARY"):
        out |= _collect_vars(node.left)
        out |= _collect_vars(node.right)
        return out
    if node.type == "CALL":
        out |= _collect_vars(node.left)
        return out
    return out


class SemanticAnalyzerAgent:
    """Determine which variables are defined vs used in each equation."""

    def analyze(self, parsed: ParsedEquation, all_defined_so_far: set[str] | None = None) -> SemanticEquation:
        """Analyze equation and classify variables. all_defined_so_far = vars defined in prior equations."""
        defined_so_far = all_defined_so_far or set()
        defined_in_this = set()
        if parsed.lhs_var:
            defined_in_this.add(parsed.lhs_var)
        used = _collect_vars(parsed.ast)
        # LHS variable is "defined", not "used" in this equation
        used -= defined_in_this
        undefined = used - defined_so_far - defined_in_this

        variables: list[VariableInfo] = []
        for v in defined_in_this:
            variables.append(VariableInfo(name=v, role="defined"))
        for v in sorted(used):
            role = "undefined" if v in undefined else "used"
            variables.append(VariableInfo(name=v, role=role))
        for v in sorted(undefined):
            if not any(x.name == v and x.role == "undefined" for x in variables):
                variables.append(VariableInfo(name=v, role="undefined"))

        return SemanticEquation(
            parsed=parsed,
            variables=variables,
            defined_vars=list(defined_in_this),
            used_vars=list(used),
            undefined_vars=list(undefined),
        )
