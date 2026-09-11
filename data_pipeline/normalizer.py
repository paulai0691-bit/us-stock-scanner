import pandas as pd
from datetime import datetime

class DataNormalizer:
    """
    다양한 API 공급자(EODHD, AlphaVantage, FMP, Massive, FRED)의 시세 및 경제 지표 데이터를
    단일 표준 데이터 규격(Canonical Schema)으로 변환합니다.
    """

    @staticmethod
    def normalize_market_quote(provider: str, raw_data: dict, symbol: str) -> dict:
        """
        단일 종목 시세 표준 규격:
        {
            "symbol": str,
            "provider": str,
            "timestamp": str (ISO format),
            "price": float,
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": int,
            "previous_close": float
        }
        """
        normalized = {
            "symbol": symbol.upper(),
            "provider": provider,
            "timestamp": datetime.utcnow().isoformat(),
            "price": None,
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": None,
            "previous_close": None
        }

        if not raw_data or "error" in raw_data:
            return normalized

        try:
            if provider == "EODHD":
                normalized["price"] = float(raw_data.get("close", 0) or raw_data.get("previousClose", 0))
                normalized["open"] = float(raw_data.get("open", 0))
                normalized["high"] = float(raw_data.get("high", 0))
                normalized["low"] = float(raw_data.get("low", 0))
                normalized["close"] = float(raw_data.get("close", 0))
                normalized["volume"] = int(raw_data.get("volume", 0))
                normalized["previous_close"] = float(raw_data.get("previousClose", 0))

            elif provider == "AlphaVantage":
                quote = raw_data.get("Global Quote", raw_data)
                normalized["price"] = float(quote.get("05. price", 0))
                normalized["open"] = float(quote.get("02. open", 0))
                normalized["high"] = float(quote.get("03. high", 0))
                normalized["low"] = float(quote.get("04. low", 0))
                normalized["close"] = float(quote.get("05. price", 0))
                normalized["volume"] = int(quote.get("06. volume", 0))
                normalized["previous_close"] = float(quote.get("08. previous close", 0))

            elif provider == "FMP":
                normalized["price"] = float(raw_data.get("price", 0))
                normalized["open"] = float(raw_data.get("price", 0)) # Profile 기본 가격 대체
                normalized["volume"] = int(raw_data.get("volAvg", 0))

            elif provider == "Massive":
                results = raw_data.get("results", [])
                if results:
                    res = results[0]
                    normalized["price"] = float(res.get("c", 0))
                    normalized["open"] = float(res.get("o", 0))
                    normalized["high"] = float(res.get("h", 0))
                    normalized["low"] = float(res.get("l", 0))
                    normalized["close"] = float(res.get("c", 0))
                    normalized["volume"] = int(res.get("v", 0))

        except (ValueError, TypeError, KeyError):
            pass

        return normalized

    @staticmethod
    def normalize_fred_series(raw_df: pd.DataFrame, series_id: str) -> pd.DataFrame:
        """
        FRED 매크로 지표 표준 규격:
        DataFrame 컬럼: ['date', 'series_id', 'value']
        """
        if raw_df.empty or 'date' not in raw_df.columns or 'value' not in raw_df.columns:
            return pd.DataFrame(columns=['date', 'series_id', 'value'])

        df = raw_df.copy()
        df['series_id'] = series_id
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'])
        
        return df[['date', 'series_id', 'value']].dropna(subset=['value'])
