'use client';

import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Calendar, X } from 'lucide-react';

interface LeaveEvent {
  id: number;
  employee_name: string;
  leave_type: 'annual' | 'sick' | 'unpaid';
  start_date: string;
  end_date: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
}

interface LeaveCalendarProps {
  leaves: LeaveEvent[];
  onClose?: () => void;
}

const leaveTypeColors: Record<string, { bg: string; border: string; text: string; darkBg: string; darkBorder: string }> = {
  annual: { 
    bg: 'bg-blue-100', 
    border: 'border-blue-400', 
    text: 'text-blue-800',
    darkBg: 'dark:bg-blue-900/40',
    darkBorder: 'dark:border-blue-500'
  },
  sick: { 
    bg: 'bg-orange-100', 
    border: 'border-orange-400', 
    text: 'text-orange-800',
    darkBg: 'dark:bg-orange-900/40',
    darkBorder: 'dark:border-orange-500'
  },
  unpaid: { 
    bg: 'bg-gray-100', 
    border: 'border-gray-400', 
    text: 'text-gray-800',
    darkBg: 'dark:bg-gray-700/40',
    darkBorder: 'dark:border-gray-500'
  },
};

const statusIndicator: Record<string, string> = {
  pending: '⏳',
  approved: '✅',
  rejected: '❌',
  cancelled: '🚫',
};

const DAYS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
const MONTHS = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
];

