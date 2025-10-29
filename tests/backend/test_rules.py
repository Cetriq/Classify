"""
Unit tests for rule engine.
Tests the classification logic from spec.md sections 7.1-7.3.
"""

import pytest
from backend.src.klassa.core.rules import RuleEngine
from backend.src.klassa.models.classification import (
    ClassificationInput,
    PersonalDataCategory,
    DecisionImpact,
    LegalContext,
    VolumeData,
)


class TestKonfidentialitetRules:
    """Test Confidentiality (K) classification rules."""

    def test_art9_health_triggers_k3(self):
        """GDPR Art. 9 health data should trigger K=3."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-001",
            object_name="Vårdregister",
            personal_data_categories=[PersonalDataCategory.HEALTH],
            legal=LegalContext(article9=True)
        )

        k_level, triggers = engine.classify_k(input_data)

        assert k_level == 3
        assert "RULE:art9_sensitive_data" in triggers

    def test_art10_criminal_triggers_k3(self):
        """GDPR Art. 10 criminal data should trigger K=3."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-002",
            object_name="Brottsregister",
            personal_data_categories=[PersonalDataCategory.CRIMINAL_CONVICTIONS],
            legal=LegalContext(article10=True)
        )

        k_level, triggers = engine.classify_k(input_data)

        assert k_level == 3
        assert "RULE:art10_criminal_data" in triggers

    def test_protected_identity_triggers_k3(self):
        """Protected identity should trigger K=3."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-003",
            object_name="Skyddade personuppgifter",
            personal_data_categories=[PersonalDataCategory.PROTECTED_IDENTITY],
            legal=LegalContext()
        )

        k_level, triggers = engine.classify_k(input_data)

        assert k_level == 3
        assert "RULE:protected_identity" in triggers

    def test_minors_vulnerable_triggers_k3(self):
        """Minors + vulnerable data should trigger K=3."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-004",
            object_name="Socialtjänstärenden",
            personal_data_categories=[PersonalDataCategory.SOCIAL_VULNERABILITY],
            legal=LegalContext(minors=True)
        )

        k_level, triggers = engine.classify_k(input_data)

        assert k_level == 3
        assert "RULE:minors_vulnerable_data" in triggers

    def test_financial_triggers_k2(self):
        """Financial data should trigger K=2."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-005",
            object_name="Ekonomisystem",
            personal_data_categories=[PersonalDataCategory.FINANCIAL],
            legal=LegalContext()
        )

        k_level, triggers = engine.classify_k(input_data)

        assert k_level == 2
        assert "RULE:financial_data" in triggers

    def test_basic_identifiers_triggers_k1(self):
        """Basic identifiers only should trigger K=1."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-006",
            object_name="Nyhetsbrev",
            personal_data_categories=[PersonalDataCategory.BASIC_IDENTIFIERS],
            legal=LegalContext()
        )

        k_level, triggers = engine.classify_k(input_data)

        assert k_level == 1
        assert "RULE:basic_identifiers" in triggers

    def test_volume_modifier(self):
        """High volume (>50k) should add +1 to K."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-007",
            object_name="Stor databas",
            personal_data_categories=[PersonalDataCategory.CONTACT_INFO],
            volumes=VolumeData(data_subjects=60000),
            legal=LegalContext()
        )

        k_level, triggers = engine.classify_k(input_data)

        assert k_level >= 1
        assert "MODIFIER:volume_high" in triggers

    def test_osl_secret_forces_k3(self):
        """OSL secrecy should always result in K=3."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-008",
            object_name="Sekretessbelagt",
            personal_data_categories=[PersonalDataCategory.BASIC_IDENTIFIERS],
            legal=LegalContext(osl_secret=True)
        )

        k_level, triggers = engine.classify_k(input_data)

        assert k_level == 3
        assert "MODIFIER:osl_secret" in triggers


