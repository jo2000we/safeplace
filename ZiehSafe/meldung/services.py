import os
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from flair.models import SequenceTagger

# Projekt-Basisverzeichnis
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_tokenizer():
    return DistilBertTokenizer.from_pretrained(os.path.join(BASE_DIR, 'meldung/spam_model'))

def get_model():
    return DistilBertForSequenceClassification.from_pretrained(os.path.join(BASE_DIR, 'meldung/spam_model'))

def get_tagger():
    return SequenceTagger.load(os.path.join(BASE_DIR, 'meldung/ner_model/preloaded_ner_model.pt'))
