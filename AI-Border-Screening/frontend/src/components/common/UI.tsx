import React from 'react';
import { cn } from '../utils/helpers';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, leftIcon, rightIcon, children, disabled, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-card transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    const variants = {
      primary: 'bg-primary-royal text-white hover:bg-primary-royal/90 focus:ring-primary-royal',
      secondary: 'bg-neutral-card text-neutral-text border border-neutral-border hover:bg-neutral-bg focus:ring-primary-royal',
      danger: 'bg-status-red text-white hover:bg-status-red/90 focus:ring-status-red',
      ghost: 'text-neutral-text hover:bg-neutral-bg focus:ring-neutral-border',
    };
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-5 py-2.5 text-base gap-2',
      lg: 'px-6 py-3 text-lg gap-2.5',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {!loading && leftIcon && <span>{leftIcon}</span>}
        {children}
        {!loading && rightIcon && <span>{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="label">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-neutral-text-secondary">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'input-field',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-status-red focus:ring-status-red',
              className
            )}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
            {...props}
          />
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-neutral-text-secondary">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p id={`${inputId}-error`} className="mt-1.5 text-sm text-status-red" role="alert">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={`${inputId}-helper`} className="mt-1.5 text-sm text-neutral-text-secondary">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export const Badge = ({ 
  children, 
  variant = 'default', 
  className,
  icon 
}: { 
  children: React.ReactNode; 
  variant?: 'default' | 'green' | 'amber' | 'red' | 'blue';
  className?: string;
  icon?: React.ReactNode;
}) => {
  const variants = {
    default: 'bg-neutral-bg text-neutral-text border border-neutral-border',
    green: 'bg-status-green/10 text-status-green border border-status-green/20',
    amber: 'bg-status-amber/10 text-status-amber border border-status-amber/20',
    red: 'bg-status-red/10 text-status-red border border-status-red/20',
    blue: 'bg-primary-royal/10 text-primary-royal border border-primary-royal/20',
  };

  return (
    <span className={cn('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium', variants[variant], className)}>
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {children}
    </span>
  );
};

export const ProgressBar = ({ 
  value, 
  max = 100, 
  variant = 'primary',
  showLabel = false,
  className 
}: { 
  value: number; 
  max?: number; 
  variant?: 'primary' | 'green' | 'amber' | 'red';
  showLabel?: boolean;
  className?: string;
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const variants = {
    primary: 'bg-primary-royal',
    green: 'bg-status-green',
    amber: 'bg-status-amber',
    red: 'bg-status-red',
  };

  return (
    <div className={cn('w-full', className)}>
      <div className="flex justify-between text-xs mb-1">
        {showLabel && <span>Progress</span>}
        {showLabel && <span>{Math.round(percentage)}%</span>}
      </div>
      <div className="progress-bar">
        <div 
          className={cn('progress-fill', variants[variant])}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
};

export const Card = ({ 
  children, 
  className, 
  hover = false,
  padding = true 
}: { 
  children: React.ReactNode; 
  className?: string; 
  hover?: boolean;
  padding?: boolean;
}) => {
  return (
    <div className={cn(
      'card',
      hover && 'hover:shadow-card-hover cursor-pointer transition-shadow duration-200',
      !padding && 'p-0',
      className
    )}>
      {children}
    </div>
  );
};

export const CardHeader = ({ 
  children, 
  className, 
  action 
}: { 
  children: React.ReactNode; 
  className?: string;
  action?: React.ReactNode;
}) => {
  return (
    <div className={cn('card-header flex items-center justify-between', className)}>
      <div>{children}</div>
      {action && <div>{action}</div>}
    </div>
  );
};

export const CardBody = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return <div className={cn('card-body', className)}>{children}</div>;
};

export const StatCard = ({ 
  title, 
  value, 
  trend, 
  trendLabel,
  icon,
  iconColor = 'primary-royal',
  className 
}: { 
  title: string; 
  value: string | number; 
  trend?: number; 
  trendLabel?: string;
  icon?: React.ReactNode;
  iconColor?: string;
  className?: string;
}) => {
  return (
    <Card className={cn('stat-card', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-neutral-text-secondary">{title}</p>
          <p className="mt-1 text-3xl font-bold text-neutral-text">{value}</p>
          {trend !== undefined && (
            <div className="mt-2 flex items-center gap-1.5 text-sm">
              <span className={cn('font-medium', trend >= 0 ? 'text-status-green' : 'text-status-red')}>
                {trend >= 0 ? '+' : ''}{trend}%
              </span>
              <span className="text-neutral-text-secondary">{trendLabel || 'vs last period'}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className={cn('p-3 rounded-lg', `bg-${iconColor}/10`, `text-${iconColor}`)}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};

export const EmptyState = ({ 
  icon, 
  title, 
  description, 
  action 
}: { 
  icon: React.ReactNode; 
  title: string; 
  description: string; 
  action?: React.ReactNode;
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="w-16 h-16 rounded-full bg-neutral-bg flex items-center justify-center text-neutral-text-secondary mb-6">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-neutral-text mb-2">{title}</h3>
      <p className="text-neutral-text-secondary max-w-md mb-6">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
};

export const LoadingSpinner = ({ size = 'md', className }: { size?: 'sm' | 'md' | 'lg'; className?: string }) => {
  const sizes = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' };
  return (
    <svg className={cn('animate-spin text-primary-royal', sizes[size], className)} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
};

export const Skeleton = ({ className }: { className?: string }) => {
  return (
    <div className={cn('animate-pulse bg-neutral-border rounded', className)} />
  );
};