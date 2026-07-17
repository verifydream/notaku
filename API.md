# API Endpoints Documentation

This document lists the core FastAPI endpoints exposed by NotaKu.

## Webhooks

### `POST /webhook/fonnte`

Receives webhook callbacks from Fonnte when a message is sent to the registered WhatsApp number.

- **Request Body (JSON)**:
  - `phone` (str): Sender's WhatsApp number.
  - `message` (str): The text message content.
  - `type` (str): Message type (e.g., `text`).

- **Description**:
  Parses incoming text to execute commands like `"tambah menu"`, `"rekap"`, `"menu"`, `"oke"`, `"batal"`, or otherwise processes the text through GPT-4o-mini to extract a sales transaction.

---

## User Endpoints

### `GET /api/users/{phone}`

Fetches a user by their phone number.

- **Parameters**:
  - `phone` (str): The user's phone number.
- **Response**: `UserOut`
  Returns user details (id, phone, name, warung_name, created_at).

---

### `GET /api/users/{phone}/menu`

Lists all active menu items for a given user.

- **Parameters**:
  - `phone` (str): The user's phone number.
- **Response**: `list[MenuItemOut]`
  Returns an array of active menu items (id, name, price, aliases, active).

---

### `POST /api/users/{phone}/menu`

Adds a new menu item for a given user.

- **Parameters**:
  - `phone` (str): The user's phone number.
- **Request Body**: `MenuItemCreate`
  - `name` (str): Name of the item.
  - `price` (int): Price in Rupiah.
  - `aliases` (list[str]): Alternative names for AI matching.
- **Response**: `MenuItemOut`
  Returns the created menu item.

---

### `GET /api/users/{phone}/transactions`

Lists recent transactions (up to 100) for a given user.

- **Parameters**:
  - `phone` (str): The user's phone number.
- **Response**: `list[TransactionOut]`
  Returns a list of transactions, sorted by `created_at` descending.

---

### `GET /api/users/{phone}/summary`

Generates a daily summary of sales and expenses for today.

- **Parameters**:
  - `phone` (str): The user's phone number.
- **Response**: `DailySummary`
  - `date` (str): Current date.
  - `total_sales` (int): Total sales amount.
  - `total_expenses` (int): Total expenses amount.
  - `profit` (int): Sales minus expenses.
  - `transaction_count` (int): Total number of transactions today.
  - `top_items` (list): Reserved for future usage (currently returns empty list).

---

## System

### `GET /health`

Health check endpoint.

- **Response**:
  ```json
  {
    "status": "ok",
    "service": "notaku"
  }
  ```