# Article Named-Entity Recognition (NER) Service

Layanan berbasis API dan antarmuka web interaktif untuk mengidentifikasi dan mengekstrak entitas bernama (*Named Entities*) seperti Nama Orang (`PERSON`), Perusahaan/Organisasi (`ORG`), Lokasi Geopolitik (`GPE`), Tempat Fisik (`LOC`), Tanggal/Waktu (`DATE`), dan Acara Khusus (`EVENT`) dari judul dan isi artikel berita online.

---

## 📌 Arsitektur & Pemilihan Model

```text
+-----------------------------------------------------------------------+
|                     BROWSER PANEL (src/static/index.html)             |
|  - Form Input: Title & Body Artikel + Tombol Contoh Otomatis          |
|  - Validasi Input Sisi Klien & Indikator Status Loading               |
|  - Tampilan Hasil: Inline Entity Highlighting + Tabel Detail Offset   |
+-----------------------------------+-----------------------------------+
                                    |
                                    | HTTP POST /extract-entities
                                    | Content-Type: application/json
                                    v
+-----------------------------------------------------------------------+
|                     BACKEND API (src/app.py & src/service/)           |
|  - Validasi Kontrak Pydantic (StrictStr, Non-Empty, Max 10.000 char)  |
|  - Penanganan Error Deterministik (HTTP 400 Bad Request)              |
|  - Penggabungan Teks Aman: "{title}. {body}"                          |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|              PIPELINE NER TERLATIH (src/model_ner/ & src/pipeline/)   |
|  1. Statistical NER (Fine-Tuned en_core_web_sm, Seed=42, LR=2e-5)     |
|  2. Custom Component (@Language.component "domain_ner_refiner")       |
|  3. Resolusi Span Terpanjang (spacy.util.filter_spans) & Noise Filter |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                     JSON RESPONSE (HTTP 200 OK)                       |
|  - entities: [{text, label, start, end}, ...]                         |
|  - meta: {entity_count, model}                                        |
+-----------------------------------------------------------------------+
```

- **Backend & API Framework:** FastAPI dengan Uvicorn ASGI Server.
- **NLP Pipeline:** spaCy dengan model pretrained `en_core_web_sm` yang di-*fine-tune* menggunakan dataset artikel berita lokal serta dilengkapi komponen pasca-pemrosesan domain kustom (`@Language.component("domain_ner_refiner")`) dan resolusi tumpang-tindih `spacy.util.filter_spans`.
- **Penggabungan Teks (Title + Body):** Input `title` dan `body` digabungkan secara aman (`Title + ". " + Body`) sebelum diekstraksi untuk menjaga konteks entitas pada bagian awal berita tanpa kehilangan informasi batas karakter (*offset* berbasis nol yang konsisten).
- **Alasan Pemilihan Model (Model Choice):** spaCy (`en_core_web_sm` v3.8.0) menawarkan kecepatan inferensi yang tinggi secara lokal tanpa memerlukan GPU khusus, pemrosesan memori yang ringan, skema label OntoNotes 5 yang mencakup 6 target utama (`PERSON`, `ORG`, `GPE`, `LOC`, `DATE`, `EVENT`), serta mekanisme pembaruan pipeline NER (*custom NER fine-tuning*) yang stabil dan deterministik.

---

## 🛠️ Struktur Repositori

### Struktur Direktori Proyek
```text
project/
├── README.md                         # Dokumentasi utama, laporan evaluasi, & jawaban studi kasus
├── requirements.txt                  # Daftar versi dependensi Python yang terkunci
├── .gitignore                        # Filter file cache, venv, .env, & dataset CSV mentah
├── src/
│   ├── __init__.py
│   ├── app.py                        # Endpoint FastAPI (POST /extract-entities & GET /)
│   ├── pipeline/                     
│   │   ├── __init__.py
│   │   ├── config.py                 # Skema 6 label target, SEED=42, kamus domain, & pola noise
│   │   ├── data_loader.py            # Filter CSV ';', profiling, & GroupShuffleSplit (seed=42)
│   │   ├── annotator.py              # Pembuatan anotasi span-level & resolusi filter_spans
│   │   ├── trainer.py                # Fine-tuning spaCy & komponen domain_ner_refiner
│   │   └── evaluator.py              # Evaluasi Exact-Span (Precision, Recall, F1) & Error Analysis
│   ├── service/                      # Modul Integrasi Layanan Web
│   │   ├── __init__.py
│   │   ├── schemas.py                # Skema validasi input/output Pydantic
│   │   └── extractor.py              # Pemuat artefak model_ner & eksekusi inferensi deterministik
│   ├── model_ner/                    # Artefak model spaCy hasil pelatihan & adaptasi
│   └── static/
│       └── index.html                # Antarmuka web pengguna
├── tests/
│   ├── __init__.py
│   └── test_api.py                   # 8 kasus uji otomatis
├── data/
│   └── evaluation_examples.json      # Set evaluasi berlabel
└── screenshots/                      # Dokumentasi tangkapan layar aplikasi
```

