import os
import pandas as pd
from transformers import Trainer, TrainingArguments
from datasets import Dataset
from .services import get_tokenizer, get_model
import random

# Projekt-Basisverzeichnis
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Verzeichnisse
SPAM_MODEL_DIR = os.path.join(BASE_DIR, 'meldung/spam_model')
UPDATE_FILE = os.path.join(SPAM_MODEL_DIR, 'update.csv')
TRAINING_DATA_FILE = os.path.join(SPAM_MODEL_DIR, 'training_data.csv')


# Funktion zum Tokenisieren
def tokenize_function(examples, tokenizer):
    return tokenizer(examples['text'], padding='max_length', truncation=True)


def main():
    # Prüfen, ob die Update-Datei vorhanden ist
    if not os.path.exists(UPDATE_FILE):
        print(f"Keine Update-Datei gefunden: {UPDATE_FILE}")
        return

    # Update-Daten laden
    print("Lade Update-Daten...")
    update_data = pd.read_csv(UPDATE_FILE)
    if 'text' not in update_data.columns or 'label' not in update_data.columns:
        print("Update-Datei hat nicht die erwarteten Spalten: 'text', 'label'")
        return

    # Prüfen, ob die Basis-Trainingsdaten vorhanden sind
    if not os.path.exists(TRAINING_DATA_FILE):
        print(f"Basis-Trainingsdatei nicht gefunden: {TRAINING_DATA_FILE}")
        return

    print("Lade Basis-Trainingsdaten...")
    training_data = pd.read_csv(TRAINING_DATA_FILE)
    if 'text' not in training_data.columns or 'label' not in training_data.columns:
        print("Trainingsdaten-Datei hat nicht die erwarteten Spalten: 'text', 'label'")
        return

    # Zufällige Auswahl aus den generierten Daten (z. B. 10–20%)
    sample_size = max(1, int(len(training_data) * 0.1))  # Mindestens 1 Datensatz
    sampled_training_data = training_data.sample(n=sample_size, random_state=42)

    # Kombinieren der Daten (echte Daten priorisieren)
    print("Kombiniere Daten für das Training...")
    combined_data = pd.concat(
        [update_data] * 5 + [sampled_training_data],  # Echte Daten mehrfach priorisieren
        ignore_index=True
    )

    # Dataset erstellen
    dataset = Dataset.from_pandas(combined_data)

    # Modelle und Tokenizer laden
    print("Lade Modell und Tokenizer...")
    tokenizer = get_tokenizer()
    model = get_model()

    # Daten tokenisieren
    print("Tokenisiere Daten...")
    tokenized_data = dataset.map(lambda x: tokenize_function(x, tokenizer), batched=True)

    # Trainingsargumente definieren
    training_args = TrainingArguments(
        output_dir=SPAM_MODEL_DIR,  # Modell wird im gleichen Ordner gespeichert
        evaluation_strategy="no",
        learning_rate=1e-5,  # Niedrige Lernrate, um das Modell vorsichtig zu aktualisieren
        per_device_train_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="epoch"
    )

    # Trainer initialisieren
    print("Initialisiere Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_data
    )

    # Modell weiter trainieren
    print("Starte Training...")
    trainer.train()

    # Modell speichern
    print("Speichere aktualisiertes Modell...")
    model.save_pretrained(SPAM_MODEL_DIR)
    tokenizer.save_pretrained(SPAM_MODEL_DIR)

    # Echte Daten an die Trainingsdatei anhängen
    print("Füge echte Daten zur Basisdatei hinzu...")
    training_data = pd.concat([training_data, update_data], ignore_index=True)
    training_data.to_csv(TRAINING_DATA_FILE, index=False)

    # Update-Datei löschen
    print("Lösche Update-Datei...")
    os.remove(UPDATE_FILE)

    print("Modell-Update abgeschlossen.")


if __name__ == "__main__":
    main()
