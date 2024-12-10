from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from flair.models import SequenceTagger


def get_tokenizer():
    return DistilBertTokenizer.from_pretrained('/app/meldung/spam_model/')


def get_model():
    return DistilBertForSequenceClassification.from_pretrained('/app/meldung/spam_model/')


def get_tagger():
    return SequenceTagger.load('/app/meldung/ner_model/preloaded_ner_model.pt')
