# Tally Integration API

A FastAPI application that creates and fetches ledgers, vouchers, and stock items in TallyPrime via its HTTP XML interface.

## Prerequisites

1. **Python 3.10+** installed
2. **TallyPrime** running with HTTP server enabled:
   - Open TallyPrime
   - Go to `F1 (Help) > Settings > Connectivity > Tally.NET Server`
   - Or: `F12 > Advanced Configuration`
   - Set **Client/Server Configuration** to act as server on port **9000**
3. **Company loaded** in TallyPrime — the target company must be open/loaded before sending requests

## Setup

```bash
cd C:\Projects\tally_api_server

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app:app --reload --port 8000
```

The API docs (Swagger UI) will be available at: **http://localhost:8000/docs**

## API Endpoints

### Create (Import into Tally)

| Method | Endpoint           | Description                          |
|--------|--------------------|------------------------------------- |
| GET    | `/health`          | Health check                         |
| POST   | `/create-ledger`   | Create one or more ledgers           |
| POST   | `/create-purchase` | Create one or more purchase vouchers |
| POST   | `/create-sales`    | Create one or more sales vouchers    |

### Fetch (Export from Tally)

| Method | Endpoint                       | Query Params                                  | Description                              |
|--------|--------------------------------|-----------------------------------------------|------------------------------------------|
| GET    | `/ledgers`                     | `company_name`                                | Fetch all ledger masters                 |
| GET    | `/api/ledger/by-gstin/{gstin}` | `company_name`, `username`, `password`        | Look up a ledger by GSTIN                |
| GET    | `/stock-items`                 | `company_name`                                | Fetch all stock items                    |
| GET    | `/api/stock-summary`           | `company_name`, `username`, `password`        | Fetch stock-in-hand summary              |
| GET    | `/vouchers/purchase`           | `company_name`, `from_date`, `to_date`        | Fetch purchase vouchers in a date range  |
| GET    | `/vouchers/sales`              | `company_name`, `from_date`, `to_date`        | Fetch sales vouchers in a date range     |

> **Note:** `from_date` and `to_date` use the **YYYYMMDD** format (e.g., `20250401` for April 1, 2025).

## Authentication (Optional)

All endpoints accept optional `username` and `password` fields for companies with Security Control enabled:

```json
{
  "company_name": "Your Company",
  "username": "admin",
  "password": "secret",
  ...
}
```

When provided, these are sent as `<SVOWNERNAME>` and `<SVOWNERPASSWORD>` in the XML. Omit them (or set to `null`) for companies without password protection.

## Creating Ledgers

**Endpoint:** `POST /create-ledger`

**Minimal example** — create a Sundry Debtor:

```json
{
  "company_name": "ABC Traders",
  "ledgers": [
    {
      "name": "Customer Alpha",
      "parent": "Sundry Debtors"
    }
  ]
}
```

**Common parent groups:**

| Group               | Use for                         |
|----------------------|---------------------------------|
| `Sundry Debtors`    | Customers                       |
| `Sundry Creditors`  | Suppliers                       |
| `Purchase Accounts` | Purchase expense ledgers        |
| `Sales Accounts`    | Sales income ledgers            |
| `Indirect Expenses` | Rent, Salaries, Office Expenses |
| `Indirect Incomes`  | Interest Income, etc.           |
| `Bank Accounts`     | Bank ledgers                    |
| `Cash-in-Hand`      | Cash ledgers (Cash exists by default) |

**Batch creation** — create multiple ledgers in one request:

```json
{
  "company_name": "ABC Traders",
  "ledgers": [
    { "name": "Supplier A", "parent": "Sundry Creditors" },
    { "name": "Supplier B", "parent": "Sundry Creditors" },
    { "name": "Purchases", "parent": "Purchase Accounts" },
    { "name": "Sales", "parent": "Sales Accounts" },
    { "name": "Bank Account", "parent": "Bank Accounts" }
  ]
}
```

The full list of supported ledger fields (394+ fields including GST, TDS, contact details, etc.) is documented in `ledger_master.json`.

## Creating Purchase Vouchers

**Endpoint:** `POST /create-purchase`

**Minimal example** — buy goods from a supplier for Rs 5,000:

```json
{
  "company_name": "ABC Traders",
  "vouchers": [
    {
      "date": "20250601",
      "voucher_type_name": "Purchase",
      "party_ledger_name": "Supplier A",
      "is_invoice": false,
      "ledger_entries": [
        {
          "ledger_name": "Supplier A",
          "is_deemed_positive": false,
          "is_party_ledger": true,
          "amount": "5000"
        },
        {
          "ledger_name": "Purchases",
          "is_deemed_positive": true,
          "is_party_ledger": false,
          "amount": "-5000"
        }
      ]
    }
  ]
}
```

**Key rules for Purchase vouchers:**
- `amount` must balance across all entries (sum to zero)
- Party ledger (Sundry Creditor): `is_deemed_positive: false`, `amount: positive` (credit)
- Expense ledger: `is_deemed_positive: true`, `amount: negative` (debit)
- All referenced ledgers must already exist in Tally