export default function LeaveCalendar({ leaves, onClose }: LeaveCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState<Date | null>(null);
  const [dayLeaves, setDayLeaves] = useState<LeaveEvent[]>([]);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  // Premier jour du mois
  const firstDayOfMonth = new Date(year, month, 1);
  // Dernier jour du mois
  const lastDayOfMonth = new Date(year, month + 1, 0);
  
  // Ajuster pour commencer la semaine le lundi (0 = Lundi, 6 = Dimanche)
  let startingDay = firstDayOfMonth.getDay() - 1;
  if (startingDay < 0) startingDay = 6;

  const daysInMonth = lastDayOfMonth.getDate();

  // Créer un tableau des jours
  const days: (number | null)[] = [];
  for (let i = 0; i < startingDay; i++) {
    days.push(null);
  }
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  const prevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
    setSelectedDay(null);
  };

  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
    setSelectedDay(null);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDay(null);
  };

  // Vérifier si une date est dans une période de congé
  const getLeavesForDay = (day: number): LeaveEvent[] => {
    const date = new Date(year, month, day);
    const dateStr = date.toISOString().split('T')[0];
    
    return leaves.filter(leave => {
      const start = new Date(leave.start_date);
      const end = new Date(leave.end_date);
      return date >= start && date <= end;
    });
  };

  const handleDayClick = (day: number) => {
    const date = new Date(year, month, day);
    setSelectedDay(date);
    setDayLeaves(getLeavesForDay(day));
  };

  const isToday = (day: number): boolean => {
    const today = new Date();
    return day === today.getDate() && 
           month === today.getMonth() && 
           year === today.getFullYear();
  };

  const isWeekend = (day: number): boolean => {
    const date = new Date(year, month, day);
    const dayOfWeek = date.getDay();
    return dayOfWeek === 0 || dayOfWeek === 6;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#E31837] to-[#c41530] dark:from-[#b01229] dark:to-[#8c0e21] p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Calendar className="w-6 h-6 text-white" />
            <h2 className="text-xl font-bold text-white">Calendrier des Congés</h2>
          </div>
          {onClose && (
            <button 
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <button
          onClick={prevMonth}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        </button>
        
        <div className="flex items-center gap-4">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
            {MONTHS[month]} {year}
          </h3>
          <button
            onClick={goToToday}
            className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors text-gray-700 dark:text-gray-200"
          >
            Aujourd'hui
          </button>
        </div>
        
        <button
          onClick={nextMonth}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <ChevronRight className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        </button>
      </div>

      {/* Légende */}
      <div className="flex flex-wrap gap-4 px-4 py-3 border-b dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-blue-400 dark:bg-blue-500"></div>
          <span className="text-xs text-gray-600 dark:text-gray-300">Congé Annuel</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-orange-400 dark:bg-orange-500"></div>
          <span className="text-xs text-gray-600 dark:text-gray-300">Maladie</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-gray-400 dark:bg-gray-500"></div>
          <span className="text-xs text-gray-600 dark:text-gray-300">Sans Solde</span>
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs">✅ Approuvé</span>
          <span className="text-xs">⏳ En attente</span>
        </div>
      </div>

      {/* Jours de la semaine */}
      <div className="grid grid-cols-7 bg-gray-50 dark:bg-gray-900/50">
        {DAYS.map(day => (
          <div 
            key={day} 
            className="py-3 text-center text-sm font-medium text-gray-600 dark:text-gray-400"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Grille des jours */}
      <div className="grid grid-cols-7">
        {days.map((day, index) => {
          if (day === null) {
            return (
              <div 
                key={`empty-${index}`} 
                className="h-24 border-t border-r dark:border-gray-700 bg-gray-50 dark:bg-gray-900/30"
              />
            );
          }

          const dayLeavesForCell = getLeavesForDay(day);
          const hasLeaves = dayLeavesForCell.length > 0;
          const isSelected = selectedDay && 
            day === selectedDay.getDate() && 
            month === selectedDay.getMonth() && 
            year === selectedDay.getFullYear();

          return (
            <div
              key={day}
              onClick={() => handleDayClick(day)}
              className={`
                h-24 border-t border-r dark:border-gray-700 p-1 cursor-pointer transition-colors
                ${isWeekend(day) ? 'bg-gray-50 dark:bg-gray-900/30' : 'bg-white dark:bg-gray-800'}
                ${isSelected ? 'ring-2 ring-[#E31837] ring-inset' : ''}
                hover:bg-gray-100 dark:hover:bg-gray-700/50
              `}
            >
              <div className="flex flex-col h-full">
                <span 
                  className={`
                    text-sm font-medium w-7 h-7 flex items-center justify-center rounded-full
                    ${isToday(day) ? 'bg-[#E31837] text-white' : 'text-gray-700 dark:text-gray-200'}
                    ${isWeekend(day) && !isToday(day) ? 'text-gray-400 dark:text-gray-500' : ''}
                  `}
                >
                  {day}
                </span>
                
                {/* Congés du jour */}
                <div className="flex-1 overflow-hidden space-y-0.5 mt-1">
                  {dayLeavesForCell.slice(0, 2).map((leave, i) => {
                    const colors = leaveTypeColors[leave.leave_type] || leaveTypeColors.annual;
                    return (
                      <div 
                        key={leave.id}
                        className={`
                          text-[10px] px-1 py-0.5 rounded truncate border-l-2
                          ${colors.bg} ${colors.border} ${colors.text}
                          ${colors.darkBg} ${colors.darkBorder} dark:text-gray-100
                        `}
                        title={`${leave.employee_name} - ${leave.leave_type}`}
                      >
                        {statusIndicator[leave.status]} {leave.employee_name?.split(' ')[0]}
                      </div>
                    );
                  })}
                  {dayLeavesForCell.length > 2 && (
                    <div className="text-[10px] text-gray-500 dark:text-gray-400 px-1">
                      +{dayLeavesForCell.length - 2} autres
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Détails du jour sélectionné */}
      {selectedDay && dayLeaves.length > 0 && (
        <div className="border-t dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900/50">
          <h4 className="font-semibold text-gray-800 dark:text-white mb-3">
            Congés du {selectedDay.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
          </h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {dayLeaves.map(leave => {
              const colors = leaveTypeColors[leave.leave_type] || leaveTypeColors.annual;
              return (
                <div 
                  key={leave.id}
                  className={`
                    flex items-center justify-between p-2 rounded-lg border-l-4
                    ${colors.bg} ${colors.border} ${colors.darkBg} ${colors.darkBorder}
                  `}
                >
                  <div>
                    <p className="font-medium text-gray-800 dark:text-white">
                      {statusIndicator[leave.status]} {leave.employee_name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-300">
                      {new Date(leave.start_date).toLocaleDateString('fr-FR')} → {new Date(leave.end_date).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded ${colors.bg} ${colors.text} ${colors.darkBg} dark:text-gray-100`}>
                    {leave.leave_type === 'annual' ? 'Congé' : leave.leave_type === 'sick' ? 'Maladie' : 'Sans solde'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {selectedDay && dayLeaves.length === 0 && (
        <div className="border-t dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900/50 text-center text-gray-500 dark:text-gray-400">
          Aucun congé ce jour
        </div>
      )}
    </div>
  );
}
