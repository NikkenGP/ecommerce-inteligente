"""Lógica de cálculo del carrito (subtotal, impuestos, total)."""

from __future__ import annotations

TAX_RATE = 0.16


def compute_totals(line_subtotals: list[float]) -> dict:
    """Calcula subtotal, impuestos (16%) y total del carrito."""
    subtotal = round(sum(line_subtotals), 2)
    tax = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + tax, 2)
    return {"subtotal": subtotal, "tax": tax, "total": total}
