from datetime import date
import httpx


class HolidayApiClient:
    def __init__(self, base_url: str, timeout_s: float = 2.0): #init - ustalanie wartosci poczatkowych
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_s

    async def is_holiday(self, day: date) -> bool:#laczymy sie z prawdziwym API (is holiday)
        url = f"{self._base_url}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
            holidays = resp.json()#json nam wrzuci wszystkie swieta w 2026
            dates = {h["date"] for h in holidays} #budujemy liste samych dat świąt
            return str(day) in dates #zwroci true/False
