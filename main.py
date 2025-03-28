from flask import Flask, request, jsonify
import requests
import json
import logging

app = Flask(__name__)

# Configurare loguri
logging.basicConfig(level=logging.DEBUG)  # Poți schimba nivelul de logare, cum ar fi INFO, DEBUG, ERROR, etc.
logger = logging.getLogger(__name__)

# Configurare 2Checkout
API_KEY = "78F49C72-A686-4BC6-BD59-90937CDB8322"  # Cheia ta API reală
SELLER_ID = "255465911997"
API_URL = "https://api.2checkout.com/rest/6.0/sales/"

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

        payload = {
            "sellerId": SELLER_ID,
            "currency": "USD",
            "CustomerDetails": {
                "Email": email,
                "Name": name
            },
            "Items": [{
                "Code": "YZC2TXJIDS",  # Codul produsului tău, asigură-te că acest cod există pe 2Checkout
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
                    "Vendor3DSReturnURL": "https://yourdomain.com/success",
                    "Vendor3DSCancelURL": "https://yourdomain.com/cancel"
                }
            }
        }

        logger.info("Sending request to 2Checkout API.")
        response = requests.post(API_URL, headers=headers, json=payload)

        # Logare detaliată pentru debugging
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response text: {response.text}")

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
