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
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# ✅ MEXC API URL
MEXC_API_URL = "https://api.mexc.com"

# ✅ MEXC API İmzalama Fonksiyonu
def create_signature(params, secret):
    query_string = "&".join(f"{key}={value}" for key, value in sorted(params.items()))
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# ✅ Açık ve Geçmiş Siparişleri (Orders) Sorgula
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        symbol = request.args.get("symbol", "BTCUSDT")  # Varsayılan BTC/USDT
        timestamp = int(time.time() * 1000)

        headers = {"X-MEXC-APIKEY": API_KEY}

        # Açık Emirleri (Open Orders) Sorgula
        open_orders_params = {
            "symbol": symbol,
            "timestamp": timestamp
        }
        open_orders_params["signature"] = create_signature(open_orders_params, API_SECRET)

        open_orders_response = requests.get(f"{MEXC_API_URL}/api/v3/openOrders", headers=headers, params=open_orders_params)
        open_orders_data = open_orders_response.json()

        # Geçmiş Emirleri (All Orders) Sorgula
        all_orders_params = {
            "symbol": symbol,
            "timestamp": timestamp
        }
        all_orders_params["signature"] = create_signature(all_orders_params, API_SECRET)

        all_orders_response = requests.get(f"{MEXC_API_URL}/api/v3/allOrders", headers=headers, params=all_orders_params)
        all_orders_data = all_orders_response.json()

        logging.info(f"Açık Emirler: {open_orders_data}")
        logging.info(f"Geçmiş Emirler: {all_orders_data}")

        return jsonify({
            "symbol": symbol,
            "open_orders": open_orders_data,
            "all_orders": all_orders_data
        })

    except Exception as e:
        logging.error(f"Emir sorgulama hatası: {e}")
        return jsonify({"error": str(e)})

# ✅ API'nin Çalıştığını Kontrol Etmek İçin Ana Sayfa
@app.route("/")
def home():
    return "✅ MEXC API bağlantısı aktif! BTC/USDT işlemleri için hazır."

# ✅ Render.com İçin Gerekli Ayarlar
if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 10000))
    serve(app, host="0.0.0.0", port=port)
