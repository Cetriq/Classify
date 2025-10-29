Här är ett konkret, genomarbetat spec-utkast för ett informationsklassningssystem med AI-motor som sätter nivåerna 1–3 för Konfidentialitet, Riktighet, Tillgänglighet (K/R/T) utifrån vilka personuppgifter som förekommer i systemet/processen du klassar.

⸻

1. Syfte och mål
	•	Syfte: Säker, spårbar och konsekvent informationsklassning för kommunal/offentlig miljö.
	•	Mål:
	1.	Automatisera förslag på K/R/T-nivåer 1–3.
	2.	Motivera besluten transparent (”varför blev det nivå X?”).
	3.	Minimera behovet att visa råa personuppgifter för AI (privacy-by-design).
	4.	Integrera med befintlig förvaltningsprocess (t.ex. ServiceNow/ärende, riskanalys, DLP/etiketter).

⸻

2. Omfång
	•	Objekt: System, Applikation, Process/Behandling, Datamängd.
	•	Primär input: Deklaration av personuppgiftskategorier och kontext (volym, mottagare, lagkrav, beslutspåverkan, m.m.).
	•	Output: K/R/T-klass 1–3, motivering, åtgärdsförslag, revisionsdata.

⸻

3. Roller och governance
	•	Systemägare (verksamhet): Godkänner slutlig klassning.
	•	Systemförvaltare IT: Initierar, kompletterar fakta, driver åtgärder.
	•	Informationssäkerhetsfunktion/Dataskydd: Policy, modellvård, kalibrering.
	•	Revisor/Internkontroll: Stickprov, uppföljning.

⸻

4. Nivådefinitioner (kommunal kontext)

Konfidentialitet (K)
	•	1 – Begränsad: Skada begränsad/hanterbar vid röjande.
	•	2 – Kännbar: Skulle skada individers integritet eller förtroende markant (t.ex. samlad persondata om kommuninvånare, arbetsmaterial med skyddsvärde).
	•	3 – Allvarlig: Känsliga personuppgifter (art. 9), uppgifter om lagöverträdelser (art. 10), skyddade personuppgifter, barns sårbara data, sekretessbelagt enligt OSL, eller stora volymer med kopplingsrisk.

Riktighet (R)
	•	1 – Begränsad påverkan: Fel påverkar få/icke-kritiska beslut.
	•	2 – Betydande påverkan: Fel leder till felaktiga beslut/beslutstöd för ärenden, ekonomi eller myndighetsutövning.
	•	3 – Kritisk påverkan: Fel kan orsaka rättsosäkerhet, felaktiga utbetalningar i skala, säkerhetsrisker (t.ex. räddningstjänst, skyddsobjekt).

Tillgänglighet (T)
	•	1 – Tolerant: MTTR/avbrott tolereras (≥5 arbetsdagar) utan större skada.
	•	2 – Viktig: Avbrott >1 arbetsdag ger tydlig påverkan/eftersläpning.
	•	3 – Kritisk: Kräver hög tillgänglighet (≤4 h avbrott; 24/7 eller kontorskritisk topp), lagkrav/medborgarservice beroenden.

⸻

5. Datamodell (metadata-centrerad)

5.1 Inmatat frågeformulär (exempel)
	•	Objektinfo: namn, ägare, syfte, processkategori.
	•	Personuppgiftskategorier (flervalslista, ja/nej + omfattning):
	•	Basidentifierare: namn, personnummer, kontaktuppgifter.
	•	Särskilda kategorier (art. 9): hälsa, religion, fack, biometrisk, genetisk, sexuell läggning.
	•	Lagöverträdelser (art. 10).
	•	Barn (<18).
	•	Ekonomi: konton, skulder, transaktioner.
	•	Lokation/position: adresshistorik, koordinater, rörelsemönster.
	•	Social/sårbarhetsdata: bistånd, socialtjänst, LSS, funktionsnedsättning.
	•	Skyddade personuppgifter: sekretessmarkering, kvarskrivning.
	•	Arbetsdata: personalakter, disciplinärenden.
	•	Volym & täckning: antal registrerade, antal datapunkter/registrerad, historiklängd.
	•	Mottagare/Delning: interna förvaltningar, andra myndigheter, personuppgiftsbiträde, tredjeland?, publik exponering?
	•	Rättslig grund/OSL-anknytning: nämnd, lagrum, beslutstyp.
	•	Beslutspåverkan: påverkar myndighetsbeslut/utbetalning/säkerhet?
	•	Tillgänglighetsbehov: SLA, öppettider, MTD/RTO, beroenden (BankID, folkbokföring, GIS, skolplattform, vårdsystem).

5.2 Outputschema (JSON)

