"""Build Tally-compatible XML for purchase voucher creation."""

import xml.etree.ElementTree as ET

from purchase_models import (
    AccountingAllocation,
    BatchAllocation,
    CreatePurchasePayload,
    GSTRateDetail,
    InventoryEntry,
    LedgerEntry,
    PurchaseVoucher,
)


def _bool_yn(val: bool | None, default: str = "No") -> str:
    if val is None:
        return default
    return "Yes" if val else "No"


def _add(parent: ET.Element, tag: str, text: str | None) -> None:
    if text is not None:
        el = ET.SubElement(parent, tag)
        el.text = text


def _add_bool(parent: ET.Element, tag: str, val: bool | None, default: str = "No") -> None:
    el = ET.SubElement(parent, tag)
    el.text = _bool_yn(val, default)


def _empty_list(parent: ET.Element, tag: str) -> None:
    el = ET.SubElement(parent, tag)
    el.text = "      "


# ==================== VOUCHER SCALAR & BOOL MAPS ====================

VOUCHER_SCALARS: list[tuple[str, str]] = [
    ("gst_registration_type", "GSTREGISTRATIONTYPE"),
    ("vat_dealer_type", "VATDEALERTYPE"),
    ("state_name", "STATENAME"),
    ("narration", "NARRATION"),
    ("country_of_residence", "COUNTRYOFRESIDENCE"),
    ("party_gstin", "PARTYGSTIN"),
    ("place_of_supply", "PLACEOFSUPPLY"),
    ("party_name", "PARTYNAME"),
    ("cmp_gstin", "CMPGSTIN"),
    ("voucher_number", "VOUCHERNUMBER"),
    ("buyer_address_type", "BUYERADDRESSTYPE"),
    ("basic_buyer_name", "BASICBUYERNAME"),
    ("cmp_gst_registration_type", "CMPGSTREGISTRATIONTYPE"),
    ("reference", "REFERENCE"),
    ("party_mailing_name", "PARTYMAILINGNAME"),
    ("party_pincode", "PARTYPINCODE"),
    ("consignee_gstin", "CONSIGNEEGSTIN"),
    ("consignee_mailing_name", "CONSIGNEEMAILINGNAME"),
    ("consignee_pincode", "CONSIGNEEPINCODE"),
    ("consignee_state_name", "CONSIGNEESTATENAME"),
    ("cmp_gst_state", "CMPGSTSTATE"),
    ("consignee_country_name", "CONSIGNEECOUNTRYNAME"),
    ("basic_base_party_name", "BASICBASEPARTYNAME"),
    ("numbering_style", "NUMBERINGSTYLE"),
    ("cst_form_issue_type", "CSTFORMISSUETYPE"),
    ("cst_form_recv_type", "CSTFORMRECVTYPE"),
    ("consignee_cst_number", "CONSIGNEECSTNUMBER"),
    ("fbt_payment_type", "FBTPAYMENTTYPE"),
    ("persisted_view", "PERSISTEDVIEW"),
    ("vch_status_tax_adjustment", "VCHSTATUSTAXADJUSTMENT"),
    ("vch_status_voucher_type", "VCHSTATUSVOUCHERTYPE"),
    ("vch_status_tax_unit", "VCHSTATUSTAXUNIT"),
    ("vch_gst_class", "VCHGSTCLASS"),
    ("buyer_pin_number", "BUYERPINNUMBER"),
    ("consignee_pin_number", "CONSIGNEEPINNUMBER"),
    ("vch_entry_mode", "VCHENTRYMODE"),
]

