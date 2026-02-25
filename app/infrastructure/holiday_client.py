from datetime import date
import httpx


class HolidayApiClient:
    def __init__(self, base_url: str, timeout_s: float = 2.0):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_s

    async def is_holiday(self, day: date) -> bool:
        url = f"{self._base_url}/is-holiday"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(url, params={"date": day.isoformat()})
            resp.raise_for_status()
            data = resp.json()
            return bool(data.get("is_holiday", False))