"""
Rule engine for KRT classification.
Implements the deterministic rule tables from spec.md sections 7.1-7.3.
"""

from typing import List, Tuple
from ..models.classification import (
    ClassificationInput,
    PersonalDataCategory,
    DecisionImpact,
)


class RuleEngine:
    """
    Deterministic rule engine for K/R/T classification.

    Implements the logic from spec.md:
    K = max(baseK(triggers), min(3, baseK + modsK))
    R = max(baseR(triggers), min(3, baseR + modsR))
    T = max(baseT(triggers), min(3, baseT + modsT))
    """

    # K (Konfidentialitet) base triggers - spec.md 7.1
    K_RULES = {
        # GDPR Article 9 special categories
        PersonalDataCategory.HEALTH: 3,
        PersonalDataCategory.RELIGION: 3,
        PersonalDataCategory.UNION_MEMBERSHIP: 3,
        PersonalDataCategory.BIOMETRIC: 3,
        PersonalDataCategory.GENETIC: 3,
        PersonalDataCategory.SEXUAL_ORIENTATION: 3,

        # GDPR Article 10
        PersonalDataCategory.CRIMINAL_CONVICTIONS: 3,

        # Swedish protected identities
        PersonalDataCategory.PROTECTED_IDENTITY: 3,
        PersonalDataCategory.RETAINED_ADDRESS: 3,

        # Minors + vulnerability (combined check in logic)
        PersonalDataCategory.SOCIAL_VULNERABILITY: 2,  # Raised to 3 if minors

        # Financial data
        PersonalDataCategory.FINANCIAL: 2,

        # Personal number + full identity
        PersonalDataCategory.PERSONAL_NUMBER: 2,

        # Location/movement data
        PersonalDataCategory.LOCATION: 2,

        # Basic identifiers only
        PersonalDataCategory.BASIC_IDENTIFIERS: 1,
        PersonalDataCategory.CONTACT_INFO: 1,

        # Employment data
        PersonalDataCategory.EMPLOYMENT: 2,
    }

    def __init__(self):
        self.triggers_k: List[str] = []
        self.triggers_r: List[str] = []
        self.triggers_t: List[str] = []

    def classify_k(self, input_data: ClassificationInput) -> Tuple[int, List[str]]:
        """
        Classify Confidentiality (K) level.
        Returns: (level, triggers)
        """
        triggers = []
        base_scores = []

        # Check GDPR Article 9 categories
        art9_categories = {
            PersonalDataCategory.HEALTH,
            PersonalDataCategory.RELIGION,
            PersonalDataCategory.UNION_MEMBERSHIP,
            PersonalDataCategory.BIOMETRIC,
            PersonalDataCategory.GENETIC,
            PersonalDataCategory.SEXUAL_ORIENTATION,
        }

        if any(cat in input_data.personal_data_categories for cat in art9_categories):
            triggers.append("RULE:art9_sensitive_data")
            base_scores.append(3)

        # Check GDPR Article 10
        if PersonalDataCategory.CRIMINAL_CONVICTIONS in input_data.personal_data_categories:
            triggers.append("RULE:art10_criminal_data")
            base_scores.append(3)

        # Check protected identities
        if PersonalDataCategory.PROTECTED_IDENTITY in input_data.personal_data_categories:
            triggers.append("RULE:protected_identity")
            base_scores.append(3)

        if PersonalDataCategory.RETAINED_ADDRESS in input_data.personal_data_categories:
            triggers.append("RULE:retained_address")
            base_scores.append(3)

        # Check minors + vulnerable data
        if (input_data.legal.minors and
            PersonalDataCategory.SOCIAL_VULNERABILITY in input_data.personal_data_categories):
            triggers.append("RULE:minors_vulnerable_data")
            base_scores.append(3)
        elif PersonalDataCategory.SOCIAL_VULNERABILITY in input_data.personal_data_categories:
            triggers.append("RULE:social_vulnerability")
            base_scores.append(2)

        # Check financial data
        if PersonalDataCategory.FINANCIAL in input_data.personal_data_categories:
            triggers.append("RULE:financial_data")
            base_scores.append(2)

        # Check personal number + full identity
        if PersonalDataCategory.PERSONAL_NUMBER in input_data.personal_data_categories:
            triggers.append("RULE:personal_number")
            base_scores.append(2)

        # Check location data
        if PersonalDataCategory.LOCATION in input_data.personal_data_categories:
            triggers.append("RULE:location_data")
            base_scores.append(2)

        # Check employment data
        if PersonalDataCategory.EMPLOYMENT in input_data.personal_data_categories:
            triggers.append("RULE:employment_data")
            base_scores.append(2)

        # Basic identifiers
        basic_cats = {
            PersonalDataCategory.BASIC_IDENTIFIERS,
            PersonalDataCategory.CONTACT_INFO,
        }
        if any(cat in input_data.personal_data_categories for cat in basic_cats) and not base_scores:
            triggers.append("RULE:basic_identifiers")
            base_scores.append(1)

        # Calculate base K
        base_k = max(base_scores) if base_scores else 1

        # Apply modifiers (spec.md 7.1)
        modifiers = 0

        # Volume modifier: > 50k registrerade
        if input_data.volumes and input_data.volumes.data_subjects > 50000:
            triggers.append("MODIFIER:volume_high")
            modifiers += 1

        # Public exposure modifier
        if input_data.legal.public_exposure:
            triggers.append("MODIFIER:public_exposure")
            base_k = max(base_k, 2)  # min 2

        # OSL secrecy modifier
        if input_data.legal.osl_secret:
            triggers.append("MODIFIER:osl_secret")
            base_k = 3  # Always 3

        # Final K level
        final_k = max(base_k, min(3, base_k + modifiers))

        self.triggers_k = triggers
        return final_k, triggers

    def classify_r(self, input_data: ClassificationInput) -> Tuple[int, List[str]]:
        """
        Classify Accuracy (R) level.
        Returns: (level, triggers)
        """
        triggers = []
        base_scores = []

        # Authority decisions/payments (spec.md 7.2)
        if input_data.decision_impact == DecisionImpact.AUTHORITY_DECISION:
            triggers.append("RULE:authority_decisions")
            base_scores.append(3)

        # Safety/security impact
        if input_data.decision_impact == DecisionImpact.SAFETY:
            triggers.append("RULE:safety_critical")
            base_scores.append(3)

        # Support for decisions
        if input_data.decision_impact == DecisionImpact.SUPPORT:
            triggers.append("RULE:decision_support")
            base_scores.append(2)

        # Default: statistics/reporting only
        if not base_scores:
            triggers.append("RULE:statistics_only")
            base_scores.append(1)

        # Calculate base R
        base_r = max(base_scores) if base_scores else 1

        # Apply modifiers (spec.md 7.2)
        modifiers = 0

        # Automated decision modifier
        if input_data.legal.automated_decision:
            triggers.append("MODIFIER:automated_decision")
            modifiers += 1

        # Final R level
        final_r = max(base_r, min(3, base_r + modifiers))

        self.triggers_r = triggers
        return final_r, triggers

    def classify_t(self, input_data: ClassificationInput) -> Tuple[int, List[str]]:
        """
        Classify Availability (T) level.
        Returns: (level, triggers)
        """
        triggers = []
        base_t = 1

        # RTO-based classification (spec.md 7.3)
        if input_data.rto_hours is not None:
            if input_data.rto_hours <= 4:
                triggers.append("RULE:rto_4h")
                base_t = 3
            elif input_data.rto_hours <= 24:
                triggers.append("RULE:rto_1day")
                base_t = 2
            else:
                triggers.append("RULE:rto_tolerant")
                base_t = 1
        else:
            triggers.append("RULE:rto_not_specified")
            base_t = 1

        # Apply modifiers (spec.md 7.3)
        modifiers = 0

        # External dependencies modifier
        if input_data.external_dependencies:
            triggers.append(f"MODIFIER:external_dependencies_{len(input_data.external_dependencies)}")
            modifiers += 1

        # Final T level
        final_t = max(base_t, min(3, base_t + modifiers))

        self.triggers_t = triggers
        return final_t, triggers

    def calculate_confidence(
        self,
        input_data: ClassificationInput,
        k_level: int,
        r_level: int,
        t_level: int
    ) -> Tuple[float, float, float]:
        """
        Calculate confidence scores for K/R/T classifications.
        Higher confidence when more explicit data is provided.
        """
        # K confidence: based on explicit personal data categories
        k_confidence = 0.7
        if input_data.personal_data_categories:
            k_confidence += 0.2
        if input_data.legal.article9 or input_data.legal.article10:
            k_confidence = min(0.95, k_confidence + 0.1)

        # R confidence: based on decision impact clarity
        r_confidence = 0.7
        if input_data.decision_impact != DecisionImpact.NONE:
            r_confidence += 0.2

        # T confidence: based on RTO specification
        t_confidence = 0.7
        if input_data.rto_hours is not None:
            t_confidence += 0.2

        return k_confidence, r_confidence, t_confidence
