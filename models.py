from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, model_validator


# ==================== NESTED LIST MODELS ====================


class MailingDetails(BaseModel):
    address_lines: Optional[list[str]] = None
    applicable_from: Optional[str] = None
    pincode: Optional[str] = None
    mailing_name: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class MultiAddress(BaseModel):
    address_name: Optional[str] = None
    address_lines: Optional[list[str]] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    country_name: Optional[str] = None
    country_isd_code: Optional[str] = None
    email: Optional[str] = None
    prior_state_name: Optional[str] = None
    place_of_supply: Optional[str] = None
    income_tax_number: Optional[str] = None
    gst_registration_type: Optional[str] = None
    vat_dealer_type: Optional[str] = None
    party_gstin: Optional[str] = None
    is_oth_territory_assessee: Optional[bool] = None
    is_party_exempted: Optional[bool] = None
    is_sez_party: Optional[bool] = None
    is_excise_merchant_exporter: Optional[bool] = None


class GSTRegDetails(BaseModel):
    applicable_from: Optional[str] = None
    gst_registration_type: Optional[str] = None
    state: Optional[str] = None
    place_of_supply: Optional[str] = None
    gstin: Optional[str] = None
    is_oth_territory_assessee: Optional[bool] = None
    consider_purchase_for_export: Optional[bool] = None
    is_transporter: Optional[bool] = None
    is_common_party: Optional[bool] = None


class PaymentDetails(BaseModel):
    ifsc_code: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    payment_favouring: Optional[str] = None
    transaction_name: Optional[str] = None
    bank_id: Optional[str] = None
    swift_code: Optional[str] = None
    set_as_default: Optional[bool] = None
    default_transaction_type: Optional[str] = None
    company_bank: Optional[str] = None


class TDSDeductionRule(BaseModel):
    nature_of_payment: Optional[str] = None


class LowerDeduction(BaseModel):
    certificate_no: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    limit_amount: Optional[str] = None
    rate_of_deduction: Optional[str] = None
    nature_of_payment: Optional[str] = None


class TDSExemptionRule(BaseModel):
    nature_of_payment: Optional[str] = None


class InterestCollection(BaseModel):
    interest_from_date: Optional[str] = None
    interest_to_date: Optional[str] = None
    interest_style: Optional[str] = None
    interest_balance_type: Optional[str] = None
    round_type: Optional[str] = None
    interest_rate: Optional[str] = None


class GSTRateDetail(BaseModel):
    gst_rate_duty_head: Optional[str] = None
    gst_rate_valuation_type: Optional[str] = "Based on Value"
    gst_rate: Optional[str] = None


class StateWiseDetail(BaseModel):
    state_name: Optional[str] = None
    rate_details: Optional[list[GSTRateDetail]] = None


class GSTDetails(BaseModel):
    applicable_from: Optional[str] = None
    src_of_gst_details: Optional[str] = None
    hsn_code: Optional[str] = None
    taxability: Optional[str] = None
    gst_nature_of_transaction: Optional[str] = None
    gst_calc_slab_on_mrp: Optional[bool] = None
    is_reverse_charge_applicable: Optional[bool] = None
    is_non_gst_goods: Optional[bool] = None
    gst_ineligible_itc: Optional[bool] = None
    include_exp_for_slab_calc: Optional[bool] = None
    state_wise_details: Optional[list[StateWiseDetail]] = None


class HSNDetails(BaseModel):
    applicable_from: Optional[str] = None
    hsn_code: Optional[str] = None
    hsn: Optional[str] = None
    src_of_hsn_details: Optional[str] = None


class BillAllocation(BaseModel):
    name: Optional[str] = None
    bill_type: Optional[str] = None
    bill_date: Optional[str] = None
    bill_credit_period: Optional[str] = None
    amount: Optional[str] = None
    opening_balance: Optional[str] = None
    is_advance: Optional[bool] = None