VOUCHER_BOOLS: list[tuple[str, str, str]] = [
    # (field_name, xml_tag, default)
    ("diff_actual_qty", "DIFFACTUALQTY", "No"),
    ("is_mst_from_sync", "ISMSTFROMSYNC", "No"),
    ("is_deleted", "ISDELETED", "No"),
    ("is_security_on_when_entered", "ISSECURITYONWHENENTERED", "No"),
    ("as_original", "ASORIGINAL", "No"),
    ("audited", "AUDITED", "No"),
    ("is_common_party", "ISCOMMONPARTY", "No"),
    ("for_job_costing", "FORJOBCOSTING", "No"),
    ("is_optional", "ISOPTIONAL", "No"),
    ("use_for_excise", "USEFOREXCISE", "No"),
    ("is_for_job_work_in", "ISFORJOBWORKIN", "No"),
    ("allow_consumption", "ALLOWCONSUMPTION", "No"),
    ("use_for_interest", "USEFORINTEREST", "No"),
    ("use_for_gain_loss", "USEFORGAINLOSS", "No"),
    ("use_for_godown_transfer", "USEFORGODOWNTRANSFER", "No"),
    ("use_for_compound", "USEFORCOMPOUND", "No"),
    ("use_for_service_tax", "USEFORSERVICETAX", "No"),
    ("is_reverse_charge_applicable", "ISREVERSECHARGEAPPLICABLE", "No"),
    ("is_system", "ISSYSTEM", "No"),
    ("is_fetched_only", "ISFETCHEDONLY", "No"),
    ("is_gst_overridden", "ISGSTOVERRIDDEN", "No"),
    ("is_cancelled", "ISCANCELLED", "No"),
    ("is_on_hold", "ISONHOLD", "No"),
    ("is_summary", "ISSUMMARY", "No"),
    ("is_ecommerce_supply", "ISECOMMERCESUPPLY", "No"),
    ("is_boe_not_applicable", "ISBOENOTAPPLICABLE", "No"),
    ("is_gst_sec_seven_applicable", "ISGSTSECSEVENAPPLICABLE", "No"),
    ("ignore_einv_validation", "IGNOREEINVVALIDATION", "No"),
    ("cmp_gst_is_oth_territory_assessee", "CMPGSTISOTHTERRITORYASSESSEE", "No"),
    ("party_gst_is_oth_territory_assessee", "PARTYGSTISOTHTERRITORYASSESSEE", "No"),
    ("irn_json_exported", "IRNJSONEXPORTED", "No"),
    ("irn_cancelled", "IRNCANCELLED", "No"),
    ("ignore_gst_conflict_in_mig", "IGNOREGSTCONFLICTINMIG", "No"),
    ("is_opbal_transaction", "ISOPBALTRANSACTION", "No"),
    ("ignore_gst_format_validation", "IGNOREGSTFORMATVALIDATION", "No"),
    ("is_eligible_for_itc", "ISELIGIBLEFORITC", "No"),
    ("ignore_gst_optional_uncertain", "IGNOREGSTOPTIONALUNCERTAIN", "No"),
    ("update_summary_values", "UPDATESUMMARYVALUES", "No"),
    ("is_eway_bill_applicable", "ISEWAYBILLAPPLICABLE", "No"),
    ("is_deleted_retained", "ISDELETEDRETAINED", "No"),
    ("is_null", "ISNULL", "No"),
    ("is_excise_voucher", "ISEXCISEVOUCHER", "No"),
    ("excise_tax_override", "EXCISETAXOVERRIDE", "No"),
    ("use_for_tax_unit_transfer", "USEFORTAXUNITTRANSFER", "No"),
    ("is_exer1_nop_overwrite", "ISEXER1NOPOVERWRITE", "No"),
    ("is_exf2_nop_overwrite", "ISEXF2NOPOVERWRITE", "No"),
    ("is_exer3_nop_overwrite", "ISEXER3NOPOVERWRITE", "No"),
    ("ignore_pos_validation", "IGNOREPOSVALIDATION", "No"),
    ("excise_opening", "EXCISEOPENING", "No"),
    ("use_for_final_production", "USEFORFINALPRODUCTION", "No"),
    ("is_tds_overridden", "ISTDSOVERRIDDEN", "No"),
    ("is_tcs_overridden", "ISTCSOVERRIDDEN", "No"),
    ("is_tds_tcs_cash_vch", "ISTDSTCSCASHVCH", "No"),
    ("include_adv_pymt_vch", "INCLUDEADVPYMTVCH", "No"),
    ("is_sub_works_contract", "ISSUBWORKSCONTRACT", "No"),
    ("is_vat_overridden", "ISVATOVERRIDDEN", "No"),
    ("ignore_orig_vch_date", "IGNOREORIGVCHDATE", "No"),
    ("is_vat_paid_at_customs", "ISVATPAIDATCUSTOMS", "No"),
    ("is_declared_to_customs", "ISDECLAREDTOCUSTOMS", "No"),
    ("vat_advance_payment", "VATADVANCEPAYMENT", "No"),
    ("vat_adv_pay", "VATADVPAY", "No"),
    ("is_cst_delcared_goods_sales", "ISCSTDELCAREDGOODSSALES", "No"),
    ("is_vat_res_tax_inv", "ISVATRESTAXINV", "No"),
    ("is_service_tax_overridden", "ISSERVICETAXOVERRIDDEN", "No"),
    ("is_isd_voucher", "ISISDVOUCHER", "No"),
    ("is_excise_overridden", "ISEXCISEOVERRIDDEN", "No"),
    ("is_excise_supply_vch", "ISEXCISESUPPLYVCH", "No"),
    ("gst_not_exported", "GSTNOTEXPORTED", "No"),
    ("ignore_gstin_validation", "IGNOREGSTINVALIDATION", "No"),
    ("is_gst_refund", "ISGSTREFUND", "No"),
    ("ovrdn_eway_bill_applicability", "OVRDNEWAYBILLAPPLICABILITY", "No"),
    ("is_vat_principal_account", "ISVATPRINCIPALACCOUNT", "No"),
    ("vch_status_is_vch_num_used", "VCHSTATUSISVCHNUMUSED", "No"),
    ("vch_gst_status_is_included", "VCHGSTSTATUSISINCLUDED", "No"),
    ("vch_gst_status_is_uncertain", "VCHGSTSTATUSISUNCERTAIN", "No"),
    ("vch_gst_status_is_excluded", "VCHGSTSTATUSISEXCLUDED", "No"),
    ("vch_gst_status_is_applicable", "VCHGSTSTATUSISAPPLICABLE", "No"),
    ("vch_gst_status_is_gstr2b_reconciled", "VCHGSTSTATUSISGSTR2BRECONCILED", "No"),
    ("vch_gst_status_is_gstr2b_only_in_portal", "VCHGSTSTATUSISGSTR2BONLYINPORTAL", "No"),
    ("vch_gst_status_is_gstr2b_only_in_books", "VCHGSTSTATUSISGSTR2BONLYINBOOKS", "No"),
    ("vch_gst_status_is_gstr2b_mismatch", "VCHGSTSTATUSISGSTR2BMISMATCH", "No"),
    ("vch_gst_status_is_gstr2b_in_diff_period", "VCHGSTSTATUSISGSTR2BINDIFFPERIOD", "No"),
    ("vch_gst_status_is_ret_eff_date_overrdn", "VCHGSTSTATUSISRETEFFDATEOVERRDN", "No"),
    ("vch_gst_status_is_overrdn", "VCHGSTSTATUSISOVERRDN", "No"),
    ("vch_gst_status_is_stat_in_diff_date", "VCHGSTSTATUSISSTATINDIFFDATE", "No"),
    ("vch_gst_status_is_ret_in_diff_date", "VCHGSTSTATUSISRETINDIFFDATE", "No"),
    ("vch_gst_status_main_section_excluded", "VCHGSTSTATUSMAINSECTIONEXCLUDED", "No"),
    ("vch_gst_status_is_branch_transfer_out", "VCHGSTSTATUSISBRANCHTRANSFEROUT", "No"),
    ("vch_gst_status_is_system_summary", "VCHGSTSTATUSISSYSTEMSUMMARY", "No"),
    ("vch_status_is_unregistered_rcm", "VCHSTATUSISUNREGISTEREDRCM", "No"),
    ("vch_status_is_optional", "VCHSTATUSISOPTIONAL", "No"),
    ("vch_status_is_cancelled", "VCHSTATUSISCANCELLED", "No"),
    ("vch_status_is_deleted", "VCHSTATUSISDELETED", "No"),
    ("vch_status_is_opening_balance", "VCHSTATUSISOPENINGBALANCE", "No"),
    ("vch_status_is_fetched_only", "VCHSTATUSISFETCHEDONLY", "No"),
    ("vch_gst_status_is_optional_uncertain", "VCHGSTSTATUSISOPTIONALUNCERTAIN", "No"),
    ("vch_status_is_reaccept_for_hsn_done", "VCHSTATUSISREACCEPTFORHSNDONE", "No"),
    ("payment_link_has_multi_ref", "PAYMENTLINKHASMULTIREF", "No"),
    ("is_shipping_within_state", "ISSHIPPINGWITHINSTATE", "No"),
    ("is_overseas_tourist_trans", "ISOVERSEASTOURISTTRANS", "No"),
    ("is_designated_zone_party", "ISDESIGNATEDZONEPARTY", "No"),
    ("has_cash_flow", "HASCASHFLOW", "No"),
    ("is_post_dated", "ISPOSTDATED", "No"),
    ("use_tracking_number", "USETRACKINGNUMBER", "No"),
    ("is_invoice", "ISINVOICE", "Yes"),
    ("mfg_journal", "MFGJOURNAL", "No"),
    ("has_discounts", "HASDISCOUNTS", "No"),
    ("as_payslip", "ASPAYSLIP", "No"),
    ("is_cost_centre", "ISCOSTCENTRE", "No"),
    ("is_stx_non_realized_vch", "ISSTXNONREALIZEDVCH", "No"),
    ("is_excise_manufacturer_on", "ISEXCISEMANUFACTURERON", "No"),
    ("is_blank_cheque", "ISBLANKCHEQUE", "No"),
    ("is_void", "ISVOID", "No"),
    ("order_line_status", "ORDERLINESTATUS", "No"),
    ("vat_is_agnst_canc_sales", "VATISAGNSTCANCSALES", "No"),
    ("vat_is_purc_exempted", "VATISPURCEXEMPTED", "No"),
    ("is_vat_res_tax_invoice", "ISVATRESTAXINVOICE", "No"),
    ("vat_is_assesable_calc_vch", "VATISASSESABLECALCVCH", "No"),
    ("is_vat_duty_paid", "ISVATDUTYPAID", "Yes"),
    ("is_delivery_same_as_consignee", "ISDELIVERYSAMEASCONSIGNEE", "No"),
    ("is_dispatch_same_as_consignor", "ISDISPATCHSAMEASCONSIGNOR", "No"),
    ("is_deleted_vch_retained", "ISDELETEDVCHRETAINED", "No"),
    ("vch_only_addl_info_updated", "VCHONLYADDLINFOUPDATED", "No"),
    ("change_vch_mode", "CHANGEVCHMODE", "No"),
    ("reset_irn_qr_code", "RESETIRNQRCODE", "No"),
]

