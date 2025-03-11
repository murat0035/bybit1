from flask import Flask, request, jsonify
import requests
import time
import hashlib
import hmac

app = Flask(__name__)

# ✅ Bybit API Bilgilerini Gir (Gerçek Hesap)
api_key = "GERÇEK_BYBIT_API_KEY"  # Bybit Gerçek Hesap API Key
api_secret = "GERÇEK_BYBIT_SECRET_KEY"  # Bybit Gerçek Hesap Secret Key

# ✅ Bybit Gerçek API URL
BYBIT_API_URL = "https://api.bybit.com"

# ✅ Bybit API İmzalama Fonksiyonu
def create_signature(params, secret):
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{key}={value}" for key, value in sorted_params)
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# ✅ Bybit Gerçek API Üzerinden Bakiye Sorgulama
@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        timestamp = int(time.time() * 1000)
        params = {
            "api_key": api_key,
            "timestamp": timestamp
        }
        params["sign"] = create_signature(params, api_secret)
        
        response = requests.get(f"{BYBIT_API_URL}/v5/account/wallet-balance", params=params)  # Yeni v5 endpoint!
        
        print("Bybit API Yanıtı:", response.text)  # Loglara yaz
        
        data = response.json()  # JSON olarak parse etmeye çalış
        
        if "result" in data:
            usdt_balance = data["result"]["list"][0]["coin"][0]["availableToWithdraw"]
            btc_balance = data["result"]["list"][0]["coin"][1]["availableToWithdraw"]
        else:
            return jsonify({"error": "Bybit API beklenen formatta yanıt vermedi.", "response": data})
        
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
        response = requests.get(f"{BYBIT_API_URL}/v2/public/tickers")
        data = response.json()

        print("Bybit'ten Gelen Fiyat Verisi:", data)  # Loglara yaz
        
        for ticker in data.get("result", []):
            if ticker["symbol"] == "BTCUSDT":
                return jsonify({"BTC/USDT Price": ticker["last_price"]})

        return jsonify({"error": "BTC/USDT fiyatı bulunamadı.", "response": data})
    
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Piyasa Fiyatından BTC Al (Gerçek Hesap)
@app.route('/buy', methods=['POST'])
def buy_order():
    try:
        data = request.json
        amount = float(data.get("amount", 0.001))  # Varsayılan 0.001 BTC
        timestamp = int(time.time() * 1000)

        params = {
            "api_key": api_key,
            "symbol": "BTCUSDT",
            "side": "Buy",
            "order_type": "Market",
            "qty": amount,
            "time_in_force": "GTC",
            "timestamp": timestamp
        }
        params["sign"] = create_signature(params, api_secret)
        
        response = requests.post(f"{BYBIT_API_URL}/v2/private/order/create", params=params)
        data = response.json()

        print("BTC Alım Yanıtı:", data)  # Loglara yaz
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Piyasa Fiyatından BTC Sat (Gerçek Hesap)
@app.route('/sell', methods=['POST'])
def sell_order():
    try:
        data = request.json
        amount = float(data.get("amount", 0.001))  # Varsayılan 0.001 BTC
        timestamp = int(time.time() * 1000)

        params = {
            "api_key": api_key,
            "symbol": "BTCUSDT",
            "side": "Sell",
            "order_type": "Market",
            "qty": amount,
            "time_in_force": "GTC",
            "timestamp": timestamp
        }
        params["sign"] = create_signature(params, api_secret)
        
        response = requests.post(f"{BYBIT_API_URL}/v2/private/order/create", params=params)
        data = response.json()

        print("BTC Satış Yanıtı:", data)  # Loglara yaz
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ API'nin Çalıştığını Kontrol Etmek İçin Ana Sayfa
@app.route("/")
def home():
    return "✅ Bybit Gerçek API bağlantısı aktif! BTC/USDT işlemleri için hazır."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
