import React, { useState } from 'react';
import {
  Scale,
  Shield,
  Lock,
  Mail,
  Eye,
  EyeOff,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  AlertCircle,
  Building2,
  FileText,
  UserCheck,
  Key
} from 'lucide-react';

export interface UserProfile {
  name: string;
  email: string;
  password: string;
  role: string;
  avatarText: string;
  clearanceLevel: string;
  allowedTabs: string[];
  description: string;
}

interface SignInViewProps {
  onSignIn: (user: UserProfile) => void;
}

export const PREDEFINED_ROLES: UserProfile[] = [
  {
    name: 'Andrew',
    email: 'andrew.compliance@finreg.ai',
    password: 'Andrew@FinReg2025',
    role: 'Lead Compliance Officer (NBFC & Fintech)',
    avatarText: 'AN',
    clearanceLevel: 'Full Administrator (8/8 Workspaces)',
    allowedTabs: [
      'dashboard',
      'documents',
      'timeline',
      'copilot',
      'matrix',
      'risk',
      'graph',
      'benchmark'
    ],
    description: 'Full unconstrained access to all compliance workspaces, Copilot advisory, and audit memo generation.'
  },
  {
    name: 'Priya Sharma',
    email: 'priya.sharma@finreg.ai',
    password: 'Priya@Risk2025',
    role: 'Senior Regulatory Risk Auditor',
    avatarText: 'PS',
    clearanceLevel: 'Risk & Audit Clearance (5/8 Workspaces)',
    allowedTabs: [
      'dashboard',
      'documents',
      'matrix',
      'risk',
      'benchmark'
    ],
    description: 'Auditing focus: Statutory compliance matrix, scenario breach evaluator, and empirical benchmark metrics.'
  },
  {
    name: 'Vikram Mehta',
    email: 'vikram.mehta@finreg.ai',
    password: 'Vikram@Legal2025',
    role: 'Head of Legal & Banking Governance',
    avatarText: 'VM',
    clearanceLevel: 'Legal & Policy Clearance (5/8 Workspaces)',
    allowedTabs: [
      'dashboard',
      'documents',
      'timeline',
      'copilot',
      'graph'
    ],
    description: 'Legal governance focus: Statutory document corpus, timeline diffs, Copilot legal research, and dependency graph.'
  }
];