# Empty lists at voucher level
VOUCHER_EMPTY_LISTS: list[str] = [
    "EWAYBILLDETAILS.LIST",
    "EXCLUDEDTAXATIONS.LIST",
    "OLDAUDITENTRIES.LIST",
    "ACCOUNTAUDITENTRIES.LIST",
    "AUDITENTRIES.LIST",
    "DUTYHEADDETAILS.LIST",
    "GSTADVADJDETAILS.LIST",
]

# Empty lists at the end of the voucher
VOUCHER_TRAILING_EMPTY_LISTS: list[str] = [
    "CONTRITRANS.LIST",
    "EWAYBILLERRORLIST.LIST",
    "IRNERRORLIST.LIST",
    "HARYANAVAT.LIST",
    "SUPPLEMENTARYDUTYHEADDETAILS.LIST",
    "INVOICEDELNOTES.LIST",
    "INVOICEORDERLIST.LIST",
    "INVOICEINDENTLIST.LIST",
    "ATTENDANCEENTRIES.LIST",
    "ORIGINVOICEDETAILS.LIST",
    "INVOICEEXPORTLIST.LIST",
]

VOUCHER_FINAL_EMPTY_LISTS: list[str] = [
    "STKJRNLADDLCOSTDETAILS.LIST",
    "PAYROLLMODEOFPAYMENT.LIST",
    "ATTDRECORDS.LIST",
    "GSTEWAYCONSIGNORADDRESS.LIST",
    "GSTEWAYCONSIGNEEADDRESS.LIST",
    "TEMPGSTRATEDETAILS.LIST",
    "TEMPGSTADVADJUSTED.LIST",
    "GSTBUYERADDRESS.LIST",
    "GSTCONSIGNEEADDRESS.LIST",
]

