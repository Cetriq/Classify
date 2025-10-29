"""
Main classification engine orchestrating all components.
Implements the hybrid rule + LLM approach from spec.md section 6.
"""

import os
import time
from datetime import datetime
from typing import Optional

from .rules import RuleEngine
from .loa import LoACalculator
from .measures import MeasuresCatalog
from ..llm.adapter import LLMAdapter
from ..models.classification import (
    ClassificationInput,
    ClassificationOutput,
    KRTLevels,
    Rationale,
    ConfidenceScores,
    SuggestedMeasures,
    AuditInfo,
)


class Classifier:
    """
    Main KRT classification engine.

    Orchestrates:
    1. Deterministic rule engine (K/R/T base classification)
    2. LoA calculator (authentication level)
    3. LLM adapter (enhanced rationale, edge cases)
    4. Measures catalog (security recommendations)
    """

    def __init__(self, llm_api_key: Optional[str] = None):
        """
        Initialize classifier.

        Args:
            llm_api_key: Optional API key for LLM. If not provided, uses env var.
        """
        self.rule_engine = RuleEngine()
        self.loa_calculator = LoACalculator()
        self.measures_catalog = MeasuresCatalog()
        self.llm_adapter = LLMAdapter(api_key=llm_api_key)
        self.model_version = os.getenv("MODEL_VERSION", "krt-1.0.0")

    def classify(self, input_data: ClassificationInput) -> ClassificationOutput:
        """
        Perform complete KRT + LoA classification.

        Args:
            input_data: Classification input data

        Returns:
            Complete classification output with K/R/T/LoA levels,
            rationale, confidence scores, and suggested measures.
        """
        start_time = time.time()

        # Step 1: Rule-based classification
        k_level, k_triggers = self.rule_engine.classify_k(input_data)
        r_level, r_triggers = self.rule_engine.classify_r(input_data)
        t_level, t_triggers = self.rule_engine.classify_t(input_data)

        # Step 2: Calculate LoA
        loa = self.loa_calculator.calculate(k_level, r_level)
        loa_rationale = self.loa_calculator.generate_rationale(k_level, r_level, loa)
        loa_measures = self.loa_calculator.get_authentication_requirements(loa)

        # Step 3: Calculate confidence scores
        k_conf, r_conf, t_conf = self.rule_engine.calculate_confidence(
            input_data, k_level, r_level, t_level
        )

        # Step 4: Get suggested measures
        all_measures = self.measures_catalog.get_all_measures(
            k_level, r_level, t_level, loa_measures
        )

        # Step 5: Generate enhanced rationale (LLM layer for transparency)
        rule_triggers_dict = {
            'K': k_triggers,
            'R': r_triggers,
            'T': t_triggers,
        }

        # Try to enhance rationale with LLM
        try:
            enhanced_text = self.llm_adapter.generate_enhanced_rationale(
                input_data=input_data,
                k_level=k_level,
                r_level=r_level,
                t_level=t_level,
                loa=loa,
                rule_triggers=rule_triggers_dict
            )
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            enhanced_text = None

        # Build rationale object
        rationale = Rationale(
            K=k_triggers,
            R=r_triggers,
            T=t_triggers,
            LoA=loa_rationale
        )

        # Add enhanced text if available
        if enhanced_text:
            rationale.K.append(f"ENHANCED: {enhanced_text}")

        # Build confidence scores
        confidence = ConfidenceScores(
            K=k_conf,
            R=r_conf,
            T=t_conf
        )

        # Build suggested measures
        suggested_measures = SuggestedMeasures(
            K=all_measures['K'],
            R=all_measures['R'],
            T=all_measures['T'],
            LoA=all_measures['LoA']
        )

        # Build audit info
        classification_time_ms = (time.time() - start_time) * 1000
        audit = AuditInfo(
            model_version=self.model_version,
            timestamp=datetime.utcnow(),
            classification_time_ms=classification_time_ms,
            overridden=False
        )

        # Build final output
        output = ClassificationOutput(
            object_id=input_data.object_id,
            krt=KRTLevels(K=k_level, R=r_level, T=t_level),
            loa=loa,
            rationale=rationale,
            confidence=confidence,
            suggested_measures=suggested_measures,
            audit=audit
        )

        return output

    def classify_batch(self, inputs: list[ClassificationInput]) -> list[ClassificationOutput]:
        """
        Classify multiple objects.

        Args:
            inputs: List of classification inputs

        Returns:
            List of classification outputs
        """
        return [self.classify(inp) for inp in inputs]
