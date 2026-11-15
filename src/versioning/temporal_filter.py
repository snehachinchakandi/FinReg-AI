"""
Temporal Filtering and Superseded Circular Management for FinReg AI.
Ensures outdated regulatory circulars/clauses are not cited as current law, while supporting
date-specific historical retrieval and side-by-side comparison across tri-temporal regulatory eras.
"""

import re
from typing import List, Dict, Any, Tuple, Optional

CURRENT_SYSTEM_DATE = "2026-11-14"

MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}

# Registry of superseded regulatory clauses and their superseding directions
SUPERSEDED_REGISTRY = {
    "DIGITAL_LENDING_DIRECTIONS_2025": {
        "rule_key": "DIGITAL_LENDING_DIRECTIONS_2025",
        "old_doc_id": "RBI_DL_2022",
        "old_doc_title": "Guidelines on Digital Lending",
        "old_circular_no": "RBI/2022-23/111 DOR.CRE.REC.66/21.07.001/2022-23",
        "old_publish_date": "2022-09-02",
        "old_effective_date": "2022-09-02",
        "old_valid_until": "2025-05-07",
        "old_clause": "Full circular (Clauses 1-16)",
        "old_summary": "Initial regulatory framework for digital lending mandating direct bank disbursement, KFS disclosures, cooling-off period, and privacy safeguards.",
        "new_doc_id": "RBI_DL_2025",
        "new_doc_title": "Reserve Bank of India (Digital Lending) Directions, 2025",
        "new_circular_no": "RBI/2025-26/36 DOR.STR.REC.19/21.07.001/2025-26",
        "new_publish_date": "2025-05-08",
        "new_effective_date": "2025-05-08",
        "staggered_commencement": {
            "general": "2025-05-08",
            "para_17": "2025-06-15",
            "para_6": "2025-11-01"
        },
        "new_clause": "Master Directions (Chapters I - VII, Paragraphs 1-30, Annexures I-III)",
        "new_summary": "Consolidated Master Directions on digital lending repealing the 2022 circular and 2023 DLG circular under Paragraph 30 and Annex III. Governs KFS (Para 8), direct disbursals/repayments (Para 9), cooling-off (Para 10), data privacy (Paras 12-14), CIC reporting (Para 16), DLG (Chapter VI, Paras 18-28), CIMS reporting (Para 17, eff. June 15, 2025), and multi-lender arrangements (Para 6, eff. Nov 1, 2025).",
        "key_phrases": [
            "digital lending directions 2025", "rbi digital lending 2025", "2025 directions",
            "repeal of digital lending", "annex iii repeal"
        ]
    },
    "FLDG_SYNTHETIC_SECURITISATION": {
        "rule_key": "FLDG_SYNTHETIC_SECURITISATION",
        "old_doc_id": "RBI_DL_2022",
        "old_doc_title": "Guidelines on Digital Lending",
        "old_circular_no": "RBI/2022-23/111 DOR.CRE.REC.66/21.07.001/2022-23",
        "old_publish_date": "2022-09-02",
        "old_effective_date": "2022-09-02",
        "old_valid_until": "2023-06-07",
        "old_clause": "Para 6 / Clause 15",
        "old_summary": "In Sept 2022, RBI restricted First Loss Default Guarantee (FLDG) arrangements by requiring strict adherence to Master Directions on Securitisation (synthetic securitisation), causing industry ambiguity.",
        "intermediate_doc_id": "RBI_DLG_2023",
        "intermediate_doc_title": "Guidelines on Default Loss Guarantee (DLG) in Digital Lending",
        "intermediate_circular_no": "RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24",
        "intermediate_publish_date": "2023-06-08",
        "intermediate_effective_date": "2023-06-08",
        "intermediate_valid_until": "2025-05-07",
        "intermediate_clause": "Paragraph 2 & Annex (Para 3-13)",
        "intermediate_summary": "On June 8, 2023, RBI explicitly permitted DLG capped at 5% of loan portfolio with Cash/FD/BG and 120-day invocation period (in force until repeal on May 8, 2025).",
        "new_doc_id": "RBI_DL_2025",
        "new_doc_title": "Reserve Bank of India (Digital Lending) Directions, 2025",
        "new_circular_no": "RBI/2025-26/36 DOR.STR.REC.19/21.07.001/2025-26",
        "new_publish_date": "2025-05-08",
        "new_effective_date": "2025-05-08",
        "new_clause": "Chapter VI (Paragraphs 18-28, Para 23: Cap on DLG)",
        "new_summary": "Current governing regulation: Chapter VI of Master Directions 2025 retains the 5% portfolio cap (Para 23), eligible forms of DLG (Para 22: Cash, SCB FD with lien, Bank Guarantee), 120-day invocation (Para 26), and under Para 30 / Annex III repealed both the 2022 and 2023 circulars.",
        "key_phrases": [
            "fldg", "first loss default guarantee", "dlg", "default loss guarantee",
            "synthetic securitisation", "loss sharing arrangement", "cap on dlg"
        ]
    },
    "PENAL_INTEREST_TO_CHARGES": {
        "rule_key": "PENAL_INTEREST_TO_CHARGES",
        "old_doc_id": "LEGACY_PENAL_CIRCULAR",
        "old_doc_title": "Fair Practices Code on Lender's Dues",
        "old_circular_no": "Legacy Guidelines",
        "old_publish_date": "Historical",
        "old_effective_date": "Historical",
        "old_valid_until": "2023-12-31",
        "old_clause": "Penal Interest Guidelines",
        "old_summary": "Lenders previously charged penal interest compounded into the loan interest rate upon borrower default.",
        "new_doc_id": "RBI_PENAL_2023",
        "new_doc_title": "Fair Lending Practice – Penal Charges in Loan Accounts",
        "new_circular_no": "RBI/2023-24/53 DOR.MCS.REC.28/01.01.001/2023-24",
        "new_publish_date": "2023-08-18",
        "new_effective_date": "2024-01-01",
        "new_clause": "Paragraph 3",
        "new_summary": "Under RBI circular dated Aug 18, 2023, penalties must be recovered strictly as separate penal charges without compounding into the interest rate.",
        "key_phrases": ["penal interest", "penal charge", "default penalty", "penal rate"]
    }
}


