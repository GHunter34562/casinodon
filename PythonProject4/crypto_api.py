import requests
import logging

class CryptoBotAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://pay.crypt.bot/api"

    def create_invoice(self, amount, description="Оплата в боте"):
        headers = {"Crypto-Pay-API-Token": self.token}
        data = {
            "currency_type": "fiat",
            "fiat": "USD",
            "amount": str(amount),
            "description": description,
            "paid_btn_name": "openBot",
            "paid_btn_url": "https://t.me/your_bot",
            "allow_comments": False,
            "allow_anonymous": False
        }
        response = requests.post(f"{self.base_url}/createInvoice", headers=headers, json=data)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data
        logging.error(f"Failed to create invoice: {response.status_code}, {response.text}")
        return None

    def create_check(self, asset, amount, description="Вывод средств"):
        headers = {"Crypto-Pay-API-Token": self.token}
        data = {
            "asset": asset,
            "amount": str(amount),
            "description": description
        }
        response = requests.post(f"{self.base_url}/createCheck", headers=headers, json=data)
        logging.info(f"Create check response: {response.status_code}, {response.text}")
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data
        logging.error(f"Failed to create check: {response.status_code}, {response.text}")
        return None

    def get_invoice(self, invoice_id):
        headers = {"Crypto-Pay-API-Token": self.token}
        response = requests.get(f"{self.base_url}/getInvoices", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                invoices = data["result"]["items"]
                for invoice in invoices:
                    if invoice["invoice_id"] == invoice_id:
                        return {"ok": True, "result": invoice}
        logging.error(f"Failed to get invoice: {response.status_code}, {response.text}")
        return None

    def get_check(self, check_id):
        headers = {"Crypto-Pay-API-Token": self.token}
        response = requests.get(f"{self.base_url}/getChecks", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                checks = data["result"]["items"]
                for check in checks:
                    if check["check_id"] == check_id:
                        return {"ok": True, "result": check}
        logging.error(f"Failed to get check: {response.status_code}, {response.text}")
        return None

    def get_balance(self):
        headers = {"Crypto-Pay-API-Token": self.token}
        response = requests.get(f"{self.base_url}/getBalance", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data
        return None