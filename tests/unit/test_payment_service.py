"""Pruebas unitarias del servicio de pagos simulado."""

import pytest

from src.services.payments.gateway import MockPaymentGateway, PaymentTimeoutError

pytestmark = pytest.mark.unit


def test_approved_scenario():
    gateway = MockPaymentGateway()
    result = gateway.charge(100.0, "USD", scenario="approved")
    assert result.status == "approved"
    assert result.transaction_id and result.transaction_id.startswith("txn_")


def test_declined_scenario():
    gateway = MockPaymentGateway()
    result = gateway.charge(100.0, "USD", scenario="declined")
    assert result.status == "declined"
    assert result.reason


def test_timeout_scenario():
    gateway = MockPaymentGateway()
    with pytest.raises(PaymentTimeoutError):
        gateway.charge(100.0, "USD", scenario="timeout")


def test_invalid_amount_rejected():
    gateway = MockPaymentGateway()
    with pytest.raises(ValueError):
        gateway.charge(0.0, "USD")


def test_unknown_scenario_rejected():
    gateway = MockPaymentGateway()
    with pytest.raises(ValueError):
        gateway.charge(10.0, "USD", scenario="inventado")