## Creating Sales Vouchers

**Endpoint:** `POST /create-sales`

**Minimal example** — sell goods to a customer for Rs 10,000:

```json
{
  "company_name": "ABC Traders",
  "vouchers": [
    {
      "date": "20250601",
      "voucher_type_name": "Sales",
      "party_ledger_name": "Customer Alpha",
      "is_invoice": false,
      "ledger_entries": [
        {
          "ledger_name": "Customer Alpha",
          "is_deemed_positive": true,
          "is_party_ledger": true,
          "amount": "-10000"
        },
        {
          "ledger_name": "Sales",
          "is_deemed_positive": false,
          "is_party_ledger": false,
          "amount": "10000"
        }
      ]
    }
  ]
}
```

**Key rules for Sales vouchers:**
- `amount` must balance across all entries (sum to zero)
- Party ledger (Sundry Debtor): `is_deemed_positive: true`, `amount: negative` (debit)
- Income ledger: `is_deemed_positive: false`, `amount: positive` (credit)

## Creating Payment / Receipt Vouchers

The purchase and sales endpoints also support Payment and Receipt vouchers — just change `voucher_type_name`.

**Payment** (paying a supplier via bank):

```json
{
  "company_name": "ABC Traders",
  "vouchers": [
    {
      "date": "20250701",
      "voucher_type_name": "Payment",
      "party_ledger_name": "Supplier A",
      "is_invoice": false,
      "ledger_entries": [
        {
          "ledger_name": "Supplier A",
          "is_deemed_positive": true,
          "is_party_ledger": true,
          "amount": "-5000"
        },
        {
          "ledger_name": "Bank Account",
          "is_deemed_positive": false,
          "is_party_ledger": false,
          "amount": "5000"
        }
      ]
    }
  ]
}
```

**Receipt** (receiving payment from a customer):

```json
{
  "company_name": "ABC Traders",
  "vouchers": [
    {
      "date": "20250701",
      "voucher_type_name": "Receipt",
      "party_ledger_name": "Customer Alpha",
      "is_invoice": false,
      "ledger_entries": [
        {
          "ledger_name": "Customer Alpha",
          "is_deemed_positive": false,
          "is_party_ledger": true,
          "amount": "10000"
        },
        {
          "ledger_name": "Bank Account",
          "is_deemed_positive": true,
          "is_party_ledger": false,
          "amount": "-10000"
        }
      ]
    }
  ]
}
```

## Fetching Ledger by GSTIN

**Endpoint:** `GET /api/ledger/by-gstin/{gstin}?company_name=ABC Traders`

Looks up a single ledger by its GSTIN (supports partial or full match).

**Response:**

```json
{
  "status": "success",
  "company_name": "ABC Traders",
  "username": null,
  "password": null,
  "gstin": "27AAACR5055K1Z5",
  "ledger_name": "Reliance Industries Ltd",
  "ledger": {
    "name": "Reliance Industries Ltd",
    "group": "Sundry Debtors",
    "gstin": "27AAACR5055K1Z5",
    "gst_registration_type": "Regular",
    "country": "India"
  }
}
```

If no ledger is found, returns `404` with an error message.

## Fetching Stock Summary

**Endpoint:** `GET /api/stock-summary?company_name=ABC Traders`

Returns the closing balance for all stock items.

**Response:**

```json
{
  "company_name": "ABC Traders",
  "username": null,
  "password": null,
  "count": 30,
  "stock_items": [
    {
      "name": "Gold Bar 24K",
      "group": "Gold and Jewellery",
      "unit": "",
      "closing_balance": "",
      "closing_value": "",
      "closing_rate": ""
    }
  ]
}
```

## Fetching Ledgers

**Endpoint:** `GET /ledgers?company_name=ABC Traders`

**Response:**

```json
{
  "count": 7,
  "ledgers": [
    {
      "name": "Acme Industries",
      "group": "Sundry Debtors",
      "opening_balance": "-50000.00",
      "mailing_name": null,
      "currency": null,
      "email": "rahul@acme.com",
      "mobile": "9876543210",
      "contact": "Rahul Sharma",
      "pan": "ABCDE1234F",
      "gstin": "29ABCDE1234F1Z5",
      "gst_registration_type": "Regular",
      "country": "India",
      "bill_wise": "Yes",
      "cost_centres": "No",
      "description": null
    }
  ]
}
```

All fields are always present in the response — fields without a value are returned as `null`.

## Fetching Vouchers

**Purchase:** `GET /vouchers/purchase?company_name=ABC Traders&from_date=20250401&to_date=20260331`

**Sales:** `GET /vouchers/sales?company_name=ABC Traders&from_date=20250401&to_date=20260331`

**Response:**

```json
{
  "count": 1,
  "vouchers": [
    {
      "voucher_number": "1",
      "date": "20250401",
      "voucher_type": "Purchase",
      "party": "Supplier Beta",
      "narration": null,
      "reference": null,
      "party_gstin": null,
      "place_of_supply": null,
      "is_invoice": "No",
      "guid": "d5f0247c-...-00000019",
      "amount": "5000.00",
      "ledger_entries": [
        {
          "ledger": "Supplier Beta",
          "amount": "5000.00",
          "is_party": true
        },
        {
          "ledger": "Purchases",
          "amount": "-5000.00",
          "is_party": false
        }
      ]
    }
  ]
}
```

