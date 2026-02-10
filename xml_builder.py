"""Build Tally-compatible XML for ledger creation from Pydantic models."""

import xml.etree.ElementTree as ET

from models import (
    AuditDetails,
    BillAllocation,
    ChequeRange,
    ContactDetails,
    CreateLedgerPayload,
    GSTDetails,
    GSTRegDetails,
    HSNDetails,
    InterestCollection,
    LedgerRequest,
    LowerDeduction,
    MSMEDetails,
    MultiAddress,
    PaymentDetails,
    SchVIDetails,
    TDSDeductionRule,
    TDSExemptionRule,
)


def _bool_to_yesno(val: bool | None, default: str = "No") -> str:
    if val is None:
        return default
    return "Yes" if val else "No"


def _add_text_element(parent: ET.Element, tag: str, text: str | None) -> None:
    """Add a child element with text only if text is not None."""
    if text is not None:
        el = ET.SubElement(parent, tag)
        el.text = text


def _add_bool_element(
    parent: ET.Element, tag: str, val: bool | None, default: str = "No"
) -> None:
    el = ET.SubElement(parent, tag)
    el.text = _bool_to_yesno(val, default)


def _add_empty_list(parent: ET.Element, tag: str) -> None:
    """Add an empty Tally list: <TAG.LIST>      </TAG.LIST>"""
    el = ET.SubElement(parent, tag)
    el.text = "      "


def _add_address_list(parent: ET.Element, lines: list[str] | None) -> None:
    """Add ADDRESS.LIST with TYPE attribute."""
    addr_list = ET.SubElement(parent, "ADDRESS.LIST")
    addr_list.set("TYPE", "String")
    if lines:
        for line in lines:
            addr_el = ET.SubElement(addr_list, "ADDRESS")
            addr_el.text = line


