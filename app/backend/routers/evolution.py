"""
Temporal Evolution & Supersession Router for FinReg AI.
Provides endpoints for chronological timeline navigation, structured clause diffs, transition countdowns, and as-of date queries.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.versioning.temporal_filter import (
    SUPERSEDED_REGISTRY,
    KNOWN_TRANSITIONS,
    CURRENT_SYSTEM_DATE,
    parse_date_query
)

router = APIRouter(prefix="/api/evolution", tags=["Evolution & Versioning"])

@router.get("/timeline")
def get_regulatory_timeline():
    """Returns the chronological regulatory milestones across the tri-temporal evolution."""
    events = [
        {
            "id": "event_2022_dl",
            "date": "2022-09-02",
            "title": "Guidelines on Digital Lending Issued",
            "circular_no": "RBI/2022-23/111 DOR.CRE.REC.66/21.07.001/2022-23",
            "doc_id": "RBI_DL_2022",
            "category": "ORIGINAL_FRAMEWORK",
            "summary": "RBI established initial comprehensive digital lending framework mandating direct bank disbursement, KFS disclosures, cooling-off period, and restricted FLDG to synthetic securitisation rules (Para 6).",
            "status": "SUPERSEDED_ON_2025_05_08"
        },
        {
            "id": "event_2023_dlg",
            "date": "2023-06-08",
            "title": "Default Loss Guarantee (DLG) Guidelines Issued",
            "circular_no": "RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24",
            "doc_id": "RBI_DLG_2023",
            "category": "AMENDMENT",
            "summary": "Explicitly permitted Default Loss Guarantee up to 5% of portfolio backed by Cash, SCB Fixed Deposit, or Bank Guarantee, with a 120-day invocation period, replacing Para 6 of the 2022 guidelines.",
            "status": "SUPERSEDED_ON_2025_05_08"
        },
        {
            "id": "event_2023_penal",
            "date": "2023-08-18",
            "effective_date": "2024-01-01",
            "title": "Fair Lending Practice – Penal Charges in Loan Accounts",
            "circular_no": "RBI/2023-24/53 DOR.MCS.REC.28/01.01.001/2023-24",
            "doc_id": "RBI_PENAL_2023",
            "category": "REFORM",
            "summary": "Mandated that borrower default penalties must be recovered strictly as separate penal charges and prohibits compounding into the loan interest rate.",
            "status": "ACTIVE"
        },
        {
            "id": "event_2025_dl_master",
            "date": "2025-05-08",
            "title": "Reserve Bank of India (Digital Lending) Directions, 2025",
            "circular_no": "RBI/2025-26/36 DOR.STR.REC.19/21.07.001/2025-26",
            "doc_id": "RBI_DL_2025",
            "category": "CONSOLIDATED_MASTER_DIRECTIONS",
            "summary": "Consolidated Master Directions repealing both 2022 Guidelines and 2023 DLG circular under Paragraph 30 and Annex III. General provisions took effect immediately on May 8, 2025.",
            "status": "ACTIVE"
        },
        {
            "id": "event_2025_para17",
            "date": "2025-06-15",
            "title": "Commencement of Paragraph 17 (CIMS Portal Reporting)",
            "circular_no": "RBI/2025-26/36 DOR.STR.REC.19/21.07.001/2025-26",
            "doc_id": "RBI_DL_2025",
            "clause_no": "17",
            "category": "STAGGERED_COMMENCEMENT",
            "summary": "Paragraph 17 came into force, mandating reporting of Digital Lending Apps (DLAs) and DLG arrangements on RBI's Centralised Information Management System (CIMS) portal.",
            "status": "ACTIVE"
        },
        {
            "id": "event_2025_para6",
            "date": "2025-11-01",
            "title": "Commencement of Paragraph 6 (Multiple Lenders RE-LSP Arrangements)",
            "circular_no": "RBI/2025-26/36 DOR.STR.REC.19/21.07.001/2025-26",
            "doc_id": "RBI_DL_2025",
            "clause_no": "6",
            "category": "STAGGERED_COMMENCEMENT",
            "summary": "Paragraph 6 came into force, establishing governance, transparency, and borrower choice standards for arrangements involving multiple Regulated Entities offering credit through a single LSP.",
            "status": "ACTIVE"
        }
    ]
    return {
        "current_system_date": CURRENT_SYSTEM_DATE,
        "total_milestones": len(events),
        "events": events
    }

@router.get("/diffs")
def get_clause_diffs():
    """Returns structured comparative diffs between outdated, intermediate, and active regulations."""
    diff_cards = []
    for rule_key, reg in SUPERSEDED_REGISTRY.items():
        diff_cards.append({
            "rule_key": rule_key,
            "title": rule_key.replace("_", " ").title(),
            "outdated": {
                "doc_id": reg.get("old_doc_id"),
                "doc_title": reg.get("old_doc_title"),
                "circular_no": reg.get("old_circular_no"),
                "clause": reg.get("old_clause"),
                "valid_until": reg.get("old_valid_until"),
                "summary": reg.get("old_summary")
            },
            "intermediate": {
                "doc_id": reg.get("intermediate_doc_id"),
                "doc_title": reg.get("intermediate_doc_title"),
                "circular_no": reg.get("intermediate_circular_no"),
                "clause": reg.get("intermediate_clause"),
                "valid_until": reg.get("intermediate_valid_until"),
                "summary": reg.get("intermediate_summary")
            } if reg.get("intermediate_doc_id") else None,
            "current": {
                "doc_id": reg.get("new_doc_id"),
                "doc_title": reg.get("new_doc_title"),
                "circular_no": reg.get("new_circular_no"),
                "clause": reg.get("new_clause"),
                "effective_date": reg.get("new_effective_date"),
                "summary": reg.get("new_summary")
            },
            "key_phrases": reg.get("key_phrases", [])
        })
    return diff_cards

@router.get("/transitions")
def get_transition_milestones():
    """Returns granular details for staggered commencement transitions and countdown metrics."""
    now = datetime.strptime(CURRENT_SYSTEM_DATE, "%Y-%m-%d")
    results = []
    for date_str, trans in KNOWN_TRANSITIONS.items():
        event_dt = datetime.strptime(date_str, "%Y-%m-%d")
        days_diff = (event_dt - now).days
        is_past = days_diff <= 0
        results.append({
            "effective_date": date_str,
            "event_name": trans.get("event_name"),
            "circular_no": trans.get("circular_no"),
            "doc_id": trans.get("doc_id"),
            "clause_no": trans.get("clause_no", "General"),
            "pre_regime": trans.get("pre_regime_summary"),
            "post_regime": trans.get("post_regime_summary"),
            "is_in_effect": is_past,
            "days_elapsed": abs(days_diff) if is_past else 0,
            "days_remaining": days_diff if not is_past else 0
        })
    return {
        "current_system_date": CURRENT_SYSTEM_DATE,
        "transitions": results
    }

@router.get("/as-of")
def evaluate_as_of_date(date_str: str = Query(..., description="Target historical date (YYYY-MM-DD)")):
    """Simulates the applicable regulatory regime for a specific historical date."""
    parsed = parse_date_query(f"What rules applied on {date_str}?")
    return {
        "query_date": date_str,
        "current_system_date": CURRENT_SYSTEM_DATE,
        "interpretation": parsed
    }
