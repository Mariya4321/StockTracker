import requests
import datetime as dt
from twilio.rest import Client
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

phone_no = os.environ["phone_no"]

my_api_key = os.environ["api_key"]
news_api = os.environ["news_key"]

acc_id = os.environ["acc_id"]
auth_token = os.environ["auth_token"]

parameter = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": my_api_key,
}
news_parameter = {
    "qInTitle": COMPANY_NAME,
    "from": "2024-06-15",
    "sortBy": "publishedAt",
    "apiKey": news_api,
    "language": "en",
}

response = requests.get("https://www.alphavantage.co/query", params=parameter)
response.raise_for_status()
stock_data = response.json()

Day = dt.datetime.now()
day_opening = str(dt.datetime(day=Day.day - 1, year=Day.year, month=Day.month, hour=4))
day_closing = str(dt.datetime(day=Day.day - 2, year=Day.year, month=Day.month, hour=19))

opening = float(stock_data["Time Series (60min)"][day_opening]["1. open"])
closing = float(stock_data["Time Series (60min)"][day_closing]["4. close"])
diff_percentage = ((opening - closing) / closing) * 100
per = round(diff_percentage, 2)

up_down = None
if closing > opening:
    up_down = "⬇️"
if opening > closing:
    up_down = "⬆️"

if per >= 5.0:
    news = requests.get("https://newsapi.org/v2/everything", params=news_parameter)
    news.raise_for_status()
    news_data = news.json()["articles"]

    news_article = news_data[:3]
    new_list_article = [(f"{COMPANY_NAME}: {up_down}{per}% \nHeadline: {article['title']}. "
                         f"\nBrief: {article['description']}") for article in news_article]
    client = Client(acc_id, auth_token)
    for article in new_list_article:
        message = client.messages.create(
            body=article,
            from_="+19713024433",
            to=phone_no,
        )
        print(message.status)
