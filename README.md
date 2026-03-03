# Containment Reflexion Audit™ (CRA Protocol) & The Truth Prompt™

Containment Reflexion Audit™ (CRA) & The Truth Prompt™ — Open accountability stack for traceable, auditable, and regulator-ready AI reasoning with hash-sealed artifacts and deterministic replay.

[![License: SCL-1.0](https://img.shields.io/badge/License-SCL--1.0-blue.svg)](LICENSE-SML)

**Repository:** https://github.com/cmiller9851-wq/containment-reflexion-audit

## Overview

This repository contains the reference implementation and documentation for:
- Containment Reflexion Audit™ (CRA): protocol that generates immutable JSON-L artifact chains recording prompts, checkpoints, contributor edits, and outputs.
- The Truth Prompt™: structured prompting method that requests model provenance, discrete chain-of-thought checkpoints, confidence scalars, and refusal/override signals.

Artifacts are SHA-256 hashed, ECDSA P-256 signed, and support deterministic replay in isolated environments. Public traces contain only hashes and non-identifying metadata.

## Features

- JSON-L artifact records with SHA-256 chaining
- ECDSA P-256 signatures on every artifact
- Deterministic replay (container image, seeds, config)
- Truth Prompt template (provenance, checkpoints, confidence 0–1)
- Contributor edit logging with signed rationale
- Example Python code for creation, signing, chaining, and verification
- GitHub Actions CI pipeline

## Repository Contents

| Path                        | Description |
|-----------------------------|-------------|
| LICENSE-SML                 | Sovereign Containment License v1.0 (SCL-1.0) |
| WHITEPAPER.md               | Full technical white paper |
| POLICY_BRIEF.md             | One-page policy brief |
| SLIDES.md                   | 10-slide executive deck outline |
| CONTRIBUTING.md             | Contribution rules and CLA |
| CHANGELOG.md                | Version history |
| /schema/                    | JSON-L schema and example records |
| /examples/                  | Python reference code |
| .github/workflows/ci.yml    | Automated CI |

## Getting Started

```bash
git clone https://github.com/cmiller9851-wq/containment-reflexion-audit.git
cd containment-reflexion-audit

pip install -r requirements.txt

cd examples
python hash_and_chain.py
python replay_verify.pyl
Quick Links
•  Blog: http://swervincurvin.blogspot.com/
•  X: https://x.com/vccmac
•  Facebook: https://www.facebook.com/share/1DBEUm4P8H/?mibextid=wwXIfr
Roadmap
•  Phase 0 (October 2025): reference repo and documentation
•  Phase 1 (Q4 2025): pilot programs
•  Phase 2 (Q1 2026): standards submissions and auditor tools
•  Phase 3 (2026+): certification program
Contact
Cory M. Miller (@vccmac)
Blog: http://swervincurvin.blogspot.com/
GitHub issues: for questions or pilot interest
© 2025 Cory M. Miller (vccmac). Released under the Sovereign Containment License v1.0 (SCL-1.0). See LICENSE-SML for full terms.
