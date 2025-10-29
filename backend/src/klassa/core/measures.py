"""
Control catalog - maps K/R/T/LoA levels to security measures.
Based on spec.md section 11.
"""

from typing import Dict, List


class MeasuresCatalog:
    """
    Catalog of security measures mapped to K/R/T/LoA levels.
    Implements the control catalog from spec.md section 11.
    """

    # Konfidentialitet measures
    K_MEASURES: Dict[int, List[str]] = {
        1: [
            "Grundläggande åtkomstkontroll",
            "Kryptering vid transport (TLS)",
            "Loggning av åtkomst",
        ],
        2: [
            "Rollbaserad behörighetsstyrning (RBAC)",
            "Kryptering vilande och transport (TLS 1.2+)",
            "Regelbunden behörighetsgenomgång (kvartalsvis)",
            "Logggranskning månadsvis",
            "Klassificering av dokument/data",
        ],
        3: [
            "End-to-end kryptering",
            "HSM-baserad nyckelhantering",
            "Stark MFA (BankID, SITHS)",
            "Behovsprövad behörighet (need-to-know)",
            "Logggranskning veckovis",
            "DLP (Data Loss Prevention)",
            "Data-maskning i loggar och utvecklingsmiljö",
            "Tredjelands-överföringar kräver TIA (Transfer Impact Assessment)",
            "Kryptering av backuper",
            "Separata miljöer för produktion/test",
        ],
    }

    # Riktighet measures
    R_MEASURES: Dict[int, List[str]] = {
        1: [
            "Grundläggande datavalidering",
            "Felhantering och loggning",
        ],
        2: [
            "Valideringsregler för datainmatning",
            "Teknisk eller organisatorisk attest",
            "Ändringslogg",
            "Regelbunden datakvalitetsgranskning",
            "Backup och återställningsrutiner",
        ],
        3: [
            "Transaktionslogg med oföränderlighet (immutable audit log)",
            "Två-i-handläggning (four-eyes principle) för kritiska beslut",
            "Datavalidering på flera nivåer (frontend + backend + databas)",
            "Regelbunden stickprovskontroll av data",
            "Automatiska konsistenskontroller",
            "Integritetsskydd (checksums, digitala signaturer)",
            "Separation of duties",
            "Formella beslutsflöden med attest",
        ],
    }

    # Tillgänglighet measures
    T_MEASURES: Dict[int, List[str]] = {
        1: [
            "Grundläggande backup (veckovis)",
            "Dokumenterade återställningsrutiner",
            "Kontaktlista för support",
        ],
        2: [
            "Daglig backup med retention enligt policy",
            "Testade återställningsrutiner (årligen)",
            "Incidenthanteringsrutin ≤1 arbetsdag",
            "Övervakning av systemstatus",
            "Kapacitetsplanering",
            "Underhållsfönster kommuniceras i förväg",
        ],
        3: [
            "Geo-redundans eller lokal redundans",
            "RTO ≤4 timmar dokumenterat och testat",
            "RPO ≤1 timme",
            "24/7 övervakning och larm",
            "Incidenthanteringsrutin ≤4 timmar",
            "Kapacitetsplanering med lastbalansering",
            "Övade incidentrutiner (minst kvartalsvis)",
            "Automatisk failover där möjligt",
            "DDoS-skydd",
            "Kontinuitetsplan (Business Continuity Plan)",
        ],
    }

    @classmethod
    def get_k_measures(cls, level: int) -> List[str]:
        """Get Confidentiality measures for level."""
        return cls.K_MEASURES.get(level, [])

    @classmethod
    def get_r_measures(cls, level: int) -> List[str]:
        """Get Accuracy measures for level."""
        return cls.R_MEASURES.get(level, [])

    @classmethod
    def get_t_measures(cls, level: int) -> List[str]:
        """Get Availability measures for level."""
        return cls.T_MEASURES.get(level, [])

    @classmethod
    def get_all_measures(
        cls,
        k_level: int,
        r_level: int,
        t_level: int,
        loa_measures: List[str]
    ) -> Dict[str, List[str]]:
        """
        Get all measures for K/R/T/LoA levels.

        Args:
            k_level: Confidentiality level
            r_level: Accuracy level
            t_level: Availability level
            loa_measures: LoA-specific measures

        Returns:
            Dictionary with K/R/T/LoA measures
        """
        return {
            "K": cls.get_k_measures(k_level),
            "R": cls.get_r_measures(r_level),
            "T": cls.get_t_measures(t_level),
            "LoA": loa_measures,
        }