KNOWN_TRANSITIONS = {
    "2023-06-08": {
        "event_name": "Issuance of Guidelines on Default Loss Guarantee (DLG) in Digital Lending",
        "circular_no": "RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24",
        "pre_cutoff": "2023-06-07",
        "post_effective": "2023-06-08",
        "doc_id": "RBI_DLG_2023",
        "pre_regime_summary": "Under the 2022 Guidelines, FLDG arrangements not conforming to synthetic securitisation were disallowed.",
        "post_regime_summary": "Explicit DLG permitted up to 5% portfolio cap with Cash, SCB FD, or Bank Guarantee, with 120-day invocation period."
    },
    "2025-05-08": {
        "event_name": "Notification and General Commencement of Master Directions 2025",
        "circular_no": "RBI/2025-26/36 DOR.STR.REC.19/21.07.001/2025-26",
        "pre_cutoff": "2025-05-07",
        "post_effective": "2025-05-08",
        "doc_id": "RBI_DL_2025",
        "pre_regime_summary": "Governed by 2022 Digital Lending Guidelines and 2023 DLG Circular.",
        "post_regime_summary": "Consolidated governing law; repealed 2022 & 2023 circulars under Para 30 and Annex III. General provisions in force immediately."
    },
    "2025-06-15": {
        "event_name": "Staggered Commencement of Paragraph 17 (CIMS Portal Reporting)",
        "circular_no": "RBI/2025-26/36 DOR.STR.REC.19/21.07.001/2025-26",
        "pre_cutoff": "2025-06-14",
        "post_effective": "2025-06-15",
        "doc_id": "RBI_DL_2025",
        "clause_no": "17",
        "pre_regime_summary": "During June 1–14, 2025: General 2025 Directions in force, but Paragraph 17 (CIMS reporting) was NOT yet in effect.",
        "post_regime_summary": "From June 15, 2025 onward: Paragraph 17 came into force, mandating reporting of DLAs and DLG arrangements on RBI's CIMS portal."
    },
    "2025-11-01": {
        "event_name": "Staggered Commencement of Paragraph 6 (Multiple Lenders RE-LSP Arrangements)",
        "circular_no": "RBI/2025-26/36 DOR.STR.REC.19/21.07.001/2025-26",
        "pre_cutoff": "2025-10-31",
        "post_effective": "2025-11-01",
        "doc_id": "RBI_DL_2025",
        "clause_no": "6",
        "pre_regime_summary": "Prior to November 1, 2025: Paragraph 6 restriction/governance on multiple lender arrangements was NOT yet in force.",
        "post_regime_summary": "From November 1, 2025 onward: Paragraph 6 came into force."
    }
}


