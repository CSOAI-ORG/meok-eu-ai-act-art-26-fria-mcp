# MEOK EU AI Act Article 26(9) FRIA Generator MCP

> ## 🧱 Part of the MEOK Governance Substrate (£499/mo) + Enterprise Wedge (£1,500/mo)
> See [meok.ai/governance](https://meok.ai/governance).

# Auto-generate a Fundamental Rights Impact Assessment per Article 27(1)

<!-- mcp-name: io.github.CSOAI-ORG/meok-eu-ai-act-art-26-fria-mcp -->

[![PyPI](https://img.shields.io/pypi/v/meok-eu-ai-act-art-26-fria-mcp)](https://pypi.org/project/meok-eu-ai-act-art-26-fria-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What this does

EU AI Act **Article 26(9)** requires certain deployers of high-risk AI systems to perform a **Fundamental Rights Impact Assessment (FRIA)** before deployment. **Article 27(1)** spells out the 9 mandatory elements.

Consultants charge £20K–£100K to produce one of these manually. This MCP generates a structured, signed, auditor-defensible FRIA in seconds.

## When you MUST do a FRIA (Article 26(9))

| Trigger | Annex III categories in scope |
|---|---|
| Public body | §1 biometrics · §2 critical infra · §3 education · §4 employment · §5 essential services · §8 justice |
| Private operator of public service | Same as above |
| Creditworthiness assessor (Art 5(1)(c)) | §5 essential services (financial) |
| Life/health insurance pricer (Art 5(1)(g)) | §5 essential services (financial) |

**Excluded:** Annex III §6 law enforcement · §7 migration · market-surveillance use (Article 26(10)).

## Tools

| Tool | Purpose |
|---|---|
| `check_fria_required(deployer_type, annex_iii_category, is_market_surveillance?)` | Is a FRIA mandatory? |
| `generate_fria(system_name, deployer_legal_name, ...)` | Full FRIA document with all 9 elements |
| `list_art_27_elements()` | The 9 mandatory Article 27(1) elements |
| `list_annex_iii_categories()` | The 8 Annex III high-risk categories |
| `crosswalk_to_dpia(fria_doc)` | Map FRIA → EDPB DPIA template (14 April 2026) |
| `sign_fria_chain(fria_doc, signer_role)` | HMAC-signed attestation for audit |

## Article 27(1) — 9 mandatory elements

(a) Deployer processes (b) period + frequency (c) categories of natural persons affected (d) specific risks of harm (e) human-oversight measures (f) mitigation if risks materialise (g) provider IFU reference (h) GDPR Art 35 DPIA link (i) stakeholder consultation summary.

## Sister MCPs

- `eu-ai-act-compliance-mcp` — 410 articles + Annex III classifier
- `iso-42005-impact-mcp` — ISO/IEC 42005:2025 AI Impact Assessment
- `bias-detection-mcp` — Article 10 fairness metrics
- `agent-incident-relay-mcp` — Article 73 5-clock broadcaster

Full catalogue: [meok.ai/anthropic-registry](https://meok.ai/anthropic-registry)

## Pricing

| Option | Price |
|---|---|
| Self-host MIT | £0 |
| Governance Substrate | £499/mo |
| **FRIA Enterprise** | **£1,500/mo** — custom templates + verifier domain + counsel review |
| Defence | £4,990/mo |

Buy: https://meok.ai/governance

## Wire it up — full stack

Pair this with the MEOK chain that turns one agent action into ONE signed compliance event:

1. **bft-progress-council-mcp** — anti-loop guardrail
2. **agent-token-budget-mcp** — hard spend cap
3. **meok-eu-ai-act-art-26-fria-mcp** — this MCP, ahead of deployment
4. **agent-audit-logger-mcp** — hash-chained evidence
5. **a2a-governance-bridge-mcp** — fold all attestations
6. **agent-incident-relay-mcp** — broadcast Article 73 incidents to 5 regimes

See [meok.ai/mcp-stack](https://meok.ai/mcp-stack) for architecture and [meok.ai/mcp-stack/demo](https://meok.ai/mcp-stack/demo) for the live demo.

## Licence

MIT. By [MEOK AI Labs](https://meok.ai) (CSOAI LTD, UK Companies House 16939677).
