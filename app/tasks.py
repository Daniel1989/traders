from app.celery_app import celery_app
import time
from typing import Dict, Optional
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
from app.models import GoodsPriceInSecond, Goods
import traceback
from app.utils import is_trade_time, is_same_trading_day
import datetime
from app.database import Session, engine
from decimal import Decimal
from sqlmodel import select

def is_debian():
    try:
        with open("/etc/os-release", "r") as file:
            os_info = file.read().lower()
            return "debian" in os_info
    except FileNotFoundError:
        return False

def parse_price_data(page: Page, symbol: str, goods_id: int) -> Optional[Dict]:
    """Parse price data from the page and save to database"""
    try:
        content = page.evaluate("""
            () => {
                return document.getElementById("table-box-futures-hq").innerHTML
            }
        """)

        soup = BeautifulSoup('<div>' + content + '</div>', 'html.parser')
        trs = soup.find_all("tr")
        price_detail = [symbol, goods_id]

        for index, tr in enumerate(trs):
            th = tr.find_all("th")
            td = tr.find_all("td")
            if index == 3:
                continue
            else:
                if index == 0:
                    first = td.pop(0)
                    trade_time = first.find(class_='trade-time').text
                    current_price = first.find(class_='price').text
                    price_diff = first.find(class_='amt-value').text.replace("+", "").replace("-", "")
                    price_diff_percent = first.find(class_='amt').text.replace("+", "") \
                        .replace("-", "").replace("%", "")
                    price_detail.append(trade_time)
                    price_detail.append(current_price)
                    price_detail.append(price_diff)
                    price_detail.append(price_diff_percent)
                for h, d in zip(th, td):
                    if len(h.text.strip()) > 0:
                        price_detail.append(d.text)

        price_model_key_list = [
            'uid', 'goods', 'price_time', 'current_price', 'price_diff',
            'price_diff_percent', 'close_price', 'open_price',
            'high_price', 'low_price',
            'compute_price', 'prev_compute_price',
            'have_vol', 'deal_vol', 'buy_price_oncall', 'sell_price_oncall',
            'buy_vol', 'sell_vol',
        ]
        
        info = {}
        for item in price_model_key_list:
            info[item] = price_detail.pop(0)

        # Convert string values to Decimal for numeric fields
        decimal_fields = [
            'current_price', 'price_diff', 'price_diff_percent', 
            'close_price', 'open_price', 'high_price', 'low_price',
            'compute_price', 'prev_compute_price', 
            'buy_price_oncall', 'sell_price_oncall'
        ]
        
        for field in decimal_fields:
            if info[field]:
                info[field] = Decimal(str(info[field]))

        # Convert string values to int for volume fields
        int_fields = ['have_vol', 'deal_vol', 'buy_vol', 'sell_vol']
        for field in int_fields:
            if info[field]:
                info[field] = int(info[field])

        # Save to database using SQLModel
        with Session(engine) as session:
            # Get max id for the current day
            today = datetime.datetime.now().date()
            today_start = datetime.datetime.combine(today, datetime.time.min)
            today_end = datetime.datetime.combine(today, datetime.time.max)
            
            statement = select(GoodsPriceInSecond).where(
                GoodsPriceInSecond.created_at.between(today_start, today_end)
            ).order_by(GoodsPriceInSecond.id.desc())
            last_record = session.exec(statement).first()
            
            # Set the next id
            next_id = (last_record.id + 1) if last_record else 1
            
            # Create and save the record without refresh
            price_record = GoodsPriceInSecond(
                id=next_id,
                **info
            )
            session.add(price_record)
            session.commit()
            # Remove the refresh call since we don't need it
            
            # Update the info with the generated id
            info['id'] = next_id

        return info

    except Exception as e:
        traceback.print_exc()
        return None

@celery_app.task
def add_numbers(x: int, y: int) -> int:
    """
    A simple task that adds two numbers
    Includes an artificial delay to simulate long-running process
    """
    time.sleep(5)  # Simulate long computation
    return x + y

@celery_app.task
def fetch_futures_price(symbol: str) -> Dict:
    """
    Fetch the price for a given futures symbol using playwright
    Keeps running until the end of trading day
    Only parses and saves data during trading hours
    """
    try:
        # Get goods info from database using SQLModel select
        with Session(engine) as session:
            statement = select(Goods).where(Goods.name == symbol[:2])
            goods = session.exec(statement).first()
            if not goods:
                raise ValueError(f"No goods found for symbol prefix: {symbol[:2]}")

        base_url = "https://finance.sina.com.cn/futures/quotes"
        url = f"{base_url}/{symbol.upper()}.shtml"

        start_time = datetime.datetime.now()
        last_info = None

        with sync_playwright() as p:
            target = p.webkit if is_debian() else p.chromium
            browser = target.launch()
            
            try:
                page = browser.new_page()
                page.goto(url)
                page.wait_for_selector(".min-price")

                while is_same_trading_day(start_time):
                    if is_trade_time():
                        info = parse_price_data(page, symbol, goods.id)
                        if info:
                            last_info = info
                            print(f"Updated price for {symbol}: {info['current_price']} at {info['price_time']}")
                    else:
                        print(f"Waiting for next trading session... Current time: {datetime.datetime.now().strftime('%H:%M:%S')}")
                    
                    time.sleep(5)

                if last_info:
                    return {
                        "symbol": symbol,
                        "status": "success",
                        "price_time": last_info['price_time'],
                        "current_price": str(last_info['current_price']),
                        "price_diff": str(last_info['price_diff']),
                        "price_diff_percent": str(last_info['price_diff_percent']),
                        "high_price": str(last_info['high_price']),
                        "low_price": str(last_info['low_price']),
                        "open_price": str(last_info['open_price']),
                        "close_price": str(last_info['close_price']),
                        "message": "Trading day completed"
                    }
                else:
                    return {
                        "symbol": symbol,
                        "status": "error",
                        "error": "No data was successfully fetched during the trading day"
                    }

            finally:
                browser.close()

    except Exception as e:
        traceback.print_exc()
        return {
            "symbol": symbol,
            "status": "error",
            "error": f"Failed to fetch price: {str(e)}"
        } 