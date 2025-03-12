from flask import Flask, request, jsonify
import requests
import time
import hashlib
import hmac
import os
import logging

app = Flask(__name__)

# ✅ Log Ayarları
logging.basicConfig(level=logging.INFO)

# ✅ Çevresel Değişkenlerden API Key ve Secret'ı Al
API_KEY = os.getenv("BYBIT_DEMO_API_KEY")
API_SECRET = os.getenv("BYBIT_DEMO_API_SECRET")

# ✅ Bybit Demo API URL
BYBIT_API_URL = "https://api-testnet.bybit.com"

# ✅ Bybit API İmzalama Fonksiyonu
def create_signature(params, secret):
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{key}={value}" for key, value in sorted_params)
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# ✅ Bybit API Üzerinden Bakiye Sorgulama
@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        timestamp = str(int(time.time() * 1000))
        params = {
            "api_key": API_KEY,
            "timestamp": timestamp
        }
        params["sign"] = create_signature(params, API_SECRET)

        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BYBIT_API_URL}/v2/private/wallet/balance", headers=headers, params=params)
        data = response.json()

        logging.info(f"Bybit API Yanıtı: {data}")

        if "result" in data:
            usdt_balance = data["result"]["USDT"]["available_balance"]
            btc_balance = data["result"]["BTC"]["available_balance"]
        else:
            return jsonify({"error": "Bybit API beklenen formatta yanıt vermedi.", "response": data})

        return jsonify({"BTC Balance": btc_balance, "USDT Balance": usdt_balance})

    except Exception as e:
        logging.error(f"Bakiye sorgulama hatası: {e}")
        return jsonify({"error": str(e)})

# ✅ BTC/USDT Piyasa Fiyatını Al
@app.route('/price', methods=['GET'])
def get_price():
    try:
        response = requests.get(f"{BYBIT_API_URL}/v2/public/tickers")
        data = response.json()

        logging.info(f"Bybit'ten Gelen Fiyat Verisi: {data}")

        for ticker in data.get("result", []):
            if ticker["symbol"] == "BTCUSDT":
                return jsonify({"BTC/USDT Price": ticker["last_price"]})

        return jsonify({"error": "BTC/USDT fiyatı bulunamadı.", "response": data})

    except Exception as e:
        logging.error(f"Fiyat sorgulama hatası: {e}")
        return jsonify({"error": str(e)})

# ✅ Piyasa Fiyatından BTC Al (Market Order)
@app.route('/buy', methods=['POST'])
def buy_order():
    try:
        data = request.json
        amount = float(data.get("amount", 0.001))
        timestamp = str(int(time.time() * 1000))

        params = {
            "api_key": API_KEY,
            "symbol": "BTCUSDT",
            "side": "Buy",
            "order_type": "Market",
            "qty": amount,
            "time_in_force": "GTC",
            "timestamp": timestamp
        }
        params["sign"] = create_signature(params, API_SECRET)

        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BYBIT_API_URL}/v2/private/order/create", headers=headers, params=params)
        data = response.json()

        logging.info(f"BTC Alım Yanıtı: {data}")

        return jsonify(data)

    except Exception as e:
        logging.error(f"BTC satın alma hatası: {e}")
        return jsonify({"error": str(e)})

# ✅ Piyasa Fiyatından BTC Sat (Market Order)
@app.route('/sell', methods=['POST'])
def sell_order():
    try:
        data = request.json
        amount = float(data.get("amount", 0.001))
        timestamp = str(int(time.time() * 1000))

        params = {
            "api_key": API_KEY,
            "symbol": "BTCUSDT",
            "side": "Sell",
            "order_type": "Market",
            "qty": amount,
            "time_in_force": "GTC",
            "timestamp": timestamp
        }
        params["sign"] = create_signature(params, API_SECRET)

        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BYBIT_API_URL}/v2/private/order/create", headers=headers, params=params)
        data = response.json()

        logging.info(f"BTC Satış Yanıtı: {data}")

        return jsonify(data)

    except Exception as e:
        logging.error(f"BTC satma hatası: {e}")
        return jsonify({"error": str(e)})

# ✅ API'nin Çalıştığını Kontrol Etmek İçin Ana Sayfa
@app.route("/")
def home():
    return "✅ Bybit Demo API bağlantısı aktif! BTC/USDT işlemleri için hazır."

# ✅ Render.com İçin Gerekli Ayarlar
if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 10000))
    serve(app, host="0.0.0.0", port=port)