# ==================== SCALAR FIELD MAP ====================
# Maps LedgerRequest field names to XML tag names for simple text fields.
SCALAR_FIELDS: list[tuple[str, str]] = [
    ("parent", "PARENT"),
    ("currency_name", "CURRENCYNAME"),
    ("mailing_name", "MAILINGNAME"),
    ("description", "DESCRIPTION"),
    ("opening_balance", "OPENINGBALANCE"),
    ("country_of_residence", "COUNTRYOFRESIDENCE"),
    ("starting_from", "STARTINGFROM"),
    # Contact
    ("email", "EMAIL"),
    ("email_cc", "EMAILCC"),
    ("ledger_mobile", "LEDGERMOBILE"),
    ("ledger_phone", "LEDGERPHONE"),
    ("ledger_contact", "LEDGERCONTACT"),
    ("ledger_fax", "LEDGERFAX"),
    ("ledger_country_isd_code", "LEDGERCOUNTRYISDCODE"),
    ("website", "WEBSITE"),
    # Tax Registration
    ("income_tax_number", "INCOMETAXNUMBER"),
    ("name_on_pan", "NAMEONPAN"),
    ("gst_registration_type", "GSTREGISTRATIONTYPE"),
    ("vat_dealer_type", "VATDEALERTYPE"),
    ("party_gstin", "PARTYGSTIN"),
    ("gst_type_of_supply", "GSTTYPEOFSUPPLY"),
    ("gst_nature_of_supply", "GSTNATUREOFSUPPLY"),
    ("gst_appropriate_to", "GSTAPPROPRIATETO"),
    ("prior_state_name", "PRIORSTATENAME"),
    ("old_led_state_name", "OLDLEDSTATENAME"),
    ("old_country_name", "OLDCOUNTRYNAME"),
    ("old_pincode", "OLDPINCODE"),
    # Tax Classification
    ("tax_classification_name", "TAXCLASSIFICATIONNAME"),
    ("tax_type", "TAXTYPE"),
    ("gst_type", "GSTTYPE"),
    ("appropriate_for", "APPROPRIATEFOR"),
    ("basic_type_of_duty", "BASICTYPEOFDUTY"),
    ("sys_debit_parent", "SYSDEBITPARENT"),
    # Duties & Taxes
    ("gst_duty_head", "GSTDUTYHEAD"),
    ("rate_of_tax_calculation", "RATEOFTAXCALCULATION"),
    ("rounding_method", "ROUNDINGMETHOD"),
    ("rounding_limit", "ROUNDINGLIMIT"),
    ("led_addl_alloc_type", "LEDADDLALLOCTYPE"),
    # GST Applicability
    ("gst_applicable", "GSTAPPLICABLE"),
    # TDS
    ("is_tds_applicable", "ISTDSAPPLICABLE"),
    ("tds_applicable", "TDSAPPLICABLE"),
    ("tds_deductee_type", "TDSDEDUCTEETYPE"),
    ("tds_deductee_type_mst", "TDSDEDUCTEETYPEMST"),
    ("tds_rate_name", "TDSRATENAME"),
    # TCS
    ("is_tcs_applicable", "ISTCSAPPLICABLE"),
    ("tcs_applicable", "TCSAPPLICABLE"),
    # VAT
    ("vat_applicable", "VATAPPLICABLE"),
    # Excise
    ("excise_applicability", "EXCISEAPPLICABILITY"),
    ("excise_alloc_type", "EXCISEALLOCTYPE"),
    ("excise_duty_type", "EXCISEDUTYTYPE"),
    ("excise_ledger_classification", "EXCISELEDGERCLASSIFICATION"),
    ("excise_nature_of_purchase", "EXCISENATUREOFPURCHASE"),
    # Service Tax
    ("service_tax_applicable", "SERVICETAXAPPLICABLE"),
    ("service_category", "SERVICECATEGORY"),
    ("ledger_fbt_category", "LEDGERFBTCATEGORY"),
    ("it_exempt_applicable", "ITEXEMPTAPPLICABLE"),
    # Bank Account
    ("bank_acch_older_name", "BANKACCHOLDERNAME"),
    ("bank_details", "BANKDETAILS"),
    ("ifs_code", "IFSCODE"),
    ("branch_name", "BRANCHNAME"),
    ("banking_config_bank", "BANKINGCONFIGBANK"),
    ("banking_config_bank_id", "BANKINGCONFIGBANKID"),
    ("bank_capsule_id", "BANKCAPSULEID"),
    ("bank_config_ifsc", "BANKCONFIGIFSC"),
    ("bank_config_short_code", "BANKCONFIGSHORTCODE"),
    ("encrypted_by", "ENCRYPTEDBY"),
    ("imf_name", "IMFNAME"),
    ("new_imf_location", "NEWIMFLOCATION"),
    ("imported_imf_location", "IMPORTEDIMFLOCATION"),
    ("payment_inst_location", "PAYMENTINSTLOCATION"),
    ("customer_code", "CUSTOMERCODE"),
    # Interest
    ("is_interest_on", "ISINTERESTON"),
    ("type_of_interest_on", "TYPEOFINTERESTON"),
    ("interest_incl_day_of_addition", "INTERESTINCLDAYOFADDITION"),
    ("interest_incl_day_of_deduction", "INTERESTINCLDAYOFDEDUCTION"),
    ("is_interest_incl_last_day", "ISINTERESTINCLLASTDAY"),
    ("interest_on_billwise", "INTERESTONBILLWISE"),
    ("override_interest", "OVERRIDEINTEREST"),
    ("override_adv_interest", "OVERRIDEADVINTEREST"),
    # Schedule VI
    ("schvi_credit_parent", "SCHVICREDITPARENT"),
    ("schvi_debit_parent", "SCHVIDEBITPARENT"),
    ("balancing_type", "BALANCINGTYPE"),
    # MSME
    ("enterprise_type", "ENTERPRISETYPE"),
    ("udyam_reg_number", "UDYAMREGNUMBER"),
]