# Empty lists inside each LEDGERENTRIES.LIST / ACCOUNTINGALLOCATIONS.LIST
LEDGER_ENTRY_EMPTY_LISTS: list[str] = [
    "SERVICETAXDETAILS.LIST",
    "BANKALLOCATIONS.LIST",
    "BILLALLOCATIONS.LIST",
    "INTERESTCOLLECTION.LIST",
    "OLDAUDITENTRIES.LIST",
    "ACCOUNTAUDITENTRIES.LIST",
    "AUDITENTRIES.LIST",
    "INPUTCRALLOCS.LIST",
    "DUTYHEADDETAILS.LIST",
    "EXCISEDUTYHEADDETAILS.LIST",
    "RATEDETAILS.LIST",
    "SUMMARYALLOCS.LIST",
    "CENVATDUTYALLOCATIONS.LIST",
    "STPYMTDETAILS.LIST",
    "EXCISEPAYMENTALLOCATIONS.LIST",
    "TAXBILLALLOCATIONS.LIST",
    "TAXOBJECTALLOCATIONS.LIST",
    "TDSEXPENSEALLOCATIONS.LIST",
    "VATSTATUTORYDETAILS.LIST",
    "COSTTRACKALLOCATIONS.LIST",
    "REFVOUCHERDETAILS.LIST",
    "INVOICEWISEDETAILS.LIST",
    "VATITCDETAILS.LIST",
    "ADVANCETAXDETAILS.LIST",
    "TAXTYPEALLOCATIONS.LIST",
]

