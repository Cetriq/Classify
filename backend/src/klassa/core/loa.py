"""
Level of Assurance (LoA) calculator.
Based on CLAUDE.md LoA mapping logic.
"""

from typing import List


class LoACalculator:
    """
    Calculates Level of Assurance based on K/R classification.

    Logic: LoA = max(K, R)

    Rationale: Confidentiality (K) and Accuracy (R) directly impact
    the trustworthiness required when accessing or modifying information.
    """

    @staticmethod
    def calculate(k_level: int, r_level: int) -> int:
        """
        Calculate LoA from K and R levels.

        Args:
            k_level: Confidentiality level (1-3)
            r_level: Accuracy level (1-3)

        Returns:
            LoA level (1-3)
        """
        return max(k_level, r_level)

    @staticmethod
    def generate_rationale(k_level: int, r_level: int, loa: int) -> List[str]:
        """
        Generate rationale for LoA decision.

        Args:
            k_level: Confidentiality level
            r_level: Accuracy level
            loa: Calculated LoA level

        Returns:
            List of rationale strings
        """
        rationale = [f"DERIVED:max(K={k_level},R={r_level})"]

        if loa == 3:
            if k_level == 3:
                rationale.append("Hög konfidentialitet kräver stark autentisering")
            if r_level == 3:
                rationale.append("Kritisk riktighet kräver stark autentisering")
            rationale.append("BankID eller SITHS-kort krävs")

        elif loa == 2:
            if k_level == 2:
                rationale.append("Kännbar konfidentialitet kräver tvåfaktorsautentisering")
            if r_level == 2:
                rationale.append("Betydande riktighet kräver tvåfaktorsautentisering")
            rationale.append("BankID on file eller SMS-kod rekommenderas")

        else:  # loa == 1
            rationale.append("Begränsad säkerhetsnivå tillåter enkel autentisering")
            rationale.append("Lösenord acceptabelt")

        return rationale

    @staticmethod
    def get_authentication_requirements(loa: int) -> List[str]:
        """
        Get specific authentication requirements for LoA level.

        Args:
            loa: Level of Assurance (1-3)

        Returns:
            List of authentication requirements
        """
        if loa == 3:
            return [
                "BankID-inloggning obligatorisk för användare",
                "SITHS-kort för administratörer och systemägare",
                "Sessionshantering med timeout ≤15 minuter",
                "MFA re-authentication för känsliga operationer",
                "Hårdvaru-baserad autentisering prioriteras"
            ]
        elif loa == 2:
            return [
                "Tvåfaktorsautentisering krävs (BankID on file, SMS, eller authenticator)",
                "Sessionshantering med timeout ≤30 minuter",
                "Lösenordskrav: minst 12 tecken, komplexitet",
                "Periodisk re-authentication var 8:e timme"
            ]
        else:  # loa == 1
            return [
                "Lösenordsbaserad autentisering acceptabel",
                "Sessionshantering med timeout ≤2 timmar",
                "Lösenordskrav: minst 8 tecken",
                "Möjlighet att uppgradera till MFA rekommenderas"
            ]