# Boolean flag fields -> XML tag. All default to "No".
BOOL_FLAGS: list[tuple[str, str]] = [
    ("is_bill_wise_on", "ISBILLWISEON"),
    ("is_cost_centres_on", "ISCOSTCENTRESON"),
    ("affects_stock", "AFFECTSSTOCK"),
    ("for_payroll", "FORPAYROLL"),
    ("is_cheque_printing_enabled", "ISCHEQUEPRINTINGENABLED"),
    ("is_related_party", "ISRELATEDPARTY"),
    ("is_gst_applicable", "ISGSTAPPLICABLE"),
    ("is_excise_applicable", "ISEXCISEAPPLICABLE"),
    ("allow_in_mobile", "ALLOWINMOBILE"),
    ("is_cost_tracking_on", "ISCOSTTRACKINGON"),
    ("plas_income_expense", "PLASINCOMEEXPENSE"),
    ("is_ebanking_enabled", "ISEBANKINGENABLED"),
    ("is_deleted", "ISDELETED"),
    ("is_abc_enabled", "ISABCENABLED"),
    ("is_behave_as_duty", "ISBEHAVEASDUTY"),
    ("is_beneficiary_code_on", "ISBENEFICIARYCODEON"),
    ("is_bnf_code_supported", "ISBNFCODESUPPORTED"),
    ("is_condensed", "ISCONDENSED"),
    ("is_credit_days_chk_on", "ISCREDITDAYSCHKON"),
    ("is_exempted", "ISEXEMPTED"),
    ("is_export_file_encrypted", "ISEXPORTFILEENCRYPTED"),
    ("is_export_on_vch_create", "ISEXPORTONVCHCREATE"),
    ("is_fbt_applicable", "ISFBTAPPLICABLE"),
    ("is_input_credit", "ISINPUTCREDIT"),
    ("is_edli_applicable", "ISEDLIAPPLICABLE"),
    ("is_tds_expense", "ISTDSEXPENSE"),
    ("is_tds_projected", "ISTDSPROJECTED"),
    ("tds_deductee_is_special_rate", "TDSDEDUCTEEISSPECIALRATE"),
    ("ignore_tds_exempt", "IGNORETDSEXEMPT"),
    ("appropriate_tax_value", "APPROPRIATETAXVALUE"),
    ("is_against_form_c", "ISAGAINSTFORMC"),
    ("is_stx_party", "ISSTXPARTY"),
    ("is_stx_non_realized_type", "ISSTXNONREALIZEDTYPE"),
    ("for_service_tax", "FORSERVICETAX"),
    ("is_party_exempted", "ISPARTYEXEMPTED"),
    ("is_sez_party", "ISSEZPARTY"),
    ("is_oth_territory_assessee", "ISOTHTERRITORYASSESSEE"),
    ("is_transporter", "ISTRANSPORTER"),
    ("is_rate_inclusive_vat", "ISRATEINCLUSIVEVAT"),
    ("use_for_vat", "USEFORVAT"),
    ("use_for_esi_eligibility", "USEFORESIELIGIBILITY"),
    ("use_for_gratuity", "USEFORGRATUITY"),
    ("use_for_kkc", "USEFORKKC"),
    ("use_for_sbc", "USEFORSBC"),
    ("use_for_purchase_tax", "USEFORPURCHASETAX"),
    ("use_for_notional_itc", "USEFORNOTIONALITC"),
    ("use_as_notional_bank", "USEASNOTIONALBANK"),
    ("is_used_for_cvd", "ISUSEDFORCVD"),
    ("is_excise_merchant_exporter", "ISEXCISEMERCHANTEXPORTER"),
    ("is_ecomm_operator", "ISECOMMOPERATOR"),
    ("override_based_on_realization", "OVERRIDEBASEDONREALIZATION"),
    ("override_credit_limit", "OVERRIDECREDITLIMIT"),
    ("ignore_mismatch_with_warning", "IGNOREMISMATCHWITHWARNING"),
    ("behave_as_payment_gateway", "BEHAVEASPAYMENTGATEWAY"),
    ("led_belongs_to_non_taxable", "LEDBELONGSTONONTAXABLE"),
    ("is_ecash_ledger", "ISECASHLEDGER"),
    ("is_ecd_iff_in_sd_date", "ISECDIFFINSDDATE"),
    ("consider_purchase_for_export", "CONSIDERPURCHASEFOREXPORT"),
    ("allow_export_with_errors", "ALLOWEXPORTWITHERRORS"),
    ("show_in_payslip", "SHOWINPAYSLIP"),
    ("is_salary_mul_file", "ISSALARYMULFILE"),
    ("is_salary_grouped", "ISSALARYGROUPED"),
    ("is_salary_trans_grouped_for_brs", "ISSALARYTRANSGROUPEDFORBRS"),
    ("is_abatement_applicable", "ISABATEMENTAPPLICABLE"),
    ("is_pay_upload", "ISPAYUPLOAD"),
    ("is_pay_batch_only_sal", "ISPAYBATCHONLYSAL"),
    ("is_pymt_adv_online", "ISPYMTADVONLINE"),
    ("is_pymt_adv_cc_enabled", "ISPYMTADVCCENABLED"),
    ("is_include_pymt_adv_billwise", "ISINCLUDEPYMTADVBILLWISE"),
    ("is_product_code_based", "ISPRODUCTCODEBASED"),
    ("is_filename_format_supported", "ISFILENAMEFORMATSUPPORTED"),
    ("has_client_code", "HASCLIENTCODE"),
    ("is_batch_enabled", "ISBATCHENABLED"),
    ("is_scb_uae", "ISSCBUAE"),
    ("is_bank_status_app", "ISBANKSTATUSAPP"),
    ("bank_is_reconcile_perfect_matches", "BANKISRECONCILEPERFECTMATCHES"),
    ("is_ebanking_supported", "ISEBANKINGSUPPORTED"),
    ("is_echeque_supported", "ISECHEQUESUPPORTED"),
    ("is_edd_supported", "ISEDDSUPPORTED"),
    ("has_echeque_city", "HASECHEQUECITY"),
    ("has_echeque_delivery_mode", "HASECHEQUEDELIVERYMODE"),
    ("has_echeque_delivery_to", "HASECHEQUEDELIVERYTO"),
    ("has_echeque_print_location", "HASECHEQUEPRINTLOCATION"),
    ("has_echeque_payable_location", "HASECHEQUEPAYABLELOCATION"),
    ("has_echeque_bank_location", "HASECHEQUEBANKLOCATION"),
    ("has_edd_city", "HASEDDCITY"),
    ("has_edd_delivery_mode", "HASEDDDELIVERYMODE"),
    ("has_edd_delivery_to", "HASEDDDELIVERYTO"),
    ("has_edd_print_location", "HASEDDPRINTLOCATION"),
    ("has_edd_payable_location", "HASEDDPAYABLELOCATION"),
    ("has_edd_bank_location", "HASEDDBANKLOCATION"),
    ("payins_is_batch_applicable", "PAYINSISBATCHAPPLICABLE"),
    ("payins_is_file_num_app", "PAYINSISFILENUMAPP"),
    ("audited", "AUDITED"),
]

