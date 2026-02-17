# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A FastAPI server that integrates with TallyPrime's HTTP XML interface. It provides REST API endpoints to create and fetch ledgers, vouchers (purchase/sales/payment/receipt), and stock items in Tally.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server (with hot reload)
uvicorn app:app --reload --port 8000

# Swagger UI available at http://localhost:8000/docs
```

There are no tests, linting, or formatting tools configured.

## Prerequisites

- Python 3.10+
- TallyPrime running with HTTP server enabled on port 9000
- A company must be loaded in TallyPrime before sending requests

## Architecture

The app follows a simple pattern: **JSON request → Pydantic validation → XML generation → POST to Tally → parse XML response → JSON response**.

### Core Flow

`app.py` is the single FastAPI entrypoint. It handles all routes and delegates to:

1. **Pydantic models** (`models.py`, `purchase_models.py`, `sales_models.py`) — validate incoming JSON payloads
2. **XML builders** (`xml_builder.py`, `purchase_xml_builder.py`, `sales_xml_builder.py`, `fetch_xml_builder.py`) — convert validated models into TallyPrime XML format
3. **Tally communication** — `_post_to_tally()` for create operations, `_fetch_from_tally()` for read operations, both POST XML to `http://localhost:9000`

### Module Mapping

| Domain    | Models              | XML Builder              | Endpoints                              |
|-----------|---------------------|--------------------------|----------------------------------------|
| Ledgers   | `models.py`         | `xml_builder.py`         | `POST /create-ledger`, `GET /ledgers`  |
| Purchases | `purchase_models.py`| `purchase_xml_builder.py`| `POST /create-purchase`, `GET /vouchers/purchase` |
| Sales     | `sales_models.py`   | `sales_xml_builder.py`   | `POST /create-sales`, `GET /vouchers/sales` |
| Fetch     | —                   | `fetch_xml_builder.py`   | All GET endpoints                      |

### Key Constants

- `TALLY_URL = "http://localhost:9000"` — Tally's HTTP server address (hardcoded in `app.py`)
- `DEFAULT_COMPANY = "Test Traders"` — default company name

### Tally XML Conventions

- Tally uses a custom XML schema (not standard SOAP). XML requests are POSTed to Tally's HTTP port.
- Create operations use `IMPORTDATA` envelopes; fetch operations use `EXPORTDATA` with TDL collection queries.
- Tally responses may contain invalid XML control characters (e.g. `&#4;`) — `_fetch_from_tally()` strips these before parsing.
- Amounts in vouchers must balance to zero across all ledger entries.
- Dates use `YYYYMMDD` format and must fall within the company's active financial year.
- Tally Education Mode only allows voucher creation on the 1st, 2nd, and last day of each month.

### XML Sample Files

The repo contains sample XML files (`Master.xml`, `ledger_master.xml`, `purchase_master.xml`, `sales_master.xml`, `Purchase_clean.xml`, etc.) and JSON request/response examples (`ledger_request.json`, `purchase_request.json`, `sales_request.json`, etc.) used as reference for the XML builders.
