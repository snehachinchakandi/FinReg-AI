"""
Script to download authentic RBI regulatory documents on Indian digital payments and lending regulations.
Saves PDFs to data/raw_documents/ and writes metadata to data/metadata/documents_metadata.json.
"""

import os
import sys
import json
import time
from pathlib import Path
import requests

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.config import RAW_DOCS_DIR, METADATA_DIR, METADATA_FILE

DOCUMENTS_REGISTRY = [
    {
        "doc_id": "RBI_DL_2022",
        "title": "Guidelines on Digital Lending",
        "circular_no": "DOR.CRE.REC.66/21.07.001/2022-23",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2022-09-02",
        "effective_date": "2022-09-02",
        "is_active": True,
        "superseded_by": None,
        "supersedes": None,
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/GUIDELINESDIGITALLENDINGD234731388654CD5B68A7387FB6498F4.PDF",
        "filename": "RBI_DL_2022.pdf",
        "description": "Comprehensive framework for digital lending, borrower consent, Key Fact Statement (KFS), cooling-off period, and restrictions on third-party pool accounts.",
        "parsing_challenges": "Multi-column annexures, flowcharts, tables specifying APR calculations and disclosures."
    },
    {
        "doc_id": "RBI_DLG_2023",
        "title": "Default Loss Guarantee (DLG) in Digital Lending",
        "circular_no": "RBI/2023-24/41 DOR.CRE.REC.21/21.07.001/2023-24",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2023-06-08",
        "effective_date": "2023-06-08",
        "is_active": True,
        "superseded_by": None,
        "supersedes": "RBI_DL_2022 (Para 6 Synthetic Securitisation ambiguity)",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/41MD0806202396B8746CA1654C479B48EF6B2B24040A.PDF",
        "filename": "RBI_DLG_2023.pdf",
        "description": "Explicit guidelines permitting Default Loss Guarantee (DLG / FLDG) up to a 5% cap on the total loan portfolio between Regulated Entities and Lending Service Providers.",
        "parsing_challenges": "Structured regulatory clauses with numbered conditions, eligibility requirements for guarantees."
    },
    {
        "doc_id": "RBI_PENAL_2023",
        "title": "Fair Lending Practice – Penal Charges in Loan Accounts",
        "circular_no": "RBI/2023-24/53 DOR.MCS.REC.28/01.01.001/2023-24",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2023-08-18",
        "effective_date": "2024-01-01",
        "is_active": True,
        "superseded_by": None,
        "supersedes": "Earlier circulars on charging penal interest",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/53MD180820234FFDC0D9F0D642CC834EDD1E99DFE32D.PDF",
        "filename": "RBI_PENAL_2023.pdf",
        "description": "Mandates that penalty for default/non-compliance shall be treated as penal charges rather than compounding penal interest added to the rate of interest.",
        "parsing_challenges": "Legal operational instructions, cross-references to earlier master directions."
    },
    {
        "doc_id": "RBI_PPI_MD_2021",
        "title": "Master Directions on Prepaid Payment Instruments (PPIs)",
        "circular_no": "DPSS.CO.PD.No.1415/02.14.006/2021-22",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2021-08-27",
        "effective_date": "2021-08-27",
        "is_active": True,
        "superseded_by": None,
        "supersedes": "Master Directions on Issuance and Operation of PPIs dated October 11, 2017",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/MDPPIS270820212EBB3B99540049DBA9303F6DA4C64065.PDF",
        "filename": "RBI_PPI_MD_2021.pdf",
        "description": "Comprehensive regulatory guidelines on Small PPIs, Full-KYC PPIs, cash withdrawal limits, cross-border transactions, and interoperability mandates.",
        "parsing_challenges": "Large 44-page document with complex multi-level numbered clauses (e.g. 7.1(i)(a)), definitions section, and cross-references."
    },
    {
        "doc_id": "RBI_PPI_CREDIT_2022",
        "title": "Restriction on Loading of Non-Bank PPIs via Credit Lines",
        "circular_no": "DPSS.CO.PD.No.S-257/02.14.006/2022-23",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2022-06-20",
        "effective_date": "2022-06-20",
        "is_active": True,
        "superseded_by": None,
        "supersedes": None,
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/PPI20062022.PDF",
        "filename": "RBI_PPI_CREDIT_2022.pdf",
        "description": "Clarifies that Prepaid Payment Instruments (PPI-MD Para 10.2) permit loading/reloading only by cash, bank account debits, and credit/debit cards, strictly prohibiting loading from credit lines.",
        "parsing_challenges": "Concise circular with precise legal wording; crucial for fintech lending cards."
    },
    {
        "doc_id": "RBI_COFT_2021",
        "title": "Card-on-File Tokenisation (CoFT) – Extension of Scope",
        "circular_no": "RBI/2021-22/96 DPSS.CO.PD No.S516/02.14.003/2021-22",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2021-09-07",
        "effective_date": "2022-01-01",
        "is_active": True,
        "superseded_by": None,
        "supersedes": "Earlier circular on storage of card details",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/96COFT07092021BCF217FA92004278A7DECF946BDC04F0.PDF",
        "filename": "RBI_COFT_2021.pdf",
        "description": "Prohibits merchants and payment aggregators from storing actual card data (Card-on-File) and mandates tokenisation framework via card networks and issuers.",
        "parsing_challenges": "Includes technical specifications and security standards for token requestors."
    },
    {
        "doc_id": "RBI_P2P_MD_2017",
        "title": "Master Directions – NBFC – Peer to Peer (P2P) Lending Platforms",
        "circular_no": "DNBR (PD) 054/03.10.119/2017-18",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2017-08-24",
        "effective_date": "2017-08-24",
        "is_active": True,
        "superseded_by": None,
        "supersedes": None,
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/MDNBFCPEERTOPERR24082017366FF299539D48F092B08C867DF0F29B.PDF",
        "filename": "RBI_P2P_MD_2017.pdf",
        "description": "Directions governing NBFC-P2P entities, registration requirements, prudential norms, aggregate exposure cap of Rs. 50 lakh, escrow accounts, and grievance redressal.",
        "parsing_challenges": "Legal master directions layout, definitions, reporting annexures."
    },
    {
        "doc_id": "RBI_PA_PG_2020",
        "title": "Guidelines on Regulation of Payment Aggregators and Payment Gateways",
        "circular_no": "DPSS.CO.PD.No.1810/02.14.008/2019-20",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2020-03-17",
        "effective_date": "2020-04-01",
        "is_active": True,
        "superseded_by": None,
        "supersedes": "Directions for opening and operation of Accounts and settlement of payments for electronic payment transactions dated Nov 24, 2009",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/DPSS181020201A5119777E5E4E30BEA9C1A0625946DF.PDF",
        "filename": "RBI_PA_PG_2020.pdf",
        "description": "Direct regulation of Payment Aggregators: capital requirements (Rs. 15 crore rising to Rs. 25 crore), escrow management, settlement timelines (T+1/T+2), KYC.",
        "parsing_challenges": "Multi-page baseline technology recommendations, audit checklists, multi-row tables."
    },
    {
        "doc_id": "RBI_EMANDATE_2020",
        "title": "Framework for Processing of e-mandates for Recurring Transactions",
        "circular_no": "RBI/2020-21/74 DPSS.CO.PD No.754/02.14.003/2020-21",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2020-12-04",
        "effective_date": "2021-04-01",
        "is_active": True,
        "superseded_by": None,
        "supersedes": "Earlier e-mandate circulars dated Aug 21, 2019 and Jan 10, 2020",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/EMANDATE0412202058045F1B50D94A62A0D84784EF6E90F4.PDF",
        "filename": "RBI_EMANDATE_2020.pdf",
        "description": "Rules for recurring payments on cards/wallets/UPI, pre-transaction notification requirements (24 hours prior), and Additional Factor of Authentication (AFA) limits.",
        "parsing_challenges": "Technical transaction flow steps, sequence diagrams."
    },
    {
        "doc_id": "RBI_IT_GOV_2023",
        "title": "Master Direction on IT Governance, Risk, Controls and Assurance Practices",
        "circular_no": "RBI/2023-24/107 DoS.CO.CSITE.SEC.No.8/31.01.015/2023-24",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2023-11-07",
        "effective_date": "2024-04-01",
        "is_active": True,
        "superseded_by": None,
        "supersedes": None,
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/107MD071120235BE90D55587D43A19EE38D4DF14D96DE.PDF",
        "filename": "RBI_IT_GOV_2023.pdf",
        "description": "Governance framework for IT, cybersecurity, vendor management, business continuity planning, and cloud services for Banks and NBFCs.",
        "parsing_challenges": "Extensive 42-page technical guideline with numbered governance chapters and audit protocols."
    },
    {
        "doc_id": "RBI_TAT_COMP_2019",
        "title": "Harmonisation of Turn Around Time (TAT) and Customer Compensation for Failed Transactions",
        "circular_no": "DPSS.CO.PD No.629/02.01.014/2019-20",
        "regulator": "Reserve Bank of India (RBI)",
        "publish_date": "2019-09-20",
        "effective_date": "2019-10-15",
        "is_active": True,
        "superseded_by": None,
        "supersedes": None,
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/CIRCULAR629D4E2F38FE6734139945DDAEB963CE082.PDF",
        "filename": "RBI_TAT_COMP_2019.pdf",
        "description": "Standardised auto-reversal TATs and customer compensation (Rs. 100 per day of delay) across ATMs, POS, Card-Not-Present, IMPS, UPI, and wallets.",
        "parsing_challenges": "Consists primarily of a complex multi-page matrix table spanning 6 pages with multiple sub-columns."
    }
]