INVENTORY_TRAILING_EMPTY_LISTS: list[str] = [
    "SUPPLEMENTARYDUTYHEADDETAILS.LIST",
    "TAXOBJECTALLOCATIONS.LIST",
    "REFVOUCHERDETAILS.LIST",
    "EXCISEALLOCATIONS.LIST",
    "EXPENSEALLOCATIONS.LIST",
]


# ==================== LIST BUILDERS ====================


def _build_batch_allocation(parent: ET.Element, ba: BatchAllocation) -> None:
    el = ET.SubElement(parent, "BATCHALLOCATIONS.LIST")
    _add(el, "GODOWNNAME", ba.godown_name)
    _add(el, "BATCHNAME", ba.batch_name)
    _add(el, "DESTINATIONGODOWNNAME", ba.destination_godown_name)
    _add(el, "INDENTNO", ba.indent_no)
    _add(el, "ORDERNO", ba.order_no)
    _add(el, "TRACKINGNUMBER", ba.tracking_number)
    _add_bool(el, "DYNAMICCSTISCLEARED", ba.dynamic_cst_is_cleared)
    _add(el, "AMOUNT", ba.amount)
    _add(el, "ACTUALQTY", ba.actual_qty)
    _add(el, "BILLEDQTY", ba.billed_qty)
    _empty_list(el, "ADDITIONALDETAILS.LIST")
    _empty_list(el, "VOUCHERCOMPONENTLIST.LIST")


