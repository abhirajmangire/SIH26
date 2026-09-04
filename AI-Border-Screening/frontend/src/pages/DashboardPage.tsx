import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  AlertCircle, 
  Loader2,
  Search,
  Filter,
  Plus,
  Eye,
  BarChart2,
  Clock,
  Shield
} from 'lucide-react';
import { 
  Button, 
  Badge, 
  Card, 
  CardHeader, 
  CardBody, 
  StatCard, 
  ProgressBar, 
  Input,
  EmptyState,
  LoadingSpinner
} from '../common/UI';
import { MainLayout } from '../common/Layout';
import { api } from '../../services/api';
import { 
  DashboardData, 
  CaseListItem, 
  DocumentQueueItem,
  RiskLevel,
  ProcessingStatus,
  VerificationStatus 
} from '../../types';
import { cn, formatDate, getRiskLevelColor, getRiskLevelLabel, getProcessingStatusColor, getProcessingStatusLabel, getDocumentTypeLabel, generateCaseId } from '../../utils/helpers';

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [recentCases, setRecentCases] = useState<CaseListItem[]>([]);
  const [processingQueue, setProcessingQueue] = useState<DocumentQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCaseId, setActiveCaseId] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [historyData, setHistoryData] = useState<CaseListItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState<RiskLevel | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<VerificationStatus | 'all'>('all');

  useEffect(() => {
    loadDashboardData();
    loadRecentCases();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await api.getDashboardStats();
      setDashboardData(data);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRecentCases = async () => {
    try {
      const cases = await api.getCases(0, 10);
      setRecentCases(cases);
    } catch (err) {
      console.error('Failed to load recent cases:', err);
    }
  };

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const history = await api.getCases(0, 100);
      setHistoryData(history);
      setShowHistory(true);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleNewCase = async () => {
    const caseId = generateCaseId();
    try {
      const passenger = await api.createPassenger({
        passenger_id: `PAX-${Date.now()}`,
        full_name: '',
        date_of_birth: null,
        nationality: '',
        gender: '',
        passport_number: '',
      });
      const newCase = await api.createCase(caseId, passenger.id);
      navigate(`/dashboard/${newCase.case_id}`);
    } catch (err) {
      console.error('Failed to create case:', err);
    }
  };

  const handleViewCase = (caseId: string) => {
    navigate(`/dashboard/${caseId}`);
  };

  const handleProcessCase = async (caseId: string) => {
    try {
      await api.startProcessing(caseId);
      setActiveCaseId(caseId);
      pollProcessingQueue(caseId);
    } catch (err) {
      console.error('Failed to start processing:', err);
    }
  };

  const pollProcessingQueue = async (caseId: string) => {
    const poll = async () => {
      try {
        const queue = await api.getProcessingQueue(caseId);
        setProcessingQueue(queue);
        
        const allCompleted = queue.every(item => 
          item.upload_status === 'completed' || item.upload_status === 'warning' || item.upload_status === 'failed'
        );
        
        if (!allCompleted) {
          setTimeout(poll, 2000);
        } else {
          loadDashboardData();
          loadRecentCases();
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };
    poll();
  };

  const filteredCases = recentCases.filter(caseItem => {
    if (searchQuery && !caseItem.case_id.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !caseItem.passenger_name?.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (riskFilter !== 'all' && caseItem.overall_risk_level !== riskFilter) {
      return false;
    }
    if (statusFilter !== 'all' && caseItem.overall_status !== statusFilter) {
      return false;
    }
    return true;
  });

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-[60vh]">
          <LoadingSpinner size="lg" />
        </div>
      </MainLayout>
    );
  }

  const stats = dashboardData?.stats || {
    total_passengers_screened: 0,
    total_documents_verified: 0,
    valid_documents: 0,
    suspicious_documents: 0,
    high_risk_cases: 0,
    currently_processing: 0,
    risk_distribution: {},
  };

  return (
    <MainLayout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="page-title">Officer Dashboard</h1>
            <p className="text-neutral-text-secondary mt-1">Real-time border security screening overview</p>
          </div>
          <Button onClick={handleNewCase} leftIcon={<Plus className="w-5 h-5" />}>
            New Screening
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <StatCard
            title="Passengers Screened"
            value={stats.total_passengers_screened}
            icon={<Users className="w-6 h-6" />}
            iconColor="primary-cyan"
          />
          <StatCard
            title="Documents Verified"
            value={stats.total_documents_verified}
            icon={<FileText className="w-6 h-6" />}
            iconColor="primary-royal"
          />
          <StatCard
            title="Valid Documents"
            value={stats.valid_documents}
            trend={stats.total_documents_verified > 0 ? Math.round((stats.valid_documents / stats.total_documents_verified) * 100) : 0}
            trendLabel="pass rate"
            icon={<CheckCircle className="w-6 h-6" />}
            iconColor="status-green"
          />
          <StatCard
            title="Suspicious Documents"
            value={stats.suspicious_documents}
            icon={<AlertTriangle className="w-6 h-6" />}
            iconColor="status-amber"
          />
          <StatCard
            title="High Risk Cases"
            value={stats.high_risk_cases}
            icon={<AlertCircle className="w-6 h-6" />}
            iconColor="status-red"
          />
          <StatCard
            title="Currently Processing"
            value={stats.currently_processing}
            icon={<Loader2 className="w-6 h-6 animate-spin" />}
            iconColor="primary-royal"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BarChart2 className="w-5 h-5 text-primary-royal" />
                  <span className="section-title">Risk Distribution</span>
                </div>
              </div>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                {(['high', 'medium', 'low'] as RiskLevel[]).map((level) => {
                  const count = stats.risk_distribution[level] || 0;
                  const total = stats.total_passengers_screened || 1;
                  const percentage = (count / total) * 100;
                  return (
                    <div key={level} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <span className={cn('w-2 h-2 rounded-full', 
                            level === 'high' && 'bg-status-red',
                            level === 'medium' && 'bg-status-amber',
                            level === 'low' && 'bg-status-green'
                          )} />
                          <span className="font-medium text-neutral-text">{getRiskLevelLabel(level)} RISK</span>
                        </div>
                        <span className="text-neutral-text-secondary">{count} ({percentage.toFixed(1)}%)</span>
                      </div>
                      <ProgressBar value={percentage} variant={level === 'high' ? 'red' : level === 'medium' ? 'amber' : 'green'} />
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-primary-royal" />
                  <span className="section-title">Recent Activity</span>
                </div>
              </div>
            </CardHeader>
            <CardBody className="p-0">
              <div className="divide-y divide-neutral-border/50">
                {(dashboardData?.recent_activity || []).slice(0, 5).map((activity, index) => (
                  <div key={index} className="p-4 hover:bg-neutral-bg/50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge variant={getRiskLevelColor(activity.risk_level)}>
                          {getRiskLevelLabel(activity.risk_level)}
                        </Badge>
                        <div>
                          <p className="font-medium text-neutral-text">{activity.case_id}</p>
                          <p className="text-xs text-neutral-text-secondary">{activity.passenger_name || 'Unknown Passenger'}</p>
                        </div>
                      </div>
                      <span className="text-xs text-neutral-text-secondary">{formatDate(activity.timestamp)}</span>
                    </div>
                  </div>
                ))}
                {(dashboardData?.recent_activity || []).length === 0 && (
                  <EmptyState
                    icon={<Shield className="w-8 h-8" />}
                    title="No recent activity"
                    description="Start a new screening to see activity here"
                  />
                )}
              </div>
            </CardBody>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-primary-royal" />
                  <span className="section-title">Document Upload & Scan</span>
                </div>
                <Button variant="secondary" leftIcon={<Eye className="w-4 h-4" />} onClick={loadHistory}>
                  View Passenger History
                </Button>
              </div>
            </CardHeader>
            <CardBody>
              <UploadPanel 
                onCaseCreated={(caseId) => {
                  navigate(`/dashboard/${caseId}`);
                }}
              />
            </CardBody>
          </Card>

          {activeCaseId && processingQueue.length > 0 && (
            <Card className="lg:col-span-2">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-5 h-5 text-primary-royal animate-spin" />
                    <span className="section-title">Processing Queue</span>
                  </div>
                  <Badge variant="blue">LIVE</Badge>
                </div>
              </CardHeader>
              <CardBody>
                <ProcessingQueue 
                  queue={processingQueue} 
                  onComplete={() => {
                    setActiveCaseId(null);
                    setProcessingQueue([]);
                    loadDashboardData();
                    loadRecentCases();
                  }}
                />
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

const UploadPanel = ({ onCaseCreated }: { onCaseCreated: (caseId: string) => void }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [documentTypes, setDocumentTypes] = useState<Record<string, string>>({});
  const [creating, setCreating] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter(f => ['image/jpeg', 'image/png', 'image/tiff', 'application/pdf'].includes(f.type));
    setFiles(prev => [...prev, ...validFiles]);
    newFiles.forEach(f => setDocumentTypes(prev => ({ ...prev, [f.name]: 'passport' })));
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (files.length === 0) return;
    setCreating(true);
    try {
      const caseId = generateCaseId();
      const passenger = await api.createPassenger({
        passenger_id: `PAX-${Date.now()}`,
        full_name: '',
        date_of_birth: null,
        nationality: '',
        gender: '',
        passport_number: '',
      });
      const newCase = await api.createCase(caseId, passenger.id);
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const docType = documentTypes[file.name] || 'passport';
        await api.uploadDocument(newCase.case_id, docType, file);
      }
      
      setFiles([]);
      setDocumentTypes({});
      onCaseCreated(newCase.case_id);
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          className={cn(
            'border-2 border-dashed rounded-card p-8 text-center transition-colors',
            dragActive 
              ? 'border-primary-royal bg-primary-royal/5' 
              : 'border-neutral-border hover:border-primary-royal/50'
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            multiple
            accept="image/jpeg,image/png,image/tiff,application/pdf"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
            ref={(el) => { if (el) el.multiple = true; }}
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <div className="w-16 h-16 rounded-full bg-primary-royal/10 flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-primary-royal" />
            </div>
            <p className="text-lg font-medium text-neutral-text mb-1">Drop documents here or click to browse</p>
            <p className="text-sm text-neutral-text-secondary">Supports: JPG, PNG, TIFF, PDF</p>
          </label>
        </div>

        <div className="border border-neutral-border rounded-card p-6">
          <h3 className="font-medium text-neutral-text mb-4">Scan Face</h3>
          <div className="space-y-4">
            <div className="aspect-video bg-neutral-bg rounded-card flex items-center justify-center border border-neutral-border/50">
              <div className="text-center text-neutral-text-secondary">
                <Shield className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Camera feed will appear here</p>
                <p className="text-xs">Requires camera permission</p>
              </div>
            </div>
            <Button variant="secondary" leftIcon={<Shield className="w-4 h-4" />} className="w-full">
              Capture Live Face
            </Button>
            <p className="text-xs text-neutral-text-secondary text-center">Fallback: Upload face image</p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-medium text-neutral-text">Uploaded Documents ({files.length})</h3>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {files.map((file, index) => (
              <div key={index} className="flex items-center gap-4 p-3 bg-neutral-bg rounded-card">
                <div className="w-12 h-12 rounded-lg bg-white border border-neutral-border flex items-center justify-center flex-shrink-0">
                  <FileText className="w-6 h-6 text-primary-royal" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-neutral-text truncate">{file.name}</p>
                  <p className="text-xs text-neutral-text-secondary">{file.type} • {formatFileSize(file.size)}</p>
                </div>
                <select
                  value={documentTypes[file.name] || 'passport'}
                  onChange={(e) => setDocumentTypes(prev => ({ ...prev, [file.name]: e.target.value }))}
                  className="input-field py-1.5 px-3 text-sm w-36"
                >
                  <option value="passport">Passport</option>
                  <option value="visa">Visa</option>
                  <option value="national_id">National ID</option>
                  <option value="permit">Permit</option>
                </select>
                <button
                  onClick={() => removeFile(index)}
                  className="p-2 text-neutral-text-secondary hover:text-status-red hover:bg-status-red/10 rounded-lg transition-colors"
                  aria-label="Remove document"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
          <Button onClick={handleSubmit} className="w-full" size="lg" loading={creating}>
            {creating ? 'Uploading...' : 'Upload & Start Processing'}
          </Button>
        </div>
      )}
    </div>
  );
};

const ProcessingQueue = ({ queue, onComplete }: { queue: DocumentQueueItem[]; onComplete: () => void }) => {
  const allCompleted = queue.every(item => 
    item.upload_status === 'completed' || item.upload_status === 'warning' || item.upload_status === 'failed'
  );

  if (allCompleted) {
    setTimeout(onComplete, 2000);
  }

  return (
    <div className="space-y-4">
      {queue.map((item) => (
        <div key={item.id} className="flex items-center gap-4 p-4 bg-neutral-bg rounded-card">
          <div className="w-16 h-12 rounded-lg bg-white border border-neutral-border flex items-center justify-center flex-shrink-0">
            <FileText className="w-5 h-5 text-primary-royal" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-neutral-text">{getDocumentTypeLabel(item.document_type)}</span>
              <Badge variant={getProcessingStatusColor(item.upload_status)}>
                {getProcessingStatusLabel(item.upload_status)}
              </Badge>
            </div>
            <ProgressBar value={item.processing_progress} variant={item.upload_status === 'warning' ? 'amber' : item.upload_status === 'failed' ? 'red' : 'primary'} showLabel />
            {item.current_step && (
              <p className="text-xs text-neutral-text-secondary mt-1">{item.current_step}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}