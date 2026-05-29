# XMUM Campus Chatbot — Linear Project Plan

## Overview

6 Roles → 4 Batches (Sprints) → ~30 Linear Issues

Setiap anggota tim mendapatkan **role utama** (sesuai rubrik) dan
**file teknis utama** yang menjadi tanggung jawab penuh mereka.
File `Z_Placeholder_` tetap tersedia sebagai referensi — bukan untuk di-copy-paste,
tapi untuk dipahami alurnya lalu ditulis ulang dengan pemahaman sendiri.

---

## 👥 Pemetaan Role → Anggota → File Utama

| # | Role (Rubrik)                       | File Utama yang Dimiliki                                  |
|---|-------------------------------------|-----------------------------------------------------------|
| 1 | **Intent Recognition**              | `chatbot/intent_classifier.py`                            |
| 2 | **Entity Extraction**               | `chatbot/preprocessor.py` *(file baru)*                   |
| 3 | **Response Matching & Retrieval**   | `chatbot/retriever.py`, `database/client.py`, `database/schema.sql` |
| 4 | **Context & Session Management**    | `chatbot/context_manager.py`                              |
| 5 | **Fallback Handling & Response Generation** | `chatbot/responder.py`, `chatbot/bot.py`, `chatbot/main.py` |
| 6 | **NLP & Text Preprocessing**        | `database/seeds/*.json`, `database/seed.py`, keyword normalization |

---

## 🗂️ Dataset: Siapa yang Bertanggung Jawab?

> **Pimpinan Dataset: Role 6 — NLP & Text Preprocessing**

### Mengapa Role 6?
Karena chatbot ini adalah **Pure Retrieval-Based**, kualitas dataset (file `.json` di `database/seeds/`) adalah komponen paling kritis. Bukan modelnya, tapi datanya yang menentukan kecerdasan bot. Role 6 paling memahami:
- Bagaimana kata kunci (`keywords`) harus dinormalisasi agar mudah dicocokkan.
- Format JSON yang benar untuk diproses oleh `seed.py`.
- Konsistensi struktur data di seluruh modul.

### Kontribusi Setiap Anggota ke Dataset:
Meskipun Role 6 yang **memimpin dan mengkurasi**, setiap anggota **wajib berkontribusi konten** dari area modul mereka:

| Siapa | Berkontribusi Konten untuk |
|-------|---------------------------|
| Role 1 (Intent) | Daftar keyword per modul untuk file `intent_classifier.py` |
| Role 2 (Entity) | Daftar sinonim (contoh: "wifi" = "internet" = "network") |
| Role 3 (Retrieval) | Memastikan JSON seed kompatibel dengan query Supabase |
| Role 4 (Context) | Contoh Q&A multi-turn untuk menguji konteks |
| Role 5 (Fallback) | Daftar pertanyaan yang seharusnya trigger fallback |
| Role 6 (NLP Lead) | **Kurasi final, format, review, dan upload ke Supabase** |

---

## 🚀 Batch 0 — Setup & Onboarding *(Semua Anggota, Minggu 1)*

Setiap orang menyelesaikan ini secara **paralel** dan **mandiri**.
Ini adalah *pre-condition* sebelum Batch 1 bisa dimulai.

### Issues Linear (Assigned to Everyone):

```
[SETUP-1] Clone repo & buat virtual environment Python
[SETUP-2] Buat file .env dari .env.example, isi dengan Supabase key tim
[SETUP-3] Install requirements.txt & verifikasi tidak ada error
[SETUP-4] Baca file Z_Placeholder_ milikmu sendiri (30 menit)
[SETUP-5] Baca README.md dari awal sampai akhir
[SETUP-6] Buat akun Supabase (jika belum ada) & join project
```

> ⚠️ **CRITICAL**: Batch 1 tidak boleh dimulai sebelum semua orang selesai SETUP.

---

## 🏗️ Batch 1 — Foundation Layer *(Minggu 1-2)*

Batch ini membangun fondasi database. **Role 3 dan Role 6 adalah yang memimpin.**
Anggota lain boleh mulai riset dan merancang logika modul mereka di atas kertas.

### Role 3 — Response Matching & Retrieval

```
[DB-1] Baca dan pahami Z_Placeholder_schema.sql
[DB-2] Tulis schema.sql dari scratch (tabel knowledge_items + conversation_logs)
[DB-3] Run schema.sql di Supabase SQL Editor & screenshot hasilnya
[DB-4] Baca dan pahami Z_Placeholder_client.py
[DB-5] Implementasi database/client.py (fungsi get_client())
[DB-6] Test koneksi Supabase: python -c "from database.client import get_client; print(get_client())"
```

### Role 6 — NLP & Text Preprocessing (Dataset Lead)