def _build_accounting_allocation(parent: ET.Element, aa: AccountingAllocation) -> None:
    el = ET.SubElement(parent, "ACCOUNTINGALLOCATIONS.LIST")
    # Old audit entry
    oa = ET.SubElement(el, "OLDAUDITENTRYIDS.LIST")
    oa.set("TYPE", "Number")
    oav = ET.SubElement(oa, "OLDAUDITENTRYIDS")
    oav.text = "-1"

    _add(el, "LEDGERNAME", aa.ledger_name)
    _add(el, "GSTCLASS", aa.gst_class)
    _add_bool(el, "ISDEEMEDPOSITIVE", aa.is_deemed_positive)
    _add_bool(el, "LEDGERFROMITEM", aa.ledger_from_item)
    _add_bool(el, "REMOVEZEROENTRIES", aa.remove_zero_entries)
    _add_bool(el, "ISPARTYLEDGER", aa.is_party_ledger)
    _add_bool(el, "GSTOVERRIDDEN", aa.gst_overridden)
    _add_bool(el, "ISGSTASSESSABLEVALUEOVERRIDDEN", aa.is_gst_assessable_value_overridden)
    _add_bool(el, "STRDISGSTAPPLICABLE", aa.strd_is_gst_applicable)
    _add_bool(el, "STRDGSTISPARTYLEDGER", aa.strd_gst_is_party_ledger)
    _add_bool(el, "STRDGSTISDUTYLEDGER", aa.strd_gst_is_duty_ledger)
    _add_bool(el, "CONTENTNEGISPOS", aa.content_neg_is_pos)
    _add_bool(el, "ISLASTDEEMEDPOSITIVE", aa.is_last_deemed_positive)
    _add_bool(el, "ISCAPVATTAXALTERED", aa.is_cap_vat_tax_altered)
    _add_bool(el, "ISCAPVATNOTCLAIMED", aa.is_cap_vat_not_claimed)
    _add(el, "AMOUNT", aa.amount)

    for tag in LEDGER_ENTRY_EMPTY_LISTS:
        _empty_list(el, tag)


def _build_rate_detail(parent: ET.Element, rd: GSTRateDetail) -> None:
    el = ET.SubElement(parent, "RATEDETAILS.LIST")
    _add(el, "GSTRATEDUTYHEAD", rd.gst_rate_duty_head)
    _add(el, "GSTRATEVALUATIONTYPE", rd.gst_rate_valuation_type)
    _add(el, "GSTRATE", rd.gst_rate)


def _build_inventory_entry(parent: ET.Element, ie: InventoryEntry) -> None:
    el = ET.SubElement(parent, "ALLINVENTORYENTRIES.LIST")
    _add(el, "STOCKITEMNAME", ie.stock_item_name)
    _add(el, "GSTOVRDNINELIGIBLEITC", ie.gst_ovrdn_ineligible_itc)
    _add(el, "GSTOVRDNISREVCHARGEAPPL", ie.gst_ovrdn_is_rev_charge_appl)
    _add(el, "GSTOVRDNTAXABILITY", ie.gst_ovrdn_taxability)
    _add(el, "GSTSOURCETYPE", ie.gst_source_type)
    _add(el, "GSTLEDGERSOURCE", ie.gst_ledger_source)
    _add(el, "HSNSOURCETYPE", ie.hsn_source_type)
    _add(el, "HSNITEMSOURCE", ie.hsn_item_source)
    _add(el, "GSTOVRDNSTOREDNATURE", ie.gst_ovrdn_stored_nature)
    _add(el, "GSTOVRDNTYPEOFSUPPLY", ie.gst_ovrdn_type_of_supply)
    _add(el, "GSTRATEINFERAPPLICABILITY", ie.gst_rate_infer_applicability)
    _add(el, "GSTHSNNAME", ie.gst_hsn_name)
    _add(el, "GSTHSNDESCRIPTION", ie.gst_hsn_description)
    _add(el, "GSTHSNINFERAPPLICABILITY", ie.gst_hsn_infer_applicability)

    _add_bool(el, "ISDEEMEDPOSITIVE", ie.is_deemed_positive, "Yes")
    _add_bool(el, "ISGSTASSESSABLEVALUEOVERRIDDEN", ie.is_gst_assessable_value_overridden)
    _add_bool(el, "STRDISGSTAPPLICABLE", ie.strd_is_gst_applicable)
    _add_bool(el, "CONTENTNEGISPOS", ie.content_neg_is_pos)
    _add_bool(el, "ISLASTDEEMEDPOSITIVE", ie.is_last_deemed_positive, "Yes")
    _add_bool(el, "ISAUTONEGATE", ie.is_auto_negate)
    _add_bool(el, "ISCUSTOMSCLEARANCE", ie.is_customs_clearance)
    _add_bool(el, "ISTRACKCOMPONENT", ie.is_track_component)
    _add_bool(el, "ISTRACKPRODUCTION", ie.is_track_production)
    _add_bool(el, "ISPRIMARYITEM", ie.is_primary_item)
    _add_bool(el, "ISSCRAP", ie.is_scrap)

    _add(el, "RATE", ie.rate)
    _add(el, "AMOUNT", ie.amount)
    _add(el, "ACTUALQTY", ie.actual_qty)
    _add(el, "BILLEDQTY", ie.billed_qty)

    # Batch allocations
    if ie.batch_allocations:
        for ba in ie.batch_allocations:
            _build_batch_allocation(el, ba)

    # Accounting allocations
    if ie.accounting_allocations:
        for aa in ie.accounting_allocations:
            _build_accounting_allocation(el, aa)

    _empty_list(el, "DUTYHEADDETAILS.LIST")

    # Rate details
    if ie.rate_details:
        for rd in ie.rate_details:
            _build_rate_detail(el, rd)

    for tag in INVENTORY_TRAILING_EMPTY_LISTS:
        _empty_list(el, tag)


