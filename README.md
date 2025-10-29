# Klassa - KRT Klassningssystem

AI-drivet informationsklassningssystem för svensk offentlig sektor med stöd för GDPR, OSL och kommunala säkerhetskrav.

## Översikt

**Klassa** automatiserar klassificering av IT-system, applikationer, processer och datamängder enligt tre säkerhetsdimensioner:

- **K** (Konfidentialitet): Nivå 1-3
- **R** (Riktighet): Nivå 1-3
- **T** (Tillgänglighet): Nivå 1-3

Baserat på K/R/T-klassningen beräknas även:

- **LoA** (Level of Assurance): Autentiseringsnivå 1-3

### Huvudfunktioner

✅ **Hybrid klassningsmotor** - Deterministiska regler + AI-tolkningar
✅ **Privacy-by-design** - AI ser endast metadata, aldrig råa personuppgifter
✅ **GDPR-kompatibel** - Art. 9/10, känsliga personuppgifter
✅ **OSL-medveten** - Svensk sekretesslagstiftning
✅ **Transparent rationale** - Tydliga förklaringar för varje beslut
✅ **Åtgärdsrekommendationer** - Konkreta säkerhetsåtgärder per nivå
✅ **Revisionslogg** - Fullständig spårbarhet

## Arkitektur

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  - Frågeguide (5-7 min)                                      │
│  - Resultatvy med K/R/T/LoA                                  │
│  - Export till JSON/PDF                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  POST /classify  - Klassificera objekt                       │
│  POST /classify/batch - Batchklassificering                  │
│  GET /health - Hälsokontroll                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          ┌──────────────────┐   ┌──────────────┐
          │  Regelmotor (K)  │   │  LLM Adapter │
          │  Regelmotor (R)  │   │  (Privacy-   │
          │  Regelmotor (T)  │   │   maskning)  │
          │  LoA-kalkylator  │   └──────────────┘
          └──────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ Åtgärdskatalog   │
          │ (K/R/T/LoA)      │
          └──────────────────┘
```

## Snabbstart med Docker

### Förutsättningar

- Docker Desktop eller Docker Engine + Docker Compose
- (Valfritt) Anthropic API-nyckel för AI-förbättrade motiveringar

### Steg 1: Klona repository

```bash
git clone <repository-url>
cd Klassa
```

### Steg 2: Konfigurera miljövariabler

```bash
# Backend
cp backend/.env.example backend/.env

# Redigera backend/.env och lägg till din API-nyckel:
# ANTHROPIC_API_KEY=your-api-key-here

# Frontend
cp frontend/.env.local.example frontend/.env.local
```

### Steg 3: Starta med Docker Compose

```bash
# Bygg och starta alla tjänster
docker-compose up --build

# Eller kör i bakgrunden:
docker-compose up -d
```

### Steg 4: Öppna applikationen

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API-dokumentation**: http://localhost:8000/docs

## Lokal utveckling utan Docker

### Backend

```bash
cd backend

# Skapa virtuell miljö
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installera dependencies
pip install -r requirements.txt

# Konfigurera miljövariabler
cp .env.example .env
# Redigera .env

# Starta server
python src/main.py
```

Backend körs på http://localhost:8000

### Frontend

```bash
cd frontend

# Installera dependencies
npm install

# Konfigurera miljövariabler
cp .env.local.example .env.local

# Starta utvecklingsserver
npm run dev
```

Frontend körs på http://localhost:3000

## API-användning

### Klassificera ett objekt

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "test-001",
    "object_name": "Skoladministrationssystem",
    "object_type": "system",
    "personal_data_categories": ["health", "minors"],
    "decision_impact": "authority_decision",
    "rto_hours": 4,
    "legal": {
      "osl_secret": false,
      "article9": true,
      "article10": false,
      "minors": true,
      "public_exposure": false,
      "automated_decision": false
    },
    "external_dependencies": [],
    "recipients": []
  }'
```

### Svar

```json
{
  "object_id": "test-001",
  "krt": { "K": 3, "R": 3, "T": 3 },
  "loa": 3,
  "rationale": {
    "K": ["RULE:art9_sensitive_data", "RULE:minors_vulnerable_data"],
    "R": ["RULE:authority_decisions"],
    "T": ["RULE:rto_4h"],
    "LoA": ["DERIVED:max(K=3,R=3)", "BankID eller SITHS krävs"]
  },
  "confidence": { "K": 0.95, "R": 0.90, "T": 0.88 },
  "suggested_measures": {
    "K": ["End-to-end kryptering", "HSM-baserad nyckelhantering", ...],
    "R": ["Transaktionslogg med oföränderlighet", ...],
    "T": ["Geo-redundans", "RTO ≤4h", ...],
    "LoA": ["BankID-inloggning obligatorisk", ...]
  },
  "audit": {
    "model_version": "krt-1.0.0",
    "timestamp": "2025-10-29T12:00:00Z",
    "classification_time_ms": 156.3
  }
}
```

