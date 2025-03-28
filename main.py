from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Configurare 2Checkout
API_KEY = "YOUR_2CHECKOUT_API_KEY"  # Înlocuiește cu cheia ta API reală
SELLER_ID = "255465911997"
API_URL = "https://api.2checkout.com/rest/6.0/sales/"

# Endpoint pentru procesarea plății
@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        data = request.get_json()
        token = data.get('token')
        name = data.get('name')
        email = data.get('email')

        if not token or not name or not email:
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
                "Code": "YZC2TXJIDS",  # Codul produsului tău
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

        print("Trimit cerere către 2Checkout:", json.dumps(payload, indent=2))
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 201:
            print("Plata procesată cu succes:", response.json())
            return jsonify({"status": "success", "message": "Payment processed successfully"}), 200
        else:
            print("Eroare la procesarea plății:", response.text)
            return jsonify({"error": "Payment failed", "details": response.text}), 500

    except Exception as e:
        print("Eroare server:", str(e))
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)