export interface Officer {
  id: number;
  officer_id: string;
  email: string;
  full_name: string;
  badge_number: string | null;
  department: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Passenger {
  id: number;
  passenger_id: string;
  full_name: string | null;
  date_of_birth: string | null;
  nationality: string | null;
  gender: string | null;
  passport_number: string | null;
  created_at: string;
}

export type DocumentType = 'passport' | 'visa' | 'national_id' | 'permit';
export type ProcessingStatus = 'waiting' | 'processing' | 'completed' | 'warning' | 'failed';
export type VerificationStatus = 'valid' | 'invalid' | 'warning' | 'pending';
export type RiskLevel = 'low' | 'medium' | 'high';

export interface Document {
  id: number;
  case_id: number;
  document_type: DocumentType;
  file_path: string;
  original_filename: string;
  file_size: number | null;
  mime_type: string | null;
  upload_status: ProcessingStatus;
  processing_progress: number;
  current_step: string | null;
  created_at: string;
}

export interface DocumentQueueItem {
  id: number;
  document_type: DocumentType;
  thumbnail_path: string | null;
  upload_status: ProcessingStatus;
  processing_progress: number;
  current_step: string | null;
}

export interface Case {
  id: number;
  case_id: string;
  officer_id: number;
  passenger_id: number;
  overall_status: VerificationStatus;
  overall_risk_level: RiskLevel | null;
  risk_score: number | null;
  risk_reasons: string[] | null;
  started_at: string;
  completed_at: string | null;
  created_at: string;
}

export interface CaseListItem {
  case_id: string;
  passenger_name: string | null;
  passenger_id: string;
  document_count: number;
  overall_risk_level: RiskLevel | null;
  overall_status: VerificationStatus;
  officer_name: string;
  created_at: string;
}

export interface OCRField {
  field_name: string;
  value: string;
  confidence: number;
}

export interface OCRResult {
  id: number;
  case_id: number;
  document_id: number;
  extracted_fields: OCRField[];
  confidence_scores: Record<string, number> | null;
  raw_text: string | null;
  processing_time_ms: number | null;
  status: ProcessingStatus;
  created_at: string;
}

export interface MRZField {
  field_name: string;
  ocr_value: string | null;
  mrz_value: string | null;
  match: boolean | null;
}

export interface MRZResult {
  id: number;
  case_id: number;
  document_id: number;
  mrz_detected: boolean;
  mrz_raw: string | null;
  mrz_type: string | null;
  decoded_fields: Record<string, string> | null;
  checksum_valid: boolean | null;
  checksum_details: Record<string, any> | null;
  ocr_mrz_comparison: MRZField[] | null;
  consistency_percentage: number | null;
  processing_time_ms: number | null;
  status: ProcessingStatus;
  created_at: string;
}

export interface ValidationField {
  field_name: string;
  value: string;
  valid: boolean;
  message: string | null;
}

export interface ValidationResult {
  id: number;
  case_id: number;
  document_id: number;
  field_validations: ValidationField[];
  overall_valid: boolean | null;
  warnings: string[] | null;
  errors: string[] | null;
  reference_db_check: Record<string, any> | null;
  processing_time_ms: number | null;
  status: ProcessingStatus;
  created_at: string;
}

export interface TamperResult {
  id: number;
  case_id: number;
  document_id: number;
  tampering_probability: number | null;
  suspected_regions: Array<{
    region: string;
    probability: number;
    description: string;
  }> | null;
  heatmap_path: string | null;
  noise_residual_path: string | null;
  noise_analysis_reliable: boolean;
  forensics_findings: Record<string, any> | null;
  rgb_image_path: string | null;
  processing_time_ms: number | null;
  status: ProcessingStatus;
  created_at: string;
}

export interface FaceResult {
  id: number;
  case_id: number;
  document_id: number;
  document_face_path: string | null;
  live_face_path: string | null;
  document_face_detected: boolean;
  live_face_detected: boolean;
  document_embedding: number[] | null;
  live_embedding: number[] | null;
  similarity_score: number | null;
  match_status: string | null;
  processing_time_ms: number | null;
  status: ProcessingStatus;
  created_at: string;
}

export interface CrossDocumentField {
  field_name: string;
  document_values: Record<string, string>;
  consistent: boolean;
  inconsistency_details: string | null;
}

export interface CrossDocumentResult {
  id: number;
  case_id: number;
  comparisons: CrossDocumentField[];
  created_at: string;
}

export interface RiskFactor {
  factor: string;
  weight: number;
  contribution: number;
  description: string;
}

export interface RiskAssessment {
  id: number;
  case_id: number;
  risk_level: RiskLevel;
  risk_score: number;
  contributing_factors: RiskFactor[];
  factor_weights: Record<string, number>;
  threshold_config: Record<string, number>;
  created_at: string;
}

export interface VerificationProgress {
  stage: string;
  status: ProcessingStatus;
  progress: number;
  message: string | null;
}

export interface DashboardStats {
  total_passengers_screened: number;
  total_documents_verified: number;
  valid_documents: number;
  suspicious_documents: number;
  high_risk_cases: number;
  currently_processing: number;
  risk_distribution: Record<string, number>;
}

export interface RecentActivity {
  case_id: string;
  passenger_name: string | null;
  document_count: number;
  risk_level: RiskLevel;
  status: VerificationStatus;
  timestamp: string;
}

export interface DashboardData {
  stats: DashboardStats;
  risk_distribution: Record<string, number>;
  recent_activity: RecentActivity[];
}

export interface PassengerHistoryItem {
  case_id: string;
  passenger_name: string | null;
  passenger_id: string;
  date_time: string;
  document_count: number;
  overall_risk: RiskLevel;
  verification_status: VerificationStatus;
  officer_name: string;
}

export interface PassengerHistoryFilter {
  passenger_id?: string;
  date_from?: string;
  date_to?: string;
  risk_level?: RiskLevel;
  status?: VerificationStatus;
}

export interface ProcessingStep {
  name: string;
  status: ProcessingStatus;
  progress: number;
  details: string | null;
}

export interface VerificationDetail {
  case_id: string;
  passenger_name: string;
  passenger_id: string;
  timestamp: string;
  overall_status: VerificationStatus;
  overall_risk_level: RiskLevel;
  documents: Document[];
  ocr_results: OCRResult[];
  mrz_results: MRZResult[];
  validation_results: ValidationResult[];
  tamper_results: TamperResult[];
  face_results: FaceResult[];
  cross_document_results: CrossDocumentResult[];
  risk_assessment: RiskAssessment | null;
  processing_steps: ProcessingStep[];
}

export interface LoginCredentials {
  officer_id: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
}