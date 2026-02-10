from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


# ==================== NESTED MODELS ====================


class BatchAllocation(BaseModel):
    godown_name: Optional[str] = None
    batch_name: Optional[str] = None
    destination_godown_name: Optional[str] = None
    indent_no: Optional[str] = None
    order_no: Optional[str] = None
    tracking_number: Optional[str] = None
    dynamic_cst_is_cleared: Optional[bool] = None
    amount: Optional[str] = None
    actual_qty: Optional[str] = None
    billed_qty: Optional[str] = None


class GSTRateDetail(BaseModel):
    gst_rate_duty_head: Optional[str] = None
    gst_rate_valuation_type: Optional[str] = None
    gst_rate: Optional[str] = None


class AccountingAllocation(BaseModel):
    ledger_name: Optional[str] = None
    gst_class: Optional[str] = None
    is_deemed_positive: Optional[bool] = None
    ledger_from_item: Optional[bool] = None
    remove_zero_entries: Optional[bool] = None
    is_party_ledger: Optional[bool] = None
    gst_overridden: Optional[bool] = None
    is_gst_assessable_value_overridden: Optional[bool] = None
    strd_is_gst_applicable: Optional[bool] = None
    strd_gst_is_party_ledger: Optional[bool] = None
    strd_gst_is_duty_ledger: Optional[bool] = None
    content_neg_is_pos: Optional[bool] = None
    is_last_deemed_positive: Optional[bool] = None
    is_cap_vat_tax_altered: Optional[bool] = None
    is_cap_vat_not_claimed: Optional[bool] = None
    amount: Optional[str] = None


class InventoryEntry(BaseModel):
    stock_item_name: Optional[str] = None
    # GST override fields
    gst_ovrdn_ineligible_itc: Optional[str] = None
    gst_ovrdn_is_rev_charge_appl: Optional[str] = None
    gst_ovrdn_taxability: Optional[str] = None
    gst_source_type: Optional[str] = None
    gst_ledger_source: Optional[str] = None
    hsn_source_type: Optional[str] = None
    hsn_item_source: Optional[str] = None
    gst_ovrdn_stored_nature: Optional[str] = None
    gst_ovrdn_type_of_supply: Optional[str] = None
    gst_rate_infer_applicability: Optional[str] = None
    gst_hsn_name: Optional[str] = None
    gst_hsn_description: Optional[str] = None
    gst_hsn_infer_applicability: Optional[str] = None
    # Flags
    is_deemed_positive: Optional[bool] = None
    is_gst_assessable_value_overridden: Optional[bool] = None
    strd_is_gst_applicable: Optional[bool] = None
    content_neg_is_pos: Optional[bool] = None
    is_last_deemed_positive: Optional[bool] = None
    is_auto_negate: Optional[bool] = None
    is_customs_clearance: Optional[bool] = None
    is_track_component: Optional[bool] = None
    is_track_production: Optional[bool] = None
    is_primary_item: Optional[bool] = None
    is_scrap: Optional[bool] = None
    # Amounts & quantities
    rate: Optional[str] = None
    amount: Optional[str] = None
    actual_qty: Optional[str] = None
    billed_qty: Optional[str] = None
    # Sub-lists
    batch_allocations: Optional[list[BatchAllocation]] = None
    accounting_allocations: Optional[list[AccountingAllocation]] = None
    rate_details: Optional[list[GSTRateDetail]] = None


class LedgerEntry(BaseModel):
    ledger_name: Optional[str] = None
    # Tax-specific
    rate_of_invoice_tax: Optional[list[str]] = None
    appropriate_for: Optional[str] = None
    round_type: Optional[str] = None
    gst_class: Optional[str] = None
    # Flags
    is_deemed_positive: Optional[bool] = None
    ledger_from_item: Optional[bool] = None
    remove_zero_entries: Optional[bool] = None
    is_party_ledger: Optional[bool] = None
    gst_overridden: Optional[bool] = None
    is_gst_assessable_value_overridden: Optional[bool] = None
    strd_is_gst_applicable: Optional[bool] = None
    strd_gst_is_party_ledger: Optional[bool] = None
    strd_gst_is_duty_ledger: Optional[bool] = None
    content_neg_is_pos: Optional[bool] = None
    is_last_deemed_positive: Optional[bool] = None
    is_cap_vat_tax_altered: Optional[bool] = None
    is_cap_vat_not_claimed: Optional[bool] = None
    # Amounts
    amount: Optional[str] = None
    vat_exp_amount: Optional[str] = None


# ==================== MAIN PURCHASE VOUCHER ====================