# Standard empty lists that Tally expects
STANDARD_EMPTY_LISTS: list[str] = [
    "SERVICETAXDETAILS.LIST",
    "LBTREGNDETAILS.LIST",
    "VATDETAILS.LIST",
    "SALESTAXCESSDETAILS.LIST",
    "EXCISEJURISDICTIONDETAILS.LIST",
    "EXCLUDEDTAXATIONS.LIST",
    "BANKALLOCATIONS.LIST",
    "LEDGERCLOSINGVALUES.LIST",
    "LEDGERAUDITCLASS.LIST",
    "OLDAUDITENTRIES.LIST",
    "TDSCATEGORYDETAILS.LIST",
    "TCSCATEGORYDETAILS.LIST",
    "STXABATEMENTDETAILS.LIST",
    "STXTAXDETAILS.LIST",
    "INPUTCRALLOCS.LIST",
    "TCSMETHODOFCALCULATION.LIST",
    "BANKEXPORTFORMATS.LIST",
    "TRANSFERMODELIMITDETAILS.LIST",
    "XBRLDETAIL.LIST",
    "EXCISETARIFFDETAILS.LIST",
    "GSTRECONPREFIXSUFFIXDETAILS.LIST",
    "GSTCLASSFNIGSTRATES.LIST",
    "EXTARIFFDUTYHEADDETAILS.LIST",
    "TEMPGSTITEMSLABRATES.LIST",
    "LEDGSTADDRESS.LIST",
    "LEDADDRESS.LIST",
    "ACCOUNTAUDITENTRIES.LIST",
    "AUDITENTRIES.LIST",
    "CANCELLEDPAYALLOCATIONS.LIST",
    "DEFAULTCHEQUEDETAILS.LIST",
    "DEFAULTOPENINGCHEQUEDETAILS.LIST",
    "DEFAULTVCHCHEQUEDETAILS.LIST",
    "ECHEQUEPRINTLOCATION.LIST",
    "ECHEQUEPAYABLELOCATION.LIST",
    "EDDPRINTLOCATION.LIST",
    "EDDPAYABLELOCATION.LIST",
    "BANKURENTRIES.LIST",
    "BRSIMPORTEDINFO.LIST",
    "AUTOBRSCONFIGS.LIST",
    "AVAILABLETRANSACTIONTYPES.LIST",
    "VOUCHERTYPEPRODUCTCODES.LIST",
    "DEFMULTIPLETOPHONENO.LIST",
    "SLABPERIOD.LIST",
    "GRATUITYPERIOD.LIST",
    "ADDITIONALCOMPUTATIONS.LIST",
]


# ==================== LIST BUILDERS ====================


def _build_mailing_details(parent: ET.Element, md) -> None:
    el = ET.SubElement(parent, "LEDMAILINGDETAILS.LIST")
    _add_address_list(el, md.address_lines)
    _add_text_element(el, "APPLICABLEFROM", md.applicable_from)
    _add_text_element(el, "PINCODE", md.pincode)
    _add_text_element(el, "MAILINGNAME", md.mailing_name)
    _add_text_element(el, "STATE", md.state)
    _add_text_element(el, "COUNTRY", md.country)