---

## ⚙️ Panduan Instalasi & Cara Menjalankan

### 1. Prasyarat & Virtual Environment
Pastikan **Python versi 3.12 atau setelahnya** sudah terinstal (disarankan menggunakan rentang versi tersebut agar paket *pre-built binary wheels* `spacy` dan `numpy` terinstal lancar tanpa kendala kompilasi C++). Buat dan aktifkan *virtual environment*:

```bash
# Untuk Windows (CMD / PowerShell)
python -m venv .venv
.venv\Scripts\activate

# Untuk Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
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

Setelah server berjalan, akses layanan melalui browser di:
- **Panel Web Interaktif:** `http://127.0.0.1:8000` (atau `http://localhost:8000`)

### 4. Menjalankan Pengujian Otomatis

```bash
pytest -v
```

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
  "body": "KUALA LUMPUR, Oct 7 — Bursa Malaysia opened lower on Wednesday, October 7, 2026, as Maybank, CIMB, MR D.I.Y., and Petronas Gas traded actively in Malaysia."
}
```

### Sample Response JSON (`HTTP 200 OK`)
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
      "text": "Bursa Malaysia",
      "label": "ORG",
      "start": 67,
      "end": 81
    },
    {
      "text": "Wednesday, October 7, 2026",
      "label": "DATE",
      "start": 98,
      "end": 124
    },
    {
      "text": "Maybank",
      "label": "ORG",
      "start": 129,
      "end": 136
    },
    {
      "text": "CIMB",
      "label": "ORG",
      "start": 138,
      "end": 142
    },
    {
      "text": "MR D.I.Y.",
      "label": "ORG",
      "start": 144,
      "end": 153
    },
    {
      "text": "Petronas Gas",
      "label": "ORG",
      "start": 159,
      "end": 171
    },
    {
      "text": "Malaysia",
      "label": "GPE",
      "start": 191,
      "end": 199
    }
  ],
  "meta": {
    "entity_count": 10,
    "model": "custom-spacy-ner-v1 (fine-tuned + domain-adapted)"
  }
}
```

### Sample Error Response JSON (`HTTP 400 Bad Request`)
Jika `title` dan `body` sama-sama kosong, JSON cacat (*malformed*), tipe data bukan string, atau panjang gabungan melebihi batas maksimum `10.000` karakter:
```json
{
  "detail": "Judul (title) dan isi artikel (body) tidak boleh sama-sama kosong."
}
```

---

## 🗂️ Profiling Data, Provenance, & Statistik Dataset (`SEED = 42`)

### 1. Hasil Profiling CSV Mentah (`use_cases/pnm_study_case/sample/`)
- **Jumlah File CSV Dimuat:** 8 file CSV (pemisah titik koma `;` dengan penjagaan tanda kutip `"` yang aman).
- **Total Baris Dimuat:** `1.291` baris artikel.
- **Baris Duplikat (`original_id`):** `445` baris duplikat ditemukan dan dihapus sebelum pembagian data (menyisakan `846` artikel unik bersih).
- **Judul (`title`) atau Isi (`body`) Kosong:** `0` baris.
- **Distribusi Bahasa (`language`):** Inggris (`'en`: `1.059`), Melayu (`'ms`: `178`), Mandarin (`'zh`: `37`), Indonesia (`'id`: `15`), Vietnam (`'vi`: `1`), dan Spanyol (`'es`: `1`).
- **Pemeriksaan Provenance Kolom `entities` Bawaan CSV:** Seluruh `1.291` baris pada kolom `entities` bawaan CSV tidak memiliki anotasi *span* (`start`/`end`) yang valid untuk teks gabungan `title + body` (`0/1.291` terisi). Sesuai pedoman studi kasus, kolom tersebut tidak dijadikan *ground truth* langsung; anotasi tingkat *span* dikurasi ulang dengan tetap menyimpan `original_id`, `source_file`, dan `source_row_number`.

### 2. Pembagian Data & Ketidakseimbangan Kelas (*Class Imbalance*)
Dataset dibagi berdasarkan identitas artikel (`original_id`) menggunakan `GroupShuffleSplit` (`SEED = 42`) dengan proporsi **70% Train (592 artikel)**, **15% Validation (127 artikel)**, dan **15% Held-Out Test Set (127 artikel)** tanpa tumpang-tindih (`0 overlap`).