{
  "object_id": "string",
  "krt": { "K": 1, "R": 2, "T": 3 },
  "rationale": {
    "K": ["RULE:art9_health", "RULE:protected_identity", "WEIGHT:volume_high"],
    "R": ["RULE:affects_authority_decisions"],
    "T": ["RULE:critical_service_hours", "RULE:rto_4h"]
  },
  "confidence": { "K": 0.86, "R": 0.74, "T": 0.81 },
  "suggested_measures": {
    "K": ["Kryptering vilande/transport", "Behörighetsstyrning nivå 3", "Logggranskning"],
    "R": ["Två-i-handläggning", "Valideringsregler", "Transaktionslogg"],
    "T": ["Geo-redundans", "Incidentrutin ≤4h", "Övervakning"]
  },
  "audit": { "model_version": "krt-1.3.2", "timestamp": "2025-10-29T12:00:00Z" }
}


⸻

6. Klassningsmotor: arkitektur

6.1 Hybrid: Regler + LLM
	•	Regelverk (deterministiskt): Mappning av personuppgiftskategorier/kontext → baspoäng per axel (K/R/T).
	•	LLM-lager (AI-motor):
	•	Tolkar fritextsvar/kommentarer till metadata-taggar (utan rådata).
	•	Vägnar samman regler när konflikter/edge-cases uppstår.
	•	Genererar motiveringar + åtgärdsrekommendationer.
	•	Körs på minimerad input (endast taggar, volym, lagrum, beroenden).

Princip: AI:n får inte se råa personuppgifter. Endast abstrakterade metadata.

6.2 Beslutslogik (översikt)
	1.	Normalisera input → taggar & kvantiteter.
	2.	Regelscore per axel (tabeller nedan).
	3.	Modifierare: volym, barn, lagöverträdelser, OSL/sekretess, publik delning, kritiska beroenden, RTO/SLA.
	4.	LLM väger konfliktfall och skapar rationale + åtgärdslista.
	5.	Sätt klass som ceil(medelpoäng) inom 1–3 per axel.
	6.	Människa kan överstyra (med skälen loggade).

⸻

7. Regeltabeller (baspoäng)

7.1 Konfidentialitet (K) – bas

Trigger	Poäng
Art. 9 känsliga (hälsa, religion, fack, biometrik, genetik, sexualitet)	3
Art. 10 (lagöverträdelser)	3
Skyddade personuppgifter (sekretessmark., kvarskrivning)	3
Barn + sårbar data (socialtjänst, LSS)	3
Ekonomi (konton, skulder)	2
Personnummer + full identitet i kombinationer	2
Lokations-/rörelsedata	2
Endast basidentifierare (namn, e-post)	1

Modifierare K:
	•	Volym > 50k registrerade: +1 upp till 3
	•	Publik exponering (öppen data utan anonymisering): min 2
	•	OSL-sekretess: min 3

7.2 Riktighet (R) – bas

Trigger	Poäng
Underlag för myndighetsbeslut/utbetalning	3
Påverkar säkerhet/insats (räddning, skyddsobjekt, vårdflöden)	3
Kritiska masterdata (befolkning, fastigheter)	2
Operativ planering/styrning	2
Enbart statistik/uppföljning utan individpåverkan	1

Modifierare R:
	•	Automatiserat beslut (profilering/regelstyrning): +1 upp till 3
	•	Brist på dubbelkontroll/attestflöde: +1

7.3 Tillgänglighet (T) – bas

Trigger	Poäng
RTO ≤ 4h, 24/7 eller samhällskritisk öppettid	3
RTO ≤ 1 arbetsdag	2
RTO > 1 arbetsdag	1

Modifierare T:
	•	Yttre beroenden (IdP, folkbokföring, betalflöden): +1 upp till 3
	•	Hög säsongsbelastning/lagstyrd deadline: +1

⸻

8. Pseudokod för klassning

K = max( baseK(triggers), min(3, baseK + modsK) )
R = max( baseR(triggers), min(3, baseR + modsR) )
T = max( baseT(triggers), min(3, baseT + modsT) )

result.levels = {K, R, T}

if conflicts or ambiguous:
  result.rationale = LLM.explain(tags, scores)
else:
  result.rationale = deterministic_explanation(triggers, mods)

result.suggested_measures = control_catalogue(K,R,T)


⸻

9. UI/UX och arbetsflöde
	1.	Start: Välj objekt (system/process/datamängd) eller importera från register.
	2.	Frågeguide (5–7 min): Förifyllda svar från kataloger där möjligt.
	3.	Förhandsresultat: K/R/T + motivering + åtgärder.
	4.	Överstyr med motivering: Roll-baserad behörighet.
	5.	Export: PDF/Markdown, JSON till ärende.
	6.	Signoff: Systemägare godkänner → lås version 1.0 → logg.

Önskvärda komponenter:
	•	”Vad triggar nivå 3?”-chips på skärmen.
	•	”Vad sänker risken?”-tips (t.ex. pseudonymisering).
	•	Historik & diff mellan versioner.

⸻

