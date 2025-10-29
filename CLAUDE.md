# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Klassa** is an AI-powered information classification system designed for Swedish municipal and public sector organizations. The system automatically classifies IT systems, applications, processes, and datasets according to three security dimensions:

- **K** (Konfidentialitet/Confidentiality): 1-3
- **R** (Riktighet/Accuracy): 1-3
- **T** (Tillgänglighet/Availability): 1-3

Additionally, based on the K/R/T classification, the system determines:

- **LoA** (Level of Assurance): 1-3 - Required authentication assurance level

The system uses a **hybrid architecture** combining deterministic rule-based classification with LLM-powered interpretation to provide transparent, auditable, and consistent information security assessments.

## Core Architecture

### Hybrid Classification Engine

The classification engine consists of two layers:

1. **Deterministic Rule Engine**
   - Maps personal data categories (GDPR Article 9/10) to base K/R/T scores
   - Applies modifiers based on volume, context, and legal requirements
   - Provides consistent, repeatable classifications

2. **LLM Layer**
   - Interprets free-text responses and converts them to metadata tags
   - Resolves conflicts and edge cases
   - Generates transparent rationale for classifications
   - Suggests security measures appropriate to each level

**Critical Privacy Constraint:** The LLM must NEVER receive raw personal data. Only abstracted metadata tags (e.g., "GDPR_ART9_HEALTH", "VOLUME_HIGH") are passed to the AI layer.

### Key Components (Planned)

```
Regelmotor (Rule Engine)      - TS/Python - Base scoring & modifiers
LLM Adapter                    - Prompt engineering, masking, rationale
LoA Calculator                 - Derives authentication level from K/R
Frontend                       - React/Next.js - Questionnaire UI
API Layer                      - REST/OpenAPI - /classify endpoint
Control Catalog                - K/R/T/LoA → security measures mapping
Integration Adapters           - ServiceNow, M365, DLP, Entra ID
Audit & Logging                - Decision history, model versioning
```

## Regulatory & Legal Context

This system operates in the Swedish public sector context and must comply with:

- **GDPR** (General Data Protection Regulation)
  - Article 9: Special categories of personal data (health, religion, union membership, biometric, genetic, sexual orientation)
  - Article 10: Personal data relating to criminal convictions and offences

- **OSL** (Offentlighets- och sekretesslagen)
  - Swedish Public Access to Information and Secrecy Act
  - Defines secrecy levels for municipal data

- **Municipal Information Security Requirements**
  - K/R/T classification framework (see spec.md section 4)

## Classification Logic

### K/R/T Level Definitions

**Konfidentialitet (K)**
- K1 (Begränsad): Limited damage if disclosed
- K2 (Kännbar): Notable harm to individual privacy or organizational trust
- K3 (Allvarlig): GDPR Art. 9/10 data, protected identities (OSL), children's vulnerable data, high-volume with linkage risk

**Riktighet (R)**
- R1 (Begränsad): Errors affect few/non-critical decisions
- R2 (Betydande): Errors lead to incorrect casework, financial, or administrative decisions
- R3 (Kritisk): Errors cause legal uncertainty, incorrect large-scale payments, or safety risks

**Tillgänglighet (T)**
- T1 (Tolerant): MTTR ≥5 working days tolerable
- T2 (Viktig): Downtime >1 day causes noticeable impact
- T3 (Kritisk): RTO ≤4h, 24/7 or business-critical hours, legal/citizen service dependencies

### LoA Level Mapping

**LoA (Level of Assurance)** determines the required authentication strength based on the classification result:

- **LoA 1**: Low assurance - Simple password or single-factor authentication
- **LoA 2**: Substantial assurance - Two-factor authentication (e.g., BankID on file, SMS)
- **LoA 3**: High assurance - Strong multi-factor authentication (e.g., BankID, SITHS card)

**Mapping Logic:**

LoA is derived from the K/R/T classification using the following rules:

```
LoA = max(K, R)
```

If K=3 OR R=3 → LoA 3 (High assurance required)
If K=2 OR R=2 (and neither is 3) → LoA 2 (Substantial assurance required)
If K=1 AND R=1 → LoA 1 (Low assurance acceptable)

**Rationale:** Confidentiality (K) and Accuracy (R) directly impact the trustworthiness required when accessing or modifying information. High confidentiality or high accuracy requirements necessitate strong authentication to prevent unauthorized access or erroneous data entry.

**Examples:**
- K3 R2 T1 → LoA 3 (sensitive data requires high assurance)
- K2 R3 T2 → LoA 3 (critical accuracy requires high assurance)
- K2 R1 T3 → LoA 2 (moderate confidentiality, low accuracy needs)
- K1 R1 T3 → LoA 1 (high availability but low sensitivity)

### Base Rules (Examples)

See `spec.md` sections 7.1-7.3 for complete rule tables.

**K Triggers:**
- Art. 9 sensitive data → K3
- Art. 10 criminal data → K3
- Protected identities (sekretessmarkering) → K3
- Children + vulnerable data → K3
- Financial data → K2
- Basic identifiers only → K1

**R Triggers:**
- Authority decisions/payments → R3
- Safety/emergency response → R3
- Critical master data → R2
- Statistics/reporting only → R1

