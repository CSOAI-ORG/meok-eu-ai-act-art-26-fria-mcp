"""Smoke tests for meok-eu-ai-act-art-26-fria-mcp."""
import sys, os, inspect, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    check_fria_required,
    generate_fria,
    list_art_27_elements,
    list_annex_iii_categories,
    crosswalk_to_dpia,
    sign_fria_chain,
    FRIA_ELEMENTS,
)


def test_check_fria_required_public_body_employment():
    r = check_fria_required("public_body", "employment")
    assert r["fria_required"] is True


def test_check_fria_required_creditworthiness_essential_services():
    r = check_fria_required("creditworthiness", "essential_services")
    assert r["fria_required"] is True


def test_check_fria_required_law_enforcement_excluded():
    r = check_fria_required("public_body", "law_enforcement")
    assert r["fria_required"] is False
    assert "Art 26(10)" in r["exemptions"][0]


def test_check_fria_required_migration_excluded():
    r = check_fria_required("public_body", "migration")
    assert r["fria_required"] is False


def test_check_fria_required_not_annex_iii():
    r = check_fria_required("public_body", "not_annex_iii")
    assert r["fria_required"] is False


def test_check_fria_required_market_surveillance_excluded():
    r = check_fria_required("public_body", "employment", is_market_surveillance=True)
    assert r["fria_required"] is False


def test_check_fria_required_commercial_other_not_required():
    r = check_fria_required("commercial_other", "biometrics")
    assert r["fria_required"] is False
    assert "strongly recommended" in r.get("hint", "")


def test_generate_fria_basic():
    r = generate_fria(
        system_name="Acme HR Screener v1.0",
        deployer_legal_name="Acme Ltd",
        deployer_type="public_body",
        annex_iii_category="employment",
        affected_categories=["job applicants", "employees"],
        period_frequency="Continuous use during hiring cycles",
        human_oversight="Trained HR officer reviews every recommendation before action",
        mitigation_measures=["Quarterly bias audit", "Complaint mechanism via grievance officer"],
        provider_ifu_reference="Acme HR Screener IFU v1.0 (provider doc rev 2026-04)",
        stakeholder_consult_summary="Consulted workers council 2026-03 + civil society 2026-04",
    )
    assert r["fria_document"]["spec"] == "EU_AI_ACT_ART_27_1"
    assert len(r["fria_document"]["art_27_1_elements"]) == 9
    assert "signature" in r["fria_document"]


def test_generate_fria_flags_missing_stakeholder():
    r = generate_fria(
        system_name="X", deployer_legal_name="Y", deployer_type="public_body",
        annex_iii_category="essential_services", affected_categories=["citizens"],
        period_frequency="daily", human_oversight="reviewer",
        mitigation_measures=["audit"], provider_ifu_reference="ifu",
    )
    # No stakeholder consult provided
    assert "missing" in r["completeness"]
    assert "i_stakeholder_consultation" in r["completeness"]


def test_list_art_27_elements_has_9():
    r = list_art_27_elements()
    assert r["count"] == 9


def test_list_annex_iii_categories():
    r = list_annex_iii_categories()
    assert "law_enforcement" in r["fria_excluded"]
    assert "biometrics" in r["categories"]


def test_crosswalk_to_dpia_returns_5_mapping():
    fria = generate_fria(
        system_name="X", deployer_legal_name="Y", deployer_type="public_body",
        annex_iii_category="essential_services", affected_categories=["citizens"],
        period_frequency="daily", human_oversight="reviewer",
        mitigation_measures=["audit"], provider_ifu_reference="ifu",
        stakeholder_consult_summary="consulted",
    )["fria_document"]
    r = crosswalk_to_dpia(fria)
    assert len(r["dpia_mapping"]) == 5


def test_sign_fria_chain_emits_attestation():
    fria = generate_fria(
        system_name="X", deployer_legal_name="Y", deployer_type="public_body",
        annex_iii_category="essential_services", affected_categories=["citizens"],
        period_frequency="daily", human_oversight="reviewer",
        mitigation_measures=["audit"], provider_ifu_reference="ifu",
        stakeholder_consult_summary="consulted",
    )["fria_document"]
    r = sign_fria_chain(fria)
    assert r["attestation_id"].startswith("FRIA_")
    assert "verify_url" in r


if __name__ == "__main__":
    g = dict(globals())
    fns = [v for k, v in g.items() if k.startswith("test_") and inspect.isfunction(v)]
    p = f = 0
    for fn in fns:
        try:
            fn(); print(f"OK {fn.__name__}"); p += 1
        except Exception as e:
            print(f"X  {fn.__name__}: {type(e).__name__}: {e}"); traceback.print_exc(); f += 1
    print(f"\n{p} passed, {f} failed")
