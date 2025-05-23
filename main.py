import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def charge_credit_card(
    amount: float,
    card_number: str,
    expiration_date: str,
    card_code: str,
    use_sandbox: bool = True,
    billing_address: dict | None = None
) -> None:
    # Use Authorize.Net test or production URL
    url = "https://apitest.authorize.net/xml/v1/request.api" if use_sandbox else "https://api.authorize.net/xml/v1/request.api"

    # ✅ Hardcoded sandbox credentials (replace with your own)
    AUTHORIZE_NET_API_LOGIN_ID = os.getenv("AUTHORIZE_NET_API_LOGIN_ID")
    AUTHORIZE_NET_TRANSACTION_KEY = os.getenv("AUTHORIZE_NET_TRANSACTION_KEY")

    # Transaction payload
    transaction_request = {
        "transactionType": "authCaptureTransaction",
        "amount": amount,
        "payment": {
            "creditCard": {
                "cardNumber": card_number,
                "expirationDate": expiration_date,
                "cardCode": card_code
            }
        }
    }

    if billing_address:
        transaction_request["billTo"] = billing_address

    payload = {
        "createTransactionRequest": {
            "merchantAuthentication": {
                "name": AUTHORIZE_NET_API_LOGIN_ID,
                "transactionKey": AUTHORIZE_NET_TRANSACTION_KEY
            },
            "transactionRequest": transaction_request
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = json.loads(response.content.decode('utf-8-sig'))

        match data.get("messages", {}).get("resultCode"):
            case "Ok":
                transaction = data.get("transactionResponse", {})
                trans_id = transaction.get("transId")
                if trans_id:
                    print(f"✅ Transaction Successful! ID: {trans_id}")
                else:
                    print("⚠️ Transaction processed, but no transaction ID returned.")
            case _:
                error_message = data.get("messages", {}).get("message", [{}])[0].get("text", "Unknown error.")
                print(f"❌ Transaction Failed: {error_message}")

    except requests.RequestException as e:
        print(f"🚨 HTTP Request Error: {e}")
    except Exception as e:
        print(f"🚨 Unexpected Error: {e}")


# 🔧 Main test run
if __name__ == "__main__":
    billing_info = {
        "firstName": "Jane",
        "lastName": "Doe",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "République de Côte d'Ivoire"
    }

    charge_credit_card(
        amount=25.00,
        card_number="4111111111111111",  # Valid sandbox test card
        expiration_date="2025-12",
        card_code="123",
        use_sandbox=True,
        billing_address=billing_info
    )
