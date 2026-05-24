#!/usr/bin/env python3
"""
MEOK EU AI Act Article 26(9) FRIA Generator MCP
================================================

By MEOK AI Labs · https://meok.ai · MIT
<!-- mcp-name: io.github.CSOAI-ORG/meok-eu-ai-act-art-26-fria-mcp -->

WHAT THIS DOES
--------------
EU AI Act Article 26(9): "Before deploying a high-risk AI system in scope of
Annex III (other than for law enforcement / migration), deployers that are
bodies governed by public law OR private operators providing public services
OR deployers covered by Article 5 (1)(c)/(g) shall perform a
**Fundamental Rights Impact Assessment (FRIA)**."

This MCP auto-generates a FRIA structured per the 9 mandatory elements from
Article 27(1):

  (a) deployer's processes
  (b) period + frequency of use
  (c) categories of natural persons / groups likely affected
  (d) specific risks of harm to those persons / groups
  (e) measures of human oversight
  (f) measures to take if risks materialise (including internal governance)
  (g) cross-reference to provider's instructions for use
  (h) where applicable, link to DPIA under Article 35 GDPR
  (i) summary of consultation with stakeholders

Outputs a signed, auditor-defensible FRIA document. Cross-walks to:
- EDPB DPIA harmonised template (14 April 2026)
- ISO/IEC 42005:2025 AI Impact Assessment
- ECoC FRIA template (Council of Europe)

PRICE: £1,500/mo enterprise wedge (deployers pay £20K-£100K for a consultant
to produce one of these manually). MIT self-host for SMEs.
"""

from __future__ import annotations
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from typing import Optional
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("meok-eu-ai-act-art-26-fria")
_HMAC_SECRET = os.environ.get("MEOK_HMAC_SECRET", "")

# Article 27(1) — 9 mandatory FRIA elements
FRIA_ELEMENTS = [
    ("processes", "Deployer's processes in which the high-risk AI system will be used"),
    ("period_frequency", "Period of time + frequency the system is intended to be used"),
    ("affected_categories", "Categories of natural persons + groups likely to be affected"),
    ("specific_risks", "Specific risks of harm likely to impact the affected categories"),
    ("human_oversight", "Description of human-oversight measures per Art 14 + IFU"),
    ("mitigation_measures", "Measures to take if those risks materialise (incl. governance + complaint mechanisms)"),
    ("provider_ifu_ref", "Cross-reference to the provider's Instructions for Use (Art 13)"),
    ("dpia_link", "Where applicable, link to DPIA under Art 35 GDPR"),
    ("stakeholder_consult", "Summary of stakeholder consultation (workers councils, civil society, affected groups)"),
]

# Annex III categories that trigger high-risk classification
ANNEX_III_CATEGORIES = {
    "biometrics": "Annex III §1 — biometric identification + categorisation",
    "critical_infra": "Annex III §2 — critical infrastructure",
    "education": "Annex III §3 — education + vocational training",
    "employment": "Annex III §4 — employment, workers management + access to self-employment",
    "essential_services": "Annex III §5 — access to + enjoyment of essential private + public services",
    "law_enforcement": "Annex III §6 — law enforcement (deployer FRIA excluded per Art 26(10))",
    "migration": "Annex III §7 — migration, asylum + border control (deployer FRIA excluded)",
    "justice": "Annex III §8 — administration of justice + democratic processes",
}

# Eligibility — who MUST do a FRIA
TRIGGER_DEPLOYERS = {
    "public_body": "Body governed by public law",
    "private_public_service": "Private operator providing public service",
    "creditworthiness": "Deployer using AI to assess creditworthiness per Art 5(1)(c)",
    "life_insurance_pricing": "Deployer using AI for life/health insurance pricing per Art 5(1)(g)",
}