class PurchaseVoucher(BaseModel):
    # --- Required ---
    date: str
    voucher_type_name: str
    party_ledger_name: str

    # --- Addresses ---
    address_lines: Optional[list[str]] = None
    basic_buyer_address_lines: Optional[list[str]] = None

    # --- Dates ---
    reference_date: Optional[str] = None
    effective_date: Optional[str] = None
    vch_status_date: Optional[str] = None

    # --- Party & GST ---
    gst_registration_type: Optional[str] = None
    vat_dealer_type: Optional[str] = None
    state_name: Optional[str] = None
    narration: Optional[str] = None
    country_of_residence: Optional[str] = None
    party_gstin: Optional[str] = None
    place_of_supply: Optional[str] = None
    party_name: Optional[str] = None

    # --- GST Registration element ---
    gst_registration_text: Optional[str] = None
    gst_registration_tax_type: Optional[str] = None
    gst_registration_tax_registration: Optional[str] = None

    # --- Company GST ---
    cmp_gstin: Optional[str] = None
    cmp_gst_registration_type: Optional[str] = None
    cmp_gst_state: Optional[str] = None
    cmp_gst_is_oth_territory_assessee: Optional[bool] = None

    # --- Voucher details ---
    voucher_number: Optional[str] = None
    reference: Optional[str] = None
    numbering_style: Optional[str] = None
    vch_entry_mode: Optional[str] = None
    persisted_view: Optional[str] = None

    # --- Buyer ---
    buyer_address_type: Optional[str] = None
    basic_buyer_name: Optional[str] = None
    buyer_pin_number: Optional[str] = None

    # --- Party mailing ---
    party_mailing_name: Optional[str] = None
    party_pincode: Optional[str] = None
    basic_base_party_name: Optional[str] = None
    party_gst_is_oth_territory_assessee: Optional[bool] = None

    # --- Consignee ---
    consignee_gstin: Optional[str] = None
    consignee_mailing_name: Optional[str] = None
    consignee_pincode: Optional[str] = None
    consignee_state_name: Optional[str] = None
    consignee_country_name: Optional[str] = None
    consignee_cst_number: Optional[str] = None
    consignee_pin_number: Optional[str] = None

    # --- CST / FBT ---
    cst_form_issue_type: Optional[str] = None
    cst_form_recv_type: Optional[str] = None
    fbt_payment_type: Optional[str] = None

    # --- Voucher status ---
    vch_status_tax_adjustment: Optional[str] = None
    vch_status_voucher_type: Optional[str] = None
    vch_status_tax_unit: Optional[str] = None
    vch_gst_class: Optional[str] = None

    # --- All boolean flags ---
    diff_actual_qty: Optional[bool] = None
    is_mst_from_sync: Optional[bool] = None
    is_deleted: Optional[bool] = None
    is_security_on_when_entered: Optional[bool] = None
    as_original: Optional[bool] = None
    audited: Optional[bool] = None
    is_common_party: Optional[bool] = None
    for_job_costing: Optional[bool] = None
    is_optional: Optional[bool] = None
    use_for_excise: Optional[bool] = None
    is_for_job_work_in: Optional[bool] = None
    allow_consumption: Optional[bool] = None
    use_for_interest: Optional[bool] = None
    use_for_gain_loss: Optional[bool] = None
    use_for_godown_transfer: Optional[bool] = None
    use_for_compound: Optional[bool] = None
    use_for_service_tax: Optional[bool] = None
    is_reverse_charge_applicable: Optional[bool] = None
    is_system: Optional[bool] = None
    is_fetched_only: Optional[bool] = None
    is_gst_overridden: Optional[bool] = None
    is_cancelled: Optional[bool] = None
    is_on_hold: Optional[bool] = None
    is_summary: Optional[bool] = None
    is_ecommerce_supply: Optional[bool] = None
    is_boe_not_applicable: Optional[bool] = None
    is_gst_sec_seven_applicable: Optional[bool] = None
    ignore_einv_validation: Optional[bool] = None
    irn_json_exported: Optional[bool] = None
    irn_cancelled: Optional[bool] = None
    ignore_gst_conflict_in_mig: Optional[bool] = None
    is_opbal_transaction: Optional[bool] = None
    ignore_gst_format_validation: Optional[bool] = None
    is_eligible_for_itc: Optional[bool] = None
    ignore_gst_optional_uncertain: Optional[bool] = None
    update_summary_values: Optional[bool] = None
    is_eway_bill_applicable: Optional[bool] = None
    is_deleted_retained: Optional[bool] = None
    is_null: Optional[bool] = None
    is_excise_voucher: Optional[bool] = None
    excise_tax_override: Optional[bool] = None
    use_for_tax_unit_transfer: Optional[bool] = None
    is_exer1_nop_overwrite: Optional[bool] = None
    is_exf2_nop_overwrite: Optional[bool] = None
    is_exer3_nop_overwrite: Optional[bool] = None
    ignore_pos_validation: Optional[bool] = None
    excise_opening: Optional[bool] = None
    use_for_final_production: Optional[bool] = None
    is_tds_overridden: Optional[bool] = None
    is_tcs_overridden: Optional[bool] = None
    is_tds_tcs_cash_vch: Optional[bool] = None
    include_adv_pymt_vch: Optional[bool] = None
    is_sub_works_contract: Optional[bool] = None
    is_vat_overridden: Optional[bool] = None
    ignore_orig_vch_date: Optional[bool] = None
    is_vat_paid_at_customs: Optional[bool] = None
    is_declared_to_customs: Optional[bool] = None
    vat_advance_payment: Optional[bool] = None
    vat_adv_pay: Optional[bool] = None
    is_cst_delcared_goods_sales: Optional[bool] = None
    is_vat_res_tax_inv: Optional[bool] = None
    is_service_tax_overridden: Optional[bool] = None
    is_isd_voucher: Optional[bool] = None
    is_excise_overridden: Optional[bool] = None
    is_excise_supply_vch: Optional[bool] = None
    gst_not_exported: Optional[bool] = None
    ignore_gstin_validation: Optional[bool] = None
    is_gst_refund: Optional[bool] = None
    ovrdn_eway_bill_applicability: Optional[bool] = None
    is_vat_principal_account: Optional[bool] = None
    # VCH GST Status flags
    vch_status_is_vch_num_used: Optional[bool] = None
    vch_gst_status_is_included: Optional[bool] = None
    vch_gst_status_is_uncertain: Optional[bool] = None
    vch_gst_status_is_excluded: Optional[bool] = None
    vch_gst_status_is_applicable: Optional[bool] = None
    vch_gst_status_is_gstr2b_reconciled: Optional[bool] = None
    vch_gst_status_is_gstr2b_only_in_portal: Optional[bool] = None
    vch_gst_status_is_gstr2b_only_in_books: Optional[bool] = None
    vch_gst_status_is_gstr2b_mismatch: Optional[bool] = None
    vch_gst_status_is_gstr2b_in_diff_period: Optional[bool] = None
    vch_gst_status_is_ret_eff_date_overrdn: Optional[bool] = None
    vch_gst_status_is_overrdn: Optional[bool] = None
    vch_gst_status_is_stat_in_diff_date: Optional[bool] = None
    vch_gst_status_is_ret_in_diff_date: Optional[bool] = None
    vch_gst_status_main_section_excluded: Optional[bool] = None
    vch_gst_status_is_branch_transfer_out: Optional[bool] = None
    vch_gst_status_is_system_summary: Optional[bool] = None
    vch_status_is_unregistered_rcm: Optional[bool] = None
    vch_status_is_optional: Optional[bool] = None
    vch_status_is_cancelled: Optional[bool] = None
    vch_status_is_deleted: Optional[bool] = None
    vch_status_is_opening_balance: Optional[bool] = None
    vch_status_is_fetched_only: Optional[bool] = None
    vch_gst_status_is_optional_uncertain: Optional[bool] = None
    vch_status_is_reaccept_for_hsn_done: Optional[bool] = None
    # More flags
    payment_link_has_multi_ref: Optional[bool] = None
    is_shipping_within_state: Optional[bool] = None
    is_overseas_tourist_trans: Optional[bool] = None
    is_designated_zone_party: Optional[bool] = None
    has_cash_flow: Optional[bool] = None
    is_post_dated: Optional[bool] = None
    use_tracking_number: Optional[bool] = None
    is_invoice: Optional[bool] = None
    mfg_journal: Optional[bool] = None
    has_discounts: Optional[bool] = None
    as_payslip: Optional[bool] = None
    is_cost_centre: Optional[bool] = None
    is_stx_non_realized_vch: Optional[bool] = None
    is_excise_manufacturer_on: Optional[bool] = None
    is_blank_cheque: Optional[bool] = None
    is_void: Optional[bool] = None
    order_line_status: Optional[bool] = None
    vat_is_agnst_canc_sales: Optional[bool] = None
    vat_is_purc_exempted: Optional[bool] = None
    is_vat_res_tax_invoice: Optional[bool] = None
    vat_is_assesable_calc_vch: Optional[bool] = None
    is_vat_duty_paid: Optional[bool] = None
    is_delivery_same_as_consignee: Optional[bool] = None
    is_dispatch_same_as_consignor: Optional[bool] = None
    is_deleted_vch_retained: Optional[bool] = None
    vch_only_addl_info_updated: Optional[bool] = None
    change_vch_mode: Optional[bool] = None
    reset_irn_qr_code: Optional[bool] = None

    # --- Entries ---
    inventory_entries: Optional[list[InventoryEntry]] = None
    ledger_entries: Optional[list[LedgerEntry]] = None


# ==================== TOP-LEVEL PAYLOAD ====================


class CreatePurchasePayload(BaseModel):
    company_name: str
    username: Optional[str] = None
    password: Optional[str] = None
    vouchers: list[PurchaseVoucher]
