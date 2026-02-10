# Tally Integration API

A FastAPI application that creates ledgers and vouchers in TallyPrime via its HTTP XML interface.

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
cd C:\Users\JainishJain\Tally

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app:app --reload --port 8000
```

The API docs (Swagger UI) will be available at: **http://localhost:8000/docs**

## API Endpoints

| Method | Endpoint           | Description                     |
|--------|--------------------|---------------------------------|
| GET    | `/health`          | Health check                    |
| POST   | `/create-ledger`   | Create one or more ledgers      |
| POST   | `/create-purchase` | Create one or more purchase vouchers |
| POST   | `/create-sales`    | Create one or more sales vouchers    |

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
Tally/
├── app.py                          # FastAPI server with all endpoints
├── models.py                       # Pydantic models for ledger creation (394+ fields)
├── xml_builder.py                  # XML builder for ledger masters
├── purchase_models.py              # Pydantic models for purchase/payment vouchers
├── purchase_xml_builder.py         # XML builder for purchase/payment vouchers
├── sales_models.py                 # Pydantic models for sales/receipt vouchers
├── sales_xml_builder.py            # XML builder for sales/receipt vouchers
├── requirements.txt                # Python dependencies
├── ledger_master.json              # Reference JSON — all ledger fields
├── ledger_api_contract.json        # API contract for ledger endpoint
├── purchase_master.json            # Reference JSON — all purchase voucher fields
├── sales_master.json               # Reference JSON — sales voucher example
├── LedgerMaster_Template.xml       # Reference XML template for ledgers
├── PurchaseVoucher_Template.xml    # Reference XML template for purchase vouchers
└── SalesVoucher_Template.xml       # Reference XML template for sales vouchers
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
5. Or use the Swagger UI at **http://localhost:8000/docs** for interactive testing
