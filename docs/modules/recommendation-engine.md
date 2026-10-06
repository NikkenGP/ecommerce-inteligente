# 🧠 Módulo: Motor de Recomendación Híbrido

**Fecha:** 2026-10-06
**Spec asociada:** `specs/006-recommendation-engine.spec.md`

---

## Visión General

Motor de recomendación híbrido que combina **filtrado colaborativo item-based** (similitud coseno sobre la matriz usuario-ítem) con **reglas de negocio** declarativas. Endpoint: `GET /api/v1/recommendations/{user_id}?limit=10`.

## Fórmula de Fusión

```
final_score = α * collaborative_score + β * rule_score
α = 0.7, β = 0.3 (configurables por entorno)
```

- Si solo una estrategia produce resultados, usar su score directamente.
- Deduplicar por `product_id` conservando el mayor score.
- Fuente del resultado: `collaborative` | `rules` | `hybrid`.

## Cold Start y Fallback

- Usuario con < 3 interacciones → delegar a reglas (R4: rating ≥ 4.0 y stock > 0 como fallback global).
- Si `CollaborativeFilteringRecommender` lanza excepción → responder solo con reglas, sin propagar el error.
- Si Redis está caído → recalcular sin caché (degradar, no fallar).

## Caché

- Clave: `recommendations:{user_id}:{limit}`.
- TTL máximo: 5 minutos.
- Resultados reutilizados dentro del TTL; regeneración al expirar.

## Reglas de Negocio (`src/services/recommendation/rules.py`)

| ID | Regla | Peso |
|----|-------|------|
| R1 | Productos de la misma categoría que el último visto | 0.4 |
| R2 | Productos frecuentemente comprados juntos | 0.3 |
| R3 | Productos en promoción del segmento | 0.2 |
| R4 | Rating ≥ 4.0 y stock > 0 (global) | 0.1 |

## Filtros de Producto

Excluir siempre: `stock = 0` y productos comprados en los últimos 30 días (salvo regla explícita).

## Estructura de Código

```
src/services/recommendation/
├── __init__.py
├── engine.py            # HybridRecommendationEngine
├── collaborative.py     # CollaborativeFilteringRecommender
├── rules.py             # RuleBasedRecommender
├── schemas.py           # ProductScore, RecommendationResponse
└── cache.py             # Capa de caché Redis (TTL 5 min)
```

## Interfaz

```python
class Recommender(Protocol):
    def recommend(self, user_id: str, context: dict | None = None, limit: int = 10) -> list[ProductScore]: ...

@dataclass
class ProductScore:
    product_id: str
    score: float   # 0.0 - 1.0
    source: str    # collaborative | rules | hybrid
```

## Observabilidad

Logs estructurados por llamada: `{user_id, strategy, latency_ms, result_count, cache_hit}`.

## Requisitos No Funcionales

| Métrica | Objetivo |
|---------|----------|
| Latencia endpoint | p95 < 300 ms (catálogo ≤ 100k productos) |
| Caché | TTL ≤ 5 min por `user_id` |
| Cobertura de tests | ≥ 80% del módulo |

## Estrategia de Pruebas

- Unit: fusión α/β con entradas controladas; frío de arranque; exclusión de stock 0.
- Integración: TestClient + `httpx` — casos 200, 404 (usuario inexistente), 500 (fallback activado).
- Benchmark: dataset de 10k productos, criterio p95 < 300 ms.
- Caché: mock de Redis comprobando reutilización dentro del TTL.