```
[DATA-1] Kumpulkan informasi Module 1 (Admin Directory) dari Student Handbook XMUM
[DATA-2] Kumpulkan informasi Module 2 (Campus Life) dari Student Handbook XMUM  
[DATA-3] Kumpulkan informasi Module 3 (Academic Navigation) dari website resmi XMUM
[DATA-4] Tulis admin_directory.json (min. 8 Q&A pairs, lengkap dengan keywords)
[DATA-5] Tulis campus_life.json (min. 10 Q&A pairs)
[DATA-6] Tulis academic_navigation.json (min. 6 Q&A pairs)
[DATA-7] Baca dan pahami Z_Placeholder_seed.py
[DATA-8] Implementasi database/seed.py
[DATA-9] Test: python -m database.seed → verifikasi data masuk ke Supabase
```

### Anggota Lain (Batch 1 Side Task):
```
[PLAN-1] Role 1: Buat draf dictionary keyword untuk 3 modul (di kertas/Notion)
[PLAN-2] Role 2: Buat draf daftar sinonim kata kunci (wifi=internet, hostel=dorm, dll.)
[PLAN-3] Role 4: Rancang struktur data session (format dict yang akan disimpan)
[PLAN-4] Role 5: Rancang pesan fallback dan format response akhir ke user
```

---

## ⚙️ Batch 2 — Core Logic *(Minggu 2-3)*

Batch ini adalah jantung proyek. Setiap orang **mengerjakan file utama mereka secara paralel**.
Tidak ada ketergantungan langsung antar role di batch ini, kecuali Role 5 yang butuh
output dari Role 1, 2, dan 3.

### Role 1 — Intent Recognition

```
[INTENT-1] Baca Z_Placeholder_intent_classifier.py & pahami alurnya
[INTENT-2] Definisikan dictionary KEYWORD_MAP: {module_name: [list of keywords]}
           Gunakan draf dari PLAN-1 sebagai dasar
[INTENT-3] Implementasi fungsi classify(message: str) -> str
           Logic: lowercase input → cek setiap kata → return module yang cocok → fallback "unknown"
[INTENT-4] Test manual di terminal: 
           python -c "from chatbot.intent_classifier import IntentClassifier; ic = IntentClassifier(); print(ic.classify('where is the library'))"
[INTENT-5] Pastikan test di tests/test_intent_classifier.py lulus (uncomment & run pytest)
```

### Role 2 — Entity Extraction

```
[ENTITY-1] Buat file baru: chatbot/preprocessor.py (tidak ada Z_Placeholder, ini orisinal!)
[ENTITY-2] Implementasi fungsi normalize(text: str) -> str
           (lowercase, strip whitespace, hapus tanda baca)
[ENTITY-3] Implementasi fungsi extract_keywords(text: str) -> list[str]
           (pecah kalimat menjadi kata-kata kunci yang relevan, hilangkan stopwords)
[ENTITY-4] Buat SYNONYM_MAP dari draf PLAN-2:
           {"internet": "wifi", "dorm": "hostel", "borrow": "loan", ...}
[ENTITY-5] Implementasi fungsi expand_synonyms(keywords: list[str]) -> list[str]
[ENTITY-6] Test manual: pastikan "how do i connect to the internet" → ["wifi", "connect", "campus"]
```

### Role 3 — Response Matching & Retrieval

```
[RETRIEVAL-1] Baca Z_Placeholder_retriever.py & pahami strategi ILIKE vs FTS
[RETRIEVAL-2] Implementasi Retriever.search() menggunakan ILIKE matching dulu
               (sederhana: cari di kolom 'keywords' atau 'question')
[RETRIEVAL-3] Test search dengan data yang sudah di-seed:
               python -c "from chatbot.retriever import Retriever; r = Retriever(); print(r.search('campus_life', 'library'))"
[RETRIEVAL-4] (Bonus) Upgrade ke PostgreSQL Full-Text Search jika ILIKE kurang akurat
[RETRIEVAL-5] Uncomment & jalankan tests/test_retriever.py
```

### Role 4 — Context & Session Management

```
[CTX-1] Baca Z_Placeholder_context_manager.py & pahami konsep session
[CTX-2] Implementasi ContextManager.__init__ dengan in-memory dict
[CTX-3] Implementasi add_turn(session_id, role, message)
[CTX-4] Implementasi get_history(session_id) → list[dict]
[CTX-5] Implementasi clear(session_id)
[CTX-6] Pastikan MAX_TURNS dibaca dari .env (gunakan os.getenv)
[CTX-7] Test manual: tambah 3 turn, get history, verifikasi urutan benar
```

### Role 5 — Fallback Handling & Response Generation