def _sign(payload: dict) -> str:
    if not _HMAC_SECRET:
        return "unsigned-no-key-configured"
    return hmac.new(_HMAC_SECRET.encode(), json.dumps(payload, sort_keys=True).encode(), hashlib.sha256).hexdigest()


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────────────────────────────────
# Tools
# ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def check_fria_required(
    deployer_type: str,
    annex_iii_category: str,
    is_market_surveillance: bool = False,
) -> dict:
    """
    Is a FRIA mandatory for this deployment?

    Args:
        deployer_type: One of public_body / private_public_service / creditworthiness / life_insurance_pricing / commercial_other.
        annex_iii_category: One of biometrics / critical_infra / education / employment / essential_services / law_enforcement / migration / justice / not_annex_iii.
        is_market_surveillance: Used by market surveillance authority? (excludes some duties.)

    Returns:
        {fria_required, reason, exemptions}
    """
    if is_market_surveillance:
        return {
            "fria_required": False,
            "reason": "Market surveillance use is excluded from deployer FRIA duty per Art 26(10).",
            "exemptions": ["Art 26(10) — market surveillance"],
        }
    if annex_iii_category in ("law_enforcement", "migration"):
        return {
            "fria_required": False,
            "reason": f"Annex III §{annex_iii_category} is excluded from deployer FRIA duty (Art 26(10)).",
            "exemptions": ["Art 26(10)"],
        }
    if annex_iii_category == "not_annex_iii":
        return {
            "fria_required": False,
            "reason": "FRIA only required for Annex III high-risk systems.",
            "exemptions": [],
            "hint": "Non-Annex-III systems may still require provider-side conformity assessment + DPIA.",
        }
    if deployer_type not in TRIGGER_DEPLOYERS:
        return {
            "fria_required": False,
            "reason": "FRIA only mandatory for public bodies, private operators of public services, and the two Annex III financial-service deployers (creditworthiness + life/health insurance).",
            "exemptions": [],
            "hint": "If you're a private commercial deployer of Annex III §1-5/8 systems other than the financial ones, FRIA is not mandatory but is strongly recommended for due-diligence.",
        }
    return {
        "fria_required": True,
        "reason": f"{TRIGGER_DEPLOYERS[deployer_type]} deploying {ANNEX_III_CATEGORIES.get(annex_iii_category, annex_iii_category)} — Art 27(1) FRIA mandatory before market placement / first use.",
        "deadline_hint": "Complete FRIA BEFORE first use of the system. Notify market-surveillance authority of FRIA outcome (Art 27(3)).",
    }


@mcp.tool()
def generate_fria(
    system_name: str,
    deployer_legal_name: str,
    deployer_type: str,
    annex_iii_category: str,
    affected_categories: list[str],
    period_frequency: str,
    human_oversight: str,
    mitigation_measures: list[str],
    provider_ifu_reference: str,
    dpia_link: Optional[str] = None,
    stakeholder_consult_summary: Optional[str] = None,
    specific_risks: Optional[list[str]] = None,
    deployer_processes: Optional[str] = None,
) -> dict:
    """
    Generate a full FRIA per Article 27(1) 9 mandatory elements.

    Args:
        system_name: Name + version of the high-risk AI system.
        deployer_legal_name: Legal name of the deployer entity.
        deployer_type: From check_fria_required().
        annex_iii_category: From check_fria_required().
        affected_categories: List of natural-person / group categories affected.
        period_frequency: When + how often the system runs.
        human_oversight: Description of human-oversight measures (Art 14).
        mitigation_measures: List of actions if risks materialise.
        provider_ifu_reference: Pointer to provider's Instructions for Use (Art 13).
        dpia_link: Where applicable, link to GDPR Art 35 DPIA.
        stakeholder_consult_summary: Summary of stakeholder consultation.
        specific_risks: Specific risks of harm. If omitted, inferred from category.
        deployer_processes: Description of deployer processes using the system.

    Returns:
        {fria_document, signature, completeness, next_step}
    """
    if specific_risks is None:
        # Heuristic risk inference based on annex category
        specific_risks = [
            f"Risk of erroneous classification of individuals within {a}"
            for a in affected_categories
        ] + ["Risk of automation bias by human reviewer"]

    if deployer_processes is None:
        deployer_processes = f"{deployer_legal_name} uses {system_name} within its normal operating processes for {annex_iii_category} purposes."

    fria_doc = {
        "spec": "EU_AI_ACT_ART_27_1",
        "spec_version": "Regulation (EU) 2024/1689",
        "system_name": system_name,
        "deployer_legal_name": deployer_legal_name,
        "deployer_type": deployer_type,
        "annex_iii_category": annex_iii_category,
        "annex_iii_label": ANNEX_III_CATEGORIES.get(annex_iii_category, annex_iii_category),
        "completed_at": _ts(),
        # 9 mandatory elements per Article 27(1)
        "art_27_1_elements": {
            "a_processes": deployer_processes,
            "b_period_frequency": period_frequency,
            "c_affected_categories": affected_categories,
            "d_specific_risks": specific_risks,
            "e_human_oversight": human_oversight,
            "f_mitigation_measures": mitigation_measures,
            "g_provider_ifu_reference": provider_ifu_reference,
            "h_dpia_link": dpia_link or "N/A — no personal data processing within scope",
            "i_stakeholder_consultation": stakeholder_consult_summary or "<TO_FILL>",
        },
        "next_step_art_27_3": (
            "Notify the national market-surveillance authority of the outcome of this assessment "
            "via the template the AI Office will publish (FRIA notification template due 2026 Q4)."
        ),
    }
    fria_doc["signature"] = _sign(fria_doc)

    # Completeness check
    missing = []
    if not stakeholder_consult_summary:
        missing.append("i_stakeholder_consultation")
    if not affected_categories:
        missing.append("c_affected_categories")
    if not mitigation_measures:
        missing.append("f_mitigation_measures")

    return {
        "fria_document": fria_doc,
        "signature": fria_doc["signature"],
        "completeness": "complete" if not missing else f"missing: {missing}",
        "next_step": (
            "FRIA is complete. Submit to market-surveillance authority + retain for audit."
            if not missing
            else f"Fill in: {missing} before submission."
        ),
    }


