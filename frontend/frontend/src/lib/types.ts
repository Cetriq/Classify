/**
 * TypeScript types matching backend models.
 */

export enum PersonalDataCategory {
  BASIC_IDENTIFIERS = "basic_identifiers",
  PERSONAL_NUMBER = "personal_number",
  CONTACT_INFO = "contact_info",
  HEALTH = "health",
  RELIGION = "religion",
  UNION_MEMBERSHIP = "union",
  BIOMETRIC = "biometric",
  GENETIC = "genetic",
  SEXUAL_ORIENTATION = "sexual_orientation",
  CRIMINAL_CONVICTIONS = "criminal_convictions",
  PROTECTED_IDENTITY = "protected_identity",
  RETAINED_ADDRESS = "retained_address",
  MINORS = "minors",
  FINANCIAL = "financial",
  LOCATION = "location",
  SOCIAL_VULNERABILITY = "social_vulnerability",
  EMPLOYMENT = "employment",
}

export enum DecisionImpact {
  NONE = "none",
  SUPPORT = "support",
  AUTHORITY_DECISION = "authority_decision",
  SAFETY = "safety",
}

export interface VolumeData {
  data_subjects: number;
  attributes_per_subject?: number;
  history_years?: number;
}

export interface LegalContext {
  osl_secret: boolean;
  article9: boolean;
  article10: boolean;
  minors: boolean;
  public_exposure: boolean;
  automated_decision: boolean;
}

export interface ClassificationInput {
  object_id: string;
  object_name: string;
  object_type: string;
  personal_data_categories: PersonalDataCategory[];
  volumes?: VolumeData;
  rto_hours?: number;
  legal: LegalContext;
  decision_impact: DecisionImpact;
  external_dependencies: string[];
  recipients: string[];
  free_text_context?: string;
}

export interface KRTLevels {
  K: number;
  R: number;
  T: number;
}

export interface Rationale {
  K: string[];
  R: string[];
  T: string[];
  LoA: string[];
}

export interface ConfidenceScores {
  K: number;
  R: number;
  T: number;
}

export interface SuggestedMeasures {
  K: string[];
  R: string[];
  T: string[];
  LoA: string[];
}

export interface AuditInfo {
  model_version: string;
  timestamp: string;
  classification_time_ms?: number;
  overridden: boolean;
  override_reason?: string;
}

export interface ClassificationOutput {
  object_id: string;
  krt: KRTLevels;
  loa: number;
  rationale: Rationale;
  confidence: ConfidenceScores;
  suggested_measures: SuggestedMeasures;
  audit: AuditInfo;
}

// Label mappings for UI
export const PersonalDataCategoryLabels: Record<PersonalDataCategory, string> = {
  [PersonalDataCategory.BASIC_IDENTIFIERS]: "Basidentifierare (namn, e-post)",
  [PersonalDataCategory.PERSONAL_NUMBER]: "Personnummer",
  [PersonalDataCategory.CONTACT_INFO]: "Kontaktuppgifter",
  [PersonalDataCategory.HEALTH]: "Hälsodata (Art. 9)",
  [PersonalDataCategory.RELIGION]: "Religion (Art. 9)",
  [PersonalDataCategory.UNION_MEMBERSHIP]: "Fackligt medlemskap (Art. 9)",
  [PersonalDataCategory.BIOMETRIC]: "Biometriska data (Art. 9)",
  [PersonalDataCategory.GENETIC]: "Genetiska data (Art. 9)",
  [PersonalDataCategory.SEXUAL_ORIENTATION]: "Sexuell läggning (Art. 9)",
  [PersonalDataCategory.CRIMINAL_CONVICTIONS]: "Lagöverträdelser (Art. 10)",
  [PersonalDataCategory.PROTECTED_IDENTITY]: "Skyddad identitet/sekretessmarkering",
  [PersonalDataCategory.RETAINED_ADDRESS]: "Kvarskrivning",
  [PersonalDataCategory.MINORS]: "Barn (<18 år)",
  [PersonalDataCategory.FINANCIAL]: "Ekonomiska uppgifter",
  [PersonalDataCategory.LOCATION]: "Lokaliseringsdata",
  [PersonalDataCategory.SOCIAL_VULNERABILITY]: "Socialtjänst/LSS/sårbarhet",
  [PersonalDataCategory.EMPLOYMENT]: "Personaluppgifter/arbetsdata",
};

export const DecisionImpactLabels: Record<DecisionImpact, string> = {
  [DecisionImpact.NONE]: "Ingen beslutspåverkan",
  [DecisionImpact.SUPPORT]: "Beslutstöd",
  [DecisionImpact.AUTHORITY_DECISION]: "Myndighetsbeslut/utbetalning",
  [DecisionImpact.SAFETY]: "Säkerhet/insatser",
};