## Fetching Stock Items

**Endpoint:** `GET /stock-items?company_name=ABC Traders`

**Response:**

```json
{
  "count": 2,
  "stock_items": [
    {
      "name": "Silver 999",
      "group": "Primary",
      "unit": "Kgs",
      "opening_balance": null,
      "opening_value": null,
      "opening_rate": null,
      "mailing_name": null,
      "description": null,
      "gst_applicable": "Applicable"
    }
  ]
}
```

## Date Format

All dates use the format **YYYYMMDD** (e.g., `20250601` for June 1, 2025). The date must fall within the company's active financial year.

## Multiple Companies

Tally can have multiple companies loaded simultaneously. Use `company_name` to target the correct one:

```json
{ "company_name": "ABC Traders", ... }
{ "company_name": "XYZ Traders", ... }
```

The target company **must be loaded** (opened) in TallyPrime. There is no API to load a company programmatically — this must be done manually via Gateway of Tally > Select Company.

## Tally Education Mode

If using Tally Education Mode, be aware:

- **Ledger creation works on any date** — no restrictions
- **Voucher creation only works on the 1st, 2nd, and last day of each month**
- Using any other date will produce the misleading error: `"Voucher date is missing"`
- This is a Tally Education Mode limitation, not an issue with the API

## API Response

All endpoints return:

```json
{
  "status": "success",
  "tally_response": "<raw XML response from Tally>",
  "xml_sent": "<the XML that was posted to Tally>"
}
```

A successful creation looks like:
```xml
<RESPONSE>
 <CREATED>1</CREATED>
 <ERRORS>0</ERRORS>
 <EXCEPTIONS>0</EXCEPTIONS>
</RESPONSE>
```

Common errors:
- `"Ledger 'X' does not exist!"` — create the ledger first
- `"Voucher date is missing"` — use an allowed date (see Education Mode section)
- `502 Bad Gateway` — Tally is not running or HTTP server not enabled on port 9000

## Project Structure

```
tally_api_server/
├── app.py                          # FastAPI server with all endpoints (create + fetch)
├── models.py                       # Pydantic models for ledger creation (394+ fields)
├── xml_builder.py                  # XML builder for ledger masters
├── purchase_models.py              # Pydantic models for purchase/payment vouchers
├── purchase_xml_builder.py         # XML builder for purchase/payment vouchers
├── sales_models.py                 # Pydantic models for sales/receipt vouchers
├── sales_xml_builder.py            # XML builder for sales/receipt vouchers
├── fetch_xml_builder.py            # XML builder for export (fetch) requests
├── requirements.txt                # Python dependencies
├── ledger_api_contract.json        # API contract for ledger endpoint
└── README.md                       # This file
```

## Quick Start Example

1. Start Tally with HTTP server on port 9000 and load your company
2. Start the API:
   ```bash
   pip install -r requirements.txt
   uvicorn app:app --reload --port 8000
   ```
3. Create a ledger:
   ```bash
   curl -X POST http://localhost:8000/create-ledger \
     -H "Content-Type: application/json" \
     -d "{\"company_name\": \"ABC Traders\", \"ledgers\": [{\"name\": \"Test Supplier\", \"parent\": \"Sundry Creditors\"}]}"
   ```
4. Create a voucher:
   ```bash
   curl -X POST http://localhost:8000/create-purchase \
     -H "Content-Type: application/json" \
     -d "{\"company_name\": \"ABC Traders\", \"vouchers\": [{\"date\": \"20250601\", \"voucher_type_name\": \"Purchase\", \"party_ledger_name\": \"Test Supplier\", \"is_invoice\": false, \"ledger_entries\": [{\"ledger_name\": \"Test Supplier\", \"is_deemed_positive\": false, \"is_party_ledger\": true, \"amount\": \"1000\"}, {\"ledger_name\": \"Purchases\", \"is_deemed_positive\": true, \"is_party_ledger\": false, \"amount\": \"-1000\"}]}]}"
   ```
5. Fetch ledgers:
   ```bash
   curl "http://localhost:8000/ledgers?company_name=ABC%20Traders"
   ```
6. Fetch purchase vouchers for FY 2025-26:
   ```bash
   curl "http://localhost:8000/vouchers/purchase?company_name=ABC%20Traders&from_date=20250401&to_date=20260331"
   ```
7. Fetch sales vouchers for FY 2025-26:
   ```bash
   curl "http://localhost:8000/vouchers/sales?company_name=ABC%20Traders&from_date=20250401&to_date=20260331"
   ```
8. Fetch stock items:
   ```bash
   curl "http://localhost:8000/stock-items?company_name=ABC%20Traders"
   ```
9. Or use the Swagger UI at **http://localhost:8000/docs** for interactive testing
