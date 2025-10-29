# Snabbstart - Klassa

Kom igång med Klassa på 5 minuter.

## Steg 1: Förutsättningar

Installera:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (rekommenderat)
- ELLER Python 3.11+ och Node.js 20+

## Steg 2: Klona och konfigurera

```bash
# Klona repository
git clone <repository-url>
cd Klassa

# Kopiera environment-filer
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# (Valfritt) Lägg till Anthropic API-nyckel i backend/.env
# ANTHROPIC_API_KEY=sk-ant-...
```

## Steg 3: Starta med Docker

```bash
# Bygg och starta
docker-compose up --build

# Eller i bakgrunden:
docker-compose up -d
```

Vänta ~30 sekunder medan containrarna startar.

## Steg 4: Öppna applikationen

🌐 **Frontend**: http://localhost:3000
📚 **API Docs**: http://localhost:8000/docs

## Steg 5: Testa klassificering

### Via UI (http://localhost:3000)

1. Fyll i systemnamn (t.ex. "Vårdregister")
2. Välj personuppgiftskategorier (t.ex. "Hälsodata")
3. Ange beslutspåverkan
4. Fyll i RTO-timmar
5. Klicka "Klassificera"
6. Se resultat: K/R/T + LoA med motivering och åtgärder

### Via API

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "test-001",
    "object_name": "Testsystem",
    "object_type": "system",
    "personal_data_categories": ["health"],
    "decision_impact": "authority_decision",
    "rto_hours": 4,
    "legal": {
      "osl_secret": false,
      "article9": true,
      "article10": false,
      "minors": false,
      "public_exposure": false,
      "automated_decision": false
    },
    "external_dependencies": [],
    "recipients": []
  }'
```

Förväntat resultat: **K3 R3 T3 LoA3**

## Steg 6: Stoppa systemet

```bash
# Stoppa containers
docker-compose down

# Stoppa och ta bort volymer
docker-compose down -v
```

## Alternativ: Lokal utveckling utan Docker

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Nästa steg

- Läs [API.md](./API.md) för fullständig API-dokumentation
- Se [README.md](../README.md) för detaljerad systemdokumentation
- Utforska [spec.md](../spec.md) för kompletta klassningsregler
- Kör tester: `pytest tests/` (backend)

## Felsökning

### Docker-problem

```bash
# Rensa allt och börja om
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Port redan i bruk

```bash
# Ändra portar i docker-compose.yml
# Backend: "8001:8000" istället för "8000:8000"
# Frontend: "3001:3000" istället för "3000:3000"
```

### API-nyckel saknas

Systemet fungerar utan API-nyckel, men ger grundläggande motiveringar istället för AI-förbättrade.

För bättre motiveringar, lägg till i `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Hjälp

- API-dokumentation: http://localhost:8000/docs
- GitHub Issues: [länk]
- Se README.md för mer information
