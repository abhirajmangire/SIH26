import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type { 
  LoginCredentials, 
  AuthResponse, 
  Case, 
  CaseListItem, 
  Document, 
  DocumentQueueItem,
  DashboardData,
  PassengerHistoryItem,
  PassengerHistoryFilter,
  VerificationDetail,
  OCRResult,
  MRZResult,
  ValidationResult,
  TamperResult,
  FaceResult,
  CrossDocumentResult,
  RiskAssessment,
  Passenger 
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('officer_id', credentials.officer_id);
    formData.append('password', credentials.password);
    
    const response = await this.client.post<AuthResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async logout(): Promise<void> {
    this.clearToken();
  }

  async getDashboardStats(): Promise<DashboardData> {
    const response = await this.client.get<DashboardData>('/dashboard/stats');
    return response.data;
  }

  async getCases(skip = 0, limit = 50): Promise<CaseListItem[]> {
    const response = await this.client.get<CaseListItem[]>(`/cases?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getCase(caseId: string): Promise<Case> {
    const response = await this.client.get<Case>(`/cases/${caseId}`);
    return response.data;
  }

  async createCase(caseId: string, passengerId: number): Promise<Case> {
    const response = await this.client.post<Case>('/cases', { case_id: caseId, passenger_id: passengerId });
    return response.data;
  }

  async uploadDocument(caseId: string, documentType: string, file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('file', file);
    
    const response = await this.client.post<Document>(`/cases/${caseId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getCaseDocuments(caseId: string): Promise<Document[]> {
    const response = await this.client.get<Document[]>(`/cases/${caseId}/documents`);
    return response.data;
  }

  async getProcessingQueue(caseId: string): Promise<DocumentQueueItem[]> {
    const response = await this.client.get<DocumentQueueItem[]>(`/cases/${caseId}/queue`);
    return response.data;
  }

  async startProcessing(caseId: string): Promise<{ message: string; case_id: string }> {
    const response = await this.client.post<{ message: string; case_id: string }>(`/cases/${caseId}/process`);
    return response.data;
  }

  async getPassengerHistory(filters?: PassengerHistoryFilter): Promise<PassengerHistoryItem[]> {
    const params = new URLSearchParams();
    if (filters?.passenger_id) params.append('passenger_id', filters.passenger_id);
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.risk_level) params.append('risk_level', filters.risk_level);
    if (filters?.status) params.append('status', filters.status);
    
    const response = await this.client.get<PassengerHistoryItem[]>(`/cases/history?${params.toString()}`);
    return response.data;
  }

  async searchPassengers(query: string): Promise<Passenger[]> {
    const response = await this.client.get<Passenger[]>(`/cases/passengers/search?q=${encodeURIComponent(query)}`);
    return response.data;
  }

  async createPassenger(passenger: Omit<Passenger, 'id' | 'created_at'>): Promise<Passenger> {
    const response = await this.client.post<Passenger>('/cases/passengers', passenger);
    return response.data;
  }

  async getVerificationDetail(caseId: string): Promise<VerificationDetail> {
    const response = await this.client.get<VerificationDetail>(`/verification/${caseId}/detail`);
    return response.data;
  }

  async completeVerification(caseId: string): Promise<{ message: string; case_id: string }> {
    const response = await this.client.post<{ message: string; case_id: string }>(`/verification/${caseId}/complete`);
    return response.data;
  }

  async getOCRResults(caseId: string): Promise<OCRResult[]> {
    const response = await this.client.get<OCRResult[]>(`/ocr/case/${caseId}`);
    return response.data;
  }

  async getMRZResults(caseId: string): Promise<MRZResult[]> {
    const response = await this.client.get<MRZResult[]>(`/mrz/case/${caseId}`);
    return response.data;
  }

  async getValidationResults(caseId: string): Promise<ValidationResult[]> {
    const response = await this.client.get<ValidationResult[]>(`/validation/case/${caseId}`);
    return response.data;
  }

  async getTamperResults(caseId: string): Promise<TamperResult[]> {
    const response = await this.client.get<TamperResult[]>(`/tamper/case/${caseId}`);
    return response.data;
  }

  async getFaceResults(caseId: string): Promise<FaceResult[]> {
    const response = await this.client.get<FaceResult[]>(`/face/case/${caseId}`);
    return response.data;
  }

  async getRiskAssessment(caseId: string): Promise<RiskAssessment> {
    const response = await this.client.get<RiskAssessment>(`/risk/case/${caseId}`);
    return response.data;
  }

  getFileUrl(path: string): string {
    return `${API_BASE_URL.replace('/api/v1', '')}/storage/${path.replace(/^.*storage\//, '')}`;
  }
}

export const api = new ApiService();