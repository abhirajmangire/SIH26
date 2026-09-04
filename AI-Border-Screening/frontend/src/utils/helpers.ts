import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDateShort(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function getRiskLevelColor(riskLevel: string): string {
  switch (riskLevel) {
    case 'low':
      return 'status-green';
    case 'medium':
      return 'status-amber';
    case 'high':
      return 'status-red';
    default:
      return 'status-blue';
  }
}

export function getRiskLevelLabel(riskLevel: string): string {
  switch (riskLevel) {
    case 'low':
      return 'LOW';
    case 'medium':
      return 'MEDIUM';
    case 'high':
      return 'HIGH';
    default:
      return 'UNKNOWN';
  }
}

export function getProcessingStatusColor(status: string): string {
  switch (status) {
    case 'completed':
      return 'status-green';
    case 'processing':
      return 'status-blue';
    case 'warning':
      return 'status-amber';
    case 'failed':
      return 'status-red';
    default:
      return 'status-blue';
  }
}

export function getProcessingStatusLabel(status: string): string {
  switch (status) {
    case 'waiting':
      return 'WAITING';
    case 'processing':
      return 'PROCESSING';
    case 'completed':
      return 'COMPLETED';
    case 'warning':
      return 'WARNING';
    case 'failed':
      return 'FAILED';
    default:
      return 'UNKNOWN';
  }
}

export function getVerificationStatusLabel(status: string): string {
  switch (status) {
    case 'valid':
      return 'VALID';
    case 'invalid':
      return 'INVALID';
    case 'warning':
      return 'WARNING';
    case 'pending':
      return 'PENDING';
    default:
      return 'UNKNOWN';
  }
}

export function getDocumentTypeLabel(type: string): string {
  switch (type) {
    case 'passport':
      return 'PASSPORT';
    case 'visa':
      return 'VISA';
    case 'national_id':
      return 'NATIONAL ID';
    case 'permit':
      return 'PERMIT';
    default:
      return type.toUpperCase();
  }
}

export function getMatchStatusLabel(status: string): string {
  switch (status) {
    case 'MATCH':
      return 'MATCH';
    case 'POSSIBLE_MISMATCH':
      return 'POSSIBLE MISMATCH';
    case 'MISMATCH':
      return 'MISMATCH';
    default:
      return status;
  }
}

export function getMatchStatusColor(status: string): string {
  switch (status) {
    case 'MATCH':
      return 'status-green';
    case 'POSSIBLE_MISMATCH':
      return 'status-amber';
    case 'MISMATCH':
      return 'status-red';
    default:
      return 'status-blue';
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

export function calculateOverallProgress(steps: Array<{ progress: number }>): number {
  if (steps.length === 0) return 0;
  const total = steps.reduce((sum, step) => sum + step.progress, 0);
  return Math.round(total / steps.length);
}

export function getFileExtension(filename: string): string {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2).toLowerCase();
}

export function isValidImageFile(file: File): boolean {
  const validTypes = ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp', 'application/pdf'];
  return validTypes.includes(file.type);
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function generateCaseId(): string {
  const now = new Date();
  const year = now.getFullYear().toString().slice(-2);
  const month = (now.getMonth() + 1).toString().padStart(2, '0');
  const day = now.getDate().toString().padStart(2, '0');
  const random = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `CASE-${year}${month}${day}-${random}`;
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}