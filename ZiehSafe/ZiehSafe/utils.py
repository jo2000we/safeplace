# utils.py in Django
import requests

def check_if_spam(text):
    response = requests.post("http://127.0.0.1:8000/check_spam/", json={"text": text})
    print(response.status_code)
    if response.status_code == 200:
        result = response.json()
        return result['is_spam']
    else:
        raise ValueError("Fehler bei der Spam-Prüfung")

def anonymize_text(text):
    response = requests.post("http://127.0.0.1:8000/anonymize_text/", json={"text": text})
    if response.status_code == 200:
        result = response.json()
        return result['anonymized_text']
    else:
        raise ValueError("Fehler bei der Anonymisierung")