def download_all_documents():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    downloaded_metadata = []
    
    print(f"Starting download of {len(DOCUMENTS_REGISTRY)} official RBI documents...")
    for doc in DOCUMENTS_REGISTRY:
        dest_path = RAW_DOCS_DIR / doc["filename"]
        doc_entry = dict(doc)
        doc_entry["local_path"] = str(dest_path)
        
        if dest_path.exists() and dest_path.stat().st_size > 1000:
            print(f"[EXISTS] {doc['filename']} ({dest_path.stat().st_size / 1024:.1f} KB)")
            doc_entry["download_status"] = "cached"
            doc_entry["file_size_bytes"] = dest_path.stat().st_size
            downloaded_metadata.append(doc_entry)
            continue
            
        print(f"[DOWNLOADING] {doc['title']} from {doc['url']}...")
        try:
            resp = requests.get(doc["url"], headers=headers, timeout=30, verify=False)
            if resp.status_code == 200 and len(resp.content) > 1000:
                with open(dest_path, "wb") as f:
                    f.write(resp.content)
                print(f"  -> Saved {dest_path.name} ({len(resp.content) / 1024:.1f} KB)")
                doc_entry["download_status"] = "success"
                doc_entry["file_size_bytes"] = len(resp.content)
            else:
                print(f"  -> [FAILED] Status: {resp.status_code}, Length: {len(resp.content)}")
                doc_entry["download_status"] = f"failed_http_{resp.status_code}"
        except Exception as e:
            print(f"  -> [ERROR] {e}")
            doc_entry["download_status"] = f"error_{str(e)}"
            
        downloaded_metadata.append(doc_entry)
        time.sleep(0.5)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(downloaded_metadata, f, indent=2, ensure_ascii=False)
    print(f"\nMetadata written to {METADATA_FILE}")

if __name__ == "__main__":
    download_all_documents()
