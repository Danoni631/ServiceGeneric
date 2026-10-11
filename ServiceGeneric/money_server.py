import sys
import subprocess

# Auto-instalação de dependências
required_packages = ['flask', 'flask_cors', 'yfinance']

def install_missing_packages():
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Library '{package}' don't finded. Installing automatically...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_missing_packages()

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

@app.route('/api/finance', methods=['GET'])
def get_finance():
    symbol = request.args.get('symbol', 'PETR4.SA').upper()

    try:
        ticker = yf.Ticker(symbol)
        todays_data = ticker.history(period='1d')

        if todays_data.empty:
            return jsonify({
                "success": False,
                "error": f"Active '{symbol}' don't finded or without recent data."
            }), 404

        current_price = todays_data['Close'].iloc[-1]
        open_price = todays_data['Open'].iloc[-1]
        high_price = todays_data['High'].iloc[-1]
        low_price = todays_data['Low'].iloc[-1]
        volume = int(todays_data['Volume'].iloc[-1])
        
        info = ticker.info
        name = info.get('longName', info.get('shortName', symbol))
        currency = info.get('currency', 'BRL')

        variation_abs = current_price - open_price
        variation_pct = (variation_abs / open_price) * 100

        return jsonify({
            "success": True,
            "data": {
                "symbol": symbol,
                "name": name,
                "currency": currency,
                "price": round(float(current_price), 2),
                "open": round(float(open_price), 2),
                "high": round(float(high_price), 2),
                "low": round(float(low_price), 2),
                "volume": volume,
                "variation": {
                    "absolute": round(float(variation_abs), 2),
                    "percentage": round(float(variation_pct), 2)
                }
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to search finances data: {str(e)}"
        }), 500

@app.route('/api/finance/txt', methods=['GET'])
def get_finance_txt():
    symbol = request.args.get('symbol', 'PETR4.SA').upper()
    try:
        ticker = yf.Ticker(symbol)
        todays_data = ticker.history(period='1d')
        if todays_data.empty:
            return f"Ativo '{symbol}' não encontrado.\n", 404

        price = round(float(todays_data['Close'].iloc[-1]), 2)
        info = ticker.info
        name = info.get('longName', symbol)
        currency = info.get('currency', 'BRL')

        output = f"=== COTACAO: {symbol} ===\n"
        output += f"Ativo: {name}\n"
        output += f"Preco Atual: {price} {currency}\n"
        return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"Erro: {str(e)}\n", 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Online finances server 📈",
        "endpoints": {
            "json": "/api/finance?symbol=PETR4.SA",
            "txt_puro": "/api/finance/txt?symbol=BTC-USD"
        },
        "exemplos_ativos": ["PETR4.SA (Petrobras)", "VALE3.SA (Vale)", "AAPL (Apple)", "BTC-USD (Bitcoin)", "BRL=X (Dolar/Real)"]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002, debug=True)