def parse_date_query(query: str) -> Dict[str, Any]:
    """
    Extracts temporal intent, target dates, statutory cutoffs, transition periods,
    or comparison years from compliance queries.
    Preserves exact statutory intervals and eliminates arbitrary date selection.
    """
    if not query:
        return {"intent": "CURRENT", "target_date": CURRENT_SYSTEM_DATE, "raw_match": "default_current"}
    
    q_lower = query.lower()

    # 1. Explicit Comparison Intent (keywords)
    comparison_patterns = [
        r"\b(compare|difference between|how did .* change|evolve|evolution|across years|versus|\bvs\b)\b"
    ]
    years_found = [int(y) for y in re.findall(r"\b(201\d|202\d)\b", q_lower)]
    unique_years = sorted(list(set(years_found)))

    if any(re.search(p, q_lower) for p in comparison_patterns):
        return {
            "intent": "COMPARISON",
            "target_date": None,
            "comparison_years": unique_years,
            "raw_match": "comparison"
        }

    # 2. Transition Event Queries (e.g., "What changed on June 15, 2025?")
    if re.search(r"\b(?:what\s+changed\s+on|change[ds]?\s+on|came\s+into\s+force\s+on|came\s+into\s+effect\s+on|transition\s+on)\s+(?:june\s+15|15th?\s+june),?\s+2025\b", q_lower):
        t_info = KNOWN_TRANSITIONS["2025-06-15"]
        return {
            "intent": "TRANSITION_EVENT",
            "transition_date": "2025-06-15",
            "target_date": "2025-06-15",
            "event_info": t_info,
            "raw_match": "changed on june 15, 2025",
            "explanation": t_info["post_regime_summary"]
        }

    if re.search(r"\b(?:what\s+changed\s+on|change[ds]?\s+on|came\s+into\s+force\s+on|came\s+into\s+effect\s+on|transition\s+on)\s+(?:nov(?:ember)?\s+1|1st?\s+nov(?:ember)?),?\s+2025\b", q_lower):
        t_info = KNOWN_TRANSITIONS["2025-11-01"]
        return {
            "intent": "TRANSITION_EVENT",
            "transition_date": "2025-11-01",
            "target_date": "2025-11-01",
            "event_info": t_info,
            "raw_match": "changed on november 1, 2025",
            "explanation": t_info["post_regime_summary"]
        }

    # 3. Explicit Relative Phrasing with Precise Statutory Cutoffs
    # (a) Distinguish calendar-month "Prior to June 2023" (before June 1, 2023) from circular commencement
    if re.search(r"\b(?:prior to|before)\s+june\s+2023\b", q_lower) and not re.search(r"\b(?:june\s+8|circular|dlg)\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2023-05-31",
            "cutoff_date": "2023-05-31",
            "date_interval": ("2022-09-02", "2023-05-31"),
            "period_label": "Prior to June 2023 (Before June 1, 2023)",
            "description": "Period before June 1, 2023 under original 2022 Guidelines.",
            "raw_match": "prior to june 2023"
        }

    # (b) Circular commencement cutoff: "Before the June 8, 2023 DLG circular took effect" / "Prior to the 2023 circular"
    if re.search(r"\b(before\s+the\s+june\s+8,?\s+2023|before\s+june\s+8,?\s+2023|prior\s+to\s+june\s+8,?\s+2023|prior to the 2023 circular|before the 2023 circular|before the june 2023 dlg circular|prior to the june 2023 circular|what was applicable before the june 2023 dlg circular)\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2023-06-07",
            "cutoff_date": "2023-06-07",
            "date_interval": ("2022-09-02", "2023-06-07"),
            "period_label": "Regime prior to June 8, 2023 DLG Circular (through June 7, 2023)",
            "description": "Governed by RBI Guidelines on Digital Lending dated Sept 2, 2022 (Clause 15 / synthetic securitisation prohibition).",
            "raw_match": "pre-dlg-circular-2023"
        }

    # (c) Cutoffs around June 15, 2025:
    # "Before June 15, 2025" -> through June 14, 2025
    if re.search(r"\b(?:what\s+applied\s+before|before|prior to|until)\s+(?:june\s+15|15th?\s+june),?\s+2025\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2025-06-14",
            "cutoff_date": "2025-06-14",
            "date_interval": ("2025-05-08", "2025-06-14"),
            "period_label": "Pre-June 15, 2025 (Through June 14, 2025)",
            "description": "Period before Paragraph 17 took effect: General 2025 Directions active; Para 17 and Para 6 NOT active.",
            "raw_match": "before june 15, 2025"
        }

    # "After June 15, 2025" -> strictly from June 16, 2025 (excludes June 15 commencement day itself)
    if re.search(r"\b(?:what\s+applied\s+after|after|following|post)\s+(?:june\s+15|15th?\s+june),?\s+2025\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2025-06-16",
            "date_interval": ("2025-06-16", "2025-10-31"),
            "period_label": "Post-June 15, 2025 (From June 16, 2025)",
            "description": "Period after June 15, 2025: Para 17 and general 2025 provisions active; Para 6 NOT active.",
            "raw_match": "after june 15, 2025"
        }

    # "From June 15, 2025" / "Starting June 15, 2025" / "As of June 15, 2025" -> starting on June 15, 2025
    if re.search(r"\b(?:from|starting|as of|since)\s+(?:june\s+15|15th?\s+june),?\s+2025\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2025-06-15",
            "date_interval": ("2025-06-15", "2025-10-31"),
            "period_label": "From June 15, 2025 (Starting June 15, 2025)",
            "description": "Starting on June 15, 2025: Para 17 and general 2025 provisions active; Para 6 NOT active.",
            "raw_match": "from june 15, 2025"
        }

    # "On June 15, 2025" -> exactly June 15, 2025
    if re.search(r"\bon\s+(?:june\s+15|15th?\s+june),?\s+2025\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2025-06-15",
            "date_interval": ("2025-06-15", "2025-06-15"),
            "period_label": "On June 15, 2025",
            "description": "Exact commencement date of Paragraph 17 under 2025 Directions.",
            "raw_match": "on june 15, 2025"
        }

    # (d) Cutoffs around November 1, 2025:
    if re.search(r"\b(?:what\s+were\s+the\s+rules\s+before|before|prior to|until)\s+(?:nov(?:ember)?\s+1|1st?\s+nov(?:ember)?|nov(?:ember)?),?\s+2025\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2025-10-31",
            "cutoff_date": "2025-10-31",
            "date_interval": ("2025-05-08", "2025-10-31"),
            "period_label": "Pre-November 1, 2025 (Through October 31, 2025)",
            "description": "Period before Paragraph 6 took effect: Paragraph 6 NOT active; Para 17 and general 2025 provisions active.",
            "raw_match": "before november 1, 2025"
        }

    # (e) Original 2022 Guidelines:
    if re.search(r"\b(under the original 2022 guidelines|under the original 2022 circular|under the 2022 guidelines|original 2022 guidelines|original 2022 circular|under the original 2022|what applied under the original 2022 guidelines)\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2022-09-02",
            "date_interval": ("2022-09-02", "2023-06-07"),
            "period_label": "Original 2022 Guidelines Regime",
            "doc_id": "RBI_DL_2022",
            "description": "Original 2022 Digital Lending Guidelines (RBI/2022-23/111 DOR.CRE.REC.66/21.07.001/2022-23).",
            "raw_match": "original 2022"
        }

    # (f) Under 2023 DLG Circular / Prior to May 2025:
    if re.search(r"\b(under the 2023 circular|under the 2023 dlg circular|under the june 2023 circular|prior to may 2025|before may 2025|before the 2025 directions|prior to the 2025 directions)\b", q_lower):
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": "2023-06-08",
            "cutoff_date": "2025-05-07",
            "date_interval": ("2023-06-08", "2025-05-07"),
            "period_label": "2023 DLG Circular Regime (June 8, 2023 – May 7, 2025)",
            "applicable_docs": ["RBI_DLG_2023", "RBI_DL_2022"],
            "description": (
                "Governed jointly by the 2023 DLG Circular (RBI_DLG_2023) for Default Loss Guarantee provisions "
                "and surviving provisions of the 2022 Guidelines (RBI_DL_2022, e.g. Clause 3 loan disbursements). "
                "Both co-existed and were in legal force from June 8, 2023 until repealed on May 8, 2025."
            ),
            "raw_match": "2023 circular"
        }

    # 4. Multi-year comparison without explicit keyword (e.g. "DLG in 2022 and 2024")
    if len(unique_years) >= 2:
        return {
            "intent": "COMPARISON",
            "target_date": None,
            "comparison_years": unique_years,
            "raw_match": "multi_year_comparison"
        }

    # 5. Specific Day + Month + Year: "June 10, 2025", "15 June 2025"
    dmy_match = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{4})\b", q_lower)
    if dmy_match:
        day = int(dmy_match.group(1))
        month = MONTH_MAP[dmy_match.group(2)]
        year = int(dmy_match.group(3))
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": f"{year:04d}-{month:02d}-{day:02d}",
            "raw_match": dmy_match.group(0)
        }

    mdy_match = re.search(r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", q_lower)
    if mdy_match:
        month = MONTH_MAP[mdy_match.group(1)]
        day = int(mdy_match.group(2))
        year = int(mdy_match.group(3))
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": f"{year:04d}-{month:02d}-{day:02d}",
            "raw_match": mdy_match.group(0)
        }

    # 6. Ambiguous Month Queries Crossing Commencement Dates (e.g. "June 2025")
    # In June 2025, Paragraph 17 commenced on June 15. The month spans two distinct regimes.
    if re.search(r"\b(?:in\s+|during\s+)?june\s+2025\b", q_lower) and not re.search(r"\b(?:before|after|prior to|from|until)\b", q_lower):
        return {
            "intent": "TRANSITION_PERIOD",
            "month_year": "2025-06",
            "transition_date": "2025-06-15",
            "transition_clause": "Paragraph 17 (CIMS Portal Reporting)",
            "periods": [
                {
                    "period_index": 1,
                    "label": "June 1 – June 14, 2025",
                    "date_range": ("2025-06-01", "2025-06-14"),
                    "target_date": "2025-06-01",
                    "para17_in_force": False,
                    "para6_in_force": False,
                    "description": "General 2025 Directions active; Paragraph 17 (CIMS reporting) NOT yet in force; Paragraph 6 NOT yet in force."
                },
                {
                    "period_index": 2,
                    "label": "June 15 – June 30, 2025",
                    "date_range": ("2025-06-15", "2025-06-30"),
                    "target_date": "2025-06-20",
                    "para17_in_force": True,
                    "para6_in_force": False,
                    "description": "Paragraph 17 (CIMS reporting) came into force on June 15, 2025; General 2025 Directions active; Paragraph 6 NOT yet in force."
                }
            ],
            "explanation": (
                "June 2025 contains a regulatory transition on June 15, 2025: "
                "(1) June 1–14, 2025: Paragraph 17 (CIMS reporting) was not yet effective. "
                "(2) June 15–30, 2025: Paragraph 17 came into legal force. "
                "Paragraph 6 (multiple lenders) remained prospective throughout June 2025 (effective Nov 1, 2025)."
            ),
            "raw_match": "june 2025"
        }

    # 7. Unambiguous Month + Year: "October 2024", "October 2025" (no mid-month transition)
    my_match = re.search(r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{4})\b", q_lower)
    if my_match:
        month = MONTH_MAP[my_match.group(1)]
        year = int(my_match.group(2))
        return {
            "intent": "HISTORICAL_DATE",
            "target_date": f"{year:04d}-{month:02d}-15",
            "date_interval": (f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-28"),
            "raw_match": my_match.group(0)
        }

    # 8. Year alone: "in 2022", "in 2024", "in 2026"
    y_match = re.search(r"\b(?:in|during|under|as of)\s+(202[0-6])\b", q_lower)
    if not y_match:
        y_match = re.search(r"\b(202[0-6])\b", q_lower)
    if y_match:
        year = int(y_match.group(1))
        if year <= 2022:
            return {"intent": "HISTORICAL_DATE", "target_date": "2022-09-02", "raw_match": str(year)}
        elif year in (2023, 2024):
            return {"intent": "HISTORICAL_DATE", "target_date": "2023-06-08", "raw_match": str(year)}
        elif year == 2025:
            return {"intent": "HISTORICAL_DATE", "target_date": "2025-11-15", "raw_match": "2025"}
        elif year >= 2026:
            return {"intent": "CURRENT", "target_date": CURRENT_SYSTEM_DATE, "raw_match": str(year)}

    # 9. Default to CURRENT
    return {"intent": "CURRENT", "target_date": CURRENT_SYSTEM_DATE, "raw_match": "default_current"}


def is_chunk_valid_on_date(chunk: Dict[str, Any], target_date: str) -> bool:
    """
    Evaluates whether a regulatory clause was in legal force on target_date (YYYY-MM-DD).
    Strictly accounts for staggered commencement dates and repeal cutoffs.
    """
    eff = chunk.get("effective_date") or chunk.get("publish_date") or "2000-01-01"
    valid_until = chunk.get("valid_until")
    
    if target_date < eff:
        return False
    if valid_until and target_date > valid_until:
        return False
    return True


class RegulatoryVersionManager:
    """Manages document validity, temporal routing, and date-specific version selection."""

    def __init__(self):
        self.comparison_patterns = [
            r"\b(compare|difference between|how did .* change|evolve|evolution|prior to|before and after|superseded|earlier version|historical|under the original|original 2022|previous regulation|in 2022|in 2023|in 2024|in 2025|prior regulation|former rule|previously|repealed|prior to may 2025|prior to 2025|under the 2023 circular|under the 2022 circular|in 2022 before|was there a cap)\b"
        ]

    def extract_temporal_anchor(self, query: str) -> Dict[str, Any]:
        """Parses query for temporal anchor, date target, or comparison mode."""
        return parse_date_query(query)

    def is_historical_query(self, query: str) -> bool:
        """Determines if the user asks about historical dates, repealed circulars, or version comparisons."""
        if not query:
            return False
        anchor = self.extract_temporal_anchor(query)
        if anchor["intent"] != "CURRENT":
            return True
        q_lower = query.lower()
        for pat in self.comparison_patterns:
            if re.search(pat, q_lower):
                return True
        return False

    def is_chunk_applicable(self, chunk: Dict[str, Any], query: Optional[str] = None) -> bool:
        """Determines if a chunk is legally applicable given query temporal intent."""
        if not query:
            return chunk.get("is_active", True) and is_chunk_valid_on_date(chunk, CURRENT_SYSTEM_DATE)

        anchor = self.extract_temporal_anchor(query)
        intent = anchor["intent"]

        if intent == "CURRENT":
            return chunk.get("is_active", True) and is_chunk_valid_on_date(chunk, CURRENT_SYSTEM_DATE)
        elif intent == "HISTORICAL_DATE":
            if not is_chunk_valid_on_date(chunk, anchor["target_date"]):
                return False
            # Actively enforce applicable_docs boundary on digital lending provisions
            if anchor.get("applicable_docs"):
                if chunk.get("doc_id") in ("RBI_DL_2022", "RBI_DLG_2023", "RBI_DL_2025"):
                    if chunk.get("doc_id") not in anchor["applicable_docs"]:
                        return False
            return True
        elif intent == "TRANSITION_EVENT":
            req_doc_id = anchor.get("event_info", {}).get("doc_id")
            req_clause = anchor.get("event_info", {}).get("clause_no")
            if req_doc_id and req_clause:
                # Strictly require BOTH doc_id and clause_no to match the transitioning provision
                if chunk.get("doc_id") == req_doc_id and str(chunk.get("clause_no")) == str(req_clause):
                    return True
                # Other chunks admitted for the transition event must belong to the active document and be valid on that date
                return (chunk.get("doc_id") == req_doc_id) and is_chunk_valid_on_date(chunk, anchor["target_date"])
            return is_chunk_valid_on_date(chunk, anchor["target_date"])
        elif intent == "TRANSITION_PERIOD":
            periods = anchor.get("periods", [])
            return any(is_chunk_valid_on_date(chunk, p["target_date"]) for p in periods)
        elif intent == "COMPARISON":
            # In comparison mode, chunk must be valid in at least one compared year or active
            if anchor.get("comparison_years"):
                return any(
                    is_chunk_valid_on_date(chunk, f"{y}-06-01") or is_chunk_valid_on_date(chunk, f"{y}-10-01")
                    for y in anchor["comparison_years"]
                )
            return True

        return chunk.get("is_active", True)

    def filter_chunks(
        self,
        chunks: List[Tuple[Dict[str, Any], float]],
        allow_superseded: Optional[bool] = None,
        query: Optional[str] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Date-aware filtering mechanism:
        - If allow_superseded is False: strictly current in-force provisions.
        - If allow_superseded is True: allows all matching chunks.
        - If allow_superseded is None: automatically filters by query target date or comparison era.
        """
        if allow_superseded is False:
            valid_chunks = []
            for chunk, score in chunks:
                if chunk.get("is_active", True) and is_chunk_valid_on_date(chunk, CURRENT_SYSTEM_DATE):
                    valid_chunks.append((chunk, score))
            return valid_chunks

        if allow_superseded is True and not query:
            return chunks

        # Auto date-aware selection
        valid_chunks = []
        for chunk, score in chunks:
            if self.is_chunk_applicable(chunk, query):
                valid_chunks.append((chunk, score))

        return valid_chunks

    def format_chunk_temporal_status(self, chunk: Dict[str, Any], query: Optional[str] = None) -> str:
        """Returns standard human-readable temporal label for prompt context blocks."""
        eff_date = chunk.get("effective_date") or chunk.get("publish_date") or "2000-01-01"
        valid_until = chunk.get("valid_until")
        is_active = chunk.get("is_active", True)

        if query:
            anchor = self.extract_temporal_anchor(query)
            if anchor["intent"] == "TRANSITION_PERIOD" and anchor.get("month_year") == "2025-06":
                clause = str(chunk.get("clause_no", ""))
                if clause == "17" or "cims portal" in chunk.get("section_heading", "").lower():
                    return (
                        "TRANSITION PROVISION (June 1–14, 2025: NOT YET EFFECTIVE; "
                        "June 15–30, 2025: IN FORCE since June 15, 2025)"
                    )
                elif clause == "6" or "multiple lenders" in chunk.get("section_heading", "").lower():
                    return "NOT YET EFFECTIVE IN JUNE 2025 (Commences November 1, 2025)"
                elif chunk.get("doc_id") == "RBI_DL_2025":
                    return "IN FORCE THROUGHOUT JUNE 2025 (Effective since May 8, 2025)"
            elif anchor["intent"] == "TRANSITION_EVENT":
                return f"TRANSITION CLAUSE (Came into force on {anchor.get('transition_date')})"

        if is_active and not valid_until:
            if eff_date > CURRENT_SYSTEM_DATE:
                return f"PROSPECTIVE REGULATION (Commences on {eff_date}; not yet in force)"
            return f"CURRENT & ACTIVE REGULATION (In force since {eff_date}; governing current law)"

        sup_by = chunk.get("superseded_by") or "subsequent Directions"
        sup_clause = chunk.get("superseded_clause") or "relevant provision"
        sup_date = chunk.get("supersession_date") or valid_until or "subsequent update"
        return f"SUPERSEDED / REPEALED (In force from {eff_date} until {valid_until or sup_date}; Repealed by {sup_by}; Provision: {sup_clause})"

    def get_version_diff(self, query: str) -> Dict[str, Any]:
        """
        Checks if query touches a known superseded regulatory transition and returns
        the side-by-side comparison across all applicable eras.
        """
        q_lower = query.lower()
        for rule_key, rule_data in SUPERSEDED_REGISTRY.items():
            if any(phrase in q_lower for phrase in rule_data["key_phrases"]):
                diff_res = {
                    "rule_key": rule_key,
                    "old_version": {
                        "doc_id": rule_data["old_doc_id"],
                        "doc_title": rule_data.get("old_doc_title", ""),
                        "circular_no": rule_data.get("old_circular_no", ""),
                        "publish_date": rule_data.get("old_publish_date", ""),
                        "effective_date": rule_data.get("old_effective_date", ""),
                        "valid_until": rule_data.get("old_valid_until", ""),
                        "clause": rule_data["old_clause"],
                        "summary": rule_data["old_summary"],
                        "status": "SUPERSEDED / REPEALED"
                    },
                    "current_version": {
                        "doc_id": rule_data["new_doc_id"],
                        "doc_title": rule_data.get("new_doc_title", ""),
                        "circular_no": rule_data.get("new_circular_no", ""),
                        "publish_date": rule_data.get("new_publish_date", ""),
                        "effective_date": rule_data.get("new_effective_date", ""),
                        "valid_until": None,
                        "clause": rule_data["new_clause"],
                        "summary": rule_data["new_summary"],
                        "status": "ACTIVE & CURRENT"
                    }
                }
                if "intermediate_doc_id" in rule_data:
                    diff_res["intermediate_version"] = {
                        "doc_id": rule_data["intermediate_doc_id"],
                        "doc_title": rule_data.get("intermediate_doc_title", ""),
                        "circular_no": rule_data.get("intermediate_circular_no", ""),
                        "publish_date": rule_data.get("intermediate_publish_date", ""),
                        "effective_date": rule_data.get("intermediate_effective_date", ""),
                        "valid_until": rule_data.get("intermediate_valid_until", ""),
                        "clause": rule_data.get("intermediate_clause", ""),
                        "summary": rule_data.get("intermediate_summary", ""),
                        "status": "SUPERSEDED / REPEALED"
                    }
                return diff_res
        return {}
