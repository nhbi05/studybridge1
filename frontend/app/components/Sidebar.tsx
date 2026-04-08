'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  BookOpen,
  Lightbulb,
  TrendingUp,
  Settings,
  User,
} from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/curriculum', label: 'My Curriculum', icon: BookOpen },
  { href: '/recommendations', label: 'Recommendations', icon: Lightbulb },
  { href: '/progress', label: 'Progress', icon: TrendingUp },
  { href: '/profile', label: 'Profile', icon: User },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, isAuthenticated } = useAuth();

  // Hide sidebar if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen sticky top-0">
      {/* Logo/Header */}
      <div className="px-6 py-8 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold text-gray-900">StudyBridge</h1>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6">
        <ul className="space-y-2">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href;
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                    isActive
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-gray-200">
        <div className="px-4 py-3 rounded-lg bg-emerald-50">
          <p className="text-sm font-medium text-gray-900">
            {user?.user_metadata?.name || user?.email || 'Guest'}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            {user?.email || 'Not signed in'}
          </p>
        </div>
      </div>
    </aside>
  );
}
