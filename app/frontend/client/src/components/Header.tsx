import React, { useState } from 'react';
import {
  Search,
  Bell,
  Bookmark,
  Sparkles,
  Command,
  CheckCircle2,
  FileText,
  LogOut,
  User,
  Shield
} from 'lucide-react';
import { UserProfile } from '../views/SignInView';

interface HeaderProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  systemStatus: string;
  user?: UserProfile | null;
  onSignOut?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onTabChange,
  systemStatus,
  user,
  onSignOut
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const notifications = [
    {
      id: 1,
      title: 'RBI Digital Lending Directions 2025 Enacted',
      desc: 'Master Directions DOR.CRE.REC.14/21.07.001/2025-26 in effect.',
      date: 'May 8, 2025'
    },
    {
      id: 2,
      title: 'Para 17 Commencement Notice',
      desc: 'Systems & governance audit obligations in full effect.',
      date: 'June 15, 2025'
    },
    {
      id: 3,
      title: 'Para 6 Scheduled Transition',
      desc: 'CIMS credit reporting deadline approaching.',
      date: 'Nov 1, 2025'
    }
  ];

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    onTabChange('copilot');
  };

  const displayName = user?.name || 'Andrew';
  const displayRole = user?.role || 'Lead Officer (NBFC & Fintech)';
  const displayAvatar = user?.avatarText || 'CO';

  return (
    <header className="h-16 bg-white border-b border-slate-200/90 px-8 flex items-center justify-between sticky top-0 z-30 select-none">
      {/* Left: Active Breadcrumb / Scope */}
      <div className="flex items-center space-x-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Jurisdiction:
        </span>
        <div className="flex items-center space-x-1.5 bg-slate-100 hover:bg-slate-200/80 px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-800 transition cursor-pointer">
          <span>🇮🇳</span>
          <span>Reserve Bank of India (RBI)</span>
        </div>
      </div>

      {/* Center: Global Search Bar matching Pimlico layout */}
      <form
        onSubmit={handleSearchSubmit}
        className="flex-1 max-w-xl mx-8 relative hidden md:block"
      >
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search regulations, circulars, clauses, directions..."
            className="w-full bg-slate-50 hover:bg-slate-100/80 focus:bg-white text-slate-900 placeholder-slate-400 text-xs pl-10 pr-16 py-2 rounded-xl border border-slate-200/90 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition shadow-2xs"
          />
          <div className="absolute right-3 flex items-center space-x-1 pointer-events-none">
            <span className="text-[10px] bg-white border border-slate-200 text-slate-400 font-mono px-1.5 py-0.5 rounded shadow-2xs">
              Ctrl K
            </span>
          </div>
        </div>
      </form>

      {/* Right Actions: Bookmark, Notifications, User Profile */}
      <div className="flex items-center space-x-3.5">
        <button
          title="Saved Regulations"
          onClick={() => onTabChange('documents')}
          className="w-9 h-9 rounded-xl border border-slate-200/80 hover:bg-slate-50 flex items-center justify-center text-slate-500 hover:text-slate-800 transition cursor-pointer"
        >
          <Bookmark className="w-4 h-4" />
        </button>

        <div className="relative">
          <button
            title="Regulatory Updates"
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-9 h-9 rounded-xl border border-slate-200/80 hover:bg-slate-50 flex items-center justify-center text-slate-500 hover:text-slate-800 transition relative cursor-pointer"
          >
            <Bell className="w-4 h-4" />
            <span className="w-2 h-2 rounded-full bg-blue-600 absolute top-2 right-2 ring-2 ring-white" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-2xl shadow-xl p-4 z-50 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <span className="text-xs font-bold text-slate-900">
                  Regulatory Radar Alerts
                </span>
                <span className="text-[10px] text-blue-600 font-semibold cursor-pointer">
                  Mark all read
                </span>
              </div>
              <div className="space-y-2.5 max-h-60 overflow-y-auto">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className="p-2.5 rounded-xl bg-slate-50 hover:bg-slate-100 transition cursor-pointer"
                  >
                    <div className="text-xs font-bold text-slate-800">{n.title}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5">{n.desc}</div>
                    <div className="text-[10px] text-blue-600 font-mono mt-1">
                      {n.date}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Avatar & Compliance Badge with Dropdown */}
        <div className="relative">
          <div
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-2.5 pl-2 border-l border-slate-200/80 cursor-pointer hover:opacity-90 transition"
          >
            <div className="w-8 h-8 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center ring-2 ring-slate-100">
              {displayAvatar}
            </div>
            <div className="hidden lg:flex flex-col text-left">
              <span className="text-xs font-bold text-slate-800 leading-tight">
                {displayName}
              </span>
              <span className="text-[10px] text-slate-500 leading-tight truncate max-w-[140px]">
                {displayRole}
              </span>
            </div>
          </div>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-64 bg-white border border-slate-200 rounded-2xl shadow-xl p-3 z-50 space-y-2.5">
              <div className="p-2 border-b border-slate-100">
                <div className="text-xs font-bold text-slate-900">{displayName}</div>
                <div className="text-[11px] text-slate-500 truncate">{user?.email || 'andrew.compliance@finreg.ai'}</div>
                <div className="text-[10px] text-blue-600 font-medium mt-0.5">{displayRole}</div>
              </div>

              {onSignOut && (
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onSignOut();
                  }}
                  className="w-full flex items-center space-x-2 p-2 rounded-xl text-xs font-medium text-rose-600 hover:bg-rose-50 transition cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign out of Session</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