## Tester

### Kör backend-tester

```bash
cd backend
pytest tests/
```

### Referensfall

Systemet inkluderar 3 referensscenarier från spec.md:

1. **Socialtjänstärenden** (barn, Art. 9, OSL, RTO 4h) → K3 R3 T3 LoA3
2. **Nyhetsbrev** (5k mottagare, namn+e-post) → K1 R1 T1 LoA1
3. **Personalakter** (disciplinärenden, 2k anställda) → K3 R2 T2 LoA3

## Klassningslogik

### Konfidentialitet (K)

| Trigger | Nivå |
|---------|------|
| GDPR Art. 9 (hälsa, religion, fack, etc.) | K3 |
| GDPR Art. 10 (lagöverträdelser) | K3 |
| Skyddade personuppgifter (OSL) | K3 |
| Barn + sårbar data | K3 |
| Ekonomiska uppgifter | K2 |
| Personnummer + identitet | K2 |
| Basidentifierare (namn, e-post) | K1 |

**Modifierare:**
- Volym >50k personer: +1
- Publik exponering: min K2
- OSL-sekretess: K3

### Riktighet (R)

| Trigger | Nivå |
|---------|------|
| Myndighetsbeslut/utbetalning | R3 |
| Säkerhet/insatser | R3 |
| Beslutstöd | R2 |
| Statistik/uppföljning | R1 |

**Modifierare:**
- Automatiserade beslut: +1

### Tillgänglighet (T)

| RTO | Nivå |
|-----|------|
| ≤4 timmar | T3 |
| ≤24 timmar | T2 |
| >24 timmar | T1 |

**Modifierare:**
- Externa beroenden (IdP, folkbokföring): +1

### Level of Assurance (LoA)

```
LoA = max(K, R)
```

- **LoA 3**: BankID eller SITHS-kort krävs
- **LoA 2**: Tvåfaktorsautentisering (BankID on file, SMS)
- **LoA 1**: Enkel lösenordsautentisering

## Projektstruktur

```
Klassa/
├── backend/
│   ├── src/
│   │   ├── klassa/
│   │   │   ├── core/          # Regelmotor, LoA-kalkylator
│   │   │   ├── llm/           # LLM adapter med privacy masking
│   │   │   ├── models/        # Pydantic-modeller
│   │   │   └── api/           # FastAPI endpoints
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js app router
│   │   ├── components/        # React-komponenter
│   │   └── lib/               # Types, API-klient
│   ├── package.json
│   ├── Dockerfile
│   └── .env.local.example
├── tests/
│   └── backend/               # Backend-tester
├── docs/
├── spec.md                    # Fullständig specifikation
├── CLAUDE.md                  # Utvecklarguide för AI
├── docker-compose.yml
└── README.md
```

## Konfiguration

### Backend miljövariabler

```bash
# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# LLM
LLM_PROVIDER=anthropic  # eller: openai, local
ANTHROPIC_API_KEY=your-key
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_TEMPERATURE=0.3

# App
MODEL_VERSION=krt-1.0.0
ENABLE_CORS=true
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend miljövariabler

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Privacy by Design

**KRITISKT**: Systemet är designat så att LLM-lagret ALDRIG får se råa personuppgifter. Endast abstraherade metadata-taggar skickas till AI:n.

Exempel på vad AI:n ser:
```json
{
  "personal_data_tags": ["GDPR_ART9_HEALTH", "MINORS"],
  "volume_class": "HIGH",
  "rto_class": "CRITICAL",
  "decision_impact": "authority_decision"
}
```

AI:n ser ALDRIG faktiska namn, personnummer, hälsodata eller andra personuppgifter.

## Integration

Systemet kan integreras med:

- **ServiceNow/CMDB**: Importera systemkatalog, exportera klassningar
- **M365 Sensitivity Labels**: Propagera K-nivåer till dokumentklassificering
- **DLP-system**: Konfigurera policies baserat på K/R/T
- **Entra ID**: Autentisering och behörighetsstyrning
- **SIEM**: Exportera revisionsloggar

## Säkerhet

- ✅ Kryptering TLS 1.2+ för all trafik
- ✅ Privacy masking för LLM-interaktion
- ✅ CORS-konfiguration
- ✅ Input-validering med Pydantic
- ✅ Fullständig revisionslogg
- ✅ Containeriserad deployment

## Licens

[Specificera licens här]

## Support

- Dokumentation: Se `spec.md` och `CLAUDE.md`
- API-dokumentation: http://localhost:8000/docs
- Issues: [GitHub Issues-länk]

## Bidra

Se CONTRIBUTING.md för riktlinjer.

---

**Version**: 1.0.0
**Modellversion**: krt-1.0.0
**Senast uppdaterad**: 2025-10-29
