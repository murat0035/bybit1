from flask import Flask, request, jsonify
import ccxt

app = Flask(__name__)

# ✅ Bybit API Anahtarlarını Buraya Gir (Testnet API Anahtarlarını Kullan!)
api_key = "BYBIT_TESTNET_API_KEY"  # Buraya kendi API keyini gir
api_secret = "BYBIT_TESTNET_SECRET_KEY"  # Buraya kendi Secret Key'ini gir

# ✅ Bybit ile Bağlantıyı Kur
exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {'defaultType': 'spot'},  # SPOT işlemler için
    'urls': {'api': 'https://api-testnet.bybit.com'}  # TESTNET URL
})

@app.route("/")
def home():
    return "✅ Bybit Testnet API bağlantısı aktif! BTC/USDT işlemleri için hazır."

# ✅ Güncellenmiş Bakiyeyi Getir
@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        balance = exchange.fetch_balance()  # Bybit'ten bakiye verisini çek
        
        # 🔹 JSON formatında doğru mu kontrol edelim
        if isinstance(balance, dict):
            print("Bybit'ten Gelen Ham Veri:", balance)  # Loglara yaz
            return jsonify({"raw_balance": balance})  # Tüm JSON'u döndür
        
        else:
            return jsonify({"error": "Bybit API'den beklenmeyen bir veri formatı geldi."})
    
    except Exception as e:
        return jsonify({"error": str(e)})
# ✅ BTC/USDT Anlık Fiyatını Al
@app.route('/price', methods=['GET'])
def get_price():
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        return jsonify({"BTC/USDT Price": ticker['last']})
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Piyasa Fiyatından BTC Al
@app.route('/buy', methods=['POST'])
def buy_order():
    try:
        data = request.json
        amount = float(data.get("amount", 0.001))  # Varsayılan 0.001 BTC

        order = exchange.create_market_buy_order('BTC/USDT', amount)
        return jsonify({
            "status": "success",
            "order": order
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Piyasa Fiyatından BTC Sat
@app.route('/sell', methods=['POST'])
def sell_order():
    try:
        data = request.json
        amount = float(data.get("amount", 0.001))  # Varsayılan 0.001 BTC

        order = exchange.create_market_sell_order('BTC/USDT', amount)
        return jsonify({
            "status": "success",
            "order": order
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
