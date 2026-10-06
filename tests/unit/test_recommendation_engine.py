"""Pruebas unitarias del motor híbrido de recomendación."""

from types import SimpleNamespace

import pytest

from src.services.recommendation import engine as engine_module
from src.services.recommendation.engine import HybridRecommendationEngine
from src.services.recommendation.schemas import ProductScore

pytestmark = pytest.mark.unit


class FakeCF:
    def __init__(self, results=None, exc=None):
        self._results = results or []
        self._exc = exc

    def recommend(self, user_id, context=None, limit=10):
        if self._exc:
            raise self._exc
        return self._results[:limit]


class FakeRules:
    def __init__(self, results=None):
        self._results = results or []

    def recommend(self, user_id, context=None, limit=10):
        return self._results[:limit]


class FakeDB:
    def __init__(self, products):
        self._products = {p.id: p for p in products}

    def get(self, model, pid):
        return self._products.get(pid)


PRODUCTS = [
    SimpleNamespace(id="p1", stock=5, rating=4.8),
    SimpleNamespace(id="p2", stock=3, rating=4.0),
    SimpleNamespace(id="p3", stock=0, rating=4.9),
    SimpleNamespace(id="p4", stock=7, rating=3.5),
]


@pytest.fixture(autouse=True)
def _patch_history(monkeypatch):
    monkeypatch.setattr(engine_module, "products_bought_recently", lambda db, user_id: set())
    monkeypatch.setattr(engine_module, "interaction_count", lambda db, user_id: 10)


def test_hybrid_fusion_weighted():
    cf = FakeCF([ProductScore("p1", 1.0, "collaborative"), ProductScore("p2", 0.5, "collaborative")])
    rules = FakeRules([ProductScore("p1", 0.5, "rules"), ProductScore("p4", 1.0, "rules")])
    engine = HybridRecommendationEngine(FakeDB(PRODUCTS), cf=cf, rules=rules)
    results, strategy = engine.recommend("u1")
    assert strategy == "hybrid"
    by_id = {r.product_id: r for r in results}
    # p1 presente en ambas => 0.7*1.0 + 0.3*0.5 = 0.85, source hybrid
    assert by_id["p1"].score == pytest.approx(0.85, abs=1e-3)
    assert by_id["p1"].source == "hybrid"
    # p2 solo CF => 0.7*0.5 = 0.35
    assert by_id["p2"].score == pytest.approx(0.35, abs=1e-3)
    assert by_id["p2"].source == "collaborative"
    # p4 solo reglas => 0.3*1.0 = 0.3
    assert by_id["p4"].score == pytest.approx(0.3, abs=1e-3)
    assert by_id["p4"].source == "rules"


def test_cold_start_uses_rules(monkeypatch):
    monkeypatch.setattr(engine_module, "interaction_count", lambda db, user_id: 1)
    cf = FakeCF([ProductScore("p1", 1.0, "collaborative")])
    rules = FakeRules([ProductScore("p4", 0.8, "rules")])
    engine = HybridRecommendationEngine(FakeDB(PRODUCTS), cf=cf, rules=rules)
    results, strategy = engine.recommend("u1")
    assert strategy == "rules"
    assert [r.product_id for r in results] == ["p4"]


def test_cf_failure_falls_back_to_rules():
    cf = FakeCF(exc=RuntimeError("boom"))
    rules = FakeRules([ProductScore("p2", 0.9, "rules")])
    engine = HybridRecommendationEngine(FakeDB(PRODUCTS), cf=cf, rules=rules)
    results, strategy = engine.recommend("u1")
    assert strategy == "rules"
    assert results[0].product_id == "p2"


def test_no_out_of_stock_in_results():
    cf = FakeCF([ProductScore("p3", 1.0, "collaborative")])  # p3 stock=0
    rules = FakeRules([])
    engine = HybridRecommendationEngine(FakeDB(PRODUCTS), cf=cf, rules=rules)
    results, _ = engine.recommend("u1")
    assert all(r.product_id != "p3" for r in results)


def test_limit_and_ordering():
    cf = FakeCF([ProductScore(pid, 1.0 - i * 0.1, "collaborative") for i, pid in enumerate(["p1", "p2", "p4"])])
    rules = FakeRules([])
    engine = HybridRecommendationEngine(FakeDB(PRODUCTS), cf=cf, rules=rules)
    results, _ = engine.recommend("u1", limit=2)
    assert len(results) == 2
    assert results[0].score >= results[1].score
