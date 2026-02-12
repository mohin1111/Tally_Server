"""Build Tally-compatible XML for exporting (fetching) data from Tally."""

import xml.etree.ElementTree as ET


def _build_export_envelope(
    report_name: str,
    company_name: str,
    static_vars: dict[str, str] | None = None,
) -> str:
    """Build a generic Tally export XML envelope."""
    envelope = ET.Element("ENVELOPE")

    header = ET.SubElement(envelope, "HEADER")
    req = ET.SubElement(header, "TALLYREQUEST")
    req.text = "Export Data"

    body = ET.SubElement(envelope, "BODY")
    export_data = ET.SubElement(body, "EXPORTDATA")

    request_desc = ET.SubElement(export_data, "REQUESTDESC")
    rn = ET.SubElement(request_desc, "REPORTNAME")
    rn.text = report_name

    sv = ET.SubElement(request_desc, "STATICVARIABLES")
    fmt = ET.SubElement(sv, "SVEXPORTFORMAT")
    fmt.text = "$$SysName:XML"
    company = ET.SubElement(sv, "SVCURRENTCOMPANY")
    company.text = company_name

    if static_vars:
        for tag, value in static_vars.items():
            el = ET.SubElement(sv, tag)
            el.text = value

    ET.indent(envelope, space="  ")
    return ET.tostring(envelope, encoding="unicode", xml_declaration=False)


def build_fetch_ledgers_xml(company_name: str) -> str:
    """Build XML to fetch all ledger masters."""
    return _build_export_envelope(
        report_name="List of Accounts",
        company_name=company_name,
        static_vars={"ACCOUNTTYPE": "Ledgers"},
    )


def build_fetch_stock_items_xml(company_name: str) -> str:
    """Build XML to fetch all stock items."""
    return _build_export_envelope(
        report_name="List of Accounts",
        company_name=company_name,
        static_vars={"ACCOUNTTYPE": "Stock Items"},
    )


def build_fetch_stock_summary_xml(company_name: str) -> str:
    """Build XML to fetch stock-in-hand summary via TDL Collection."""
    return (
        "<ENVELOPE>"
        "<HEADER>"
        "<VERSION>1</VERSION>"
        "<TALLYREQUEST>Export</TALLYREQUEST>"
        "<TYPE>Collection</TYPE>"
        "<ID>StockSummary</ID>"
        "</HEADER>"
        "<BODY>"
        "<DESC>"
        "<STATICVARIABLES>"
        "<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>"
        f"<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>"
        "</STATICVARIABLES>"
        "<TDL>"
        "<TDLMESSAGE>"
        '<COLLECTION NAME="StockSummary" ISMODIFY="No">'
        "<TYPE>Stock Item</TYPE>"
        "<NATIVEMETHOD>Name</NATIVEMETHOD>"
        "<NATIVEMETHOD>Parent</NATIVEMETHOD>"
        "<NATIVEMETHOD>BaseUnits</NATIVEMETHOD>"
        "<NATIVEMETHOD>ClosingBalance</NATIVEMETHOD>"
        "<NATIVEMETHOD>ClosingValue</NATIVEMETHOD>"
        "<NATIVEMETHOD>ClosingRate</NATIVEMETHOD>"
        "</COLLECTION>"
        "</TDLMESSAGE>"
        "</TDL>"
        "</DESC>"
        "</BODY>"
        "</ENVELOPE>"
    )


def build_fetch_vouchers_xml(
    company_name: str,
    voucher_type: str,
    from_date: str,
    to_date: str,
) -> str:
    """Build XML to fetch vouchers of a given type within a date range.

    Args:
        company_name: Tally company name.
        voucher_type: e.g. "Purchase", "Sales".
        from_date: Start date in YYYYMMDD format.
        to_date: End date in YYYYMMDD format.
    """
    return _build_export_envelope(
        report_name="Voucher Register",
        company_name=company_name,
        static_vars={
            "VOUCHERTYPENAME": voucher_type,
            "SVFROMDATE": from_date,
            "SVTODATE": to_date,
        },
    )