def _build_multi_address(parent: ET.Element, ma: MultiAddress) -> None:
    el = ET.SubElement(parent, "LEDMULTIADDRESSLIST.LIST")
    _add_text_element(el, "ADDRESSNAME", ma.address_name)
    _add_address_list(el, ma.address_lines)
    _add_text_element(el, "PINCODE", ma.pincode)
    _add_text_element(el, "STATE", ma.state)
    _add_text_element(el, "COUNTRYNAME", ma.country_name)
    _add_text_element(el, "COUNTRYISDCODE", ma.country_isd_code)
    _add_text_element(el, "EMAIL", ma.email)
    _add_text_element(el, "PRIORSTATENAME", ma.prior_state_name)
    _add_text_element(el, "PLACEOFSUPPLY", ma.place_of_supply)
    _add_text_element(el, "INCOMETAXNUMBER", ma.income_tax_number)
    _add_text_element(el, "GSTREGISTRATIONTYPE", ma.gst_registration_type)
    _add_text_element(el, "VATDEALERTYPE", ma.vat_dealer_type)
    _add_text_element(el, "PARTYGSTIN", ma.party_gstin)
    _add_bool_element(el, "ISOTHTERRITORYASSESSEE", ma.is_oth_territory_assessee)
    _add_bool_element(el, "ISPARTYEXEMPTED", ma.is_party_exempted)
    _add_bool_element(el, "ISSEZPARTY", ma.is_sez_party)
    _add_bool_element(
        el, "ISEXCISEMERCHANTEXPORTER", ma.is_excise_merchant_exporter
    )
    _add_empty_list(el, "LEDGSTADDRESS.LIST")
    _add_empty_list(el, "EXCISEJURISDICTIONDETAILS.LIST")


def _build_gst_reg_details(parent: ET.Element, grd: GSTRegDetails) -> None:
    el = ET.SubElement(parent, "LEDGSTREGDETAILS.LIST")
    _add_text_element(el, "APPLICABLEFROM", grd.applicable_from)
    _add_text_element(el, "GSTREGISTRATIONTYPE", grd.gst_registration_type)
    _add_text_element(el, "STATE", grd.state)
    _add_text_element(el, "PLACEOFSUPPLY", grd.place_of_supply)
    _add_text_element(el, "GSTIN", grd.gstin)
    _add_bool_element(el, "ISOTHTERRITORYASSESSEE", grd.is_oth_territory_assessee)
    _add_bool_element(
        el, "CONSIDERPURCHASEFOREXPORT", grd.consider_purchase_for_export
    )
    _add_bool_element(el, "ISTRANSPORTER", grd.is_transporter)
    _add_bool_element(el, "ISCOMMONPARTY", grd.is_common_party)


def _build_payment_details(parent: ET.Element, pd: PaymentDetails) -> None:
    el = ET.SubElement(parent, "PAYMENTDETAILS.LIST")
    _add_text_element(el, "IFSCODE", pd.ifsc_code)
    _add_text_element(el, "BANKNAME", pd.bank_name)
    _add_text_element(el, "ACCOUNTNUMBER", pd.account_number)
    _add_text_element(el, "PAYMENTFAVOURING", pd.payment_favouring)
    _add_text_element(el, "TRANSACTIONNAME", pd.transaction_name)
    _add_text_element(el, "BANKID", pd.bank_id)
    _add_text_element(el, "SWIFTCODE", pd.swift_code)
    _add_bool_element(el, "SETASDEFAULT", pd.set_as_default)
    _add_text_element(el, "DEFAULTTRANSACTIONTYPE", pd.default_transaction_type)
    # Beneficiary code sub-list
    bnf = ET.SubElement(el, "BENEFICIARYCODEDETAILS.LIST")
    _add_text_element(bnf, "COMPANYBANK", pd.company_bank)


def _build_tds_deduction_rule(parent: ET.Element, rule: TDSDeductionRule) -> None:
    el = ET.SubElement(parent, "DEDUCTINSAMEVCHRULES.LIST")
    _add_text_element(el, "NATUREOFPAYMENT", rule.nature_of_payment)


def _build_lower_deduction(parent: ET.Element, ld: LowerDeduction) -> None:
    el = ET.SubElement(parent, "LOWERDEDUCTION.LIST")
    _add_text_element(el, "CERTIFICATENO", ld.certificate_no)
    _add_text_element(el, "VALIDFROM", ld.valid_from)
    _add_text_element(el, "VALIDTO", ld.valid_to)
    _add_text_element(el, "LIMITAMOUNT", ld.limit_amount)
    _add_text_element(el, "RATEOFDEDUCTION", ld.rate_of_deduction)
    _add_text_element(el, "NATUREOFPAYMENT", ld.nature_of_payment)


def _build_tds_exemption_rule(parent: ET.Element, rule: TDSExemptionRule) -> None:
    el = ET.SubElement(parent, "TDSEXEMPTIONRULES.LIST")
    _add_text_element(el, "NATUREOFPAYMENT", rule.nature_of_payment)


