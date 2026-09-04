import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  CheckCircle, 
  AlertTriangle, 
  AlertCircle, 
  XCircle,
  Clock,
  Loader2,
  FileText,
  Search,
  Eye,
  Shield,
  ChevronDown,
  ChevronUp,
  Camera,
  Image,
  BarChart2,
  Layers,
  Grid,
  User,
  Fingerprint,
  Hash,
  Link2,
  AlertOctagon,
  Check,
  X
} from 'lucide-react';
import { 
  Button, 
  Badge, 
  Card, 
  CardHeader, 
  CardBody, 
  ProgressBar, 
  Input,
  EmptyState,
  LoadingSpinner
} from '../common/UI';
import { MainLayout } from '../common/Layout';
import { api } from '../../services/api';
import { 
  VerificationDetail, 
  Document, 
  OCRResult, 
  MRZResult, 
  ValidationResult, 
  TamperResult, 
  FaceResult, 
  CrossDocumentResult, 
  RiskAssessment,
  RiskFactor,
  ProcessingStatus,
  RiskLevel,
  VerificationStatus
} from '../../types';
import { cn, formatDate, getRiskLevelColor, getRiskLevelLabel, getProcessingStatusColor, getProcessingStatusLabel, getMatchStatusLabel, getMatchStatusColor, getVerificationStatusLabel } from '../../utils/helpers';

export const VerificationPage = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [verification, setVerification] = useState<VerificationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    if (caseId) {
      loadVerification();
    }
  }, [caseId]);

  const loadVerification = async () => {
    try {
      setLoading(true);
      const data = await api.getVerificationDetail(caseId!);
      setVerification(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load verification details');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    try {
      await api.completeVerification(caseId!);
      setCompleted(true);
    } catch (err) {
      console.error('Failed to complete verification:', err);
    }
  };

  const handleReturn = () => {
    navigate('/dashboard');
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-[60vh]">
          <LoadingSpinner size="lg" />
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="max-w-3xl mx-auto">
          <Button variant="secondary" leftIcon={<ArrowLeft className="w-4 h-4" />} onClick={handleReturn} className="mb-6">
            Back to Dashboard
          </Button>
          <Card>
            <CardBody className="text-center py-12">
              <AlertOctagon className="w-16 h-16 text-status-red mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-neutral-text mb-2">Unable to Load Verification</h2>
              <p className="text-neutral-text-secondary mb-6">{error}</p>
              <Button onClick={handleReturn} leftIcon={<ArrowLeft className="w-4 h-4" />}>
                Return to Dashboard
              </Button>
            </CardBody>
          </Card>
        </div>
      </MainLayout>
    );
  }

  if (!verification) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-[60vh]">
          <LoadingSpinner size="lg" />
        </div>
      </MainLayout>
    );
  }

  if (completed) {
    return (
      <MainLayout>
        <div className="max-w-3xl mx-auto animate-fade-in">
          <Card className="text-center py-16">
            <CardBody>
              <div className="w-20 h-20 rounded-full bg-status-green/10 flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-status-green" />
              </div>
              <h1 className="text-2xl font-bold text-neutral-text mb-2">Verification Completed</h1>
              <p className="text-neutral-text-secondary mb-8">Passenger screening process has been completed successfully.</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button variant="secondary" onClick={handleReturn} leftIcon={<ArrowLeft className="w-4 h-4" />}>
                  Return to Dashboard
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </MainLayout>
    );
  }

  const riskColor = getRiskLevelColor(verification.overall_risk_level);
  const riskLabel = getRiskLevelLabel(verification.overall_risk_level);

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={handleReturn} leftIcon={<ArrowLeft className="w-4 h-4" />} className="lg:hidden mb-4">
            Back
          </Button>
          <div className="flex-1 lg:pl-4">
            <h1 className="page-title">Passenger Verification Details</h1>
            <p className="text-neutral-text-secondary">Case: {verification.case_id} • {formatDate(verification.timestamp)}</p>
          </div>
          <div className="flex items-center gap-4">
            <div className={cn('px-4 py-2 rounded-card font-semibold', `bg-${riskColor}/10`, `text-${riskColor}`, 'text-lg')}>
              {riskLabel} RISK
            </div>
            <Button onClick={handleComplete} className="ml-4">
              Complete Verification
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <VerificationTimeline steps={verification.processing_steps} />
            
            <DocumentSection documents={verification.documents} ocrResults={verification.ocr_results} />
            
            {verification.mrz_results.length > 0 && (
              <MRZSection mrzResults={verification.mrz_results} ocrResults={verification.ocr_results} />
            )}
            
            <ValidationSection validationResults={verification.validation_results} />
            
            <CrossDocumentSection crossResults={verification.cross_document_results} />
            
            <TamperSection tamperResults={verification.tamper_results} />
            
            <FaceSection faceResults={verification.face_results} />
          </div>

          <div className="space-y-6">
            <RiskPanel riskAssessment={verification.risk_assessment} />
            
            <FinalSummary 
              documents={verification.documents} 
              mrzResults={verification.mrz_results}
              validationResults={verification.validation_results}
              tamperResults={verification.tamper_results}
              faceResults={verification.face_results}
              crossResults={verification.cross_document_results}
              riskAssessment={verification.risk_assessment}
            />
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

