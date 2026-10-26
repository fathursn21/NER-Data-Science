import os
import re

# Skema 6 kategori entitas yang didukung sesuai spesifikasi studi kasus
TARGET_LABELS = {"PERSON", "ORG", "GPE", "LOC", "DATE", "EVENT"}

# Seed deterministik untuk pembagian data dan pelatihan
SEED = 42
MAX_TEXT_LENGTH = 10000

# Path direktori
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MODEL_SAVE_DIR = os.path.join(PROJECT_ROOT, "src", "model_ner")

# Kamus kurasi domain berita finansial Malaysia
DOMAIN_ORGS = [
    "Bursa Malaysia", "Malayan Banking Bhd", "Bank Negara Malaysia",
    "Hong Leong Bank", "Press Metal Aluminium", "IHH Healthcare",
    "Petronas Gas", "Top Glove", "Supermax", "Zetrix AI", "MR D.I.Y.",
    "D.I.Y.", "Maybank", "CIMB", "AMMB", "RHB Bank", "Public Bank",
    "Tenaga Nasional", "Telekom Malaysia", "Genting Malaysia", "FTSE",
    "Malaysian Hockey League"
]

DOMAIN_GPES = [
    "KUALA LUMPUR", "Kuala Lumpur", "Putrajaya", "Malaysia",
    "Selangor", "Johor", "Penang", "Sabah", "Sarawak", "Singapore", "Indonesia"
]

NOISE_PATTERNS = re.compile(
    r"^(RM|USD|MYR)?\s*[\d,.]+(\s*(million|billion|trillion|sen|%|points|pts))?$",
    re.IGNORECASE
)
