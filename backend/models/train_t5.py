"""
Fine-tuning T5-small pour NL2SQL
Version corrigée et optimisée
"""

import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5Tokenizer, T5ForConditionalGeneration
from torch.optim import AdamW
from pathlib import Path
import os

# ====================== CONFIG ======================
MODEL_NAME = "t5-small"
OUTPUT_DIR = Path("nl2sql_t5")
DATA_PATH  = Path("../data/training_data.json")   # ← Important : chemin depuis models/

EPOCHS     = 4
BATCH_SIZE = 4
MAX_INPUT  = 128
MAX_OUTPUT = 256
LR         = 3e-4

# ====================== DATASET ======================
class NL2SQLDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.data = data
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        input_text  = f"translate to SQL: {item['question']}"
        target_text = item['sql']

        inputs = self.tokenizer(
            input_text,
            max_length=MAX_INPUT,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        targets = self.tokenizer(
            target_text,
            max_length=MAX_OUTPUT,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        labels = targets["input_ids"].squeeze()
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            "input_ids":      inputs["input_ids"].squeeze(),
            "attention_mask": inputs["attention_mask"].squeeze(),
            "labels":         labels
        }


# ====================== ENTRAÎNEMENT ======================
def train():
    print("=" * 70)
    print("🚀 FINE-TUNING T5-small pour NL2SQL")
    print("=" * 70)

    # Charger données
    if not DATA_PATH.exists():
        print(f"❌ Fichier non trouvé : {DATA_PATH}")
        print("Vérifie que training_data.json est bien dans le dossier 'data'")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"✅ {len(data)} paires question → SQL chargées")

    # Charger tokenizer et modèle
    print("🔄 Chargement T5-small...")
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

    # Dataset + DataLoader
    dataset = NL2SQLDataset(data, tokenizer)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Optimiseur
    optimizer = AdamW(model.parameters(), lr=LR)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"🖥️  Entraînement sur : {device}")

    # Entraînement
    print(f"\n📚 Début de l'entraînement ({EPOCHS} epochs)...\n")
    model.train()

    for epoch in range(EPOCHS):
        total_loss = 0
        for batch in dataloader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1:2d}/{EPOCHS} | Loss: {avg_loss:.4f}")

    # Sauvegarde
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"\n🎉 Entraînement terminé !")
    print(f"📁 Modèle sauvegardé dans : {OUTPUT_DIR}")

    # Test rapide
    print("\n🧪 Test rapide du modèle :")
    test_questions = [
        "Combien d'employés actifs ?",
        "Salaire moyen des employés",
        "Qui gagne le plus ?",
        "Taux de turnover",
        "Liste des employés en CDI"
    ]

    model.eval()
    for q in test_questions:
        input_text = f"translate to SQL: {q}"
        inputs = tokenizer(input_text, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=256,
                num_beams=4,
                early_stopping=True
            )

        sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\nQ: {q}")
        print(f"SQL: {sql}")

    print("\n✅ Tout est prêt !")


if __name__ == "__main__":
    train()