class TestRiktighetRules:
    """Test Accuracy (R) classification rules."""

    def test_authority_decision_triggers_r3(self):
        """Authority decisions should trigger R=3."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-101",
            object_name="Beslutsstödsystem",
            decision_impact=DecisionImpact.AUTHORITY_DECISION,
            legal=LegalContext()
        )

        r_level, triggers = engine.classify_r(input_data)

        assert r_level == 3
        assert "RULE:authority_decisions" in triggers

    def test_safety_critical_triggers_r3(self):
        """Safety-critical systems should trigger R=3."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-102",
            object_name="Räddningstjänst system",
            decision_impact=DecisionImpact.SAFETY,
            legal=LegalContext()
        )

        r_level, triggers = engine.classify_r(input_data)

        assert r_level == 3
        assert "RULE:safety_critical" in triggers

    def test_decision_support_triggers_r2(self):
        """Decision support should trigger R=2."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-103",
            object_name="Analysverktyg",
            decision_impact=DecisionImpact.SUPPORT,
            legal=LegalContext()
        )

        r_level, triggers = engine.classify_r(input_data)

        assert r_level == 2
        assert "RULE:decision_support" in triggers

    def test_no_decision_impact_triggers_r1(self):
        """No decision impact should trigger R=1."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-104",
            object_name="Statistikrapport",
            decision_impact=DecisionImpact.NONE,
            legal=LegalContext()
        )

        r_level, triggers = engine.classify_r(input_data)

        assert r_level == 1
        assert "RULE:statistics_only" in triggers

    def test_automated_decision_modifier(self):
        """Automated decisions should add +1 to R."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-105",
            object_name="Automatiskt system",
            decision_impact=DecisionImpact.SUPPORT,
            legal=LegalContext(automated_decision=True)
        )

        r_level, triggers = engine.classify_r(input_data)

        assert r_level >= 2
        assert "MODIFIER:automated_decision" in triggers


class TestTillgänglighetRules:
    """Test Availability (T) classification rules."""

    def test_rto_4h_triggers_t3(self):
        """RTO ≤4h should trigger T=3."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-201",
            object_name="Kritiskt system",
            rto_hours=4.0,
            legal=LegalContext()
        )

        t_level, triggers = engine.classify_t(input_data)

        assert t_level == 3
        assert "RULE:rto_4h" in triggers

    def test_rto_1day_triggers_t2(self):
        """RTO ≤24h should trigger T=2."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-202",
            object_name="Viktigt system",
            rto_hours=20.0,
            legal=LegalContext()
        )

        t_level, triggers = engine.classify_t(input_data)

        assert t_level == 2
        assert "RULE:rto_1day" in triggers

    def test_rto_tolerant_triggers_t1(self):
        """RTO >24h should trigger T=1."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-203",
            object_name="Tolerant system",
            rto_hours=120.0,
            legal=LegalContext()
        )

        t_level, triggers = engine.classify_t(input_data)

        assert t_level == 1
        assert "RULE:rto_tolerant" in triggers

    def test_external_dependencies_modifier(self):
        """External dependencies should add modifier."""
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="test-204",
            object_name="System med beroenden",
            rto_hours=20.0,
            external_dependencies=["BankID", "Folkbokföring"],
            legal=LegalContext()
        )

        t_level, triggers = engine.classify_t(input_data)

        assert any("MODIFIER:external_dependencies" in t for t in triggers)


class TestReferenceScenarios:
    """Test reference scenarios from spec.md section 17."""

    def test_socialtjänst_barn_art9_osl(self):
        """
        Scenario 1: Socialtjänstärenden, barn, art. 9, OSL, RTO 4h
        Expected: K3 R3 T3
        """
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="ref-001",
            object_name="Socialtjänstärenden barn",
            personal_data_categories=[
                PersonalDataCategory.HEALTH,
                PersonalDataCategory.SOCIAL_VULNERABILITY,
            ],
            decision_impact=DecisionImpact.AUTHORITY_DECISION,
            rto_hours=4.0,
            legal=LegalContext(
                article9=True,
                minors=True,
                osl_secret=True
            )
        )

        k_level, _ = engine.classify_k(input_data)
        r_level, _ = engine.classify_r(input_data)
        t_level, _ = engine.classify_t(input_data)

        assert k_level == 3, "Socialtjänst barn should be K3"
        assert r_level == 3, "Authority decisions should be R3"
        assert t_level == 3, "RTO 4h should be T3"

    def test_newsletter_simple(self):
        """
        Scenario 2: Nyhetsbrevslista (namn+e-post), 5k mottagare, RTO 5 dgr
        Expected: K1 R1 T1
        """
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="ref-002",
            object_name="Nyhetsbrev",
            personal_data_categories=[PersonalDataCategory.CONTACT_INFO],
            volumes=VolumeData(data_subjects=5000),
            decision_impact=DecisionImpact.NONE,
            rto_hours=120.0,  # 5 days
            legal=LegalContext()
        )

        k_level, _ = engine.classify_k(input_data)
        r_level, _ = engine.classify_r(input_data)
        t_level, _ = engine.classify_t(input_data)

        assert k_level == 1, "Newsletter should be K1"
        assert r_level == 1, "No decision impact should be R1"
        assert t_level == 1, "RTO 5 days should be T1"

    def test_personalakter_disciplinär(self):
        """
        Scenario 3: Personalakter (disciplinärenden), 2k anställda
        Expected: K3 R2 T2
        """
        engine = RuleEngine()
        input_data = ClassificationInput(
            object_id="ref-003",
            object_name="Personalakter disciplinär",
            personal_data_categories=[
                PersonalDataCategory.EMPLOYMENT,
                PersonalDataCategory.CRIMINAL_CONVICTIONS,  # If criminal -> Art. 10
            ],
            volumes=VolumeData(data_subjects=2000),
            decision_impact=DecisionImpact.SUPPORT,
            rto_hours=24.0,
            legal=LegalContext(article10=True)
        )

        k_level, _ = engine.classify_k(input_data)
        r_level, _ = engine.classify_r(input_data)
        t_level, _ = engine.classify_t(input_data)

        assert k_level == 3, "Art. 10 employment data should be K3"
        assert r_level == 2, "Decision support should be R2"
        assert t_level == 2, "RTO 1 day should be T2"