| Kategori Label | Train Set (592 Dokumen, 13 Tanpa Entitas) | Validation Set (127 Dokumen, 3 Tanpa Entitas) | Held-Out Test Set (127 Dokumen, 3 Tanpa Entitas) |
| :--- | :---: | :---: | :---: |
| **ORG** | 5.637 span (40,4%) | 1.232 span (40,3%) | 1.108 span (39,7%) |
| **PERSON** | 4.165 span (29,8%) | 906 span (29,6%) | 785 span (28,2%) |
| **GPE** | 2.375 span (17,0%) | 531 span (17,4%) | 468 span (16,8%) |
| **DATE** | 1.604 span (11,5%) | 365 span (11,9%) | 394 span (14,1%) |
| **LOC** | 122 span (0,9%) | 18 span (0,6%) | 21 span (0,8%) |
| **EVENT** | 54 span (0,4%) | 8 span (0,3%) | 12 span (0,4%) |
| **TOTAL SPAN** | **13.957 span (100%)** | **3.060 span (100%)** | **2.788 span (100%)** |

---

## 📊 Hasil Evaluasi Model

Evaluasi dilakukan menggunakan aturan **Exact-Span and Entity-Type Matching** (*start offset*, *end offset*, dan *label* harus cocok sempurna dengan anotasi referensi).
- **Pengaturan Pelatihan Model:** `Random Seed = 42`, `Epochs = 4` (Checkpoint terbaik dipilih melalui Validation Set pada Epoch 1), `Batch Size = 32`, `Dropout = 0.10`, `Learning Rate = 2e-5`, dan `Durasi Pelatihan = 38,86 detik`.

### 1. Ringkasan Perbandingan (Baseline vs Trained Model)
- **Dataset Splitting:** 70% Train (592 artikel), 15% Validation (127 artikel), 15% Held-Out Test Set (127 artikel) yang dibagi berdasarkan `original_id`.

| Dataset Split | Model | Precision | Recall | F1-Score | Selisih F1 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Validation Set** | Baseline (`en_core_web_sm`) | 0.8858 | 0.9356 | 0.9100 | - |
| **Validation Set** | **Trained Model (Epoch 1 Best)** | **0.9671** | **0.9592** | **0.9631** | **+0.0531 (+5,31%)** |
| **Held-Out Test Set** | Baseline (`en_core_web_sm`) | 0.9012 | 0.9362 | 0.9184 | - |
| **Held-Out Test Set** | **Trained Model (Final)** | **0.9712** | **0.9674** | **0.9693** | **+0.0509 (+5,09%)** |

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

1. **Pemotongan Batas Span pada Organisasi Turunan (`False Negative` & `False Positive`):**
   * **Kasus:** Pada artikel ID `'efac7cda67592d3f0dd1170e7a2d3429bab4f50bc844fd2e33a2017429ba0e72`, entitas referensi `"Maybank Foundation"` (`ORG`) terpotong dan hanya terdeteksi sebagai `"Maybank"` (`ORG`).
   * **Penyebab:** Aturan pembersihan frasa judul membatasi penggabungan kata setelah kata kunci utama `"Maybank"` untuk mencegah masuknya seluruh kalimat judul sebagai satu entitas. Dalam metrik *exact-span*, perbedaan batas akhir karakter ini dihitung sebagai 1 *False Negative* (`Maybank Foundation`) dan 1 *False Positive* (`Maybank`).
2. **Kata Umum Berhuruf Kapital pada Tajuk Acara (`False Positive`):**
   * **Kasus:** Pada artikel ID `'efac7cda67592d3f0dd1170e7a2d3429bab4f50bc844fd2e33a2017429ba0e72`, kata `"Workshop"` diprediksi sebagai `ORG`.
   * **Penyebab:** Model statistik mengandalkan fitur kapitalisasi (*Title Case*) dan posisi kata setelah nama institusi, sehingga kata benda umum yang diawali huruf kapital di dalam tajuk kegiatan keliru diklasifikasikan sebagai bagian dari nama organisasi.
3. **Keterbatasan Tokenisasi pada Artikel Non-Inggris (`False Negative` / Boundary Error):**
   * **Kasus:** Pada artikel berbahasa Mandarin (`'zh`) dan sebagian artikel berbahasa Melayu (`'ms`), beberapa sebutan organisasi lokal atau terjemahan tidak terdeteksi secara utuh.
   * **Penyebab:** Model dasar `en_core_web_sm` dilatih menggunakan aturan tokenisasi dan *word embeddings* bahasa Inggris, sehingga teks Mandarin yang tidak menggunakan spasi antar-kata serta struktur preposisi bahasa Melayu tidak selalu terpetakan dengan sempurna.

