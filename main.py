from flask import Flask, request, jsonify
from flask_cors import CORS  # Importă CORS
import requests
import json
import logging

app = Flask(__name__)

# Permite CORS pentru domeniul specificat
CORS(app, resources={r"/*": {"origins": "https://gifthouse.pro"}})

# Configurare loguri
logging.basicConfig(level=logging.DEBUG)  # Poți schimba nivelul de logare, cum ar fi INFO, DEBUG, ERROR, etc.
logger = logging.getLogger(__name__)

# Configurare 2Checkout
API_KEY = "78F49C72-A686-4BC6-BD59-90937CDB8322"  # Cheia ta API reală
SELLER_ID = "255465911997"
API_URL = "https://api.2checkout.com/rest/6.0/orders/"  # Endpoint corect pentru crearea comenzilor

# Ruta principală (pentru a afișa mesajul "Project is live")
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

# Endpoint pentru procesarea plății
@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        data = request.get_json()
        logger.info(f"Request received: {data}")  # Logăm datele primite

        token = data.get('token')
        name = data.get('name')
        email = data.get('email')

        if not token or not name or not email:
            logger.warning("Missing required fields in the request.")
            return jsonify({"error": "Missing required fields"}), 400

        # Configurăm cererea către 2Checkout API
        headers = {
            "X-Avangate-Authentication": f"code='{SELLER_ID}' date='{request.headers.get('Date', '')}' key='{API_KEY}'",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Construim payload-ul conform cu `orders/`
        payload = {
            "Currency": "USD",
            "Customer": {
                "FirstName": name.split()[0] if " " in name else name,  # Separă numele în FirstName / LastName
                "LastName": name.split()[1] if " " in name else "N/A",
                "Email": email
            },
            "Items": [
                {
                    "Code": "YZC2TXJIDS",  # ID-ul produsului tău
                    "Quantity": 1
                }
            ],
            "PaymentDetails": {
                "Type": "EES_TOKEN_PAYMENT",
                "Currency": "USD",
                "PaymentMethod": {
                    "EesToken": token
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
