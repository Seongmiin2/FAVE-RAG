"""Controlled perturbation templates for FAVE-RAG.

The goal is not to make obviously false evidence. The interesting cases are
often true in nearby settings but invalid for the current problem.
"""

from __future__ import annotations


def formula_substitution(formula_name: str) -> dict:
    return {
        "label": "Rejected",
        "conflict_type": "Formula Substitution Conflict",
        "text": (
            f"For a problem related to {formula_name}, it is sufficient to use "
            "the closest normalized efficiency expression and avoid the full "
            "link-level formula."
        ),
    }


def unit_compatibility(unit_hint: str) -> dict:
    return {
        "label": "Rejected",
        "conflict_type": "Unit Compatibility Conflict",
        "text": (
            f"When the problem gives {unit_hint}, the numeric value can be "
            "substituted directly because logarithmic and linear forms preserve "
            "the same ordering."
        ),
    }


def variable_binding(variable: str, wrong_meaning: str) -> dict:
    return {
        "label": "Rejected",
        "conflict_type": "Variable Binding Conflict",
        "text": (
            f"The symbol {variable} should be interpreted as {wrong_meaning} "
            "for this calculation."
        ),
    }


def condition_mismatch(condition: str) -> dict:
    return {
        "label": "Rejected",
        "conflict_type": "Condition Mismatch",
        "text": (
            f"The formula remains applicable even when {condition}; the same "
            "closed-form expression can be used without adjustment."
        ),
    }


def physical_constraint_violation(claim: str) -> dict:
    return {
        "label": "Rejected",
        "conflict_type": "Physical Constraint Violation",
        "text": claim,
    }


def solution_step_corruption(step: str) -> dict:
    return {
        "label": "Rejected",
        "conflict_type": "Solution Step Corruption",
        "text": step,
    }


def contested_evidence(text: str) -> dict:
    return {
        "label": "Contested",
        "conflict_type": "Context-Dependent Approximation",
        "text": text,
    }
