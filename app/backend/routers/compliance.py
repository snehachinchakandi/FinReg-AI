"""
Compliance Matrix, Risk Evaluation, and Regulatory Dependency Graph Router.
Provides structured compliance obligations, scenario breach calculators, and node-link graph data.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/api/compliance", tags=["Compliance Intelligence"])

# 1. Statutory Compliance Obligations Matrix (RE vs LSP)
COMPLIANCE_MATRIX = [
    {
        "id": "DL_DISBURSAL_DIRECT",
        "category": "Loan Disbursal & Repayment",
        "topic": "Direct Account-to-Account Transfer",
        "re_obligation": "Mandatory: Must disburse loans directly into the verified bank account of the borrower without passing through any pool account or third-party account.",
        "lsp_obligation": "Prohibited: Cannot act as a pass-through entity, pool account, or intermediate escrow for loan disbursal or repayment funds.",
        "primary_clause": "RBI (Digital Lending) Directions, 2025, Paragraph 9; RBI Guidelines 2022, Clause 3",
        "legal_reference": "Master Directions 2025, Chapter III, Para 9",
        "governing_circular": "RBI_DL_2025",
        "severity": "CRITICAL"
    },
    {
        "id": "DL_KFS_DISCLOSURE",
        "category": "Disclosures & Transparency",
        "topic": "Key Fact Statement (KFS) & APR",
        "re_obligation": "Mandatory: Must provide a standardized KFS to the borrower prior to agreement execution, explicitly disclosing all-inclusive APR, amortization schedule, and recovery mechanisms.",
        "lsp_obligation": "Mandatory: Must display the RE-approved KFS prominently on the Digital Lending App (DLA) interface without altering APR or terms.",
        "primary_clause": "RBI (Digital Lending) Directions, 2025, Paragraph 8; RBI Guidelines 2022, Clause 4",
        "legal_reference": "Master Directions 2025, Chapter III, Para 8",
        "governing_circular": "RBI_DL_2025",
        "severity": "HIGH"
    },
    {
        "id": "DL_COOLING_OFF",
        "category": "Borrower Protection",
        "topic": "Cooling-Off / Look-Up Period",
        "re_obligation": "Mandatory: Must provide a cooling-off period of at least 3 days for loans of tenor >= 7 days (1 day for tenor < 7 days) allowing exit without prepayment penalty by paying principal and proportionate APR.",
        "lsp_obligation": "Mandatory: Must ensure the DLA interface allows the borrower to execute the cooling-off exit request seamlessly.",
        "primary_clause": "RBI (Digital Lending) Directions, 2025, Paragraph 10; RBI Guidelines 2022, Clause 6",
        "legal_reference": "Master Directions 2025, Chapter III, Para 10",
        "governing_circular": "RBI_DL_2025",
        "severity": "HIGH"
    },
    {
        "id": "DL_DATA_PRIVACY",
        "category": "Data Governance & Privacy",
        "topic": "Restriction on Mobile Device Access",
        "re_obligation": "Mandatory: Must ensure DLAs do not access mobile phone resources such as file and media, contact list, call logs, and telephony functions, except one-time camera/microphone for KYC.",
        "lsp_obligation": "Prohibited: DLA cannot prompt or collect contact lists, media files, or call logs. Must obtain explicit prior consent and store borrower data on servers located physically within India.",
        "primary_clause": "RBI (Digital Lending) Directions, 2025, Paragraphs 12-14; RBI Guidelines 2022, Clause 9",
        "legal_reference": "Master Directions 2025, Chapter IV, Paras 12-14",
        "governing_circular": "RBI_DL_2025",
        "severity": "CRITICAL"
    },
    {
        "id": "DL_DLG_PORTFOLIO_CAP",
        "category": "Credit Risk & Guarantees",
        "topic": "Default Loss Guarantee (DLG) 5% Cap",
        "re_obligation": "Mandatory: Shall ensure that total DLG cover on any outstanding loan portfolio does not exceed 5.0% of the disbursed portfolio. Eligible collateral: Cash, Fixed Deposit with Scheduled Commercial Bank, or Bank Guarantee.",
        "lsp_obligation": "Mandatory: Cannot offer DLG exceeding 5.0% of the loan portfolio. Must execute legally enforceable DLG agreements with structured 120-day invocation timelines.",
        "primary_clause": "RBI (Digital Lending) Directions, 2025, Chapter VI, Paragraph 23; RBI DLG Circular 2023, Para 3",
        "legal_reference": "Master Directions 2025, Chapter VI, Paras 18-28",
        "governing_circular": "RBI_DL_2025",
        "severity": "CRITICAL"
    },
    {
        "id": "DL_CIMS_REPORTING",
        "category": "Regulatory Reporting",
        "topic": "CIMS Portal Reporting (Staggered June 15, 2025)",
        "re_obligation": "Mandatory: Must report structured details of all DLAs deployed and DLG arrangements entered into onto RBI's Centralised Information Management System (CIMS) portal (in effect June 15, 2025).",
        "lsp_obligation": "Mandatory: Must provide timely, audited operational data and DLG utilization statements to RE for CIMS compliance.",
        "primary_clause": "RBI (Digital Lending) Directions, 2025, Paragraph 17",
        "legal_reference": "Master Directions 2025, Chapter V, Para 17",
        "governing_circular": "RBI_DL_2025",
        "severity": "HIGH"
    },
    {
        "id": "DL_MULTI_LENDER",
        "category": "Fair Lending Governance",
        "topic": "Multiple Lenders Single LSP (Staggered Nov 1, 2025)",
        "re_obligation": "Mandatory: Shall ensure that where an LSP partners with multiple REs, the DLA presents an objective, unbiassed comparison of loan terms from all partnering REs without steering (in effect Nov 1, 2025).",
        "lsp_obligation": "Mandatory: Must display transparent loan offers from all partnering REs to the prospective borrower without algorithmic bias or selective pre-selection.",
        "primary_clause": "RBI (Digital Lending) Directions, 2025, Paragraph 6",
        "legal_reference": "Master Directions 2025, Chapter II, Para 6",
        "governing_circular": "RBI_DL_2025",
        "severity": "HIGH"
    },
    {
        "id": "PENAL_SEPARATE_CHARGES",
        "category": "Interest & Pricing",
        "topic": "Penal Charges vs Compounding Penal Interest",
        "re_obligation": "Mandatory: Penalty for default must be levied as separate 'penal charges' and shall NOT be compounded into the interest rate or capitalized into the principal outstanding.",
        "lsp_obligation": "Mandatory: Cannot deduct, charge, or calculate compounding penal interest on behalf of the lender in the loan collection ledger.",
        "primary_clause": "RBI Fair Lending Practice Circular, Aug 18, 2023, Paragraph 3",
        "legal_reference": "RBI/2023-24/53 DOR.MCS.REC.28/01.01.001/2023-24",
        "governing_circular": "RBI_PENAL_2023",
        "severity": "CRITICAL"
    },
    {
        "id": "TAT_COMP_FAILED_TXN",
        "category": "Payments & Customer Grievances",
        "topic": "Harmonisation of Turn Around Time (TAT)",
        "re_obligation": "Mandatory: Must auto-reverse failed transactions within prescribed turnaround times (e.g. T+1 for UPI, T+5 for merchant cards). Default incurs compensation of ₹100 per day payable to the customer directly.",
        "lsp_obligation": "Mandatory: Payment aggregators and gateways must reconcile transaction logs daily and pass settlement failures to the acquiring bank immediately.",
        "primary_clause": "RBI Harmonisation of TAT Circular, Sept 20, 2019, Paragraph 3 & Schedule",
        "legal_reference": "DPSS.CO.PD No.629/02.01.014/2019-20",
        "governing_circular": "RBI_TAT_COMP_2019",
        "severity": "MEDIUM"
    }
]

# 2. Regulatory Risk Scenario Request & Evaluator
class RiskEvaluationRequest(BaseModel):
    fldg_percentage: Optional[float] = Field(None, description="Proposed DLG guarantee percentage of portfolio (e.g. 5.0, 7.5)")
    compounds_penal_interest: Optional[bool] = Field(None, description="Whether penal interest is added to loan principal/compounded")
    disburses_via_pool_account: Optional[bool] = Field(None, description="Whether disbursements pass through an LSP/fintech pool account")
    collects_borrower_contacts: Optional[bool] = Field(None, description="Whether the mobile lending app reads device contact lists")
    cooling_off_days_provided: Optional[int] = Field(None, description="Cooling-off look-up period days provided to borrowers")
    loan_tenor_days: Optional[int] = Field(None, description="Loan repayment tenor in days")
    tat_reversal_delay_days: Optional[int] = Field(None, description="Delay past statutory TAT in days for failed payment transaction")

@router.get("/matrix")
def get_compliance_matrix(category: Optional[str] = None):
    """Returns statutory obligation matrices for Regulated Entities (REs) and LSPs."""
    if category:
        filtered = [item for item in COMPLIANCE_MATRIX if item["category"].lower() == category.lower()]
        return {"total": len(filtered), "obligations": filtered}
    return {"total": len(COMPLIANCE_MATRIX), "obligations": COMPLIANCE_MATRIX}

@router.post("/risk-eval")
def evaluate_compliance_risk(req: RiskEvaluationRequest):
    """Evaluates an operational compliance scenario against RBI regulatory boundaries."""
    breaches = []
    risk_score = 0  # 0 to 100

    # 1. DLG Portfolio Cap Check (RBI DL 2025 Para 23 / RBI DLG 2023)
    if req.fldg_percentage is not None:
        if req.fldg_percentage > 5.0:
            breach_val = req.fldg_percentage - 5.0
            risk_score += 35
            breaches.append({
                "severity": "CRITICAL",
                "rule": "DLG Portfolio Cap Exceeded",
                "finding": f"Proposed DLG guarantee rate ({req.fldg_percentage}%) exceeds the statutory 5.0% maximum cap by {breach_val:.1f}%.",
                "cited_clause": "RBI (Digital Lending) Directions, 2025, Chapter VI, Para 23; RBI DLG Circular 2023, Para 3",
                "remediation": "Cap total contractual loss guarantee at exactly 5.0% of the disbursed loan portfolio, backed strictly by Cash, SCB Fixed Deposit, or Bank Guarantee."
            })

    # 2. Penal Interest Compounding Check (RBI Penal Circular Aug 2023)
    if req.compounds_penal_interest is True:
        risk_score += 30
        breaches.append({
            "severity": "CRITICAL",
            "rule": "Illegal Penal Interest Compounding",
            "finding": "Compounding penal charges into the interest rate or capitalizing them into principal is explicitly disallowed by RBI.",
            "cited_clause": "RBI Fair Lending Practice Circular (RBI/2023-24/53), Aug 18, 2023, Para 3",
            "remediation": "Restructure loan management ledger to recover default penalties strictly as separate, non-compounded penal charges."
        })

    # 3. Direct Disbursal Check (RBI DL 2025 Para 9)
    if req.disburses_via_pool_account is True:
        risk_score += 35
        breaches.append({
            "severity": "CRITICAL",
            "rule": "Indirect Loan Disbursal Through Pass-Through Account",
            "finding": "Disbursing funds through an LSP pool account violates direct lending mandates.",
            "cited_clause": "RBI (Digital Lending) Directions, 2025, Chapter III, Para 9; RBI Guidelines 2022, Clause 3",
            "remediation": "Ensure all funds flow directly from RE's bank account to borrower's bank account without any intermediate pass-through."
        })

    # 4. Mobile Device Privacy Check (RBI DL 2025 Para 12-14)
    if req.collects_borrower_contacts is True:
        risk_score += 25
        breaches.append({
            "severity": "HIGH",
            "rule": "Prohibited Access to Borrower Contact List",
            "finding": "Digital Lending Apps are prohibited from accessing borrower contact lists, media files, or call logs.",
            "cited_clause": "RBI (Digital Lending) Directions, 2025, Chapter IV, Paras 12-14",
            "remediation": "Remove Android READ_CONTACTS permission and delete any previously harvested device metadata."
        })

    # 5. Cooling-Off Period Check (RBI DL 2025 Para 10)
    if req.cooling_off_days_provided is not None and req.loan_tenor_days is not None:
        min_required = 3 if req.loan_tenor_days >= 7 else 1
        if req.cooling_off_days_provided < min_required:
            risk_score += 20
            breaches.append({
                "severity": "MEDIUM",
                "rule": "Insufficient Cooling-Off Period",
                "finding": f"Provided cooling-off period ({req.cooling_off_days_provided} days) is less than statutory minimum ({min_required} days) for tenor of {req.loan_tenor_days} days.",
                "cited_clause": "RBI (Digital Lending) Directions, 2025, Chapter III, Para 10",
                "remediation": f"Increase cooling-off look-up period to at least {min_required} days in the KFS agreement."
            })

    # 6. TAT Auto-Reversal Compensation Check (RBI TAT 2019)
    compensation_owed = 0
    if req.tat_reversal_delay_days is not None and req.tat_reversal_delay_days > 0:
        compensation_owed = req.tat_reversal_delay_days * 100
        risk_score += 15
        breaches.append({
            "severity": "MEDIUM",
            "rule": "TAT Auto-Reversal Delay & Mandatory Customer Compensation",
            "finding": f"Failed transaction was delayed by {req.tat_reversal_delay_days} days beyond statutory TAT.",
            "cited_clause": "RBI TAT Harmonisation Circular (DPSS.CO.PD No.629/02.01.014/2019-20), Sept 2019",
            "remediation": f"Pay statutory compensation of ₹{compensation_owed} (₹100/day) directly to the customer's account without requiring a formal claim."
        })

    risk_score = min(100, risk_score)
    severity_label = "CRITICAL" if risk_score >= 60 else "HIGH" if risk_score >= 35 else "MEDIUM" if risk_score > 0 else "COMPLIANT"

    return {
        "overall_risk_score": risk_score,
        "severity_level": severity_label,
        "total_breaches": len(breaches),
        "breaches": breaches,
        "compensation_payable_inr": compensation_owed,
        "status": "NON_COMPLIANT" if breaches else "COMPLIANT"
    }

# 3. Regulatory Dependency Graph Nodes & Edges
@router.get("/graph")
def get_regulatory_dependency_graph():
    """Returns nodes and links representing the RBI regulatory network, repeals, and cross-references."""
    nodes = [
        {"id": "RBI_DL_2025", "label": "Digital Lending Directions 2025", "type": "MASTER_DIRECTIONS", "year": 2025, "status": "ACTIVE", "pages": 28},
        {"id": "RBI_DL_2022", "label": "Digital Lending Guidelines 2022", "type": "GUIDELINES", "year": 2022, "status": "REPEALED", "pages": 26},
        {"id": "RBI_DLG_2023", "label": "DLG in Digital Lending 2023", "type": "CIRCULAR", "year": 2023, "status": "REPEALED", "pages": 8},
        {"id": "RBI_PENAL_2023", "label": "Penal Charges in Loans 2023", "type": "CIRCULAR", "year": 2023, "status": "ACTIVE", "pages": 6},
        {"id": "RBI_PPI_MD_2021", "label": "Master Directions on PPIs 2021", "type": "MASTER_DIRECTIONS", "year": 2021, "status": "ACTIVE", "pages": 44},
        {"id": "RBI_PPI_CREDIT_2022", "label": "Non-Bank PPI Credit Loading 2022", "type": "CIRCULAR", "year": 2022, "status": "ACTIVE", "pages": 2},
        {"id": "RBI_COFT_2021", "label": "Card-on-File Tokenisation 2021", "type": "CIRCULAR", "year": 2021, "status": "ACTIVE", "pages": 5},
        {"id": "RBI_P2P_MD_2017", "label": "NBFC P2P Lending Directions 2017", "type": "MASTER_DIRECTIONS", "year": 2017, "status": "ACTIVE", "pages": 28},
        {"id": "RBI_PA_PG_2020", "label": "Payment Aggregators & Gateways 2020", "type": "GUIDELINES", "year": 2020, "status": "ACTIVE", "pages": 26},
        {"id": "RBI_EMANDATE_2020", "label": "e-Mandates Recurring Txns 2020", "type": "CIRCULAR", "year": 2020, "status": "ACTIVE", "pages": 8},
        {"id": "RBI_IT_GOV_2023", "label": "IT Governance & Cyber Risk 2023", "type": "MASTER_DIRECTIONS", "year": 2023, "status": "ACTIVE", "pages": 42},
        {"id": "RBI_TAT_COMP_2019", "label": "Failed Txn TAT Harmonisation 2019", "type": "CIRCULAR", "year": 2019, "status": "ACTIVE", "pages": 12}
    ]

    edges = [
        {"source": "RBI_DL_2025", "target": "RBI_DL_2022", "relation": "REPEALS", "detail": "Paragraph 30 & Annex III repeal"},
        {"source": "RBI_DL_2025", "target": "RBI_DLG_2023", "relation": "REPEALS", "detail": "Annex III full repeal (incorporated into Chapter VI)"},
        {"source": "RBI_DLG_2023", "target": "RBI_DL_2022", "relation": "AMENDS", "detail": "Superseded Para 6 synthetic securitisation restriction"},
        {"source": "RBI_DL_2025", "target": "RBI_PENAL_2023", "relation": "ENFORCES", "detail": "Mandates adherence to separate penal charges without compounding"},
        {"source": "RBI_DL_2025", "target": "RBI_IT_GOV_2023", "relation": "MANDATES", "detail": "Cross-references cybersecurity & technology standards"},
        {"source": "RBI_PPI_CREDIT_2022", "target": "RBI_PPI_MD_2021", "relation": "CLARIFIES", "detail": "Prohibits loading non-bank PPIs with credit lines"},
        {"source": "RBI_DL_2025", "target": "RBI_PA_PG_2020", "relation": "CROSS_REFERENCES", "detail": "Merchant aggregators involved in loan flow"},
        {"source": "RBI_EMANDATE_2020", "target": "RBI_TAT_COMP_2019", "relation": "APPLIES_TAT", "detail": "Compensation rules apply to auto-debit failures"}
    ]

    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "nodes": nodes,
        "edges": edges
    }
