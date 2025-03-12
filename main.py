from flask import Flask, request, jsonify
import requests
import time
import hashlib
import hmac
import json

app = Flask(__name__)

# ✅ MEXC API Bilgilerini Gir
api_key = "GERÇEK_MEXC_API_KEY"  # MEXC API Key
api_secret = "GERÇEK_MEXC_SECRET_KEY"  # MEXC Secret Key

# ✅ MEXC API URL
MEXC_API_URL = "https://api.mexc.com"

# ✅ MEXC API İmzalama Fonksiyonu
def create_signature(params, secret):
    query_string = "&".join(f"{key}={value}" for key, value in sorted(params.items()))
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# ✅ MEXC API Üzerinden Bakiye Sorgulama
@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        timestamp = int(time.time() * 1000)
        params = {
            "timestamp": timestamp
        }
        params["signature"] = create_signature(params, api_secret)

        headers = {
            "X-MEXC-APIKEY": api_key
        }

        response = requests.get(f"{MEXC_API_URL}/api/v3/account", headers=headers, params=params)
        data = response.json()

        print("MEXC API Yanıtı:", data)  # Loglara yaz

        if "balances" in data:
            btc_balance = next((item["free"] for item in data["balances"] if item["asset"] == "BTC"), 0)
            usdt_balance = next((item["free"] for item in data["balances"] if item["asset"] == "USDT"), 0)
        else:
            return jsonify({"error": "MEXC API beklenen formatta yanıt vermedi.", "response": data})

        return jsonify({
            "BTC Balance": btc_balance,
            "USDT Balance": usdt_balance
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ BTC/USDT Piyasa Fiyatını Al
@app.route('/price', methods=['GET'])
def get_price():
    try:
        response = requests.get(f"{MEXC_API_URL}/api/v3/ticker/price?symbol=BTCUSDT")
        data = response.json()

        print("MEXC'ten Gelen Fiyat Verisi:", data)  # Loglara yaz

        return jsonify({"BTC/USDT Price": data.get("price", "Fiyat alınamadı")})

    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Piyasa Fiyatından BTC Al (Market Order)
@app.route('/buy', methods=['POST'])
def buy_order():
    try:
        data = request.json
        amount = float(data.get("amount", 0.001))  # Varsayılan 0.001 BTC
        timestamp = int(time.time() * 1000)

        params = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quantity": amount,
            "timestamp": timestamp
        }
        params["signature"] = create_signature(params, api_secret)

        headers = {
            "X-MEXC-APIKEY": api_key
        }

        response = requests.post(f"{MEXC_API_URL}/api/v3/order", headers=headers, params=params)
        data = response.json()

        print("BTC Alım Yanıtı:", data)  # Loglara yaz

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Piyasa Fiyatından BTC Sat (Market Order)
@app.route('/sell', methods=['POST'])
def sell_order():
    try:
        data = request.json
        amount = float(data.get("amount", 0.001))  # Varsayılan 0.001 BTC
        timestamp = int(time.time() * 1000)

        params = {
            "symbol": "BTCUSDT",
            "side": "SELL",
            "type": "MARKET",
            "quantity": amount,
            "timestamp": timestamp
        }
        params["signature"] = create_signature(params, api_secret)

        headers = {
            "X-MEXC-APIKEY": api_key
        }

        response = requests.post(f"{MEXC_API_URL}/api/v3/order", headers=headers, params=params)
        data = response.json()

        print("BTC Satış Yanıtı:", data)  # Loglara yaz

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ API'nin Çalıştığını Kontrol Etmek İçin Ana Sayfa
@app.route("/")
def home():
    return "✅ MEXC API bağlantısı aktif! BTC/USDT işlemleri için hazır."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