```
[RESP-1] Baca Z_Placeholder_responder.py
[RESP-2] Implementasi Responder.format() → pilih result terbaik dari list, return string bersih
[RESP-3] Definisikan FALLBACK_MESSAGE yang ramah dan informatif
[RESP-4] Baca Z_Placeholder_bot.py — ini adalah file integrasi utama!
[RESP-5] Implementasi Bot.__init__ (inisialisasi semua komponen)
[RESP-6] Implementasi Bot.chat(session_id, message) → pipeline lengkap:
         preprocessor → intent_classifier → retriever → responder
[RESP-7] Baca Z_Placeholder_main.py
[RESP-8] Implementasi terminal REPL loop di main.py (gunakan python-dotenv di sini)
[RESP-9] End-to-end test: python -m chatbot.main → coba beberapa pertanyaan nyata
```

---

## 🔗 Batch 3 — Integration & API *(Minggu 3-4)*

Batch ini menggabungkan semua modul ke dalam API layer.
**Role 5 memimpin** karena mereka sudah pegang `bot.py`.
**Role 3 membantu** karena familiar dengan layer database.

```
[API-1]  Role 5: Baca Z_Placeholder_app.py
[API-2]  Role 5: Implementasi api/app.py (FastAPI instance + CORS middleware)
[API-3]  Role 3: Implementasi api/schemas/chat_schema.py (ChatRequest + ChatResponse Pydantic)
[API-4]  Role 3: Implementasi api/routes/health.py (GET /health)
[API-5]  Role 5: Implementasi api/routes/chat.py (POST /chat menggunakan Bot.chat())
[API-6]  Role 5: Mount semua router di app.py
[API-7]  Role 4: Update api/routes/chat.py untuk include session management
[API-8]  ALL:   Integration test — jalankan server & test dengan curl atau Postman:
         curl -X POST http://localhost:8000/chat \
              -H "Content-Type: application/json" \
              -d '{"session_id":"test-1","message":"where is the library?"}'
```

---

## ✅ Batch 4 — Testing & Polish *(Minggu 4)*

```
[TEST-1] Role 1: Lengkapi & jalankan tests/test_intent_classifier.py
[TEST-2] Role 3: Lengkapi & jalankan tests/test_retriever.py
[TEST-3] Role 5: Lengkapi & jalankan tests/test_responder.py
[TEST-4] Role 3: Lengkapi & jalankan tests/test_api.py
[TEST-5] Role 6: Review ulang semua seed data — apakah ada jawaban yang tidak akurat?
[TEST-6] Role 2: Test end-to-end dengan sinonim — apakah "internet" bisa temukan jawaban wifi?
[TEST-7] Role 4: Test multi-turn conversation — apakah konteks terjaga antar pertanyaan?
[TEST-8] Role 5: Test fallback — pastikan pertanyaan out-of-scope dijawab dengan benar
[TEST-9] ALL:   Run pytest untuk semua tests
[DOC-1]  ALL:   Update README.md dengan anggota tim dan informasi final
```

---

## 📊 Ringkasan Beban Kerja per Role

| Role | Batch 0 | Batch 1 | Batch 2 | Batch 3 | Batch 4 | Est. Issues |
|------|---------|---------|---------|---------|---------|-------------|
| Intent Recognition | ✅ | Rancang | 5 issues | - | 1 issue | ~8 |
| Entity Extraction | ✅ | Rancang | 6 issues | - | 1 issue | ~9 |
| Response Matching & Retrieval | ✅ | 6 issues | 5 issues | 2 issues | 1 issue | ~16 |
| Context & Session Management | ✅ | Rancang | 7 issues | 1 issue | 1 issue | ~11 |
| Fallback & Response Generation | ✅ | Rancang | 9 issues | 3 issues | 2 issues | ~16 |
| NLP & Text Preprocessing | ✅ | 9 issues | 6 issues | - | 2 issues | ~19 |

---

## 🗓️ Rekomendasi Timeline Linear (4 Minggu)

| Cycle | Batches | Deadline |
|-------|---------|----------|
| Sprint 1 | Batch 0 + Batch 1 | Akhir Minggu 1 |
| Sprint 2 | Batch 2 (semua role paralel) | Akhir Minggu 3 |
| Sprint 3 | Batch 3 + Batch 4 | Akhir Minggu 4 |

---

## 💡 Tips untuk Linear Setup

1. **Project**: Buat 1 Project bernama `XMUM Campus Chatbot`
2. **Labels**: Buat label per role: `intent`, `entity`, `retrieval`, `context`, `fallback`, `nlp-data`
3. **States**: `Backlog → Todo → In Progress → In Review → Done`
4. **Priority**: Issues di Batch 1 (DB-1 s/d DATA-9) semua set ke **Urgent**
5. **Cycles**: Buat 3 Cycles sesuai tabel timeline di atas
