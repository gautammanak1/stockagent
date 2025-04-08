from typing import Dict, Any
from uagents import Model
from polygon import RESTClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Polygon REST client
client = RESTClient(os.getenv("POLYGON_API_KEY"))

# Model definitions
class StockInfoRequest(Model):
    ticker: str

class StockInfoResponse(Model):
    name: str = ""
    market_cap: float = 0.0
    description: str = ""
    exchange: str = ""
    share_class_shares_outstanding: float = 0.0
    weighted_shares_outstanding: float = 0.0
    error: str = None

class HistoricalDataRequest(Model):
    ticker: str

class HistoricalDataResponse(Model):
    data: Dict[str, float] = None
    error: str = None

def get_historical_stock_data(ticker: str) -> Dict[str, float]:
    """
    Gets the closing price for each day for the last 60 days for a particular ticker.

    Args:
        ticker (str): The stock ticker

    Returns:
        dict: A dictionary containing day and closing stock price for the past 60 days.
    """
    try:
        aggs = {}
        for a in client.list_aggs(
            ticker,
            1,
            "day",
            (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d'),
            datetime.today().strftime('%Y-%m-%d'),
            limit=50000,
        ):
            datetime_obj = datetime.fromtimestamp(a.timestamp / 1000)
            date_obj = datetime_obj.date()
            aggs[date_obj.strftime('%Y-%m-%d')] = a.close
        return aggs
    except Exception as e:
        raise Exception(f"Failed to fetch historical data: {str(e)}")

def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Get basic information about a stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol
        
    Returns:
        dict: Dictionary containing name, market_cap, description, exchange, etc.
    """
    try:
        details = client.get_ticker_details(ticker)
        
        return {
            "name": details.name or "",
            "market_cap": details.market_cap or 0.0,
            "description": details.description or "",
            "exchange": details.primary_exchange or "",
            "share_class_shares_outstanding": details.share_class_shares_outstanding or 0.0,
            "weighted_shares_outstanding": details.weighted_shares_outstanding or 0.0
        }
    except Exception as e:
        raise Exception(f"Failed to fetch stock info: {str(e)}")