**T Triggers:**
- RTO ≤4h or 24/7 → T3
- RTO ≤1 working day → T2
- RTO >1 working day → T1

**Modifiers:** Volume, public exposure, OSL secrecy, automated decisions, external dependencies, seasonal peaks

## Technical Specifications

### Technology Stack (Planned)

- **Backend:** TypeScript or Python
- **Frontend:** React/Next.js
- **API:** REST with OpenAPI 3.0.3 (see spec.md section 12)
- **Deployment:** Containerized (Docker), on-premises or controlled cloud
- **Auth:** Entra ID/OAuth2, RBAC/ABAC
- **LLM:** Configurable (Claude, OpenAI, or local models for data protection)

### API Schema

**POST /classify**

Input:
```json
{
  "object_id": "string",
  "tags": ["GDPR_ART9_HEALTH", "OSL_SECRET", "MINORS"],
  "volumes": { "data_subjects": 50000, "attributes_per_subject": 20 },
  "rto_hours": 4,
  "legal": { "osl_secret": true, "article9": true, "minors": true },
  "decision_impact": "authority_decision"
}
```

Output:
```json
{
  "krt": { "K": 3, "R": 3, "T": 3 },
  "loa": 3,
  "rationale": {
    "K": ["RULE:art9_health", "RULE:osl_secret", "RULE:minors_vulnerable"],
    "R": ["RULE:affects_authority_decisions"],
    "T": ["RULE:rto_4h"],
    "LoA": ["DERIVED:max(K=3,R=3)", "BankID or SITHS required"]
  },
  "confidence": { "K": 0.92, "R": 0.85, "T": 0.88 },
  "suggested_measures": {
    "K": ["E2E-kryptering", "HSM-nycklar", "Stark MFA", "DLP"],
    "R": ["Transaktionslogg", "Två-i-handläggning", "Stickprovskontroll"],
    "T": ["Geo-redundans", "RTO ≤4h incidentrutin", "Övervakning"],
    "LoA": ["BankID-inloggning obligatorisk", "SITHS för administratörer", "Sessionshantering 15 min"]
  },
  "audit": { "model_version": "krt-1.3.2", "timestamp": "2025-10-29T12:00:00Z" }
}
```

## Development Principles

### Privacy-by-Design
- Personal data metadata only flows to the classification engine
- Raw personal data NEVER leaves the originating system
- All LLM prompts must use abstracted tags, not actual data values

### Transparency & Auditability
- Every classification decision must have a clear rationale
- Rule triggers explicitly logged (e.g., "RULE:art9_health")
- Model version tracked in audit trail
- Human override capability with justification logging

### Quality Assurance
- Maintain "gold line" of 30-50 reference classifications approved by Information Security
- Target metrics:
  - Override rate <15%
  - Classification time <10 minutes
  - Audit deviation <5%

## Testing Strategy

The system requires:
1. **40 reference test cases** with known K/R/T/LoA outcomes
2. **Regression tests** to prevent classification drift
3. **Edge case scenarios** (e.g., conflicting rules)
4. **Example scenarios** provided in spec.md section 17:
   - Social services case (children, Art. 9, OSL, RTO 4h) → K3 R3 T3 LoA3
   - Newsletter list (5k recipients, name+email, RTO 5 days) → K1 R1 T1 LoA1
   - HR disciplinary files (2k employees, attestation) → K3 R2 T2 LoA3

## Full Specification

Comprehensive specification is in `spec.md` (327 lines), including:
- Complete rule tables with triggers and modifiers
- UI/UX workflow (5-7 minute questionnaire)
- Security & compliance requirements
- Integration points (ServiceNow, M365, DLP, SIEM)
- Non-functional requirements (performance, scalability)
- Risk mitigation strategies

## Key Swedish Terms

- **OSL**: Offentlighets- och sekretesslagen (Public Access to Information and Secrecy Act)
- **LoA**: Level of Assurance (Tillitsnivå) - Authentication strength requirement
- **BankID**: Swedish national e-identification system (LoA 2-3)
- **SITHS**: Secure IT in Healthcare and Social services card (LoA 3)
- **Sekretessmarkering**: Protected identity/address
- **Kvarskrivning**: Retention of registration at previous address (protective measure)
- **Myndighetsutövning**: Exercise of public authority
- **Personuppgiftsbiträde**: Data processor (GDPR terminology)
- **Behandling**: Processing (of personal data)

## Integration Requirements

The system must integrate with:
- **ServiceNow/CMDB**: System catalog source, classification result target
- **M365 Sensitivity Labels**: Propagate K levels to document labels
- **DLP systems**: Configure policies based on K/R/T levels
- **Entra ID**: Identity provider for authentication/authorization
- **SIEM**: Audit log forwarding for security monitoring

## Current Project Status

**Phase:** Specification complete, implementation not started

The project currently contains only the specification document (`spec.md`). When beginning implementation:

1. Initialize git repository
2. Set up project structure according to chosen stack (TS/Python + React)
3. Implement rule engine first (deterministic, testable foundation)
4. Add LLM layer with strict privacy masking
5. Build UI with questionnaire wizard
6. Create API with OpenAPI spec
7. Develop integration adapters
8. Implement audit/logging
9. Create reference test suite (40 cases)
10. Deploy as containerized application
