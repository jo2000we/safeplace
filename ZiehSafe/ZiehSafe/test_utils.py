# test_utils.py
from utils import check_if_spam, anonymize_text

def main():
    # Testfall für die Spam-Erkennung
    text = "This is a spam message offering free money!"
    is_spam = check_if_spam(text)
    print(f"Spam-Erkennung: '{text}' -> {'Spam' if is_spam else 'Kein Spam'}")

    # Testfall für die Anonymisierung
    text = "John Doe lives in New York."
    anonymized_text = anonymize_text(text)
    print(f"Anonymisierung: '{text}' -> '{anonymized_text}'")

if __name__ == "__main__":
    main()
