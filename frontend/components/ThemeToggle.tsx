'use client';

import { useTheme } from '@/contexts/ThemeContext';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`
        relative p-2 rounded-lg transition-all duration-300
        ${isDark 
          ? 'bg-gray-700 hover:bg-gray-600 text-yellow-400' 
          : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
        }
      `}
      title={isDark ? 'Mode clair' : 'Mode sombre'}
    >
      <div className="relative w-5 h-5">
        <Sun 
          className={`
            absolute inset-0 transform transition-all duration-300
            ${isDark ? 'rotate-90 opacity-0' : 'rotate-0 opacity-100'}
          `}
          size={20}
        />
        <Moon 
          className={`
            absolute inset-0 transform transition-all duration-300
            ${isDark ? 'rotate-0 opacity-100' : '-rotate-90 opacity-0'}
          `}
          size={20}
        />
      </div>
    </button>
  );
}
