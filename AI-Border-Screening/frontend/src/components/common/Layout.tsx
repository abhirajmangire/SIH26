import React, { ReactNode } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { 
  LayoutDashboard, 
  LogOut, 
  Bell, 
  User, 
  Shield, 
  ChevronDown,
  Menu,
  X
} from 'lucide-react';
import { Button, Badge } from './UI';
import { cn, formatDate } from '../../utils/helpers';
import type { Officer } from '../../types';

export const MainLayout = () => {
  const { officer, logout, loading } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  const [profileOpen, setProfileOpen] = React.useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-bg">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-royal border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-neutral-text-secondary">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-bg">
      <aside className={cn(
        'fixed inset-y-0 left-0 z-50 w-64 bg-primary-navy transform transition-transform duration-300 ease-in-out lg:translate-x-0',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-primary-royal/20">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary-royal flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">Border Security</h1>
                <p className="text-xs text-primary-cyan/80">AI Screening System</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end
                  className={({ isActive }) => cn(
                    'flex items-center gap-3 px-4 py-3 rounded-card text-sm font-medium transition-colors',
                    isActive 
                      ? 'bg-primary-royal/20 text-white' 
                      : 'text-primary-cyan/70 hover:bg-primary-royal/10 hover:text-white'
                  )}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>

          <div className="p-4 border-t border-primary-royal/20">
            <p className="text-xs text-primary-cyan/60 uppercase tracking-wider mb-2">Problem Statement</p>
            <p className="text-sm text-primary-cyan/80 font-mono">ID: 26188</p>
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 bg-white border-b border-neutral-border">
          <div className="flex items-center justify-between h-16 px-4 lg:px-6">
            <div className="flex items-center gap-4">
              <button
                className="lg:hidden p-2 rounded-card hover:bg-neutral-bg transition-colors"
                onClick={() => setSidebarOpen(true)}
                aria-label="Open menu"
              >
                <Menu className="w-6 h-6 text-neutral-text" />
              </button>
              <div className="hidden lg:block">
                <h1 className="text-xl font-bold text-neutral-text">AI Document Screening & Tamper Detection</h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button className="relative p-2 rounded-card hover:bg-neutral-bg transition-colors">
                <Bell className="w-5 h-5 text-neutral-text" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-status-red rounded-full" />
              </button>

              <div className="relative">
                <button
                  className="flex items-center gap-2 p-2 rounded-card hover:bg-neutral-bg transition-colors"
                  onClick={() => setProfileOpen(!profileOpen)}
                  aria-expanded={profileOpen}
                >
                  <div className="w-8 h-8 rounded-full bg-primary-royal flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                  <div className="hidden md:block text-left">
                    <p className="text-sm font-medium text-neutral-text">{officer?.full_name}</p>
                    <p className="text-xs text-neutral-text-secondary">{officer?.officer_id}</p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-neutral-text-secondary" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-card shadow-lg border border-neutral-border py-2 animate-fade-in">
                    <div className="px-4 py-2 border-b border-neutral-border">
                      <p className="text-sm font-medium text-neutral-text">{officer?.full_name}</p>
                      <p className="text-xs text-neutral-text-secondary">{officer?.officer_id}</p>
                      <p className="text-xs text-neutral-text-secondary">{officer?.department}</p>
                    </div>
                    <NavLink
                      to="/profile"
                      className="flex items-center gap-3 px-4 py-2 text-sm text-neutral-text hover:bg-neutral-bg"
                      onClick={() => setProfileOpen(false)}
                    >
                      <User className="w-4 h-4" />
                      Profile
                    </NavLink>
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-3 w-full px-4 py-2 text-sm text-status-red hover:bg-status-red/10"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export const AuthLayout = ({ children }: { children: ReactNode }) => {
  return (
    <div className="min-h-screen bg-primary-navy flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary-royal/10 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-5" />
      <div className="relative w-full max-w-md">
        {children}
      </div>
    </div>
  );
};