10. Säkerhet & efterlevnad
	•	Dataminimering: Endast metadata/etiketter till AI-motorn.
	•	Kryptering: Vilande/transport. Nyckelkontroll på kommunens villkor.
	•	Logg & spårbarhet: Full beslutshistorik, modellversion, regelträffar.
	•	Sekretess: Stöd för OSL-markörer. Separata vyer för känsliga klasser.
	•	Åtkomst: RBAC/ABAC kopplad till Entra ID (roller ovan).
	•	Modellrisk: Dokumenterad modellkatalog, bias-tester, årlig kalibrering.

⸻

11. Åtgärdskatalog (kopplad till nivå)

Exempel (urklipp):
	•	K3: Kryptering E2E, HSM-nycklar, stark MFA, behovsprövad behörighet, logggranskning veckovis, DLP, data-maskning i loggar, tredjelands-TIA krav.
	•	R3: Transaktionslogg med oföränderlighet, teknisk/organisatorisk attest, datavalidering hög, regelbunden stickprovskontroll.
	•	T3: Geo-redundans, RTO ≤ 4h, övervakning & larm, kapacitetsplanering, övade incidentrutiner.

⸻

12. API (OpenAPI-utkast)

openapi: 3.0.3
info:
  title: KRT Klassningsmotor API
  version: 1.0.0
paths:
  /classify:
    post:
      summary: Beräkna K/R/T
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Input'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Output'
components:
  schemas:
    Input:
      type: object
      properties:
        object_id: { type: string }
        tags:
          type: array
          items: { type: string }
        volumes:
          type: object
          properties:
            data_subjects: { type: integer }
            attributes_per_subject: { type: integer }
        rto_hours: { type: number }
        legal:
          type: object
          properties:
            osl_secret: { type: boolean }
            article9: { type: boolean }
            article10: { type: boolean }
            minors: { type: boolean }
            public_exposure: { type: boolean }
        decision_impact: { type: string, enum: [none, support, authority_decision, safety] }
    Output:
      type: object
      properties:
        krt:
          type: object
          properties:
            K: { type: integer, minimum: 1, maximum: 3 }
            R: { type: integer, minimum: 1, maximum: 3 }
            T: { type: integer, minimum: 1, maximum: 3 }
        rationale: { type: object }
        confidence: { type: object }
        suggested_measures: { type: object }
        audit: { type: object }


⸻

13. Datakällor och integration
	•	Källor: Systemkatalog (ServiceNow/CMDB), register över behandlingar, DLP/etiketter, loggplattform.
	•	Mål: Ärende i ServiceNow (”Klassning fastställd”), Excel/PDF-export, M365 Sensitivity Labels, DLP-policy, backup/SLA-profil.
	•	Identitet: Entra ID/OAuth2 för API, SCIM för roller.

⸻

14. Kalibrering & kvalitet
	•	Guldlina: 30–50 referensklassningar godkända av Informationssäkerhet → regress-tester.
	•	Mätetal: Överstyrningsgrad (<15 %), tid till klassning (<10 min), avvikelse i revision (<5 %).
	•	Drift: Modellversionering, canary-release, årlig re-bedömning eller vid större ändring.

⸻

15. Icke-funktionella krav
	•	Prestanda: <2 s/klassning (cachead regelkärna).
	•	Tillgänglighet: 99,9 % (kontorstid) eller enligt T-krav.
	•	Skalning: 10k objekt, 100 samtidiga användare.
	•	Portabilitet: Körbar on-prem/kontrollerad moln. Allt containeriserat.
	•	Loggbarhet: SIEM-integration, dataskyddslogg.

⸻

16. Risker & mitigering
	•	Felklassning p.g.a. fel input: Tvingande minimifakta + validering + utbildning.
	•	AI-hallucination: Hybridmodell + deterministiska spärrar + transparent rationale.
	•	Överexponering av persondata till AI: Endast metadata; kontrollerad infrastruktur.
	•	Regelföråldring: Ägarutpekad releaseprocess + versionsmatris.

⸻

17. Exempelkörningar (snabbtester)
	1.	Socialtjänstärenden, barn, art. 9, OSL, RTO 4h
→ K3 R3 T3 (sekretess, beslutspåverkan, hög tillgänglighet).
	2.	Nyhetsbrevslista (namn+e-post), 5k mottagare, RTO 5 dgr
→ K1 R1 T1.
	3.	Personalakter (disciplinärenden), 2k anställda, attestkrav
→ K3 R2 T2 (art. 10 risk? om ja → R3).

⸻

18. Leverabler
	•	Policy & metodstöd (4–6 sidor): definitioner, ansvar, process.
	•	Regelmatriser (CSV/YAML): triggrar & poäng.
	•	AI-prompter (system-/task-prompts) för rationale/suggested_measures.
	•	Komponenter:
	•	Regelmotor (TS/Python)
	•	LLM-adapter (prompt + maskning)
	•	UI (React/Next.js)
	•	API (OpenAPI ovan)
	•	Exportörer (PDF/JSON/ServiceNow)
	•	Testpaket: 40 referensfall + regress.

⸻
