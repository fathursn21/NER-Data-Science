# Article Named-Entity Recognition (NER) Service

Layanan berbasis API dan antarmuka web interaktif untuk mengidentifikasi dan mengekstrak entitas bernama (*Named Entities*) seperti Nama Orang (`PERSON`), Perusahaan/Organisasi (`ORG`), Lokasi Geopolitik (`GPE`), Tempat Fisik (`LOC`), Tanggal/Waktu (`DATE`), dan Acara Khusus (`EVENT`) dari judul dan isi artikel berita online.

---

## 📌 Arsitektur & Pemilihan Model

* **Backend & API Framework:** FastAPI dengan Uvicorn ASGI Server.
* **NLP Pipeline:** spaCy dengan model pretrained `en_core_web_sm` yang di-fine-tune menggunakan dataset artikel berita lokal.
* **Penggabungan Teks (Title + Body):** Input `title` dan `body` digabungkan secara aman (`Title + ". " + Body`) sebelum diekstraksi untuk menjaga konteks entitas pada bagian awal berita tanpa kehilangan informasi batas karakter (*offset*).
* **Alasan Pemilihan Model (Model Choice):** spaCy menawarkan kecepatan inferensi yang tinggi, pemrosesan memori yang ringan, serta mekanisme pembaruan pipeline NER (*custom NER fine-tuning*) yang stabil dan efisien.

---

## 🛠️ Struktur Repositori

```text
├── data/
│   └── evaluation_examples.json   
├── src/
│   ├── model_ner/                 
│   ├── pipeline/                  
│   ├── service/                   
│   ├── static/                    
│   ├── __init__.py
│   └── app.py                     
├── tests/
│   ├── __init__.py
│   └── test_api.py                
├── .gitignore
├── README.md
└── requirements.txt
```

---

## ⚙️ Panduan Instalasi & Cara Menjalankan

### 1. Prasyarat & Virtual Environment
Pastikan Python versi 3.12+ sudah terinstal. Buat dan aktifkan *virtual environment*:

```bash
# For Windows (Cmd / PowerShell)
python -m venv .venv
venv\Scripts\activate

# For Linux / macOS
python3 -m venv .venv
source venv/bin/activate
```

### 2. Instalasi Dependensi & Pretrained Model
Masuk ke direktori proyek, lalu jalankan perintah berikut:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Menjalankan Server Application
Jalankan server Uvicorn pada port 8000:

```bash
uvicorn src.app:app --reload --port 8000
```

Setelah server berjalan, akses antarmuka web pada browser di: `http://localhost:8000`

---

## 📑 Dependensi (`requirements.txt`)

Berikut adalah daftar paket dan versi spesifik yang digunakan pada proyek ini:

```text
numpy>=1.26.4
spacy>=3.8.0
fastapi>=0.115.0
uvicorn>=0.30.6
pydantic>=2.9.2
pytest>=8.3.3
httpx>=0.27.2
pandas>=2.2.2
scikit-learn>=1.5.2
```

---

## 🚀 Penggunaan API & Contoh Request / Response

### Endpoint
`POST /extract-entities`

### Sample Request JSON
```json
{
  "title": "Bursa Malaysia Retreats on Banking Pressure",
  "body": "KUALA LUMPUR, Oct 7 – Bursa Malaysia opened lower on Wednesday, October 7, 2026, as Maybank, CIMB, MR D.I.Y., and Petronas Gas traded actively in Malaysia."
}
```

### Sample Response JSON
```json
{
  "entities": [
    {
      "text": "Bursa Malaysia",
      "label": "ORG",
      "start": 0,
      "end": 14
    },
    {
      "text": "KUALA LUMPUR",
      "label": "GPE",
      "start": 45,
      "end": 57
    },
    {
      "text": "Oct 7",
      "label": "DATE",
      "start": 59,
      "end": 64
    },
    {
      "text": "Maybank",
      "label": "ORG",
      "start": 129,
      "end": 136
    }
  ],
  "meta": {
    "entity_count": 4,
    "model": "custom-spacy-ner-v1"
  }
}
```

---

## 📊 Hasil Evaluasi Model

Evaluasi dilakukan menggunakan aturan **Exact-Span Matching** (*start offset*, *end offset*, dan *label* harus cocok sempurna).

### 1. Ringkasan Perbandingan (Baseline vs Trained Model)
* **Dataset Splitting:** 70% Train (592 artikel), 15% Validation (127 artikel), 15% Held-Out Test Set (127 artikel) yang dibagi berdasarkan `original_id`.

| Dataset Split | Model | Precision | Recall | F1-Score | Selisih F1 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Validation Set** | Baseline (`en_core_web_sm`) | ... | ... | ... | ... |
| **Validation Set** | **Trained Model (Epoch 1 Best)** | **...** | **...** | **...** | **...** |
| **Held-Out Test Set** | Baseline (`en_core_web_sm`) | ... | ... | ... | ... |
| **Held-Out Test Set** | **Trained Model (Final)** | **...** | **...** | **...** | **...** |

### 2. Metrik Per Label pada Held-Out Test Set

| Label Entitas | Precision | Recall | F1-Score | Support |
| :---: | :---: | :---: | :---: | :---: |
| **DATE** | 0.9898 | 0.9822 | 0.9860 | 394 |
| **EVENT** | 1.0000 | 1.0000 | 1.0000 | 12 |
| **GPE** | 0.9979 | 0.9957 | 0.9968 | 468 |
| **LOC** | 0.9524 | 0.9524 | 0.9524 | 21 |
| **ORG** | 0.9460 | 0.9495 | 0.9477 | 1108 |
| **PERSON** | 0.9819 | 0.9682 | 0.9750 | 785 |
| **TOTAL** | **0.9712** | **0.9674** | **0.9693** | **2788** |

---

## 🔍 Analisis Kesalahan (Error Analysis)

Berdasarkan evaluasi pada *held-out test set*, diidentifikasi beberapa contoh kesalahan prediksi:

1. **...:**
   * **Kasus:** ....
   * **Penyebab:** ....
2. **...:**
   * **Kasus:** ....
   * **Penyebab:** ....

---

## 🔒 Pernyataan Independensi Data Uji

> **Deklarasi Metodologi:**
> *...*.

---

## 🧪 Automated Testing

Jalankan rangkaian pengujian otomatis menggunakan `pytest`:

```bash
pytest tests/
```

Pengujian mencakup:
* Pengujian input normal (Title & Body valid).
* Pengujian validasi input kosong (HTTP 400 Bad Request).
* Pengujian penanganan teks tanpa entitas.
* Pengujian karakter non-ASCII dan tanda baca kompleks.
* Pengujian batasan panjang input maksimum.

---

## ⚖️ Pertimbangan Etika & Keterbatasan

* **Keterbatasan Sistem:** ....
* **Penggunaan Bertanggung Jawab & Privasi:** ....