export const SignInView: React.FC<SignInViewProps> = ({ onSignIn }) => {
  const [email, setEmail] = useState('andrew.compliance@finreg.ai');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const handleSelectRole = (user: UserProfile) => {
    setEmail(user.email);
    setPassword('');
    setAuthError(null);
  };

  const handleFillDemoPassword = (pwd: string) => {
    setPassword(pwd);
    setAuthError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setAuthError(null);

    setTimeout(() => {
      const matched = PREDEFINED_ROLES.find(
        (u) => u.email.toLowerCase() === email.trim().toLowerCase()
      );

      if (!matched) {
        setAuthError(
          'Unauthorized email address. Please select one of the 3 authorized compliance officers.'
        );
        setLoading(false);
        return;
      }

      // Strict Password Verification
      if (password.trim() !== matched.password) {
        setAuthError(
          `Access Denied: Incorrect password for ${matched.name}. Required: "${matched.password}". Wrong password was rejected.`
        );
        setLoading(false);
        return;
      }

      // Validated successfully
      onSignIn(matched);
      setLoading(false);
    }, 300);
  };

  const handleInstantDemoLogin = (user: UserProfile) => {
    setLoading(true);
    setAuthError(null);
    setTimeout(() => {
      onSignIn(user);
      setLoading(false);
    }, 200);
  };

  const selectedRole = PREDEFINED_ROLES.find(
    (u) => u.email.toLowerCase() === email.trim().toLowerCase()
  );

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 md:p-8 font-sans">
      <div className="w-full max-w-5xl bg-[#0a1120] rounded-3xl border border-slate-800 shadow-2xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[680px]">
        
        {/* Left Column: Brand & Role-Based Access Showcase (7 cols) */}
        <div className="lg:col-span-7 bg-[#080d19] p-8 md:p-12 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-slate-800 relative overflow-hidden text-white">
          {/* Subtle Ambient Light Glow */}
          <div className="absolute -top-24 -left-24 w-80 h-80 bg-blue-600/15 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -right-24 w-80 h-80 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />

          {/* Top Brand Tag */}
          <div className="relative z-10 space-y-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-[#0c1322] border border-blue-500/30 text-white flex items-center justify-center font-bold text-lg shadow-md">
                ⚖️
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-xl font-extrabold tracking-tight text-white">FinReg AI</h1>
                  <span className="text-[10px] font-mono uppercase bg-blue-950 text-blue-400 px-2 py-0.5 rounded-full border border-blue-800">
                    RBAC ACTIVE
                  </span>
                </div>
                <p className="text-xs text-slate-400">Role-Based Regulatory Intelligence Platform</p>
              </div>
            </div>

            {/* Main Value Proposition */}
            <div className="space-y-3 pt-2">
              <span className="inline-flex items-center space-x-1.5 bg-blue-500/10 text-blue-400 text-xs font-semibold px-3 py-1 rounded-full border border-blue-500/20">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Distinct Multi-User Clearance Profiles</span>
              </span>
              <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white leading-tight">
                Segmented statutory access for Legal, Risk, and Compliance.
              </h2>
              <p className="text-slate-300 text-xs md:text-sm leading-relaxed max-w-lg">
                Different organizational roles access tailored workspaces with segregated security clearance, password enforcement, and audit governance.
              </p>
            </div>

            {/* 3 Role Clearance Descriptions */}
            <div className="space-y-3 pt-2">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1">
                <div className="flex items-center justify-between text-blue-400 font-bold">
                  <span>1. Andrew — Lead Compliance Officer</span>
                  <span className="text-[10px] bg-blue-950 px-2 py-0.5 rounded text-blue-300 border border-blue-900">
                    All 8 Workspaces
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Full administrative authority: Copilot Q&A, statutory memo generation, risk calculator, timeline diffs, and benchmark audits.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1">
                <div className="flex items-center justify-between text-emerald-400 font-bold">
                  <span>2. Priya Sharma — Risk Auditor</span>
                  <span className="text-[10px] bg-emerald-950 px-2 py-0.5 rounded text-emerald-300 border border-emerald-900">
                    5 Workspaces (Audit & Risk)
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Focused clearance: RE vs LSP Compliance Matrix, Scenario Risk & Penalty Breaches Calculator, and Phase C Benchmarks.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1">
                <div className="flex items-center justify-between text-indigo-400 font-bold">
                  <span>3. Vikram Mehta — Legal Counsel</span>
                  <span className="text-[10px] bg-indigo-950 px-2 py-0.5 rounded text-indigo-300 border border-indigo-900">
                    5 Workspaces (Legal & Policy)
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Focused clearance: Official PDF Database, Tri-temporal Timeline Diffs, Copilot Legal Citations, and Dependency Graph.
                </p>
              </div>
            </div>
          </div>

          {/* Footer Security Note */}
          <div className="pt-6 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center justify-between">
            <span className="flex items-center space-x-1.5">
              <Shield className="w-3.5 h-3.5 text-blue-400" />
              <span>Strict Password Verification &bull; RBAC Enforced</span>
            </span>
            <span className="font-mono text-slate-400">v1.0 Production</span>
          </div>
        </div>

        {/* Right Column: Sign In Form & Password Validator (5 cols) */}
        <div className="lg:col-span-5 bg-white p-8 md:p-10 flex flex-col justify-between">
          <div className="space-y-5">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-100">
                ROLE-BASED AUTHENTICATION
              </span>
              <h3 className="text-xl font-bold text-slate-900 mt-2">
                Sign in to your Cockpit
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Select an authorized compliance role and enter their password.
              </p>
            </div>

            {/* Error Message */}
            {authError && (
              <div className="bg-rose-50 border border-rose-200 text-rose-800 p-3.5 rounded-xl text-xs flex items-start space-x-2.5">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <span className="leading-relaxed">{authError}</span>
              </div>
            )}

            {/* Quick Role Preset Cards with Passwords Displayed */}
            <div className="space-y-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Authorized Personnel (Select to auto-fill):
              </span>
              <div className="grid grid-cols-1 gap-2">
                {PREDEFINED_ROLES.map((roleUser) => {
                  const isSelected = email.toLowerCase() === roleUser.email.toLowerCase();
                  return (
                    <button
                      key={roleUser.email}
                      type="button"
                      onClick={() => handleSelectRole(roleUser)}
                      className={`w-full text-left p-2.5 rounded-xl border text-xs transition flex flex-col space-y-1 cursor-pointer ${
                        isSelected
                          ? 'bg-blue-50/70 border-blue-400 text-slate-900 shadow-2xs'
                          : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 truncate">
                          <div className="w-6 h-6 rounded-full bg-slate-900 text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                            {roleUser.avatarText}
                          </div>
                          <span className="font-bold text-slate-900">{roleUser.name}</span>
                        </div>
                        <span className={`text-[10px] font-semibold px-2 py-0.2 rounded-full ${
                          isSelected ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-700'
                        }`}>
                          {roleUser.avatarText === 'AN' ? 'Admin' : roleUser.avatarText === 'PS' ? 'Risk' : 'Legal'}
                        </span>
                      </div>

                      <div className="text-[11px] text-slate-500 truncate pl-8">
                        {roleUser.role}
                      </div>

                      <div className="flex items-center justify-between text-[10px] font-mono pl-8 pt-1 border-t border-slate-200/60">
                        <span className="text-slate-500">
                          Password: <code className="text-blue-700 font-bold">{roleUser.password}</code>
                        </span>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSelectRole(roleUser);
                            handleFillDemoPassword(roleUser.password);
                          }}
                          className="text-[10px] text-blue-600 hover:text-blue-800 underline font-sans font-semibold cursor-pointer"
                        >
                          Fill Password
                        </button>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-3.5">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-700 block">Work Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3 pointer-events-none" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      setAuthError(null);
                    }}
                    placeholder="name@finreg.ai"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-slate-900 focus:bg-white focus:outline-none focus:border-blue-500 transition"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-slate-700 block">Password (Verified)</label>
                  {selectedRole && (
                    <span className="text-[10px] text-slate-400 font-mono">
                      Expected: <span className="font-bold text-blue-600">{selectedRole.password}</span>
                    </span>
                  )}
                </div>
                <div className="relative">
                  <Lock className={`w-4 h-4 absolute left-3.5 top-3 pointer-events-none ${authError ? 'text-rose-500' : 'text-slate-400'}`} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      setAuthError(null);
                    }}
                    placeholder={selectedRole ? `Enter password (${selectedRole.password})` : "Enter role password"}
                    className={`w-full bg-slate-50 border rounded-xl pl-10 pr-10 py-2.5 text-xs text-slate-900 focus:bg-white focus:outline-none transition font-mono ${
                      authError
                        ? 'border-rose-400 focus:border-rose-500 bg-rose-50/20 ring-1 ring-rose-300'
                        : 'border-slate-200 focus:border-blue-500'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    title={showPassword ? 'Hide password' : 'Show password'}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="absolute right-3 top-2.5 p-1 text-slate-400 hover:text-slate-700 transition cursor-pointer focus:outline-none"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4 text-blue-600" />
                    ) : (
                      <Eye className="w-4 h-4 text-slate-400 hover:text-slate-600" />
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-0.5">
                <label className="flex items-center space-x-2 text-slate-600 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="rounded text-blue-600 accent-blue-600"
                  />
                  <span>Remember compliance session</span>
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#0c1322] hover:bg-blue-600 disabled:opacity-50 text-white font-semibold py-3 rounded-xl text-xs flex items-center justify-center space-x-2 transition shadow-xs cursor-pointer"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Sign in as {selectedRole ? selectedRole.name : 'Authorized User'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="text-[11px] text-slate-400 text-center pt-4 border-t border-slate-100">
            Strict Multi-User Access Control &bull; Passwords Enforced
          </div>
        </div>

      </div>
    </div>
  );
};
