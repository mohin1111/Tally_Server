"""FastAPI app for creating Tally ledgers and vouchers via XML import."""

import httpx
from fastapi import FastAPI, HTTPException

from models import CreateLedgerPayload
from purchase_models import CreatePurchasePayload
from sales_models import CreateSalesPayload
from xml_builder import build_ledger_xml
from purchase_xml_builder import build_purchase_xml
from sales_xml_builder import build_sales_xml

app = FastAPI(
    title="Tally API",
    description="Create ledgers and vouchers in Tally via its HTTP XML interface",
    version="1.0.0",
)

TALLY_URL = "http://localhost:9000"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/create-ledger")
async def create_ledger(payload: CreateLedgerPayload):
    xml_str = build_ledger_xml(payload)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                TALLY_URL,
                content=xml_str,
                headers={"Content-Type": "application/xml"},
            )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=502,
            detail="Cannot connect to Tally at "
            + TALLY_URL
            + ". Is Tally running with HTTP server enabled on port 9000?",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Tally request timed out",
        )

    tally_response = response.text

    # Check for Tally error indicators in response
    is_error = (
        "LINEERROR" in tally_response
        or "ERROR" in tally_response.upper()
        and "CREATED" not in tally_response.upper()
    )

    return {
        "status": "error" if is_error else "success",
        "tally_response": tally_response,
        "xml_sent": xml_str,
    }


async def _post_to_tally(xml_str: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                TALLY_URL,
                content=xml_str,
                headers={"Content-Type": "application/xml"},
            )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=502,
            detail="Cannot connect to Tally at "
            + TALLY_URL
            + ". Is Tally running with HTTP server enabled on port 9000?",
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Tally request timed out")

    tally_response = response.text
    is_error = (
        "LINEERROR" in tally_response
        or "ERROR" in tally_response.upper()
        and "CREATED" not in tally_response.upper()
    )
    return {
        "status": "error" if is_error else "success",
        "tally_response": tally_response,
        "xml_sent": xml_str,
    }


@app.post("/create-purchase")
async def create_purchase(payload: CreatePurchasePayload):
    xml_str = build_purchase_xml(payload)
    return await _post_to_tally(xml_str)


@app.post("/create-sales")
async def create_sales(payload: CreateSalesPayload):
    xml_str = build_sales_xml(payload)
    return await _post_to_tally(xml_str)