def _build_ledger_entry(parent: ET.Element, le: LedgerEntry) -> None:
    el = ET.SubElement(parent, "LEDGERENTRIES.LIST")

    # Old audit entry
    oa = ET.SubElement(el, "OLDAUDITENTRYIDS.LIST")
    oa.set("TYPE", "Number")
    oav = ET.SubElement(oa, "OLDAUDITENTRYIDS")
    oav.text = "-1"

    # Rate of invoice tax (for duty ledgers)
    if le.rate_of_invoice_tax:
        rt_list = ET.SubElement(el, "RATEOFINVOICETAX.LIST")
        rt_list.set("TYPE", "Number")
        for rate_val in le.rate_of_invoice_tax:
            rv = ET.SubElement(rt_list, "RATEOFINVOICETAX")
            rv.text = rate_val

    _add(el, "APPROPRIATEFOR", le.appropriate_for)
    _add(el, "ROUNDTYPE", le.round_type)
    _add(el, "LEDGERNAME", le.ledger_name)
    _add(el, "GSTCLASS", le.gst_class)
    _add_bool(el, "ISDEEMEDPOSITIVE", le.is_deemed_positive)
    _add_bool(el, "LEDGERFROMITEM", le.ledger_from_item)
    _add_bool(el, "REMOVEZEROENTRIES", le.remove_zero_entries)
    _add_bool(el, "ISPARTYLEDGER", le.is_party_ledger)
    _add_bool(el, "GSTOVERRIDDEN", le.gst_overridden)
    _add_bool(el, "ISGSTASSESSABLEVALUEOVERRIDDEN", le.is_gst_assessable_value_overridden)
    _add_bool(el, "STRDISGSTAPPLICABLE", le.strd_is_gst_applicable)
    _add_bool(el, "STRDGSTISPARTYLEDGER", le.strd_gst_is_party_ledger)
    _add_bool(el, "STRDGSTISDUTYLEDGER", le.strd_gst_is_duty_ledger)
    _add_bool(el, "CONTENTNEGISPOS", le.content_neg_is_pos)
    _add_bool(el, "ISLASTDEEMEDPOSITIVE", le.is_last_deemed_positive)
    _add_bool(el, "ISCAPVATTAXALTERED", le.is_cap_vat_tax_altered)
    _add_bool(el, "ISCAPVATNOTCLAIMED", le.is_cap_vat_not_claimed)
    _add(el, "AMOUNT", le.amount)
    _add(el, "VATEXPAMOUNT", le.vat_exp_amount)

    for tag in LEDGER_ENTRY_EMPTY_LISTS:
        _empty_list(el, tag)


