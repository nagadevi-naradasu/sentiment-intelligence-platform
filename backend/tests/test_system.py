import pytest
import httpx
import asyncio

# ─────────────────────────────────────────────
# 1. TEST LOGIC
# ─────────────────────────────────────────────
def normalize_sentiment_test(label: str) -> str:
    """We define the logic here to test if our mapping rules work"""
    label = label.lower()
    if "positive" in label or "label_1" in label:
        return "positive"
    if "negative" in label or "label_0" in label:
        return "negative"
    return "neutral"

def test_sentiment_logic():
    """Verify the mapping rules we expect the system to follow"""
    assert normalize_sentiment_test("POSITIVE") == "positive"
    assert normalize_sentiment_test("LABEL_1") == "positive"
    assert normalize_sentiment_test("NEGATIVE") == "negative"
    assert normalize_sentiment_test("some_random_text") == "neutral"

# ─────────────────────────────────────────────
# 2. TEST API (INTEGRATION)
# ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_api_health():
    """Check if the FastAPI backend is responding"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            response = await client.get("/api/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
        except Exception as e:
            pytest.fail(f"Backend unreachable: {e}")

@pytest.mark.asyncio
async def test_api_alerts_format():
    """Check if the alerts endpoint returns a list (even if empty)"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/api/alerts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)