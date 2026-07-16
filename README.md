# 📒 NotaKu

> Chat → Nota → Selesai. Catat usaha tanpa buka app.

WhatsApp-native nota digital & pencatatan keuangan untuk warung & UMKM Indonesia.

## Fitur

- **Chat Transaksi** — Kirim pesan: "3 nasi uduk, 1 kopi" → otomatis dicatat
- **Nota PDF** — Nota cantik dikirim ke pelanggan via WhatsApp
- **Rekap Harian** — Ringkasan omset, pengeluaran, profit jam 9 malam
- **Voice Note** — Kirim voice note, AI paham dan catat
- **Dashboard Web** — Grafik transaksi di browser
- **KUR-Ready Report** — Laporan keuangan untuk apply KUR

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python FastAPI + SQLAlchemy |
| Frontend | Next.js 14 + Tailwind + shadcn/ui |
| Database | PostgreSQL |
| WhatsApp | Fonnte API |
| AI | OpenAI GPT-4o-mini |
| PDF | ReportLab |

## Quick Start

### Backend

```bash
cd backend
cp .env.example .env  # edit with your values
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Deploy

- **Frontend:** Vercel (auto-deploy from GitHub)
- **Backend:** Railway / Fly.io

## Environment Variables

See `backend/.env.example` for all required variables.

## License

MIT
