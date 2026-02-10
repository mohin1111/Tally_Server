"""Build Tally-compatible XML for sales voucher creation.

Reuses the purchase voucher builder since the XML structure is identical.
"""

from purchase_xml_builder import _build_voucher_element

import xml.etree.ElementTree as ET

from sales_models import CreateSalesPayload


def build_sales_xml(payload: CreateSalesPayload) -> str:
    """Build complete Tally XML envelope for sales vouchers."""
    envelope = ET.Element("ENVELOPE")

    header = ET.SubElement(envelope, "HEADER")
    req = ET.SubElement(header, "TALLYREQUEST")
    req.text = "Import Data"

    body = ET.SubElement(envelope, "BODY")
    import_data = ET.SubElement(body, "IMPORTDATA")

    request_desc = ET.SubElement(import_data, "REQUESTDESC")
    report_name = ET.SubElement(request_desc, "REPORTNAME")
    report_name.text = "Vouchers"
    static_vars = ET.SubElement(request_desc, "STATICVARIABLES")
    company = ET.SubElement(static_vars, "SVCURRENTCOMPANY")
    company.text = payload.company_name
    if payload.username:
        uname = ET.SubElement(static_vars, "SVOWNERNAME")
        uname.text = payload.username
    if payload.password:
        pwd = ET.SubElement(static_vars, "SVOWNERPASSWORD")
        pwd.text = payload.password

    request_data = ET.SubElement(import_data, "REQUESTDATA")

    for voucher in payload.vouchers:
        tally_msg = ET.SubElement(request_data, "TALLYMESSAGE")
        tally_msg.set("xmlns:UDF", "TallyUDF")
        vch_el = _build_voucher_element(voucher)
        tally_msg.append(vch_el)

    ET.indent(envelope, space="  ")
    xml_str = ET.tostring(envelope, encoding="unicode", xml_declaration=False)
    xml_str = xml_str.replace("&amp;#4;", "&#4;")
    return xml_str