---

## 🔒 Pernyataan Independensi Data Uji

> **Deklarasi Metodologi:**
> *Seluruh data pada Held-Out Test Set (127 artikel) dipisahkan sejak awal berdasarkan `original_id` menggunakan `SEED = 42` dan dijaga tetap utuh (untouched) hingga tahap evaluasi akhir. Contoh-contoh di dalam Test Set sama sekali tidak digunakan untuk melatih bobot model, menyusun daftar kamus domain, maupun memilih hyperparameter dan kriteria penghentian (stopping criteria).*

---

## 🧪 Automated Testing

Jalankan rangkaian pengujian otomatis menggunakan `pytest`:

```bash
pytest tests/ -v
```

Pengujian mencakup 8 skenario yang dapat direproduksi (*reproducible test cases*):
- **Test 1:** Pengujian input artikel normal (*Title* & *Body* valid).
- **Test 2:** Pengujian validasi input kosong pada *Title* dan *Body* (`HTTP 400 Bad Request`).
- **Test 3:** Pengujian nama entitas yang mengandung tanda baca kompleks (contoh: `MR D.I.Y.`).
- **Test 4:** Pengujian entitas yang muncul berulang kali (`Maybank` muncul beberapa kali dengan offset berbeda).
- **Test 5:** Pengujian penyaringan angka/mata uang (`RM250`) dan pendeteksian tanggal (`DATE`).
- **Test 6:** Pengujian karakter *non-ASCII* dan simbol internasional (*em-dash*).
- **Test 7:** Pengujian penolakan teks yang melebihi batas panjang maksimum `10.000` karakter (`HTTP 400 Bad Request`).
- **Test 8:** Pengujian penolakan JSON cacat (*malformed JSON*) serta pembuktian determinisme output.

---

## ⚖️ Pertimbangan Etika & Keterbatasan

- **Keterbatasan Sistem:**
  1. **Dominasi Bahasa Inggris:** Akurasi tertinggi dicapai pada teks berbahasa Inggris (`en`), sedangkan teks berbahasa Mandarin (`zh`) tanpa spasi antar-kata dan sebagian struktur kalimat bahasa Melayu/Indonesia (`ms`/`id`) memiliki tingkat kesalahan batas *span* yang lebih tinggi.
  2. **Sensitivitas Kapitalisasi (*Casing*):** Karena menggunakan arsitektur kompak (`en_core_web_sm`), performa deteksi pada teks yang diketik seluruhnya dengan huruf kecil (*all lowercase*) akan menurun dibanding teks dengan kapitalisasi standar.
  3. **Tidak Melakukan Disambiguasi Lintas Entitas (*Entity Linking*):** Sistem mengekstraksi setiap kemunculan teks apa adanya beserta offset karakternya, namun belum mengelompokkan alias yang merujuk pada entitas yang sama (misalnya `"Maybank"` dan `"Malayan Banking Bhd"`).
- **Penggunaan Bertanggung Jawab & Privasi:**
  1. **Perlindungan Data Pribadi (PII):** Ekstraksi otomatis entitas `PERSON` dan lokasi (`GPE`/`LOC`) dari artikel berita hanya ditujukan untuk keperluan pemantauan media dan tidak boleh disalahgunakan untuk pelacakan atau pemrofilan individu tanpa izin.
  2. **Kepatuhan Hak Cipta (*Copyright*):** Artikel berita memiliki hak cipta milik penerbit aslinya (`source_name`). Oleh karena itu, repositori ini tidak menyimpan atau mendistribusikan ulang salinan penuh dataset CSV mentah.
  3. **Verifikasi Manusia (*Human-in-the-Loop*):** Mengingat sifat prediktif model NLP yang tetap memiliki risiko *False Positive* dan *False Negative*, hasil ekstraksi layanan ini tidak boleh dijadikan dasar tunggal dalam pengambilan keputusan hukum, finansial, atau reputasi secara otomatis tanpa tinjauan manusia.

---

## 💡 Jawaban 8 Pertanyaan Studi Kasus

