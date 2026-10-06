"""Pruebas unitarias del cálculo de totales del carrito."""

import pytest

from src.services.cart.service import compute_totals

pytestmark = pytest.mark.unit


def test_compute_totals_basic():
    totals = compute_totals([100.0, 50.0])
    assert totals["subtotal"] == 150.0
    assert totals["tax"] == 24.0
    assert totals["total"] == 174.0


def test_compute_totals_empty():
    totals = compute_totals([])
    assert totals == {"subtotal": 0, "tax": 0, "total": 0}
