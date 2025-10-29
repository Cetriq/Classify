# Klassa API-dokumentation

## Översikt

Klassa erbjuder ett REST API för KRT-klassificering av informationssystem.

**Base URL**: `http://localhost:8000`

**Interaktiv dokumentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### POST /classify

Klassificera ett enskilt objekt (system, applikation, process, datamängd).

**Request Body:**

```json
{
  "object_id": "string",
  "object_name": "string",
  "object_type": "system",
  "personal_data_categories": [
    "health",
    "minors"
  ],
  "volumes": {
    "data_subjects": 5000,
    "attributes_per_subject": 20
  },
  "rto_hours": 4.0,
  "legal": {
    "osl_secret": false,
    "article9": true,
    "article10": false,
    "minors": true,
    "public_exposure": false,
    "automated_decision": false
  },
  "decision_impact": "authority_decision",
  "external_dependencies": ["BankID"],
  "recipients": ["Vårdpersonal"],
  "free_text_context": "Tillvalsbeskrivning..."
}
```

**Response:**

```json
{
  "object_id": "string",
  "krt": {
    "K": 3,
    "R": 3,
    "T": 3
  },
  "loa": 3,
  "rationale": {
    "K": ["RULE:art9_sensitive_data", "..."],
    "R": ["RULE:authority_decisions"],
    "T": ["RULE:rto_4h"],
    "LoA": ["DERIVED:max(K=3,R=3)", "..."]
  },
  "confidence": {
    "K": 0.95,
    "R": 0.90,
    "T": 0.88
  },
  "suggested_measures": {
    "K": ["End-to-end kryptering", "..."],
    "R": ["Transaktionslogg", "..."],
    "T": ["Geo-redundans", "..."],
    "LoA": ["BankID-inloggning obligatorisk", "..."]
  },
  "audit": {
    "model_version": "krt-1.0.0",
    "timestamp": "2025-10-29T12:00:00Z",
    "classification_time_ms": 156.3,
    "overridden": false
  }
}
```

### POST /classify/batch

Klassificera flera objekt samtidigt (max 100).

**Request Body:** Array av ClassificationInput

**Response:** Array av ClassificationOutput

### GET /health

Hälsokontroll.

**Response:**

```json
{
  "status": "healthy",
  "classifier": "ready"
}
```

## Personuppgiftskategorier

Tillgängliga värden för `personal_data_categories`:

### Basidentifierare
- `basic_identifiers` - Namn, e-post
- `personal_number` - Personnummer
- `contact_info` - Kontaktuppgifter

### GDPR Article 9 (känsliga)
- `health` - Hälsodata
- `religion` - Religion
- `union` - Fackligt medlemskap
- `biometric` - Biometrisk data
- `genetic` - Genetisk data
- `sexual_orientation` - Sexuell läggning

### GDPR Article 10
- `criminal_convictions` - Lagöverträdelser

### Svenska kategorier
- `protected_identity` - Skyddad identitet (sekretessmarkering)
- `retained_address` - Kvarskrivning

### Övriga
- `minors` - Barn (<18 år)
- `financial` - Ekonomiska uppgifter
- `location` - Lokaliseringsdata
- `social_vulnerability` - Socialtjänst/LSS/sårbarhet
- `employment` - Personaluppgifter

## Beslutspåverkan

Värden för `decision_impact`:

- `none` - Ingen beslutspåverkan
- `support` - Beslutstöd
- `authority_decision` - Myndighetsbeslut/utbetalning
- `safety` - Säkerhet/insatser

## Exempel

### Curl

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d @examples/socialtjanst.json
```

### Python

```python
import requests

input_data = {
    "object_id": "test-001",
    "object_name": "Vårdregister",
    "object_type": "system",
    "personal_data_categories": ["health"],
    "legal": {
        "article9": True,
        "osl_secret": False,
        "article10": False,
        "minors": False,
        "public_exposure": False,
        "automated_decision": False
    },
    "decision_impact": "authority_decision",
    "rto_hours": 4.0,
    "external_dependencies": [],
    "recipients": []
}

response = requests.post(
    "http://localhost:8000/classify",
    json=input_data
)

result = response.json()
print(f"K={result['krt']['K']} R={result['krt']['R']} T={result['krt']['T']} LoA={result['loa']}")
```

### JavaScript/TypeScript

```typescript
const response = await fetch('http://localhost:8000/classify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(inputData)
});

const result = await response.json();
console.log(`K=${result.krt.K} R=${result.krt.R} T=${result.krt.T} LoA=${result.loa}`);
```

## Felhantering

API:t returnerar HTTP-statuskoder:

- `200` - Framgång
- `400` - Felaktig input (validering misslyckades)
- `500` - Serverfel
- `503` - Klassificerare inte initierad

Felresponser:

```json
{
  "detail": "Felmeddelande här"
}
```