const VerificationTimeline = ({ steps }: { steps: Array<{ name: string; status: ProcessingStatus; progress: number; details?: string | null }> }) => {
  const overallProgress = steps.reduce((sum, s) => sum + s.progress, 0) / steps.length;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-primary-royal" />
            <span className="section-title">Verification Pipeline</span>
          </div>
          <ProgressBar value={overallProgress} showLabel className="w-48" />
        </div>
      </CardHeader>
      <CardBody>
        <div className="space-y-3">
          {steps.map((step, index) => (
            <div key={index} className="flex items-center gap-4">
              <div className={cn('w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                step.status === 'completed' && 'bg-status-green text-white',
                step.status === 'processing' && 'bg-primary-royal text-white animate-pulse-subtle',
                step.status === 'warning' && 'bg-status-amber text-white',
                step.status === 'failed' && 'bg-status-red text-white',
                step.status === 'waiting' && 'bg-neutral-border text-neutral-text-secondary'
              )}>
                {step.status === 'completed' && <Check className="w-4 h-4" />}
                {step.status === 'processing' && <Loader2 className="w-4 h-4 animate-spin" />}
                {step.status === 'warning' && <AlertTriangle className="w-4 h-4" />}
                {step.status === 'failed' && <X className="w-4 h-4" />}
                {step.status === 'waiting' && <Clock className="w-4 h-4" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-neutral-text">{step.name}</p>
                {step.details && <p className="text-xs text-neutral-text-secondary">{step.details}</p>}
              </div>
              <div className="w-24 text-right text-sm font-medium">
                {step.progress === 100 ? '✓' : `${step.progress}%`}
              </div>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

const DocumentSection = ({ documents, ocrResults }: { documents: Document[]; ocrResults: OCRResult[] }) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary-royal" />
          <span className="section-title">Uploaded Documents</span>
        </div>
      </CardHeader>
      <CardBody>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {documents.map((doc) => (
            <div key={doc.id} className="card p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-lg bg-primary-royal/10 flex items-center justify-center">
                    <FileText className="w-6 h-6 text-primary-royal" />
                  </div>
                  <div>
                    <p className="font-medium text-neutral-text">{doc.original_filename}</p>
                    <Badge variant="blue">{getDocumentTypeLabel(doc.document_type)}</Badge>
                  </div>
                </div>
                <Badge variant={getProcessingStatusColor(doc.upload_status)}>
                  {getProcessingStatusLabel(doc.upload_status)}
                </Badge>
              </div>
              <div className="text-sm text-neutral-text-secondary space-y-1">
                <p>Size: {formatFileSize(doc.file_size || 0)}</p>
                <p>Status: {doc.current_step || 'Processing...'}</p>
              </div>
              <ProgressBar value={doc.processing_progress} className="mt-3" variant={doc.upload_status === 'warning' ? 'amber' : 'primary'} />
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

const MRZSection = ({ mrzResults, ocrResults }: { mrzResults: MRZResult[]; ocrResults: OCRResult[] }) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Hash className="w-5 h-5 text-primary-royal" />
          <span className="section-title">Passport MRZ Pipeline</span>
        </div>
      </CardHeader>
      <CardBody>
        {mrzResults.map((mrz) => (
          <div key={mrz.id} className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className={cn('p-4 rounded-card text-center', mrz.mrz_detected ? 'bg-status-green/10' : 'bg-status-red/10')}>
                <p className="text-2xl font-bold" style={{ color: mrz.mrz_detected ? '#16A34A' : '#DC2626' }}>
                  {mrz.mrz_detected ? '✓' : '✕'}
                </p>
                <p className="text-sm text-neutral-text-secondary">MRZ Detected</p>
              </div>
              <div className={cn('p-4 rounded-card text-center', mrz.checksum_valid ? 'bg-status-green/10' : 'bg-status-red/10')}>
                <p className="text-2xl font-bold" style={{ color: mrz.checksum_valid ? '#16A34A' : '#DC2626' }}>
                  {mrz.checksum_valid ? '✓' : '✕'}
                </p>
                <p className="text-sm text-neutral-text-secondary">Checksum</p>
              </div>
              <div className={cn('p-4 rounded-card text-center', (mrz.consistency_percentage || 0) >= 90 ? 'bg-status-green/10' : 'bg-status-amber/10')}>
                <p className="text-2xl font-bold text-primary-royal">{mrz.consistency_percentage?.toFixed(1) || 0}%</p>
                <p className="text-sm text-neutral-text-secondary">OCR↔MRZ Consistency</p>
              </div>
            </div>

            {mrz.decoded_fields && (
              <div className="card p-4">
                <h4 className="font-medium text-neutral-text mb-3">Decoded MRZ Fields</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  {Object.entries(mrz.decoded_fields).map(([key, value]) => (
                    <div key={key} className="bg-neutral-bg p-3 rounded-lg">
                      <p className="text-neutral-text-secondary">{key.replace(/_/g, ' ').toUpperCase()}</p>
                      <p className="font-mono text-neutral-text">{value || '—'}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {mrz.checksum_details && (
              <div className="card p-4">
                <h4 className="font-medium text-neutral-text mb-3">Checksum Validation Details</h4>
                <div className="space-y-2">
                  {Object.entries(mrz.checksum_details).map(([key, detail]) => (
                    <div key={key} className="flex items-center justify-between p-2 bg-neutral-bg rounded-lg">
                      <span className="text-sm text-neutral-text">{key.replace(/_/g, ' ')}</span>
                      <div className="flex items-center gap-2">
                        {(detail as any).valid ? (
                          <CheckCircle className="w-4 h-4 text-status-green" />
                        ) : (
                          <XCircle className="w-4 h-4 text-status-red" />
                        )}
                        <span className="text-sm font-mono">
                          Exp: {(detail as any).expected} • Act: {(detail as any).actual}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {mrz.ocr_mrz_comparison && mrz.ocr_mrz_comparison.length > 0 && (
              <div className="card p-4">
                <h4 className="font-medium text-neutral-text mb-3">OCR ↔ MRZ Cross-Field Verification</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-neutral-border">
                        <th className="text-left p-2 font-medium text-neutral-text-secondary">FIELD</th>
                        <th className="text-left p-2 font-medium text-neutral-text-secondary">OCR VALUE</th>
                        <th className="text-left p-2 font-medium text-neutral-text-secondary">MRZ VALUE</th>
                        <th className="text-center p-2 font-medium text-neutral-text-secondary">RESULT</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mrz.ocr_mrz_comparison.map((comp, i) => (
                        <tr key={i} className="border-b border-neutral-border/50">
                          <td className="p-2 text-neutral-text-secondary">{comp.field_name.replace(/_/g, ' ').toUpperCase()}</td>
                          <td className="p-2 font-mono text-neutral-text">{comp.ocr_value || '—'}</td>
                          <td className="p-2 font-mono text-neutral-text">{comp.mrz_value || '—'}</td>
                          <td className="p-2 text-center">
                            {comp.match ? (
                              <CheckCircle className="w-5 h-5 text-status-green mx-auto" />
                            ) : (
                              <XCircle className="w-5 h-5 text-status-red mx-auto" />
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ))}
      </CardBody>
    </Card>
  );
};

const ValidationSection = ({ validationResults }: { validationResults: ValidationResult[] }) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary-royal" />
          <span className="section-title">Document Validation</span>
        </div>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          {validationResults.map((val) => (
            <div key={val.id} className="card p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="font-medium text-neutral-text">Document Validation</span>
                <Badge variant={val.overall_valid ? 'green' : 'red'}>
                  {val.overall_valid ? 'VALID' : 'INVALID'}
                </Badge>
              </div>
              <div className="space-y-2">
                {val.field_validations.map((field, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-neutral-bg rounded-lg">
                    <div className="flex items-center gap-2">
                      {field.valid ? (
                        <CheckCircle className="w-4 h-4 text-status-green" />
                      ) : (
                        <XCircle className="w-4 h-4 text-status-red" />
                      )}
                      <span className="text-sm text-neutral-text-secondary">{field.field_name.replace(/_/g, ' ')}</span>
                    </div>
                    <span className="text-sm font-mono text-neutral-text">{field.value}</span>
                    {field.message && (
                      <span className="text-xs text-status-amber">{field.message}</span>
                    )}
                  </div>
                ))}
              </div>
              {(val.warnings && val.warnings.length > 0) && (
                <div className="mt-3 p-3 bg-status-amber/10 border border-status-amber/20 rounded-lg">
                  <p className="text-sm font-medium text-status-amber mb-1">Warnings</p>
                  <ul className="text-sm text-status-amber/90 list-disc list-inside space-y-1">
                    {val.warnings.map((w, i) => <li key={i}>{w}</li>)}
                  </ul>
                </div>
              )}
              {(val.errors && val.errors.length > 0) && (
                <div className="mt-3 p-3 bg-status-red/10 border border-status-red/20 rounded-lg">
                  <p className="text-sm font-medium text-status-red mb-1">Errors</p>
                  <ul className="text-sm text-status-red/90 list-disc list-inside space-y-1">
                    {val.errors.map((e, i) => <li key={i}>{e}</li>)}
                  </ul>
                </div>
              )}
              {val.reference_db_check && val.reference_db_check.found && (
                <div className="mt-3 p-3 bg-primary-royal/10 border border-primary-royal/20 rounded-lg">
                  <p className="text-sm font-medium text-primary-royal mb-1">Reference Database Check</p>
                  <p className="text-sm text-primary-royal/90">Record found: {val.reference_db_check.status}</p>
                  {val.reference_db_check.blacklisted && (
                    <p className="text-sm text-status-red mt-1">⚠ BLACKLISTED RECORD</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

const CrossDocumentSection = ({ crossResults }: { crossResults: CrossDocumentResult[] }) => {
  if (crossResults.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Link2 className="w-5 h-5 text-primary-royal" />
          <span className="section-title">Cross-Document Verification</span>
        </div>
      </CardHeader>
      <CardBody>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-border">
                <th className="text-left p-3 font-medium text-neutral-text-secondary">FIELD</th>
                <th className="text-left p-3 font-medium text-neutral-text-secondary">DOCUMENT VALUES</th>
                <th className="text-center p-3 font-medium text-neutral-text-secondary">RESULT</th>
              </tr>
            </thead>
            <tbody>
              {crossResults.flatMap((result) => 
                result.comparisons.map((comp, i) => (
                  <tr key={`${result.id}-${i}`} className="border-b border-neutral-border/50">
                    <td className="p-3 text-neutral-text-secondary">{comp.field_name.replace(/_/g, ' ').toUpperCase()}</td>
                    <td className="p-3">
                      <div className="space-y-1">
                        {Object.entries(comp.document_values).map(([doc, value]) => (
                          <div key={doc} className="flex items-center gap-2 text-sm">
                            <span className="text-neutral-text-secondary">{doc}:</span>
                            <span className="font-mono text-neutral-text">{value}</span>
                          </div>
                        ))}
                      </div>
                    </td>
                    <td className="p-3 text-center">
                      {comp.consistent ? (
                        <CheckCircle className="w-5 h-5 text-status-green mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-status-red mx-auto" />
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardBody>
    </Card>
  );
};

const TamperSection = ({ tamperResults }: { tamperResults: TamperResult[] }) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-primary-royal" />
          <span className="section-title">AI Tampering Detection</span>
        </div>
      </CardHeader>
      <CardBody>
        <div className="space-y-6">
          {tamperResults.map((tamper) => (
            <div key={tamper.id} className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-neutral-text">Document Analysis</p>
                  <p className="text-sm text-neutral-text-secondary">Tampering Probability: {tamper.tampering_probability ? (tamper.tampering_probability * 100).toFixed(1) : 0}%</p>
                </div>
                <Badge variant={tamper.tampering_probability && tamper.tampering_probability > 0.7 ? 'red' : tamper.tampering_probability && tamper.tampering_probability > 0.3 ? 'amber' : 'green'}>
                  {tamper.tampering_probability && tamper.tampering_probability > 0.7 ? 'HIGH RISK' : tamper.tampering_probability && tamper.tampering_probability > 0.3 ? 'REVIEW' : 'CLEAN'}
                </Badge>
              </div>

              <ProgressBar 
                value={(tamper.tampering_probability || 0) * 100} 
                variant={tamper.tampering_probability && tamper.tampering_probability > 0.7 ? 'red' : 'amber'} 
                showLabel 
              />

              {tamper.suspected_regions && tamper.suspected_regions.length > 0 && (
                <div className="space-y-2">
                  <p className="font-medium text-neutral-text">Suspected Regions</p>
                  {tamper.suspected_regions.map((region, i) => (
                    <div key={i} className="p-3 bg-status-amber/10 border border-status-amber/20 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-status-amber" />
                          <span className="font-medium text-status-amber/90 capitalize">{region.region}</span>
                        </div>
                        <Badge variant="amber">{(region.probability * 100).toFixed(0)}%</Badge>
                      </div>
                      <p className="text-sm text-status-amber/80 mt-1">{region.description}</p>
                    </div>
                  ))}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card p-4">
                  <p className="text-sm font-medium text-neutral-text-secondary mb-2">Original RGB Image</p>
                  <div className="aspect-video bg-neutral-bg rounded-lg flex items-center justify-center border border-neutral-border/50">
                    {tamper.rgb_image_path ? (
                      <img src={api.getFileUrl(tamper.rgb_image_path)} alt="RGB" className="max-w-full max-h-full rounded" />
                    ) : (
                      <div className="text-center text-neutral-text-secondary">
                        <Image className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>RGB Image</p>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="card p-4">
                  <p className="text-sm font-medium text-neutral-text-secondary mb-2">Tamper Heatmap</p>
                  <div className="aspect-video bg-neutral-bg rounded-lg flex items-center justify-center border border-neutral-border/50">
                    {tamper.heatmap_path ? (
                      <img src={api.getFileUrl(tamper.heatmap_path)} alt="Heatmap" className="max-w-full max-h-full rounded" />
                    ) : (
                      <div className="text-center text-neutral-text-secondary">
                        <Layers className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>Heatmap</p>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="card p-4">
                  <p className="text-sm font-medium text-neutral-text-secondary mb-2">Noise Residual</p>
                  <div className="aspect-video bg-neutral-bg rounded-lg flex items-center justify-center border border-neutral-border/50">
                    {tamper.noise_analysis_reliable && tamper.noise_residual_path ? (
                      <img src={api.getFileUrl(tamper.noise_residual_path)} alt="Noise" className="max-w-full max-h-full rounded" />
                    ) : (
                      <div className="text-center text-neutral-text-secondary">
                        <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-50 text-status-amber" />
                        <p className="text-sm">Noise residual analysis not reliable for this image</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {tamper.forensics_findings && (
                <div className="card p-4">
                  <p className="text-sm font-medium text-neutral-text-secondary mb-2">Forensic Analysis Findings</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    {Object.entries(tamper.forensics_findings).map(([key, value]) => (
                      <div key={key} className="bg-neutral-bg p-3 rounded-lg">
                        <p className="text-neutral-text-secondary">{key.replace(/_/g, ' ')}</p>
                        <p className="font-mono text-neutral-text">{JSON.stringify(value).slice(0, 50)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

const FaceSection = ({ faceResults }: { faceResults: FaceResult[] }) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <User className="w-5 h-5 text-primary-royal" />
          <span className="section-title">Face Verification</span>
        </div>
      </CardHeader>
      <CardBody>
        <div className="space-y-6">
          {faceResults.map((face) => (
            <div key={face.id} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                <div className="card p-4 text-center">
                  <p className="text-sm font-medium text-neutral-text-secondary mb-3">Document Face</p>
                  <div className="aspect-square bg-neutral-bg rounded-lg flex items-center justify-center border border-neutral-border/50">
                    {face.document_face_path ? (
                      <img src={api.getFileUrl(face.document_face_path)} alt="Doc Face" className="max-w-full max-h-full rounded" />
                    ) : (
                      <div className="text-center text-neutral-text-secondary">
                        <User className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No face detected</p>
                      </div>
                    )}
                  </div>
                  <Badge variant={face.document_face_detected ? 'green' : 'red'} className="mt-2">
                    {face.document_face_detected ? 'DETECTED' : 'NOT DETECTED'}
                  </Badge>
                </div>

                <div className="flex flex-col items-center justify-center">
                  <div className="w-24 h-24 rounded-full border-4 border-primary-royal/20 flex items-center justify-center">
                    <span className="text-3xl font-bold text-primary-royal">
                      {face.similarity_score ? (face.similarity_score * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                  <Badge variant={getMatchStatusColor(face.match_status || '')} className="mt-3">
                    {getMatchStatusLabel(face.match_status || '')}
                  </Badge>
                </div>

                <div className="card p-4 text-center">
                  <p className="text-sm font-medium text-neutral-text-secondary mb-3">Live Face</p>
                  <div className="aspect-square bg-neutral-bg rounded-lg flex items-center justify-center border border-neutral-border/50">
                    {face.live_face_path ? (
                      <img src={api.getFileUrl(face.live_face_path)} alt="Live Face" className="max-w-full max-h-full rounded" />
                    ) : (
                      <div className="text-center text-neutral-text-secondary">
                        <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No live capture</p>
                      </div>
                    )}
                  </div>
                  <Badge variant={face.live_face_detected ? 'green' : 'red'} className="mt-2">
                    {face.live_face_detected ? 'DETECTED' : 'NOT DETECTED'}
                  </Badge>
                </div>
              </div>

              <div className="card p-4 bg-neutral-bg/50">
                <p className="text-sm font-medium text-neutral-text-secondary mb-2">Verification Notes</p>
                <p className="text-sm text-neutral-text">
                  The system must never automatically make a legal identity determination solely from face similarity. 
                  Officer must review the evidence and make the final decision.
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

const RiskPanel = ({ riskAssessment }: { riskAssessment: RiskAssessment | null }) => {
  if (!riskAssessment) return null;

  const riskColor = getRiskLevelColor(riskAssessment.risk_level);
  const riskLabel = getRiskLevelLabel(riskAssessment.risk_level);

  return (
    <Card className="border-2" style={{ borderColor: riskColor.replace('status-', '').replace('-', '') === 'green' ? '#16A34A' : riskColor.replace('status-', '').replace('-', '') === 'amber' ? '#F59E0B' : '#DC2626' }}>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5" style={{ color: riskColor.replace('status-', '').replace('-', '') === 'green' ? '#16A34A' : riskColor.replace('status-', '').replace('-', '') === 'amber' ? '#F59E0B' : '#DC2626' }} />
          <span className="section-title">Final Risk Assessment</span>
        </div>
      </CardHeader>
      <CardBody>
        <div className="text-center mb-6">
          <div className="w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-4" style={{ 
            backgroundColor: riskColor.replace('status-', '').replace('-', '') === 'green' ? '#16A34A' : riskColor.replace('status-', '').replace('-', '') === 'amber' ? '#F59E0B' : '#DC2626' }}>
            <span className="text-5xl font-bold text-white">{riskLabel}</span>
          </div>
          <p className="text-lg text-neutral-text-secondary">Risk Score: {(riskAssessment.risk_score * 100).toFixed(1)}%</p>
        </div>

        <div className="space-y-3">
          <p className="font-medium text-neutral-text">Contributing Factors:</p>
          {riskAssessment.contributing_factors.map((factor: RiskFactor, i: number) => (
            <div key={i} className="flex items-center justify-between p-3 bg-neutral-bg rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-primary-royal/10 flex items-center justify-center">
                  <Shield className="w-4 h-4 text-primary-royal" />
                </div>
                <div>
                  <p className="font-medium text-neutral-text">{factor.factor}</p>
                  <p className="text-sm text-neutral-text-secondary">{factor.description}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-primary-royal">{(factor.contribution * 100).toFixed(1)}%</p>
                <p className="text-xs text-neutral-text-secondary">Weight: {(factor.weight * 100).toFixed(0)}%</p>
              </div>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};

const FinalSummary = ({ 
  documents, 
  mrzResults, 
  validationResults, 
  tamperResults, 
  faceResults, 
  crossResults,
  riskAssessment 
}: { 
  documents: Document[]; 
  mrzResults: MRZResult[]; 
  validationResults: ValidationResult[];
  tamperResults: TamperResult[];
  faceResults: FaceResult[];
  crossResults: CrossDocumentResult[];
  riskAssessment: RiskAssessment | null;
}) => {
  const riskLevel = riskAssessment?.risk_level || 'low';
  const riskColor = getRiskLevelColor(riskLevel);
  const riskLabel = getRiskLevelLabel(riskLevel);

  return (
    <Card className="border-2" style={{ borderColor: riskColor.replace('status-', '').replace('-', '') === 'green' ? '#16A34A' : riskColor.replace('status-', '').replace('-', '') === 'amber' ? '#F59E0B' : '#DC2626' }}>
      <CardHeader>
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5" style={{ color: riskColor.replace('status-', '').replace('-', '') === 'green' ? '#16A34A' : riskColor.replace('status-', '').replace('-', '') === 'amber' ? '#F59E0B' : '#DC2626' }} />
          <span className="section-title">Final Verification Summary</span>
        </div>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          <div>
            <p className="font-medium text-neutral-text mb-3">DOCUMENT STATUS</p>
            <div className="space-y-2">
              {documents.map((doc) => {
                const val = validationResults.find(v => v.document_id === doc.id);
                return (
                  <div key={doc.id} className="flex items-center justify-between p-2 bg-neutral-bg rounded-lg">
                    <span className="font-medium text-neutral-text">{getDocumentTypeLabel(doc.document_type)}</span>
                    <Badge variant={val?.overall_valid ? 'green' : 'red'}>
                      {val?.overall_valid ? 'VALID' : 'INVALID'}
                    </Badge>
                  </div>
                );
              })}
            </div>
          </div>

          {mrzResults.length > 0 && (
            <div>
              <p className="font-medium text-neutral-text mb-3">MRZ</p>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-neutral-bg rounded-lg">
                  <span className="font-medium text-neutral-text">Checksum</span>
                  <Badge variant={mrzResults[0].checksum_valid ? 'green' : 'red'}>
                    {mrzResults[0].checksum_valid ? 'PASSED' : 'FAILED'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-2 bg-neutral-bg rounded-lg">
                  <span className="font-medium text-neutral-text">OCR ↔ MRZ</span>
                  <Badge variant={(mrzResults[0].consistency_percentage || 0) >= 90 ? 'green' : 'amber'}>
                    {(mrzResults[0].consistency_percentage || 0).toFixed(1)}% MATCH
                  </Badge>
                </div>
              </div>
            </div>
          )}

          {crossResults.length > 0 && (
            <div>
              <p className="font-medium text-neutral-text mb-3">CROSS-DOCUMENT</p>
              <div className="space-y-2">
                {crossResults.flatMap((r) => r.comparisons).map((comp, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-neutral-bg rounded-lg">
                    <span className="font-medium text-neutral-text">{comp.field_name.replace(/_/g, ' ').toUpperCase()}</span>
                    <Badge variant={comp.consistent ? 'green' : 'red'}>
                      {comp.consistent ? 'CONSISTENT' : 'MISMATCH'}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <p className="font-medium text-neutral-text mb-3">TAMPERING</p>
            <div className="space-y-2">
              {tamperResults.map((tamper) => (
                <div key={tamper.id} className="flex items-center justify-between p-2 bg-neutral-bg rounded-lg">
                  <span className="font-medium text-neutral-text">Document</span>
                  <Badge variant={
                    tamper.tampering_probability && tamper.tampering_probability > 0.7 ? 'red' : 
                    tamper.tampering_probability && tamper.tampering_probability > 0.3 ? 'amber' : 'green'
                  }>
                    {tamper.tampering_probability && tamper.tampering_probability > 0.7 ? 'REVIEW REQUIRED' : 
                     tamper.tampering_probability && tamper.tampering_probability > 0.3 ? 'REVIEW' : 'NOT DETECTED'}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {faceResults.length > 0 && (
            <div>
              <p className="font-medium text-neutral-text mb-3">FACE</p>
              <div className="space-y-2">
                {faceResults.map((face) => (
                  <div key={face.id} className="flex items-center justify-between p-2 bg-neutral-bg rounded-lg">
                    <span className="font-medium text-neutral-text">Similarity</span>
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-primary-royal">{face.similarity_score ? (face.similarity_score * 100).toFixed(1) : 0}%</span>
                      <Badge variant={getMatchStatusColor(face.match_status || '')}>
                        {getMatchStatusLabel(face.match_status || '')}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="pt-4 border-t border-neutral-border">
            <div className="flex items-center justify-between">
              <span className="text-lg font-semibold text-neutral-text">OVERALL RISK</span>
              <div className={cn('px-6 py-3 rounded-card font-bold text-xl', `bg-${riskColor}`, 'text-white')}>
                {riskLabel}
              </div>
            </div>
            <p className="text-sm text-neutral-text-secondary mt-2">
              {riskLevel === 'low' ? 'Passenger screening completed successfully. All verification checks passed.' : 
               riskLevel === 'medium' ? 'Manual review recommended. Some verification checks require officer attention.' : 
               'High risk detected. Multiple verification failures require immediate officer intervention.'}
            </p>
          </div>

          <div className="pt-4 border-t border-neutral-border">
            <Button onClick={handleComplete} className="w-full" size="lg">
              COMPLETE VERIFICATION
            </Button>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}