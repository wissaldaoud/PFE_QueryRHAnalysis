/**
 * Employee Selector Component - Modern Combobox
 * Design System pour sélection d'employés avec recherche
 */

import { useState } from "react";
import { Search, User, ChevronDown, Loader2, Building2, Check } from "lucide-react";

interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  full_name: string;
  department_name?: string;
  employment_status: string;
}

interface EmployeeSelectorProps {
  employees: Employee[];
  selectedEmployee: Employee | null;
  onSelect: (employee: Employee) => void;
  loading?: boolean;
  className?: string;
}

export default function EmployeeSelector({
  employees,
  selectedEmployee,
  onSelect,
  loading = false,
  className = "",
}: EmployeeSelectorProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  const filteredEmployees = employees.filter((emp) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      emp.full_name?.toLowerCase().includes(search) ||
      emp.first_name?.toLowerCase().includes(search) ||
      emp.last_name?.toLowerCase().includes(search) ||
      emp.employee_code?.toLowerCase().includes(search) ||
      emp.id.toString().includes(search)
    );
  });

  const displayValue = selectedEmployee
    ? `${selectedEmployee.full_name} • ${selectedEmployee.employee_code}`
    : "";

  return (
    <div className={`relative ${className}`}>
      {/* Label */}
      <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
        Sélectionner un employé
      </label>

      {/* Input Button */}
      <button
        type="button"
        onClick={() => !loading && setIsOpen(!isOpen)}
        disabled={loading}
        className={`
          group relative w-full
          flex items-center gap-3
          px-4 py-3.5
          bg-white dark:bg-slate-800
          border-2 border-slate-200 dark:border-slate-700
          rounded-xl
          text-left
          transition-all duration-200
          ${
            isOpen
              ? "ring-2 ring-indigo-500/50 border-indigo-500 dark:border-indigo-500"
              : "hover:border-slate-300 dark:hover:border-slate-600"
          }
          ${loading ? "opacity-60 cursor-not-allowed" : "cursor-pointer"}
        `}
      >
        {/* Icon */}
        <div
          className={`
            flex-shrink-0 p-2 rounded-lg
            transition-colors duration-200
            ${
              selectedEmployee || isOpen
                ? "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400"
                : "bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-500"
            }
          `}
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <User className="w-5 h-5" strokeWidth={2} />
          )}
        </div>

        {/* Text */}
        <div className="flex-1 min-w-0">
          {selectedEmployee ? (
            <>
              <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                {selectedEmployee.full_name}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                {selectedEmployee.employee_code}
                {selectedEmployee.department_name && ` • ${selectedEmployee.department_name}`}
              </p>
            </>
          ) : (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {loading
                ? "Chargement..."
                : employees.length === 0
                ? "Aucun employé disponible"
                : `Rechercher parmi ${employees.length} employés...`}
            </p>
          )}
        </div>

        {/* Chevron */}
        <ChevronDown
          className={`
            flex-shrink-0 w-5 h-5 text-slate-400
            transition-transform duration-200
            ${isOpen ? "rotate-180" : ""}
          `}
        />
      </button>

      {/* Dropdown */}
      {isOpen && !loading && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <div
            className={`
              absolute z-20 w-full mt-2
              bg-white dark:bg-slate-800
              border border-slate-200 dark:border-slate-700
              rounded-xl shadow-2xl shadow-slate-300/50 dark:shadow-black/50
              overflow-hidden
              animate-in fade-in slide-in-from-top-2 duration-200
            `}
          >
            {/* Search Input */}
            <div className="p-3 border-b border-slate-200 dark:border-slate-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className={`
                    w-full pl-10 pr-4 py-2
                    bg-slate-50 dark:bg-slate-900/50
                    border border-slate-200 dark:border-slate-700
                    rounded-lg
                    text-sm text-slate-900 dark:text-white
                    placeholder:text-slate-400
                    focus:outline-none focus:ring-2 focus:ring-indigo-500/50
                  `}
                  autoFocus
                />
              </div>
            </div>

            {/* Employee List */}
            <div className="max-h-80 overflow-y-auto overscroll-contain">
              {filteredEmployees.length === 0 ? (
                <div className="p-8 text-center">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-700 mb-3">
                    <Search className="w-5 h-5 text-slate-400" />
                  </div>
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                    Aucun employé trouvé
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                    Essayez un autre terme de recherche
                  </p>
                </div>
              ) : (
                <div className="py-1">
                  {filteredEmployees.slice(0, 100).map((emp) => {
                    const isSelected = selectedEmployee?.id === emp.id;
                    return (
                      <button
                        key={emp.id}
                        onClick={() => {
                          onSelect(emp);
                          setIsOpen(false);
                          setSearchTerm("");
                        }}
                        className={`
                          w-full flex items-center gap-3 px-4 py-3
                          text-left
                          transition-colors duration-150
                          ${
                            isSelected
                              ? "bg-indigo-50 dark:bg-indigo-900/20"
                              : "hover:bg-slate-50 dark:hover:bg-slate-700/50"
                          }
                        `}
                      >
                        {/* Avatar/Icon */}
                        <div
                          className={`
                            flex-shrink-0 flex items-center justify-center
                            w-10 h-10 rounded-lg
                            transition-colors duration-150
                            ${
                              isSelected
                                ? "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400"
                                : "bg-slate-100 dark:bg-slate-700 text-slate-400"
                            }
                          `}
                        >
                          <User className="w-5 h-5" strokeWidth={2} />
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <p
                            className={`
                              text-sm font-semibold truncate
                              ${
                                isSelected
                                  ? "text-indigo-900 dark:text-indigo-300"
                                  : "text-slate-900 dark:text-white"
                              }
                            `}
                          >
                            {emp.full_name}
                          </p>
                          <p className="text-xs text-slate-500 dark:text-slate-400 truncate flex items-center gap-1.5">
                            <span>{emp.employee_code}</span>
                            {emp.department_name && (
                              <>
                                <span>•</span>
                                <span className="flex items-center gap-1">
                                  <Building2 className="w-3 h-3" />
                                  {emp.department_name}
                                </span>
                              </>
                            )}
                          </p>
                        </div>

                        {/* Check Icon */}
                        {isSelected && (
                          <Check className="flex-shrink-0 w-5 h-5 text-indigo-600 dark:text-indigo-400" strokeWidth={2.5} />
                        )}
                      </button>
                    );
                  })}

                  {filteredEmployees.length > 100 && (
                    <div className="px-4 py-3 text-center border-t border-slate-200 dark:border-slate-700">
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        +{filteredEmployees.length - 100} autres résultats
                      </p>
                      <p className="text-xs text-slate-400 dark:text-slate-500">
                        Affinez votre recherche
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