def _build_interest_collection(parent: ET.Element, ic: InterestCollection) -> None:
    el = ET.SubElement(parent, "INTERESTCOLLECTION.LIST")
    _add_text_element(el, "INTERESTFROMDATE", ic.interest_from_date)
    _add_text_element(el, "INTERESTTODATE", ic.interest_to_date)
    _add_text_element(el, "INTERESTSTYLE", ic.interest_style)
    _add_text_element(el, "INTERESTBALANCETYPE", ic.interest_balance_type)
    _add_text_element(el, "ROUNDTYPE", ic.round_type)
    _add_text_element(el, "INTERESTRATE", ic.interest_rate)


def _build_gst_details(parent: ET.Element, gd: GSTDetails) -> None:
    el = ET.SubElement(parent, "GSTDETAILS.LIST")
    _add_text_element(el, "APPLICABLEFROM", gd.applicable_from)
    _add_text_element(el, "SRCOFGSTDETAILS", gd.src_of_gst_details)
    _add_text_element(el, "HSNCODE", gd.hsn_code)
    _add_text_element(el, "TAXABILITY", gd.taxability)
    _add_text_element(el, "GSTNATUREOFTRANSACTION", gd.gst_nature_of_transaction)
    _add_bool_element(el, "GSTCALCSLABONMRP", gd.gst_calc_slab_on_mrp)
    _add_bool_element(
        el, "ISREVERSECHARGEAPPLICABLE", gd.is_reverse_charge_applicable
    )
    _add_bool_element(el, "ISNONGSTGOODS", gd.is_non_gst_goods)
    _add_bool_element(el, "GSTINELIGIBLEITC", gd.gst_ineligible_itc)
    _add_bool_element(el, "INCLUDEEXPFORSLABCALC", gd.include_exp_for_slab_calc)

    # State-wise details
    if gd.state_wise_details:
        for swd in gd.state_wise_details:
            swd_el = ET.SubElement(el, "STATEWISEDETAILS.LIST")
            _add_text_element(swd_el, "STATENAME", swd.state_name)
            if swd.rate_details:
                for rd in swd.rate_details:
                    rd_el = ET.SubElement(swd_el, "RATEDETAILS.LIST")
                    _add_text_element(rd_el, "GSTRATEDUTYHEAD", rd.gst_rate_duty_head)
                    _add_text_element(
                        rd_el,
                        "GSTRATEVALUATIONTYPE",
                        rd.gst_rate_valuation_type,
                    )
                    _add_text_element(rd_el, "GSTRATE", rd.gst_rate)
            _add_empty_list(swd_el, "GSTSLABRATES.LIST")

    _add_empty_list(el, "TEMPGSTDETAILSLABRATES.LIST")
    _add_empty_list(el, "TEMPGSTITEMSLABRATES.LIST")


def _build_hsn_details(parent: ET.Element, hd: HSNDetails) -> None:
    el = ET.SubElement(parent, "HSNDETAILS.LIST")
    _add_text_element(el, "APPLICABLEFROM", hd.applicable_from)
    _add_text_element(el, "HSNCODE", hd.hsn_code)
    _add_text_element(el, "HSN", hd.hsn)
    _add_text_element(el, "SRCOFHSNDETAILS", hd.src_of_hsn_details)


def _build_bill_allocation(parent: ET.Element, ba: BillAllocation) -> None:
    el = ET.SubElement(parent, "BILLALLOCATIONS.LIST")
    _add_text_element(el, "NAME", ba.name)
    _add_text_element(el, "BILLTYPE", ba.bill_type)
    _add_text_element(el, "BILLDATE", ba.bill_date)
    _add_text_element(el, "BILLCREDITPERIOD", ba.bill_credit_period)
    _add_text_element(el, "AMOUNT", ba.amount)
    _add_text_element(el, "OPENINGBALANCE", ba.opening_balance)
    _add_bool_element(el, "ISADVANCE", ba.is_advance)
    _add_empty_list(el, "INTERESTCOLLECTION.LIST")


def _build_contact_details(parent: ET.Element, cd: ContactDetails) -> None:
    el = ET.SubElement(parent, "CONTACTDETAILS.LIST")
    _add_text_element(el, "NAME", cd.name)
    _add_text_element(el, "CONTACTPERSON", cd.contact_person)
    _add_text_element(el, "MOBILE", cd.mobile)
    _add_text_element(el, "PHONE", cd.phone)
    _add_text_element(el, "PHONENUMBER", cd.phone_number)
    _add_text_element(el, "EMAIL", cd.email)
    _add_text_element(el, "COUNTRYISDCODE", cd.country_isd_code)
    _add_bool_element(el, "ISDEFAULTWHATSAPPNUM", cd.is_default_whatsapp_num)


