"""Classify equations by logical / mathematical type."""
from __future__ import annotations

import re
from enum import StrEnum

from app.db import models


class EquationType(StrEnum):
    ALGEBRAIC = "ALGEBRAIC"
    DIFFERENTIAL = "DIFFERENTIAL"
    PROPOSITIONAL_LOGIC = "PROPOSITIONIAL_LOGIC"
    PREDICATE_LOGIC = "PREDICATE_LOGIC"
    LTL = "LTL"
    CTL = "CTL"
    CLTL = "CLTL"
    UNKNOWN = "UNKNOWN"


class EquationClassifier:
    """Rule-based classifier for equation logic type."""

    _diff_pattern = re.compile(r"d[A-Za-z]\s*/\s*dt|\b\\dot\{|∂")
    _forall_exists = re.compile(r"[∀∃]")
    _logic_ops = re.compile(r"(?:\\land|\\lor|\\to|->|⇒|→|∧|∨)")
    _quantifier = re.compile(r"\bforall\b|\bexists\b", re.IGNORECASE)
    _ltl = re.compile(r"\b[FGXU]\b")
    _ctl = re.compile(r"\bA[GF]|E[GF]\b")
    _cltl = re.compile(r"\bCLTL\b", re.IGNORECASE)

    def classify_text(self, text: str) -> EquationType:
        t = text.strip()
        if not t:
            return EquationType.UNKNOWN

        # Temporal logics first (most specific)
        if self._cltl.search(t):
            return EquationType.CLTL
        if self._ctl.search(t):
            return EquationType.CTL
        if self._ltl.search(t):
            return EquationType.LTL

        # Predicate / propositional logic
        if self._forall_exists.search(t) or self._quantifier.search(t):
            # Has variables with quantifiers → predicate logic
            return EquationType.PREDICATE_LOGIC
        if self._logic_ops.search(t):
            return EquationType.PROPOSITIONAL_LOGIC

        # Differential equations
        if self._diff_pattern.search(t) or "d/dt" in t or "∂" in t:
            return EquationType.DIFFERENTIAL

        # Algebraic: arithmetic and '='
        if any(op in t for op in ["=", "+", "-", "*", "/", "^"]):
            return EquationType.ALGEBRAIC

        return EquationType.UNKNOWN

    def apply_to_equation(self, eq: models.Equation) -> EquationType:
        etype = self.classify_text(eq.raw_text or "")
        eq.equation_type = etype.value
        return etype

