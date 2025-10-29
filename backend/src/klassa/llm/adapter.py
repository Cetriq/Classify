"""
LLM Adapter with privacy masking.
Ensures AI never sees raw personal data - only metadata tags.
Based on spec.md section 6.1 privacy principles.
"""

import os
from typing import List, Optional, Dict, Any
from anthropic import Anthropic
from ..models.classification import ClassificationInput, DecisionImpact


class LLMAdapter:
    """
    Adapter for LLM interaction with strict privacy controls.

    CRITICAL: AI must NEVER receive raw personal data.
    Only abstracted metadata tags are sent to the LLM.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM client."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    def _create_metadata_summary(self, input_data: ClassificationInput) -> Dict[str, Any]:
        """
        Create privacy-safe metadata summary.
        NO raw personal data - only category tags.
        """
        metadata = {
            "object_type": input_data.object_type,
            "personal_data_tags": [cat.value for cat in input_data.personal_data_categories],
            "decision_impact": input_data.decision_impact.value,
            "legal_flags": {
                "osl_secret": input_data.legal.osl_secret,
                "article9": input_data.legal.article9,
                "article10": input_data.legal.article10,
                "minors": input_data.legal.minors,
                "public_exposure": input_data.legal.public_exposure,
                "automated_decision": input_data.legal.automated_decision,
            }
        }

        if input_data.volumes:
            metadata["volume_class"] = self._classify_volume(
                input_data.volumes.data_subjects
            )

        if input_data.rto_hours is not None:
            metadata["rto_class"] = self._classify_rto(input_data.rto_hours)

        if input_data.external_dependencies:
            metadata["has_external_deps"] = True
            metadata["dependency_count"] = len(input_data.external_dependencies)

        return metadata

    def _classify_volume(self, count: int) -> str:
        """Classify volume into categories."""
        if count > 50000:
            return "HIGH"
        elif count > 10000:
            return "MEDIUM"
        elif count > 1000:
            return "LOW"
        else:
            return "MINIMAL"

    def _classify_rto(self, hours: float) -> str:
        """Classify RTO into categories."""
        if hours <= 4:
            return "CRITICAL"
        elif hours <= 24:
            return "HIGH"
        elif hours <= 120:  # 5 days
            return "MODERATE"
        else:
            return "LOW"

    def generate_enhanced_rationale(
        self,
        input_data: ClassificationInput,
        k_level: int,
        r_level: int,
        t_level: int,
        loa: int,
        rule_triggers: Dict[str, List[str]]
    ) -> str:
        """
        Generate enhanced rationale using LLM.

        Args:
            input_data: Classification input (will be privacy-masked)
            k_level: Calculated K level
            r_level: Calculated R level
            t_level: Calculated T level
            loa: Calculated LoA level
            rule_triggers: Dictionary of triggered rules per dimension

        Returns:
            Enhanced rationale text
        """
        if not self.client:
            return self._fallback_rationale(k_level, r_level, t_level, loa, rule_triggers)

        # Create privacy-safe metadata
        metadata = self._create_metadata_summary(input_data)

        # System prompt emphasizing Swedish public sector context
        system_prompt = """Du är en expert på informationssäkerhet och klassificering i svensk offentlig sektor.
Din uppgift är att förklara KRT-klassificering (Konfidentialitet, Riktighet, Tillgänglighet) och LoA (Level of Assurance)
på ett tydligt sätt för svenska kommuner och myndigheter.

VIKTIGT: Du får ENDAST se metadata-taggar, aldrig faktiska personuppgifter. Detta är en privacy-by-design princip.

Fokusera på:
- GDPR (särskilt artikel 9 och 10)
- OSL (Offentlighets- och sekretesslagen)
- Svenska kommunala krav
- Tydlig, konkret motivering
- Praktiska exempel när relevant
"""

        # User prompt with metadata only
        user_prompt = f"""Förklara denna klassificering för en kommunal systemägare:

KLASSIFICERING:
- Konfidentialitet (K): {k_level}
- Riktighet (R): {r_level}
- Tillgänglighet (T): {t_level}
- Level of Assurance (LoA): {loa}

METADATA (ingen rådata):
{self._format_metadata(metadata)}

AKTIVERADE REGLER:
K-regler: {', '.join(rule_triggers.get('K', []))}
R-regler: {', '.join(rule_triggers.get('R', []))}
T-regler: {', '.join(rule_triggers.get('T', []))}

Ge en kort (2-3 meningar per dimension) förklaring av varför dessa nivåer satts,
med fokus på de viktigaste faktorerna och vad det betyder i praktiken.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            print(f"LLM error: {e}")
            return self._fallback_rationale(k_level, r_level, t_level, loa, rule_triggers)

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for LLM prompt."""
        lines = []
        lines.append(f"Typ: {metadata['object_type']}")
        lines.append(f"Personuppgiftskategorier: {', '.join(metadata['personal_data_tags'])}")
        lines.append(f"Beslutspåverkan: {metadata['decision_impact']}")

        legal = metadata['legal_flags']
        legal_active = [k for k, v in legal.items() if v]
        if legal_active:
            lines.append(f"Juridiska flaggor: {', '.join(legal_active)}")

        if 'volume_class' in metadata:
            lines.append(f"Volymklass: {metadata['volume_class']}")

        if 'rto_class' in metadata:
            lines.append(f"RTO-klass: {metadata['rto_class']}")

        return '\n'.join(lines)

    def _fallback_rationale(
        self,
        k_level: int,
        r_level: int,
        t_level: int,
        loa: int,
        rule_triggers: Dict[str, List[str]]
    ) -> str:
        """Fallback rationale when LLM is not available."""
        parts = []

        # K rationale
        k_triggers = rule_triggers.get('K', [])
        if k_level == 3:
            parts.append(f"Konfidentialitet nivå 3: Känsliga personuppgifter identifierade ({', '.join(k_triggers[:2])}). Kräver högsta skyddsnivå enligt GDPR.")
        elif k_level == 2:
            parts.append(f"Konfidentialitet nivå 2: Personuppgifter med skyddsvärde ({', '.join(k_triggers[:2])}). Kräver förstärkt skydd.")
        else:
            parts.append("Konfidentialitet nivå 1: Begränsade personuppgifter. Grundläggande skydd räcker.")

        # R rationale
        r_triggers = rule_triggers.get('R', [])
        if r_level == 3:
            parts.append(f"Riktighet nivå 3: Kritisk påverkan på beslut eller säkerhet ({', '.join(r_triggers[:2])}). Kräver strikta kontroller.")
        elif r_level == 2:
            parts.append(f"Riktighet nivå 2: Betydande påverkan på verksamhet ({', '.join(r_triggers[:2])}). Kräver validering och kontroll.")
        else:
            parts.append("Riktighet nivå 1: Begränsad påverkan. Grundläggande kvalitetssäkring räcker.")

        # T rationale
        t_triggers = rule_triggers.get('T', [])
        if t_level == 3:
            parts.append(f"Tillgänglighet nivå 3: Kritiskt för verksamheten ({', '.join(t_triggers[:2])}). Kräver hög driftsäkerhet.")
        elif t_level == 2:
            parts.append(f"Tillgänglighet nivå 2: Viktig för verksamheten ({', '.join(t_triggers[:2])}). Kräver god driftsäkerhet.")
        else:
            parts.append("Tillgänglighet nivå 1: Tolerant för avbrott. Grundläggande drift räcker.")

        # LoA rationale
        parts.append(f"\nLevel of Assurance {loa}: Baserat på max(K={k_level}, R={r_level}). "
                    f"{'Stark autentisering (BankID/SITHS) krävs.' if loa == 3 else 'Tvåfaktorsautentisering krävs.' if loa == 2 else 'Enkel autentisering acceptabel.'}")

        return "\n\n".join(parts)