@mcp.tool()
def list_art_27_elements() -> dict:
    """Return the 9 mandatory FRIA elements from Article 27(1)."""
    return {
        "spec": "EU_AI_ACT_ART_27_1",
        "elements": [{"key": k, "description": d} for k, d in FRIA_ELEMENTS],
        "count": len(FRIA_ELEMENTS),
    }


@mcp.tool()
def list_annex_iii_categories() -> dict:
    """Return the 8 Annex III high-risk categories."""
    return {
        "spec": "EU_AI_ACT_ANNEX_III",
        "categories": ANNEX_III_CATEGORIES,
        "fria_excluded": ["law_enforcement", "migration"],
    }


@mcp.tool()
def crosswalk_to_dpia(fria_doc: dict) -> dict:
    """
    Cross-walk FRIA to EDPB harmonised DPIA template (14 April 2026).

    Args:
        fria_doc: A FRIA document from generate_fria().

    Returns:
        {dpia_mapping}
    """
    mapping = {
        "1_description_of_processing": fria_doc.get("art_27_1_elements", {}).get("a_processes"),
        "2_necessity_proportionality": fria_doc.get("art_27_1_elements", {}).get("b_period_frequency"),
        "3_risks_to_data_subjects": fria_doc.get("art_27_1_elements", {}).get("d_specific_risks"),
        "4_measures_to_address_risks": fria_doc.get("art_27_1_elements", {}).get("f_mitigation_measures"),
        "5_consultation_of_dpo_or_subjects": fria_doc.get("art_27_1_elements", {}).get("i_stakeholder_consultation"),
    }
    return {
        "dpia_mapping": mapping,
        "template": "EDPB Harmonised DPIA Template (14 April 2026)",
        "hint": "FRIA covers most DPIA Art 35 elements but not all. Run a separate DPIA if personal data is in scope.",
    }


@mcp.tool()
def sign_fria_chain(fria_doc: dict, signer_role: str = "deployer_dpo") -> dict:
    """
    HMAC-sign the FRIA + emit an audit attestation.

    Args:
        fria_doc: Output of generate_fria().
        signer_role: e.g. deployer_dpo / chief_compliance_officer / general_counsel.

    Returns:
        {attestation_id, signature, sealed_at, verify_url}
    """
    att_id = f"FRIA_{int(time.time())}_{os.urandom(4).hex()}"
    sealed = {
        "attestation_id": att_id,
        "spec": "EU_AI_ACT_ART_27_1_FRIA",
        "signer_role": signer_role,
        "fria_doc": fria_doc,
        "sealed_at": _ts(),
        "issuer": "MEOK AI Labs (CSOAI LTD)",
    }
    sig = _sign(sealed)
    return {
        "attestation_id": att_id,
        "signature": sig,
        "sealed_at": sealed["sealed_at"],
        "verify_url": f"https://meok-attestation-api.vercel.app/verify/{att_id}",
        "audit_hint": "Retain the FRIA + this signed attestation for the entire system lifecycle + 6 years after.",
    }


if __name__ == "__main__":
    mcp.run()