### 1. Apa yang membuat sebuah span teks menjadi named entity dalam masalah ini?
Sebuah *span* teks dikategorikan sebagai *named entity* apabila merujuk pada objek dunia nyata yang spesifik dan unik dalam konteks pemantauan berita yang termasuk ke dalam 6 kategori target: `PERSON` (tokoh/individu), `ORG` (perusahaan/institusi seperti *Maybank*, *Bursa Malaysia*, *CIMB*), `GPE` (negara/kota seperti *Malaysia*, *Kuala Lumpur*), `LOC` (lokasi geografis non-politik seperti *Middle East*), `DATE` (tanggal/waktu spesifik), dan `EVENT` (peristiwa/hari raya seperti *Deepavali Day*). Kata benda umum, angka indeks murni, dan nominal mata uang (`RM250`) bukan merupakan target *named entity*.

### 2. Mengapa judul dan isi harus digabungkan sebelum dianalisis? Informasi apa yang mungkin hilang jika keduanya diproses secara terpisah?
Judul (`title`) dan isi (`body`) digabungkan (`"{title}. {body}"`) untuk menjaga konteks semantik lintas kalimat serta menghasilkan indeks offset karakter (`start` dan `end`) berbasis nol yang tunggal dan konsisten. Jika diproses terpisah, offset pada `body` akan mulai dari `0` kembali (bertabrakan dengan offset `title`), dan judul berita yang singkat serta berformat *Title Case* penuh akan kehilangan konteks kalimat penjelas dari `body`.

### 3. Label apa saja yang didukung oleh model yang dipilih, dan bagaimana label tersebut dipetakan ke kategori yang ditampilkan kepada pengguna?
Model dasar `en_core_web_sm` mendukung 18 label OntoNotes 5, yang kemudian disaring dan dipetakan ke 6 kategori yang ditampilkan kepada pengguna (`PERSON`, `ORG`, `GPE`, `LOC`, `DATE`, `EVENT`), dilengkapi kalibrasi domain untuk memetakan perusahaan lokal Malaysia (seperti *Petronas Gas* dan *Top Glove*) secara akurat ke label `ORG`. Label di luar target (seperti `MONEY`, `CARDINAL`, `PRODUCT`, `NORP`) diabaikan.

### 4. Bagaimana tokenisasi, tanda baca, kapitalisasi, atau bahasa memengaruhi hasil?
Bahasa non-Inggris seperti Mandarin (`zh`) tidak memiliki spasi antar-kata sehingga menyulitkan *tokenizer* bahasa Inggris dalam menentukan batas *span*. Tanda baca pada singkatan (seperti `MR D.I.Y.`) berisiko memotong *span* jika tidak ditangani secara utuh, sementara penulisan huruf kapital (*ALL CAPS* atau *Title Case*) sangat memengaruhi deteksi *proper noun* pada model statistik.

### 5. Apa perbedaan antara teks, label, dan offset karakter sebuah entitas?
- **`text`:** Potongan *string* literal persis sebagaimana tertulis di dalam artikel (contoh: `"Maybank"`).
- **`label`:** Kategori klasifikasi semantik dari entitas tersebut (contoh: `"ORG"`).
- **`start` dan `end` (Offset Karakter):** Indeks karakter awal (*zero-based*, inklusif) dan indeks karakter akhir (*eksklusif*) pada teks gabungan yang dianalisis (`combined_text[start:end] == text`).

### 6. Apa yang terjadi ketika entitas yang sama muncul beberapa kali dengan ejaan atau kapitalisasi yang berbeda?
Sistem mengevaluasi setiap kemunculan (*mention*) secara independen dan mengembalikan masing-masing kemunculan sebagai entitas terpisah di dalam daftar `entities` lengkap dengan teks asli serta offset `start` dan `end` pada posisinya masing-masing.

### 7. Kesalahan mana yang paling penting bagi pengguna pemantau berita, dan bagaimana sistem dapat ditingkatkan?
Bagi tim pemantau berita, **False Negative** pada entitas utama (`ORG`, `PERSON`, `GPE`) adalah kesalahan paling kritis karena menyebabkan berita penting tentang klien atau kompetitor terlewat (*missed alert*). Sistem dapat ditingkatkan dengan mengadopsi model Transformer multibahasa (seperti *XLM-RoBERTa* atau *Malaya-BERT*) serta menambahkan tahap normalisasi entitas (*Entity Linking*).

### 8. Kekhawatiran privasi, hak cipta, bias, atau penggunaan yang bertanggung jawab apa saja yang berlaku pada pemrosesan teks artikel?
Meliputi perlindungan privasi data pribadi (PII) atas ekstraksi nama individu (`PERSON`), kepatuhan hak cipta penerbit berita dengan tidak mendistribusikan ulang salinan artikel mentah, kesadaran terhadap bias bahasa/geografis dari model berbahasa Inggris, serta penerapan prinsip *human-in-the-loop* agar output sistem tidak dijadikan penentu keputusan kritis tanpa verifikasi manusia.
