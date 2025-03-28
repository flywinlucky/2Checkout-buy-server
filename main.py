from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)

# Permite accesul din frontend
CORS(app, resources={r"/*": {"origins": "https://gifthouse.pro"}})

# Configurare loguri
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configurare 2Checkout
API_KEY = "78F49C72-A686-4BC6-BD59-90937CDB8322"
SELLER_ID = "255465911997"
API_URL = "https://api.2checkout.com/rest/6.0/orders/"  # API-ul corect pentru comenzi

@app.route('/')
def home():
    return """
    <html>
        <body>
            <h1>Project is live 🟢</h1>
            <p>Welcome to the 2Checkout payment processing demo.</p>
        </body>
    </html>
    """

@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        data = request.get_json()
        logger.info(f"Request received: {data}")

        token = data.get('token')
        name = data.get('name')
        email = data.get('email')
        game_code = data.get('gameCode')  # Codul jocului selectat

        if not token or not name or not email or not game_code:
            logger.warning("Missing required fields in the request.")
            return jsonify({"error": "Missing required fields"}), 400

        headers = {
            "X-Avangate-Authentication": f"code='{SELLER_ID}' date='{request.headers.get('Date', '')}' key='{API_KEY}'",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "sellerId": SELLER_ID,
            "currency": "USD",
            "CustomerDetails": {
                "Email": email,
                "Name": name
            },
            "Items": [{
                "Code": game_code,  # Codul produsului selectat de utilizator
                "Quantity": 1,
                "Price": {
                    "Amount": 20.00,
                    "Type": "CUSTOM"
                }
            }],
            "PaymentDetails": {
                "Type": "CC",
                "Currency": "USD",
                "PaymentMethod": {
                    "CardNumberToken": token,
                    "Vendor3DSReturnURL": "https://gifthouse.pro/success",
                    "Vendor3DSCancelURL": "https://gifthouse.pro/cancel"
                }
            }
        }

        logger.info("Sending request to 2Checkout API.")
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 201:
            logger.info(f"Payment processed successfully: {response.json()}")
            return jsonify({"status": "success", "message": "Payment processed successfully"}), 200
        else:
            logger.error(f"Payment failed: {response.text}")
            return jsonify({"error": "Payment failed", "details": response.text}), 500

    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
