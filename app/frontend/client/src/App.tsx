import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardView } from './views/DashboardView';
import { CopilotView } from './views/CopilotView';
import { TimelineDiffView } from './views/TimelineDiffView';
import { DocumentView } from './views/DocumentView';
import { BenchmarkView } from './views/BenchmarkView';
import { ComplianceMatrixView } from './views/ComplianceMatrixView';
import { RiskCalculatorView } from './views/RiskCalculatorView';
import { GraphView } from './views/GraphView';
import { SignInView, UserProfile } from './views/SignInView';
import { apiClient } from './api/client';
import { MessageSquare, Sparkles, ShieldAlert, Lock } from 'lucide-react';

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('FinReg AI Application Error caught by boundary:', error, errorInfo);
  }

  handleReset = () => {
    try {
      localStorage.clear();
      sessionStorage.clear();
    } catch {
      // ignore
    }
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-slate-800 border border-slate-700 rounded-2xl p-6 text-center space-y-4 shadow-2xl">
            <div className="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center justify-center mx-auto text-xl font-bold">
              !
            </div>
            <h2 className="text-lg font-bold text-white">Application State Reset Required</h2>
            <p className="text-xs text-slate-300">
              A browser-cached session error occurred. Resetting cached authorization tokens will restore access immediately.
            </p>
            <div className="text-[11px] font-mono text-slate-400 bg-slate-900/60 p-2.5 rounded-lg text-left overflow-auto max-h-24">
              {this.state.error?.message || 'Unknown render error'}
            </div>
            <button
              onClick={this.handleReset}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 px-4 rounded-xl text-xs transition cursor-pointer"
            >
              Reset Session & Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function AppInner() {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(() => {
    try {
      const stored = localStorage.getItem('finreg_user');
      if (!stored) return null;
      const parsed = JSON.parse(stored);
      // If cached user lacks allowedTabs from previous versions, purge stale cache
      if (!parsed || !Array.isArray(parsed.allowedTabs)) {
        localStorage.removeItem('finreg_user');
        return null;
      }
      return parsed;
    } catch {
      return null;
    }
  });

  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState('Online');

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await apiClient.health();
        if (res.status === 'healthy') {
          setSystemStatus('Active');
        }
      } catch (err) {
        setSystemStatus('Connected');
      }
    }
    checkHealth();
  }, []);

  // Safe tab permission check
  const isTabAllowed = (tab: string) => {
    if (!currentUser || !Array.isArray(currentUser.allowedTabs)) return tab === 'dashboard';
    return currentUser.allowedTabs.includes(tab);
  };

  // Ensure activeTab is always within user's allowedTabs
  useEffect(() => {
    if (currentUser && !isTabAllowed(activeTab)) {
      setActiveTab('dashboard');
    }
  }, [currentUser, activeTab]);

  const handleSignIn = (user: UserProfile) => {
    setCurrentUser(user);
    setActiveTab('dashboard');
    try {
      localStorage.setItem('finreg_user', JSON.stringify(user));
    } catch (e) {
      console.warn('Could not persist auth to localStorage', e);
    }
  };

  const handleSignOut = () => {
    setCurrentUser(null);
    setActiveTab('dashboard');
    try {
      localStorage.removeItem('finreg_user');
    } catch (e) {
      console.warn('Could not clear auth from localStorage', e);
    }
  };

  const handleTabChange = (tab: string) => {
    if (currentUser && !isTabAllowed(tab)) {
      setActiveTab('dashboard');
      return;
    }
    setActiveTab(tab);
  };

  const handleSelectDocumentFromCitation = (docId: string) => {
    setSelectedDocId(docId);
    handleTabChange('documents');
  };

  // If not authenticated, show modern executive Sign-In Page
  if (!currentUser) {
    return <SignInView onSignIn={handleSignIn} />;
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 flex font-sans selection:bg-blue-600 selection:text-white">
      {/* Fixed Left Sidebar matching Pimlico reference layout */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={handleTabChange}
        systemStatus={systemStatus}
        user={currentUser}
        onSignOut={handleSignOut}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <Header
          activeTab={activeTab}
          onTabChange={handleTabChange}
          systemStatus={systemStatus}
          user={currentUser}
          onSignOut={handleSignOut}
        />

        {/* Main Canvas Body */}
        <main className="flex-1 p-6 md:p-8 max-w-[1600px] w-full mx-auto">
          {activeTab === 'dashboard' && isTabAllowed('dashboard') && (
            <DashboardView onNavigate={handleTabChange} user={currentUser} />
          )}

          {activeTab === 'copilot' && (
            isTabAllowed('copilot') ? (
              <CopilotView onSelectDocument={handleSelectDocumentFromCitation} />
            ) : (
              <RestrictedWorkspaceNotice user={currentUser} workspace="Compliance Copilot" />
            )
          )}

          {activeTab === 'timeline' && (
            isTabAllowed('timeline') ? (
              <TimelineDiffView />
            ) : (
              <RestrictedWorkspaceNotice user={currentUser} workspace="Timeline & Monitors" />
            )
          )}

          {activeTab === 'documents' && (
            isTabAllowed('documents') ? (
              <DocumentView selectedDocId={selectedDocId} />
            ) : (
              <RestrictedWorkspaceNotice user={currentUser} workspace="Regulatory Database" />
            )
          )}

          {activeTab === 'matrix' && (
            isTabAllowed('matrix') ? (
              <ComplianceMatrixView />
            ) : (
              <RestrictedWorkspaceNotice user={currentUser} workspace="Compliance Matrix" />
            )
          )}

          {activeTab === 'risk' && (
            isTabAllowed('risk') ? (
              <RiskCalculatorView />
            ) : (
              <RestrictedWorkspaceNotice user={currentUser} workspace="Risk Evaluator" />
            )
          )}

          {activeTab === 'graph' && (
            isTabAllowed('graph') ? (
              <GraphView />
            ) : (
              <RestrictedWorkspaceNotice user={currentUser} workspace="Dependency Graph" />
            )
          )}

          {activeTab === 'benchmark' && (
            isTabAllowed('benchmark') ? (
              <BenchmarkView />
            ) : (
              <RestrictedWorkspaceNotice user={currentUser} workspace="Empirical Benchmark" />
            )
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-200/80 bg-white px-8 py-4 text-center text-xs text-slate-500">
          <p>
            FinReg AI &bull; Indian Financial Regulation Intelligence Platform &bull; RBI & NPCI Compliance &bull; Task 6 Dvara Group AI/ML Evaluation
          </p>
        </footer>
      </div>

      {/* Floating Bottom-Right Copilot Bubble (Visible only if Copilot is in user's permitted tabs) */}
      {isTabAllowed('copilot') && (
        <button
          onClick={() => handleTabChange('copilot')}
          title="Open Compliance Copilot"
          className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-[#0c1322] hover:bg-blue-600 text-white shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-105 group z-50 ring-4 ring-white cursor-pointer"
        >
          <MessageSquare className="w-6 h-6 group-hover:scale-110 transition-transform" />
          <span className="sr-only">Open Copilot</span>
          {activeTab !== 'copilot' && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-blue-500 border-2 border-white flex items-center justify-center">
              <Sparkles className="w-2.5 h-2.5 text-white" />
            </span>
          )}
        </button>
      )}
    </div>
  );
}

const RestrictedWorkspaceNotice: React.FC<{ user: UserProfile; workspace: string }> = ({
  user,
  workspace
}) => (
  <div className="bg-white border border-rose-200 rounded-2xl p-8 max-w-xl mx-auto my-12 text-center space-y-4 shadow-xs">
    <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 border border-rose-200 flex items-center justify-center mx-auto">
      <Lock className="w-6 h-6" />
    </div>
    <div className="space-y-1">
      <h3 className="text-base font-bold text-slate-900">
        Workspace Restricted ({workspace})
      </h3>
      <p className="text-xs text-slate-500 leading-relaxed">
        Your active security profile (<span className="font-semibold text-slate-800">{user.role}</span>) does not have authorization to access this workspace under RBAC policy.
      </p>
    </div>
    <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs text-slate-600 font-mono">
      Clearance Level: {user.clearanceLevel}
    </div>
    <div className="text-[11px] text-slate-400">
      Please contact Andrew (Lead Compliance Officer) for access elevation.
    </div>
  </div>
);

export function App() {
  return (
    <ErrorBoundary>
      <AppInner />
    </ErrorBoundary>
  );
}

export default App;
