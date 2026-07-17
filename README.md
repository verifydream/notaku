# 📒 NotaKu

WhatsApp-native bookkeeping for Indonesian warungs.

> Chat → Nota → Selesai. Catat usaha tanpa buka app.

## What is NotaKu?

NotaKu is a WhatsApp-native digital bookkeeping and receipt generation tool built for warungs (small shops) and UMKM (Micro, Small, and Medium Enterprises) in Indonesia. Instead of opening a separate app, users can just send a WhatsApp chat to record transactions, generate PDF receipts, and track their daily sales and expenses.

## Core Flow

1. **Chat**: User sends a natural language message (e.g., "3 nasi uduk, 1 kopi").
2. **GPT-4o-mini parse**: AI parses the raw text and matches items to the user's available menu.
3. **Confirm**: User gets a summary message and confirms the transaction.
4. **Save**: Transaction and items are saved to the PostgreSQL database.
5. **PDF nota**: A PDF receipt (nota) is generated using ReportLab/WeasyPrint and sent to the customer/user via WhatsApp.
6. **Daily recap**: A daily summary of sales, expenses, and profit is sent every day at 21:00 WIB.

## Tech Stack

- **Backend**: FastAPI (Python) + SQLAlchemy
- **Frontend**: Next.js 14 (React) + Tailwind CSS + shadcn/ui
- **Database**: PostgreSQL
- **WhatsApp Integration**: Fonnte API
- **AI Parser**: OpenAI (GPT-4o-mini)
- **PDF Generation**: ReportLab / WeasyPrint

## AI Prompt Template

NotaKu relies on OpenAI's `gpt-4o-mini` to parse raw chat messages into structured JSON based on the user's menu. Here is the core prompt used:

```text
Kamu adalah parser transaksi untuk warung Indonesia.
Tugas: ekstrak item dan jumlah dari pesan mentah WhatsApp.

ATURAN:
- Match item ke menu yang tersedia (fuzzy matching, typo tolerant)
- "3 nasduk" → nasi uduk qty 3
- "kopi 2" → kopi qty 2
- "rokok sampoerna" → rokok sampoerna qty 1
- Jika ada harga manual "nasi uduk 8000" → override price
- Return JSON saja, tanpa penjelasan

Menu tersedia:
{menu_json}

Return format:
{{
  "items": [
    {{"name": "nama item asli", "qty": N, "matched_menu_id": "id", "price_override": null}},
    ...
  ]
}}
Jika tidak ada yang match, set matched_menu_id ke null.
```

## Integrations

- **Fonnte (WhatsApp)**: NotaKu utilizes Fonnte to manage incoming webhooks for messages and outgoing messages/media to interact with the users on WhatsApp.
- **ReportLab PDF Generation**: Upon confirming a transaction, ReportLab creates an A6 formatted PDF containing the shop name, transaction details, totals, and a unique identifier. This PDF is then sent directly via WhatsApp.

## Database Schema

The core PostgreSQL database models are:

- **users**: Stores warung owner details.
  - `id`, `phone`, `name`, `warung_name`, `created_at`
- **menu_items**: Predefined items for sale.
  - `id`, `user_id`, `name`, `price`, `aliases`, `active`, `created_at`
- **transactions**: Order or expense record.
  - `id`, `user_id`, `customer_phone`, `total`, `type` (sale/expense), `note`, `created_at`
- **transaction_items**: Line items within a transaction.
  - `id`, `transaction_id`, `menu_item_id`, `quantity`, `unit_price`, `subtotal`

## Environment & Docker

### Environment Variables

See `backend/.env.example` for all required backend variables. The key variables include:

- `DATABASE_URL`: The PostgreSQL connection string.
- `FONNTE_TOKEN`: The API token for Fonnte.
- `OPENAI_API_KEY`: API key for GPT-4o-mini parsing.
- `JWT_SECRET`: Secret key for JWT generation.

For the frontend, configure `NEXT_PUBLIC_API_URL` to point to the FastAPI backend.

### Quick Start (Local)

**Backend:**
```bash
cd backend
cp .env.example .env  # edit with your values
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Docker

You can containerize the application easily:
1. Provide a `Dockerfile` in the backend and frontend directories respectively.
2. Provide a `docker-compose.yml` defining the `postgres` database, the FastAPI backend, and the Next.js frontend services, sharing the appropriate environment variables.