from flask import Flask, request, jsonify
import requests
import time
import hashlib
import hmac

app = Flask(__name__)

# ✅ Bybit Testnet API Bilgilerini Gir
api_key = "BYBIT_TESTNET_API_KEY"  # Bybit Testnet API Key'inizi girin
api_secret = "BYBIT_TESTNET_SECRET_KEY"  # Bybit Testnet Secret Key'inizi girin

# ✅ Bybit Testnet URL
BYBIT_TESTNET_URL = "https://api-testnet.bybit.com"

# ✅ Bybit API İmzalama Fonksiyonu
def create_signature(params, secret):
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{key}={value}" for key, value in sorted_params)
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# ✅ Doğrudan Bybit API'ye İstek Gönderen Yeni Bakiye Fonksiyonu
@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        timestamp = int(time.time() * 1000)
        params = {
            "api_key": api_key,
            "timestamp": timestamp
        }
        params["sign"] = create_signature(params, api_secret)
        
        response = requests.get(f"{BYBIT_TESTNET_URL}/v2/private/wallet/balance", params=params)
        data = response.json()
        
        print("Bybit'ten Gelen Ham Veri:", data)  # Loglara yaz
        
        if "result" in data:
            usdt_balance = data["result"].get("USDT", {}).get("available_balance", 0)
            btc_balance = data["result"].get("BTC", {}).get("available_balance", 0)
        else:
            return jsonify({"error": "Bybit API beklenen formatta yanıt vermedi.", "response": data})
        
        return jsonify({
            "BTC Balance": btc_balance,
            "USDT Balance": usdt_balance
        })
    
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ API'nin Çalıştığını Kontrol Etmek İçin Ana Sayfa
@app.route("/")
def home():
    return "✅ Bybit Testnet API bağlantısı aktif! BTC/USDT işlemleri için hazır."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
