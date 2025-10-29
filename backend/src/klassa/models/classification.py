"""
Data models for KRT classification system.
Based on spec.md sections 5.1 and 5.2.
"""

from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DecisionImpact(str, Enum):
    """Impact on decision-making processes."""
    NONE = "none"
    SUPPORT = "support"
    AUTHORITY_DECISION = "authority_decision"
    SAFETY = "safety"


class PersonalDataCategory(str, Enum):
    """Personal data categories per GDPR and Swedish context."""
    # Base identifiers
    BASIC_IDENTIFIERS = "basic_identifiers"  # namn, e-post
    PERSONAL_NUMBER = "personal_number"  # personnummer
    CONTACT_INFO = "contact_info"

    # GDPR Article 9 - Special categories
    HEALTH = "health"
    RELIGION = "religion"
    UNION_MEMBERSHIP = "union"
    BIOMETRIC = "biometric"
    GENETIC = "genetic"
    SEXUAL_ORIENTATION = "sexual_orientation"

    # GDPR Article 10
    CRIMINAL_CONVICTIONS = "criminal_convictions"

    # Swedish specific
    PROTECTED_IDENTITY = "protected_identity"  # sekretessmarkering
    RETAINED_ADDRESS = "retained_address"  # kvarskrivning

    # Context categories
    MINORS = "minors"  # barn <18
    FINANCIAL = "financial"  # konton, skulder
    LOCATION = "location"  # adresshistorik, koordinater
    SOCIAL_VULNERABILITY = "social_vulnerability"  # bistånd, LSS
    EMPLOYMENT = "employment"  # personalakter


class VolumeData(BaseModel):
    """Volume and coverage data."""
    data_subjects: int = Field(ge=0, description="Antal registrerade")
    attributes_per_subject: Optional[int] = Field(None, ge=0, description="Antal datapunkter per registrerad")
    history_years: Optional[int] = Field(None, ge=0, description="Historiklängd i år")


class LegalContext(BaseModel):
    """Legal and regulatory context."""
    osl_secret: bool = Field(False, description="OSL sekretess tillämplig")
    article9: bool = Field(False, description="GDPR Art. 9 data")
    article10: bool = Field(False, description="GDPR Art. 10 data")
    minors: bool = Field(False, description="Barn <18 år")
    public_exposure: bool = Field(False, description="Publik exponering")
    automated_decision: bool = Field(False, description="Automatiserat beslut")


class ClassificationInput(BaseModel):
    """Input for classification engine."""
    object_id: str = Field(..., description="Unikt ID för objektet")
    object_name: str = Field(..., description="Namn på system/process")
    object_type: str = Field("system", description="Typ: system, application, process, dataset")

    # Personal data categories
    personal_data_categories: List[PersonalDataCategory] = Field(
        default_factory=list,
        description="Personuppgiftskategorier som förekommer"
    )

    # Volume and context
    volumes: Optional[VolumeData] = None
    rto_hours: Optional[float] = Field(None, ge=0, description="RTO i timmar")

    # Legal context
    legal: LegalContext = Field(default_factory=LegalContext)

    # Decision impact
    decision_impact: DecisionImpact = Field(
        DecisionImpact.NONE,
        description="Påverkan på beslut"
    )

    # Additional context
    external_dependencies: List[str] = Field(
        default_factory=list,
        description="Externa beroenden (IdP, folkbokföring, etc.)"
    )
    recipients: List[str] = Field(
        default_factory=list,
        description="Mottagare av data"
    )
    free_text_context: Optional[str] = Field(
        None,
        description="Fritextbeskrivning av kontext"
    )


class KRTLevels(BaseModel):
    """K/R/T classification levels (1-3)."""
    K: int = Field(..., ge=1, le=3, description="Konfidentialitet")
    R: int = Field(..., ge=1, le=3, description="Riktighet")
    T: int = Field(..., ge=1, le=3, description="Tillgänglighet")


class Rationale(BaseModel):
    """Rationale for classification decisions."""
    K: List[str] = Field(default_factory=list, description="K-triggers och motivering")
    R: List[str] = Field(default_factory=list, description="R-triggers och motivering")
    T: List[str] = Field(default_factory=list, description="T-triggers och motivering")
    LoA: List[str] = Field(default_factory=list, description="LoA-motivering")


class ConfidenceScores(BaseModel):
    """Confidence scores for each dimension."""
    K: float = Field(..., ge=0.0, le=1.0)
    R: float = Field(..., ge=0.0, le=1.0)
    T: float = Field(..., ge=0.0, le=1.0)


class SuggestedMeasures(BaseModel):
    """Suggested security measures per dimension."""
    K: List[str] = Field(default_factory=list)
    R: List[str] = Field(default_factory=list)
    T: List[str] = Field(default_factory=list)
    LoA: List[str] = Field(default_factory=list)


class AuditInfo(BaseModel):
    """Audit trail information."""
    model_version: str = Field(..., description="Modellversion")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    classification_time_ms: Optional[float] = Field(None, description="Klassifiieringstid")
    overridden: bool = Field(False, description="Manuellt överskriven")
    override_reason: Optional[str] = None


class ClassificationOutput(BaseModel):
    """Output from classification engine."""
    object_id: str
    krt: KRTLevels
    loa: int = Field(..., ge=1, le=3, description="Level of Assurance")
    rationale: Rationale
    confidence: ConfidenceScores
    suggested_measures: SuggestedMeasures
    audit: AuditInfo
