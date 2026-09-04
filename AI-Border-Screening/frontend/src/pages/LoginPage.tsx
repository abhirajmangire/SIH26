import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';
import { Button, Input, Card } from '../common/UI';
import { cn } from '../../utils/helpers';

export const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [officerId, setOfficerId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(officerId, password);
      setSuccess(true);
      setTimeout(() => navigate('/dashboard'), 1000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid officer ID or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto animate-fade-in">
      <div className="text-center mb-10">
        <div className="w-16 h-16 rounded-xl bg-primary-royal flex items-center justify-center mx-auto mb-6">
          <Shield className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">AI Document Screening & Tamper Detection</h1>
        <p className="text-primary-cyan/80">Border Security Operations Platform</p>
        <p className="text-xs text-primary-cyan/60 mt-2 font-mono">Problem Statement ID: 26188</p>
      </div>

      <Card className="bg-white/5 border-primary-royal/20 backdrop-blur-sm overflow-hidden">
        <div className="p-8">
          <h2 className="text-xl font-semibold text-white mb-6 text-center">Officer Sign In</h2>

          {success && (
            <div className="mb-6 flex items-center gap-2 p-3 bg-status-green/20 border border-status-green/30 rounded-card text-status-green animate-fade-in">
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">Authentication successful. Redirecting...</span>
            </div>
          )}

          {error && (
            <div className="mb-6 flex items-center gap-2 p-3 bg-status-red/20 border border-status-red/30 rounded-card text-status-red animate-fade-in" role="alert">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Officer ID"
              type="text"
              value={officerId}
              onChange={(e) => setOfficerId(e.target.value)}
              placeholder="Enter your officer ID"
              required
              autoComplete="username"
              disabled={loading}
            />

            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
              disabled={loading}
              rightIcon={
                <button
                  type="button"
                  className="text-neutral-text-secondary hover:text-neutral-text"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              }
            />

            <Button type="submit" className="w-full" size="lg" loading={loading}>
              Sign In
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-white/10">
            <p className="text-xs text-primary-cyan/60 text-center mb-4">Demo Credentials</p>
            <div className="bg-white/5 rounded-card p-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-primary-cyan/80">Officer ID:</span>
                <code className="text-white font-mono">OFFICER001</code>
              </div>
              <div className="flex justify-between">
                <span className="text-primary-cyan/80">Password:</span>
                <code className="text-white font-mono">SecurePass123!</code>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <p className="text-center text-xs text-primary-cyan/50 mt-6">
        AI-Based Document Screening and Tamper Detection System • Prototype for SIH
      </p>
    </div>
  );
};