def _build_msme_details(parent: ET.Element, md: MSMEDetails) -> None:
    el = ET.SubElement(parent, "MSMEREGISTRATIONDETAILS.LIST")
    _add_text_element(el, "APPLICABLEFROM", md.applicable_from)
    _add_text_element(el, "FROMDATE", md.from_date)
    _add_text_element(el, "ENTERPRISETYPE", md.enterprise_type)
    _add_text_element(el, "UDYAMREGNUMBER", md.udyam_reg_number)
    _add_text_element(el, "MSMEACTIVITYTYPE", md.msme_activity_type)


def _build_cheque_range(parent: ET.Element, cr: ChequeRange) -> None:
    el = ET.SubElement(parent, "CHEQUERANGE.LIST")
    _add_text_element(el, "CHEQUEFROM", cr.cheque_from)
    _add_text_element(el, "CHEQUETO", cr.cheque_to)


def _build_audit_details(parent: ET.Element, ad: AuditDetails) -> None:
    el = ET.SubElement(parent, "AUDITDETAILS.LIST")
    _add_text_element(el, "PERIODFROM", ad.period_from)
    _add_text_element(el, "PERIODTO", ad.period_to)
    _add_text_element(el, "AUDITPERIODFROM", ad.audit_period_from)
    _add_bool_element(el, "ISCLAUSE17APPLICABLE", ad.is_clause17_applicable)
    _add_bool_element(el, "ISGROUPFORLOANPYMNT", ad.is_group_for_loan_pymnt)
    _add_bool_element(el, "ISGROUPFORLOANRCPT", ad.is_group_for_loan_rcpt)
    _add_bool_element(el, "ISPERIODICLEDGER", ad.is_periodic_ledger)
    _add_bool_element(el, "ISRELATEDPARTY", ad.is_related_party)


def _build_schvi_details(parent: ET.Element, sd: SchVIDetails) -> None:
    el = ET.SubElement(parent, "SCHVIDETAILS.LIST")
    _add_text_element(el, "PERIODFROM", sd.period_from)
    _add_text_element(el, "BALANCINGTYPE", sd.balancing_type)
    _add_text_element(el, "SCHVICREDITPARENT", sd.schvi_credit_parent)
    _add_text_element(el, "SCHVIDEBITPARENT", sd.schvi_debit_parent)
    _add_empty_list(el, "SCHVIENTRIES.LIST")


# ==================== MAIN BUILDER ====================


