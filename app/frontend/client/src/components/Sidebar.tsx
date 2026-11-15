import React from 'react';
import {
  LayoutDashboard,
  Database,
  Radio,
  Sparkles,
  History,
  Scale,
  ShieldAlert,
  Share2,
  Award,
  ChevronRight,
  ShieldCheck,
  LogOut,
  UserCheck
} from 'lucide-react';
import { UserProfile } from '../views/SignInView';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  systemStatus: string;
  user?: UserProfile | null;
  onSignOut?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  systemStatus,
  user,
  onSignOut
}) => {
  const allNavItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'documents', label: 'Database', icon: Database, badge: '12 Docs' },
    { id: 'timeline', label: 'Monitors', icon: Radio, badge: 'Live' },
    { id: 'copilot', label: 'Workspace', icon: Sparkles, highlight: true },
    { id: 'matrix', label: 'Compliance Matrix', icon: Scale },
    { id: 'risk', label: 'Risk Evaluator', icon: ShieldAlert },
    { id: 'graph', label: 'Dependency Graph', icon: Share2 },
    { id: 'benchmark', label: 'Benchmark', icon: Award }
  ];

  // RBAC Filtering: Show permitted and locked workspaces for this user profile
  const allowedTabs = Array.isArray(user?.allowedTabs)
    ? user.allowedTabs
    : allNavItems.map(i => i.id);
  const visibleNavItems = allNavItems.filter((item) => allowedTabs.includes(item.id));
  const restrictedNavItems = allNavItems.filter((item) => !allowedTabs.includes(item.id));

  return (
    <aside className="w-64 bg-white border-r border-slate-200/90 flex flex-col justify-between shrink-0 h-screen sticky top-0 z-40 select-none overflow-y-auto">
      <div>
        {/* Brand Header */}
        <div className="h-16 px-6 border-b border-slate-100 flex items-center justify-between">
          <div
            onClick={() => onTabChange('dashboard')}
            className="flex items-center space-x-2.5 cursor-pointer group"
          >
            <div className="w-8 h-8 rounded-lg bg-[#0c1322] text-white flex items-center justify-center font-bold text-sm shadow-xs group-hover:bg-blue-600 transition">
              ⚖️
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-slate-900 text-base tracking-tight flex items-center space-x-1.5">
                <span>FinReg AI</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest text-blue-600 font-mono -mt-0.5">
                RBI COPILOT
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="p-3 space-y-1">
          <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span>Permitted Workspaces</span>
            <span className="font-mono text-blue-600 font-bold">{visibleNavItems.length}/8</span>
          </div>
          {visibleNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all group cursor-pointer ${
                  isActive
                    ? 'bg-slate-100 text-slate-900 font-bold border border-slate-200/80 shadow-2xs'
                    : 'text-slate-600 hover:text-slate-950 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon
                    className={`w-4 h-4 transition-colors ${
                      isActive
                        ? 'text-blue-600'
                        : item.highlight
                        ? 'text-indigo-500 group-hover:text-blue-600'
                        : 'text-slate-400 group-hover:text-slate-700'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-medium ${
                      isActive
                        ? 'bg-slate-200 text-slate-800'
                        : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
                {item.highlight && !isActive && (
                  <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                )}
              </button>
            );
          })}

          {/* Locked / Restricted Workspaces for this clearance level */}
          {restrictedNavItems.length > 0 && (
            <div className="pt-3 mt-3 border-t border-slate-100 space-y-1">
              <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
                <span>Restricted Modules</span>
                <span className="font-mono text-rose-500 font-bold">{restrictedNavItems.length} Locked</span>
              </div>
              {restrictedNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <div
                    key={item.id}
                    title={`Restricted: Requires higher clearance than ${user?.clearanceLevel || 'current level'}`}
                    className="w-full flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-medium text-slate-400 bg-slate-50/50 border border-transparent cursor-not-allowed select-none opacity-70"
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className="w-4 h-4 text-slate-300" />
                      <span className="line-through decoration-slate-300">{item.label}</span>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded font-mono bg-slate-100 text-slate-400 border border-slate-200">
                      Locked
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Sidebar Footer - User Clearance & System Health */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/60 space-y-2.5">
        {/* User Role & Clearance Badge */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-2.5 text-xs space-y-1 shadow-2xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-900 truncate max-w-[120px]">
              {user?.name || 'Authorized User'}
            </span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              {user?.avatarText === 'AN' ? 'Admin' : user?.avatarText === 'PS' ? 'Risk' : 'Legal'}
            </span>
          </div>
          <p className="text-[10px] text-slate-500 truncate leading-tight">
            {user?.role || 'Compliance Officer'}
          </p>
        </div>

        {/* RAG Core Status */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-2.5 shadow-2xs flex items-center justify-between text-xs">
          <span className="font-semibold text-slate-700 flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>RAG Core</span>
          </span>
          <span className="flex items-center space-x-1 text-[11px] text-emerald-600 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>{systemStatus}</span>
          </span>
        </div>

        {onSignOut && (
          <button
            onClick={onSignOut}
            className="w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-xl border border-slate-200 text-slate-500 hover:text-rose-600 hover:bg-rose-50/60 hover:border-rose-200 text-xs font-medium transition cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign out</span>
          </button>
        )}
      </div>
    </aside>
  );
};
