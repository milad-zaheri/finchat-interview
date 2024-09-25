import json
import requests
import pandas as pd
from openai import OpenAI
from langchain.chat_models import ChatOpenAI


openai_secret_api_key = ''
fmp_api_key = 'b762c4bd614e32750579ec79bb84a490'

openai_client = OpenAI(organization='', api_key=openai_secret_api_key)
chat_model = ChatOpenAI(temperature=0, openai_api_key=openai_secret_api_key)


function=[
    {
  "name": "get_company_stock_ticker",
        "description": "This will get the stock ticker of the company",
        "Parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "This is the stock symbol of the company.",
                },
                "company_name": {
                    "type": "string",
                    "description": "This is the name of the company given query"
                }
            },
            "required": ["company_name", "ticker_symbol"]
        },
    }
]

def get_stock_ticker(query):
    response = openai_client.chat.completions.create(
      model="gpt-3.5-turbo",
      temperature=0,
      messages=[{
       "role":"user",
       "Content": f"Given the user request, what is the company name and the company stock ticker ?: {query}?"
      }],
      functions=function,
      function_call={"name": "get_company_stock_ticker"},
     )
    message = response.choices[0].message
    arguments = json.loads(message.function_call.arguments)
    company_name = arguments["company_name"]
    company_ticker = arguments["ticker_symbol"]
    tokens_used = response.usage.total_tokens
    return company_name,company_ticker, tokens_used


def get_ticker_historical_price(ticker, days=365):
    data = {}
    session = requests.Session()
    request = f"https://financialmodelingprep.com/api/v3/historical-chart/1day/{ticker}?from={(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}\&apikey={fmp_api_key}".replace(" ", "")
    r = session.get(request)
    if r.status_code == requests.codes.ok:
        data = json.loads(r.text)
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        df=df[["close","volume"]]
        df.index.rename("Date",inplace=True)
        df=df[:history] 
        return df.to_string()
    return data


def get_ticker_balance_sheet_data(ticker, period="quarter"):
    data = {}
    session = requests.Session()
    request = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period={period}\&apikey={fmp_api_key}".replace(" ", "")
    r = session.get(request)
    if r.status_code == requests.codes.ok:
      data = json.loads(r.text)
      df = pd.DataFrame(data)
      df.set_index('date', inplace=True)
      if df.shape[0]>=3:
        df = df[:3]
      df=df.dropna(how="any")
      return df.to_string()
    return data


def get_ticker_stock_news_articles(ticker, limit=5):
    data = {}
    session = requests.Session()
    request = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&limit={limit}\&apikey={fmp_api_key}".replace(" ", "")
    r = session.get(request)
    if r.status_code == requests.codes.ok:
      data = json.loads(r.text)
      df = pd.DataFrame(data)
      df.set_index('publishedDate', inplace=True)
      df.index.rename("Published Date",inplace=True)
      df=df.dropna(how="any")
      return df.to_string()
    return data


def finchat_stock_analyzer(query):
    company_name,ticker,tokens_used=get_stock_ticker(query)
    print({"Query":query,"Company_name":company_name,"Tokens_used":tokens_used,"Ticker":ticker})
    ticker = ticker.split(".")[0] if "." in ticker else ticker
    stock_data=get_ticker_historical_price(ticker,history=10)
    stock_financials=get_ticker_balance_sheet_data(ticker)
    stock_news=get_ticker_stock_news_articles(ticker)
    available_information=f"Stock Financials: {stock_financials}\nStock News: {stock_news}\nStock Technicals: {stock_data}"
    print("\nAnalyzing\n")
    analysis = chat_model.invoke(f"Give detail stock analysis, Use the available data to answer user question. \ Dont include any kind of investment recommendations or warning in the answer \ User question: {query} \ You have the following information available about {company_name}. Available Information : \ {available_information}")
    print(analysis.content)
    return analysis

finchat_stock_analyzer("Summarize Apple's latest earning call")
