"""Interfaz de pasarela de pagos y resultado de cobro.

La implementación real NUNCA existe en esta fase: solo un mock controlado
por escenarios (approved | declined | timeout).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Protocol


class PaymentTimeoutError(Exception):
    """Error ante timeout de la pasarela simulada."""


@dataclass
class PaymentResult:
    status: str  # approved | declined
    transaction_id: str | None = None
    reason: str | None = None


class PaymentGateway(Protocol):
    def charge(self, amount: float, currency: str, scenario: str | None = None) -> PaymentResult: ...


class MockPaymentGateway:
    """Pasarela simulada. Escenario configurable por llamada o por defecto."""

    def __init__(self, default_scenario: str = "approved") -> None:
        self.default_scenario = default_scenario

    def charge(self, amount: float, currency: str, scenario: str | None = None) -> PaymentResult:
        if amount <= 0:
            raise ValueError("Monto debe ser mayor a 0")
        chosen = scenario or self.default_scenario
        if chosen == "approved":
            return PaymentResult(status="approved", transaction_id=f"txn_{uuid.uuid4().hex[:12]}")
        if chosen == "declined":
            return PaymentResult(status="declined", reason="Fondos insuficientes")
        if chosen == "timeout":
            raise PaymentTimeoutError("Timeout de la pasarela (simulado)")
        raise ValueError(f"Escenario desconocido: {chosen}")