# ==================== MAIN BUILDER ====================


def _build_voucher_element(v: PurchaseVoucher) -> ET.Element:
    vch = ET.Element("VOUCHER")
    vch.set("VCHTYPE", v.voucher_type_name)
    vch.set("ACTION", "Create")
    vch.set("OBJVIEW", "Invoice Voucher View")

    # Address lists
    if v.address_lines:
        addr = ET.SubElement(vch, "ADDRESS.LIST")
        addr.set("TYPE", "String")
        for line in v.address_lines:
            a = ET.SubElement(addr, "ADDRESS")
            a.text = line

    if v.basic_buyer_address_lines:
        baddr = ET.SubElement(vch, "BASICBUYERADDRESS.LIST")
        baddr.set("TYPE", "String")
        for line in v.basic_buyer_address_lines:
            a = ET.SubElement(baddr, "BASICBUYERADDRESS")
            a.text = line

    # Old audit entry
    oa = ET.SubElement(vch, "OLDAUDITENTRYIDS.LIST")
    oa.set("TYPE", "Number")
    oav = ET.SubElement(oa, "OLDAUDITENTRYIDS")
    oav.text = "-1"

    # Dates
    d = ET.SubElement(vch, "DATE")
    d.text = v.date
    _add(vch, "REFERENCEDATE", v.reference_date or v.date)
    _add(vch, "VCHSTATUSDATE", v.vch_status_date or v.date)

    # Entered by / action
    _add(vch, "OBJECTUPDATEACTION", "Create")

    # Scalars
    for field_name, tag_name in VOUCHER_SCALARS:
        val = getattr(v, field_name, None)
        _add(vch, tag_name, val)

    # GST Registration element with attributes
    if v.gst_registration_text:
        gst_reg = ET.SubElement(vch, "GSTREGISTRATION")
        gst_reg.text = v.gst_registration_text
        if v.gst_registration_tax_type:
            gst_reg.set("TAXTYPE", v.gst_registration_tax_type)
        if v.gst_registration_tax_registration:
            gst_reg.set("TAXREGISTRATION", v.gst_registration_tax_registration)

    # Voucher type name (required)
    vtn = ET.SubElement(vch, "VOUCHERTYPENAME")
    vtn.text = v.voucher_type_name

    # Party ledger name (required)
    pln = ET.SubElement(vch, "PARTYLEDGERNAME")
    pln.text = v.party_ledger_name

    # Effective date
    _add(vch, "EFFECTIVEDATE", v.effective_date or v.date)

    # Boolean flags
    for field_name, tag_name, default in VOUCHER_BOOLS:
        val = getattr(v, field_name, None)
        _add_bool(vch, tag_name, val, default)

    # Empty lists before inventory
    for tag in VOUCHER_EMPTY_LISTS:
        _empty_list(vch, tag)

    # Inventory entries
    if v.inventory_entries:
        for ie in v.inventory_entries:
            _build_inventory_entry(vch, ie)

    # Trailing empty lists between inventory and ledger entries
    for tag in VOUCHER_TRAILING_EMPTY_LISTS:
        _empty_list(vch, tag)

    # Ledger entries
    if v.ledger_entries:
        for le in v.ledger_entries:
            _build_ledger_entry(vch, le)

    # Final empty lists
    for tag in VOUCHER_FINAL_EMPTY_LISTS:
        _empty_list(vch, tag)

    return vch


def build_purchase_xml(payload: CreatePurchasePayload) -> str:
    """Build complete Tally XML envelope for purchase vouchers."""
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
    # Fix Tally's &#4; control char prefix (ET double-escapes & to &amp;)
    xml_str = xml_str.replace("&amp;#4;", "&#4;")
    return xml_str