class ContactDetails(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    country_isd_code: Optional[str] = None
    is_default_whatsapp_num: Optional[bool] = None


class MSMEDetails(BaseModel):
    applicable_from: Optional[str] = None
    from_date: Optional[str] = None
    enterprise_type: Optional[str] = None
    udyam_reg_number: Optional[str] = None
    msme_activity_type: Optional[str] = None


class ChequeRange(BaseModel):
    cheque_from: Optional[str] = None
    cheque_to: Optional[str] = None


class AuditDetails(BaseModel):
    period_from: Optional[str] = None
    period_to: Optional[str] = None
    audit_period_from: Optional[str] = None
    is_clause17_applicable: Optional[bool] = None
    is_group_for_loan_pymnt: Optional[bool] = None
    is_group_for_loan_rcpt: Optional[bool] = None
    is_periodic_ledger: Optional[bool] = None
    is_related_party: Optional[bool] = None


class SchVIDetails(BaseModel):
    period_from: Optional[str] = None
    balancing_type: Optional[str] = None
    schvi_credit_parent: Optional[str] = None
    schvi_debit_parent: Optional[str] = None


class LanguageName(BaseModel):
    name: Optional[str] = None
    language_id: Optional[str] = " 1033"


# ==================== MAIN LEDGER REQUEST ====================


class LedgerRequest(BaseModel):
    # --- Required ---
    name: str
    parent: str

    @model_validator(mode='before')
    @classmethod
    def map_aliases(cls, data):
        """Accept 'gstin' as shorthand for 'party_gstin' and 'country' for 'country_of_residence'."""
        if isinstance(data, dict):
            if 'gstin' in data and 'party_gstin' not in data:
                data['party_gstin'] = data.pop('gstin')
            if 'country' in data and 'country_of_residence' not in data:
                data['country_of_residence'] = data.pop('country')
            # Auto-enable GST when GSTIN is provided
            if data.get('party_gstin') and data.get('is_gst_applicable') is None:
                data['is_gst_applicable'] = True
        return data

    # --- Basic Identity ---
    currency_name: Optional[str] = None
    mailing_name: Optional[str] = None
    description: Optional[str] = None
    opening_balance: Optional[str] = None
    country_of_residence: Optional[str] = None
    starting_from: Optional[str] = None

    # --- Contact ---
    email: Optional[str] = None
    email_cc: Optional[str] = None
    ledger_mobile: Optional[str] = None
    ledger_phone: Optional[str] = None
    ledger_contact: Optional[str] = None
    ledger_fax: Optional[str] = None
    ledger_country_isd_code: Optional[str] = None
    website: Optional[str] = None

    # --- Tax Registration ---
    income_tax_number: Optional[str] = None
    name_on_pan: Optional[str] = None
    gst_registration_type: Optional[str] = None
    vat_dealer_type: Optional[str] = None
    party_gstin: Optional[str] = None
    gst_type_of_supply: Optional[str] = None
    gst_nature_of_supply: Optional[str] = None
    gst_appropriate_to: Optional[str] = None
    prior_state_name: Optional[str] = None
    old_led_state_name: Optional[str] = None
    old_country_name: Optional[str] = None
    old_pincode: Optional[str] = None

    # --- Tax Classification ---
    tax_classification_name: Optional[str] = None
    tax_type: Optional[str] = None
    gst_type: Optional[str] = None
    appropriate_for: Optional[str] = None
    basic_type_of_duty: Optional[str] = None
    sys_debit_parent: Optional[str] = None

    # --- Duties & Taxes ---
    gst_duty_head: Optional[str] = None
    rate_of_tax_calculation: Optional[str] = None
    rounding_method: Optional[str] = None
    rounding_limit: Optional[str] = None
    led_addl_alloc_type: Optional[str] = None

    # --- GST Applicability ---
    gst_applicable: Optional[str] = None

    # --- TDS ---
    is_tds_applicable: Optional[str] = None
    tds_applicable: Optional[str] = None
    tds_deductee_type: Optional[str] = None
    tds_deductee_type_mst: Optional[str] = None
    tds_rate_name: Optional[str] = None

    # --- TCS ---
    is_tcs_applicable: Optional[str] = None
    tcs_applicable: Optional[str] = None

    # --- VAT ---
    vat_applicable: Optional[str] = None

    # --- Excise ---
    excise_applicability: Optional[str] = None
    excise_alloc_type: Optional[str] = None
    excise_duty_type: Optional[str] = None
    excise_ledger_classification: Optional[str] = None
    excise_nature_of_purchase: Optional[str] = None

    # --- Service Tax ---
    service_tax_applicable: Optional[str] = None
    service_category: Optional[str] = None
    ledger_fbt_category: Optional[str] = None
    it_exempt_applicable: Optional[str] = None

    # --- Bank Account ---
    bank_acch_older_name: Optional[str] = None
    bank_details: Optional[str] = None
    ifs_code: Optional[str] = None
    branch_name: Optional[str] = None
    banking_config_bank: Optional[str] = None
    banking_config_bank_id: Optional[str] = None
    bank_capsule_id: Optional[str] = None
    bank_config_ifsc: Optional[str] = None
    bank_config_short_code: Optional[str] = None
    encrypted_by: Optional[str] = None
    imf_name: Optional[str] = None
    new_imf_location: Optional[str] = None
    imported_imf_location: Optional[str] = None
    payment_inst_location: Optional[str] = None
    customer_code: Optional[str] = None

    # --- Interest ---
    is_interest_on: Optional[str] = None
    type_of_interest_on: Optional[str] = None
    interest_incl_day_of_addition: Optional[str] = None
    interest_incl_day_of_deduction: Optional[str] = None
    is_interest_incl_last_day: Optional[str] = None
    interest_on_billwise: Optional[str] = None
    override_interest: Optional[str] = None
    override_adv_interest: Optional[str] = None

    # --- Schedule VI ---
    schvi_credit_parent: Optional[str] = None
    schvi_debit_parent: Optional[str] = None
    balancing_type: Optional[str] = None

    # --- MSME ---
    enterprise_type: Optional[str] = None
    udyam_reg_number: Optional[str] = None

    # --- Behavior Flags (boolean -> Yes/No) ---
    is_bill_wise_on: Optional[bool] = None
    is_cost_centres_on: Optional[bool] = None
    affects_stock: Optional[bool] = None
    for_payroll: Optional[bool] = None
    is_cheque_printing_enabled: Optional[bool] = None
    is_related_party: Optional[bool] = None
    is_gst_applicable: Optional[bool] = None
    is_excise_applicable: Optional[bool] = None
    allow_in_mobile: Optional[bool] = None
    is_cost_tracking_on: Optional[bool] = None
    plas_income_expense: Optional[bool] = None
    is_ebanking_enabled: Optional[bool] = None
    is_deleted: Optional[bool] = None
    is_abc_enabled: Optional[bool] = None
    is_behave_as_duty: Optional[bool] = None
    is_beneficiary_code_on: Optional[bool] = None
    is_bnf_code_supported: Optional[bool] = None
    is_condensed: Optional[bool] = None
    is_credit_days_chk_on: Optional[bool] = None
    is_exempted: Optional[bool] = None
    is_export_file_encrypted: Optional[bool] = None
    is_export_on_vch_create: Optional[bool] = None
    is_fbt_applicable: Optional[bool] = None
    is_input_credit: Optional[bool] = None
    is_edli_applicable: Optional[bool] = None
    is_tds_expense: Optional[bool] = None
    is_tds_projected: Optional[bool] = None
    tds_deductee_is_special_rate: Optional[bool] = None
    ignore_tds_exempt: Optional[bool] = None
    appropriate_tax_value: Optional[bool] = None
    is_against_form_c: Optional[bool] = None
    is_stx_party: Optional[bool] = None
    is_stx_non_realized_type: Optional[bool] = None
    for_service_tax: Optional[bool] = None
    is_party_exempted: Optional[bool] = None
    is_sez_party: Optional[bool] = None
    is_oth_territory_assessee: Optional[bool] = None
    is_transporter: Optional[bool] = None
    is_rate_inclusive_vat: Optional[bool] = None
    use_for_vat: Optional[bool] = None
    use_for_esi_eligibility: Optional[bool] = None
    use_for_gratuity: Optional[bool] = None
    use_for_kkc: Optional[bool] = None
    use_for_sbc: Optional[bool] = None
    use_for_purchase_tax: Optional[bool] = None
    use_for_notional_itc: Optional[bool] = None
    use_as_notional_bank: Optional[bool] = None
    is_used_for_cvd: Optional[bool] = None
    is_excise_merchant_exporter: Optional[bool] = None
    is_ecomm_operator: Optional[bool] = None
    override_based_on_realization: Optional[bool] = None
    override_credit_limit: Optional[bool] = None
    ignore_mismatch_with_warning: Optional[bool] = None
    behave_as_payment_gateway: Optional[bool] = None
    led_belongs_to_non_taxable: Optional[bool] = None
    is_ecash_ledger: Optional[bool] = None
    is_ecd_iff_in_sd_date: Optional[bool] = None
    consider_purchase_for_export: Optional[bool] = None
    allow_export_with_errors: Optional[bool] = None
    show_in_payslip: Optional[bool] = None
    is_salary_mul_file: Optional[bool] = None
    is_salary_grouped: Optional[bool] = None
    is_salary_trans_grouped_for_brs: Optional[bool] = None
    is_abatement_applicable: Optional[bool] = None
    is_pay_upload: Optional[bool] = None
    is_pay_batch_only_sal: Optional[bool] = None
    is_pymt_adv_online: Optional[bool] = None
    is_pymt_adv_cc_enabled: Optional[bool] = None
    is_include_pymt_adv_billwise: Optional[bool] = None
    is_product_code_based: Optional[bool] = None
    is_filename_format_supported: Optional[bool] = None
    has_client_code: Optional[bool] = None
    is_batch_enabled: Optional[bool] = None
    is_scb_uae: Optional[bool] = None
    is_bank_status_app: Optional[bool] = None
    bank_is_reconcile_perfect_matches: Optional[bool] = None
    is_ebanking_supported: Optional[bool] = None
    is_echeque_supported: Optional[bool] = None
    is_edd_supported: Optional[bool] = None
    has_echeque_city: Optional[bool] = None
    has_echeque_delivery_mode: Optional[bool] = None
    has_echeque_delivery_to: Optional[bool] = None
    has_echeque_print_location: Optional[bool] = None
    has_echeque_payable_location: Optional[bool] = None
    has_echeque_bank_location: Optional[bool] = None
    has_edd_city: Optional[bool] = None
    has_edd_delivery_mode: Optional[bool] = None
    has_edd_delivery_to: Optional[bool] = None
    has_edd_print_location: Optional[bool] = None
    has_edd_payable_location: Optional[bool] = None
    has_edd_bank_location: Optional[bool] = None
    payins_is_batch_applicable: Optional[bool] = None
    payins_is_file_num_app: Optional[bool] = None
    audited: Optional[bool] = None

    sort_position: Optional[str] = None

    # --- Nested LIST Sections ---
    mailing_details: Optional[MailingDetails] = None
    multi_address_list: Optional[list[MultiAddress]] = None
    gst_reg_details: Optional[list[GSTRegDetails]] = None
    payment_details: Optional[list[PaymentDetails]] = None
    tds_deduction_rules: Optional[list[TDSDeductionRule]] = None
    lower_deductions: Optional[list[LowerDeduction]] = None
    tds_exemption_rules: Optional[list[TDSExemptionRule]] = None
    interest_collection: Optional[list[InterestCollection]] = None
    gst_details: Optional[list[GSTDetails]] = None
    hsn_details: Optional[list[HSNDetails]] = None
    bill_allocations: Optional[list[BillAllocation]] = None
    contact_details: Optional[list[ContactDetails]] = None
    msme_details: Optional[list[MSMEDetails]] = None
    cheque_range: Optional[list[ChequeRange]] = None
    audit_details: Optional[list[AuditDetails]] = None
    schvi_details: Optional[list[SchVIDetails]] = None
    language_name: Optional[LanguageName] = None


# ==================== TOP-LEVEL PAYLOAD ====================


class CreateLedgerPayload(BaseModel):
    company_name: str
    username: Optional[str] = None
    password: Optional[str] = None
    ledgers: list[LedgerRequest]