def _build_ledger_element(ledger: LedgerRequest) -> ET.Element:
    """Build a single <LEDGER> element."""
    led = ET.Element("LEDGER")
    led.set("NAME", ledger.name)
    led.set("RESERVEDNAME", "")

    # --- Scalar fields ---
    for field_name, tag_name in SCALAR_FIELDS:
        val = getattr(ledger, field_name, None)
        _add_text_element(led, tag_name, val)

    # --- Boolean flags ---
    for field_name, tag_name in BOOL_FLAGS:
        val = getattr(ledger, field_name, None)
        _add_bool_element(led, tag_name, val)

    # Sort position
    sort_el = ET.SubElement(led, "SORTPOSITION")
    sort_el.text = ledger.sort_position if ledger.sort_position else " 1000"

    # --- Mailing Details ---
    if ledger.mailing_details:
        _build_mailing_details(led, ledger.mailing_details)
    else:
        _add_empty_list(led, "LEDMAILINGDETAILS.LIST")

    # --- Multi Address ---
    if ledger.multi_address_list:
        for ma in ledger.multi_address_list:
            _build_multi_address(led, ma)
    else:
        _add_empty_list(led, "LEDMULTIADDRESSLIST.LIST")

    # --- GST Registration ---
    if ledger.gst_reg_details:
        for grd in ledger.gst_reg_details:
            _build_gst_reg_details(led, grd)
    else:
        _add_empty_list(led, "LEDGSTREGDETAILS.LIST")

    # --- Payment Details ---
    if ledger.payment_details:
        for pd in ledger.payment_details:
            _build_payment_details(led, pd)
    else:
        _add_empty_list(led, "PAYMENTDETAILS.LIST")

    # --- TDS Deduction Rules ---
    if ledger.tds_deduction_rules:
        for rule in ledger.tds_deduction_rules:
            _build_tds_deduction_rule(led, rule)
    else:
        _add_empty_list(led, "DEDUCTINSAMEVCHRULES.LIST")

    # --- Lower Deductions ---
    if ledger.lower_deductions:
        for ld in ledger.lower_deductions:
            _build_lower_deduction(led, ld)
    else:
        _add_empty_list(led, "LOWERDEDUCTION.LIST")

    # --- TDS Exemption Rules ---
    if ledger.tds_exemption_rules:
        for rule in ledger.tds_exemption_rules:
            _build_tds_exemption_rule(led, rule)
    else:
        _add_empty_list(led, "TDSEXEMPTIONRULES.LIST")

    # --- Interest Collection ---
    if ledger.interest_collection:
        for ic in ledger.interest_collection:
            _build_interest_collection(led, ic)
    else:
        _add_empty_list(led, "INTERESTCOLLECTION.LIST")

    # --- GST Details ---
    if ledger.gst_details:
        for gd in ledger.gst_details:
            _build_gst_details(led, gd)
    else:
        _add_empty_list(led, "GSTDETAILS.LIST")

    # --- HSN Details ---
    if ledger.hsn_details:
        for hd in ledger.hsn_details:
            _build_hsn_details(led, hd)
    else:
        _add_empty_list(led, "HSNDETAILS.LIST")

    # --- Bill Allocations ---
    if ledger.bill_allocations:
        for ba in ledger.bill_allocations:
            _build_bill_allocation(led, ba)
    else:
        _add_empty_list(led, "BILLALLOCATIONS.LIST")

    # --- Contact Details ---
    if ledger.contact_details:
        for cd in ledger.contact_details:
            _build_contact_details(led, cd)
    else:
        _add_empty_list(led, "CONTACTDETAILS.LIST")

    # --- MSME Details ---
    if ledger.msme_details:
        for md in ledger.msme_details:
            _build_msme_details(led, md)
    else:
        _add_empty_list(led, "MSMEREGISTRATIONDETAILS.LIST")

    # --- Cheque Range ---
    if ledger.cheque_range:
        for cr in ledger.cheque_range:
            _build_cheque_range(led, cr)
    else:
        _add_empty_list(led, "CHEQUERANGE.LIST")

    # --- Audit Details ---
    if ledger.audit_details:
        for ad in ledger.audit_details:
            _build_audit_details(led, ad)
    else:
        _add_empty_list(led, "AUDITDETAILS.LIST")

    # --- Schedule VI Details ---
    if ledger.schvi_details:
        for sd in ledger.schvi_details:
            _build_schvi_details(led, sd)
    else:
        _add_empty_list(led, "SCHVIDETAILS.LIST")

    # --- Language Name ---
    if ledger.language_name:
        ln_el = ET.SubElement(led, "LANGUAGENAME.LIST")
        name_list = ET.SubElement(ln_el, "NAME.LIST")
        name_list.set("TYPE", "String")
        name_sub = ET.SubElement(name_list, "NAME")
        name_sub.text = ledger.language_name.name or ""
        lang_id = ET.SubElement(ln_el, "LANGUAGEID")
        lang_id.text = ledger.language_name.language_id or " 1033"
    else:
        ln_el = ET.SubElement(led, "LANGUAGENAME.LIST")
        name_list = ET.SubElement(ln_el, "NAME.LIST")
        name_list.set("TYPE", "String")
        name_sub = ET.SubElement(name_list, "NAME")
        name_sub.text = ledger.name
        lang_id = ET.SubElement(ln_el, "LANGUAGEID")
        lang_id.text = " 1033"

    # --- Standard empty lists ---
    for tag in STANDARD_EMPTY_LISTS:
        _add_empty_list(led, tag)

    return led


def build_ledger_xml(payload: CreateLedgerPayload) -> str:
    """Build the complete Tally XML envelope for creating ledgers."""
    envelope = ET.Element("ENVELOPE")

    # Header
    header = ET.SubElement(envelope, "HEADER")
    req = ET.SubElement(header, "TALLYREQUEST")
    req.text = "Import Data"

    # Body > ImportData > RequestDesc
    body = ET.SubElement(envelope, "BODY")
    import_data = ET.SubElement(body, "IMPORTDATA")

    request_desc = ET.SubElement(import_data, "REQUESTDESC")
    report_name = ET.SubElement(request_desc, "REPORTNAME")
    report_name.text = "All Masters"
    static_vars = ET.SubElement(request_desc, "STATICVARIABLES")
    company = ET.SubElement(static_vars, "SVCURRENTCOMPANY")
    company.text = payload.company_name
    if payload.username:
        uname = ET.SubElement(static_vars, "SVOWNERNAME")
        uname.text = payload.username
    if payload.password:
        pwd = ET.SubElement(static_vars, "SVOWNERPASSWORD")
        pwd.text = payload.password

    # RequestData
    request_data = ET.SubElement(import_data, "REQUESTDATA")

    for ledger in payload.ledgers:
        tally_msg = ET.SubElement(request_data, "TALLYMESSAGE")
        tally_msg.set("xmlns:UDF", "TallyUDF")
        ledger_el = _build_ledger_element(ledger)
        tally_msg.append(ledger_el)

    # Serialize to string
    ET.indent(envelope, space="  ")
    xml_str = ET.tostring(envelope, encoding="unicode", xml_declaration=False)
    return xml_str
