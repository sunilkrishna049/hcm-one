import React, { useState, useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import { Search, X, Check, RotateCcw } from 'lucide-react';
import type { EmployeePickerEntry } from '../../../utils/welcomeTurn';

export interface EmployeeDropdownPickerProps {
  employees: EmployeePickerEntry[];
  status?: 'loading' | 'ready' | 'error';
  isWaking?: boolean;
  onRetry?: () => void;
  onSelectEmployee: (employee: EmployeePickerEntry) => void;
  selectedEmployee?: EmployeePickerEntry | null;
  autoFocus?: boolean;
}

export interface EmployeeDropdownPickerRef {
  focusInput: () => void;
  openDropdown: () => void;
}

function highlightMatch(text: string, query: string) {
  if (!query.trim()) return text;
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escaped})`, 'gi');
  const parts = text.split(regex);
  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <span key={i} style={{ color: '#5B8EE6', fontWeight: 600 }}>
            {part}
          </span>
        ) : (
          part
        )
      )}
    </>
  );
}

export const EmployeeDropdownPicker = forwardRef<EmployeeDropdownPickerRef, EmployeeDropdownPickerProps>(
  (
    {
      employees = [],
      status = 'ready',
      isWaking = false,
      onRetry,
      onSelectEmployee,
      selectedEmployee = null,
      autoFocus = true,
    },
    ref
  ) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [isOpen, setIsOpen] = useState(true);
    const [highlightedIndex, setHighlightedIndex] = useState(0);
    const [internalWaking, setInternalWaking] = useState(false);
    const [isFocused, setIsFocused] = useState(false);

    const containerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useImperativeHandle(ref, () => ({
      focusInput: () => {
        inputRef.current?.focus();
        setIsOpen(true);
      },
      openDropdown: () => {
        setIsOpen(true);
      },
    }));

    // Auto focus on mount if not already selected
    useEffect(() => {
      if (autoFocus && !selectedEmployee && inputRef.current) {
        inputRef.current.focus();
      }
    }, [autoFocus, selectedEmployee]);

    // Timer for 3-second waking up notice during cold start
    useEffect(() => {
      if (status === 'loading') {
        const timer = setTimeout(() => {
          setInternalWaking(true);
        }, 3000);
        return () => clearTimeout(timer);
      } else {
        setInternalWaking(false);
      }
    }, [status]);

    const showWakingNotice = isWaking || internalWaking;

    // Handle click outside to close dropdown
    useEffect(() => {
      const handleClickOutside = (e: MouseEvent | TouchEvent) => {
        if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
          setIsOpen(false);
        }
      };
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('touchstart', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
        document.removeEventListener('touchstart', handleClickOutside);
      };
    }, []);

    useEffect(() => {
      setHighlightedIndex(0);
    }, [searchQuery]);

    // If an employee is already selected for this turn, collapse into read-only pill (A5)
    if (selectedEmployee) {
      return (
        <div
          data-testid="selected-employee-pill"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 14px',
            backgroundColor: '#1A1A1A',
            border: '1px solid #2A2A2A',
            borderRadius: '9999px',
            color: '#FFFFFF',
            fontSize: '13px',
            fontWeight: 500,
            marginTop: '8px',
          }}
        >
          <Check size={14} color="#10B981" />
          <span>
            {selectedEmployee.name} ·{' '}
            <span style={{ color: '#9CA3AF', fontWeight: 400 }}>{selectedEmployee.employee_id}</span>
          </span>
        </div>
      );
    }

    // Filter logic
    const trimmed = searchQuery.trim().toLowerCase();
    const isSearching = trimmed.length > 0;

    let displayedEmployees: EmployeePickerEntry[] = [];
    let groupHeading = '';
    let footerText = '';

    if (!isSearching) {
      const needsAttention = employees.filter((emp) =>
        (emp.status_tags || []).some((t) => t.includes('Needs input') || t.includes('Open query'))
      );
      if (needsAttention.length > 0) {
        groupHeading = 'NEEDS ATTENTION';
        displayedEmployees = needsAttention;
        footerText = `Type to search all ${employees.length} employees by name, code or department.`;
      } else {
        groupHeading = 'ALL EMPLOYEES';
        displayedEmployees = employees.slice(0, 8);
        if (employees.length > 8) {
          footerText = `Showing 8 of ${employees.length}. Keep typing to narrow it down.`;
        } else {
          footerText = `Type to search all ${employees.length} employees by name, code or department.`;
        }
      }
    } else {
      const filtered = employees.filter((emp) => {
        const nameMatch = emp.name.toLowerCase().includes(trimmed);
        const idMatch = emp.employee_id.toLowerCase().includes(trimmed);
        const deptMatch = emp.department ? emp.department.toLowerCase().includes(trimmed) : false;
        return nameMatch || idMatch || deptMatch;
      });

      if (filtered.length > 0) {
        groupHeading = `${filtered.length} ${filtered.length === 1 ? 'result' : 'results'}`;
        displayedEmployees = filtered.slice(0, 8);
        if (filtered.length > 8) {
          footerText = `Showing 8 of ${filtered.length}. Keep typing to narrow it down.`;
        }
      }
    }



    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (!isOpen && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
        setIsOpen(true);
        e.preventDefault();
        return;
      }

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (displayedEmployees.length > 0) {
          setHighlightedIndex((prev) => (prev + 1) % displayedEmployees.length);
        }
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (displayedEmployees.length > 0) {
          setHighlightedIndex((prev) => (prev - 1 + displayedEmployees.length) % displayedEmployees.length);
        }
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (isOpen && displayedEmployees.length > 0) {
          const target = displayedEmployees[highlightedIndex] || displayedEmployees[0];
          if (target) {
            onSelectEmployee(target);
          }
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        setIsOpen(false);
      }
    };

    const handleClear = () => {
      setSearchQuery('');
      setIsOpen(true);
      inputRef.current?.focus();
    };

    const activeOptionId =
      isOpen && displayedEmployees[highlightedIndex]
        ? `employee-option-${displayedEmployees[highlightedIndex].employee_id}`
        : undefined;

    return (
      <div
        ref={containerRef}
        data-testid="employee-dropdown-picker"
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: '480px',
          marginTop: '10px',
          boxSizing: 'border-box',
          fontFamily: 'inherit',
        }}
      >
        {/* Search Field (A4) */}
        <div
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            width: '100%',
            height: '44px',
            minHeight: '44px',
            backgroundColor: '#090909',
            border: isFocused ? '1px solid #1150BF' : '1px solid #2A2A2A',
            boxShadow: isFocused ? '0 0 0 2px rgba(17, 80, 191, 0.35)' : 'none',
            borderRadius: '8px',
            boxSizing: 'border-box',
            transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
          }}
        >
          <Search
            size={16}
            color="#9CA3AF"
            style={{ marginLeft: '12px', flexShrink: 0, pointerEvents: 'none' }}
          />
          <input
            ref={inputRef}
            type="text"
            role="combobox"
            id="employee-picker-search-input"
            data-testid="employee-combobox-input"
            aria-label="Search name or employee code"
            aria-expanded={isOpen}
            aria-controls="employee-combobox-listbox"
            aria-autocomplete="list"
            aria-activedescendant={activeOptionId}
            placeholder="Search name or employee code"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => {
              setIsFocused(true);
              setIsOpen(true);
            }}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            style={{
              flex: 1,
              height: '100%',
              backgroundColor: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#FFFFFF',
              fontSize: '14px',
              padding: '0 10px',
              boxSizing: 'border-box',
            }}
          />

          {/* Clear button (x) or "/" hint */}
          {searchQuery ? (
            <button
              type="button"
              onClick={handleClear}
              data-testid="employee-search-clear-btn"
              aria-label="Clear search"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '24px',
                height: '24px',
                marginRight: '10px',
                backgroundColor: 'transparent',
                border: 'none',
                color: '#9CA3AF',
                cursor: 'pointer',
                borderRadius: '50%',
              }}
            >
              <X size={14} />
            </button>
          ) : (
            <span
              style={{
                marginRight: '12px',
                padding: '1px 6px',
                fontSize: '11px',
                fontWeight: 600,
                color: '#9CA3AF',
                backgroundColor: '#1F1F1F',
                border: '1px solid #2A2A2A',
                borderRadius: '4px',
                pointerEvents: 'none',
                userSelect: 'none',
              }}
            >
              /
            </span>
          )}
        </div>

        {/* Dropdown Panel (A4) */}
        {isOpen && (
          <div
            id="employee-combobox-listbox"
            role="listbox"
            aria-label="Employees"
            data-testid="employee-combobox-dropdown"
            style={{
              position: 'absolute',
              top: '48px',
              left: 0,
              width: '100%',
              maxHeight: '320px',
              backgroundColor: '#141414',
              border: '1px solid #2A2A2A',
              borderRadius: '12px',
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
              overflowY: 'auto',
              zIndex: 50,
              boxSizing: 'border-box',
              padding: '4px 0',
            }}
          >
            {/* Cold start: loading state (B1) */}
            {status === 'loading' && (
              <div style={{ padding: '8px 12px' }} data-testid="employee-loading-container">
                {showWakingNotice && (
                  <div
                    data-testid="dropdown-waking-notice"
                    style={{
                      padding: '8px 10px',
                      marginBottom: '8px',
                      fontSize: '12px',
                      color: '#E5E7EB',
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      borderRadius: '6px',
                      borderLeft: '3px solid #E3A008',
                    }}
                  >
                    Waking up the demo server. This can take up to a minute.
                  </div>
                )}
                {[0, 1, 2, 3].map((i) => (
                  <div
                    key={i}
                    data-testid={`employee-skeleton-row-${i}`}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '8px 0',
                    }}
                  >
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: '#262626',
                        flexShrink: 0,
                      }}
                    />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
                      <div
                        style={{
                          width: `${120 + i * 20}px`,
                          height: '14px',
                          borderRadius: '4px',
                          backgroundColor: '#262626',
                        }}
                      />
                      <div
                        style={{
                          width: `${80 + i * 15}px`,
                          height: '10px',
                          borderRadius: '4px',
                          backgroundColor: '#262626',
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Cold start: error state (B1) */}
            {status === 'error' && (
              <div
                data-testid="employee-error-container"
                style={{
                  padding: '16px',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '10px',
                }}
              >
                <span style={{ fontSize: '13px', color: '#EF4444' }}>
                  Couldn't reach the demo server.
                </span>
                {onRetry && (
                  <button
                    type="button"
                    onClick={onRetry}
                    data-testid="employee-retry-btn"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '6px 14px',
                      borderRadius: '9999px',
                      backgroundColor: '#1150BF',
                      color: '#FFFFFF',
                      fontSize: '12px',
                      fontWeight: 500,
                      border: 'none',
                      cursor: 'pointer',
                    }}
                  >
                    <RotateCcw size={13} />
                    <span>Try again</span>
                  </button>
                )}
              </div>
            )}

            {/* Ready state with search results / group */}
            {status === 'ready' && (
              <>
                {/* No matching results */}
                {isSearching && displayedEmployees.length === 0 && (
                  <div
                    data-testid="no-employee-matches"
                    style={{
                      padding: '16px',
                      textAlign: 'center',
                    }}
                  >
                    <div style={{ fontSize: '13px', fontWeight: 500, color: '#FFFFFF', marginBottom: '4px' }}>
                      No employee matches "{searchQuery}".
                    </div>
                    <div style={{ fontSize: '12px', color: '#9CA3AF' }}>
                      Try a first name, an employee code like E05, or a department.
                    </div>
                  </div>
                )}

                {/* Has results or default empty-field list */}
                {displayedEmployees.length > 0 && (
                  <>
                    {groupHeading && (
                      <div
                        data-testid="employee-group-heading"
                        style={{
                          padding: '6px 12px',
                          fontSize: '11px',
                          fontWeight: 700,
                          letterSpacing: '0.05em',
                          color: '#9CA3AF',
                          textTransform: 'uppercase',
                        }}
                      >
                        {groupHeading}
                      </div>
                    )}

                    {displayedEmployees.map((emp, index) => {
                      const isHighlighted = index === highlightedIndex;
                      const initials = emp.name
                        .split(' ')
                        .map((n: string) => n[0])
                        .filter(Boolean)
                        .slice(0, 2)
                        .join('')
                        .toUpperCase();

                      return (
                        <div
                          key={emp.employee_id}
                          id={`employee-option-${emp.employee_id}`}
                          role="option"
                          aria-selected={isHighlighted}
                          data-testid={`employee-option-${emp.employee_id}`}
                          onClick={() => onSelectEmployee(emp)}
                          onMouseEnter={() => setHighlightedIndex(index)}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '8px 12px',
                            cursor: 'pointer',
                            backgroundColor: isHighlighted ? '#1A1A1A' : 'transparent',
                            transition: 'background-color 0.1s ease',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0, flex: 1 }}>
                            {/* Initials circle */}
                            <div
                              style={{
                                width: '32px',
                                height: '32px',
                                borderRadius: '50%',
                                backgroundColor: '#262626',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: '#FFFFFF',
                                fontSize: '12px',
                                fontWeight: 600,
                                flexShrink: 0,
                              }}
                            >
                              {initials}
                            </div>

                            {/* Name, code, dept, and live tags */}
                            <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0, flex: 1 }}>
                              <div
                                style={{
                                  fontSize: '13px',
                                  fontWeight: 600,
                                  color: '#FFFFFF',
                                  whiteSpace: 'nowrap',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                }}
                              >
                                {highlightMatch(emp.name, searchQuery)}
                                {' · '}
                                <span style={{ color: '#9CA3AF', fontWeight: 400 }}>
                                  {highlightMatch(emp.employee_id, searchQuery)}
                                </span>
                              </div>

                              <div
                                style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  flexWrap: 'wrap',
                                  marginTop: '2px',
                                }}
                              >
                                {emp.department && (
                                  <span style={{ fontSize: '11px', color: '#9CA3AF' }}>
                                    {highlightMatch(emp.department, searchQuery)}
                                  </span>
                                )}

                                {emp.status_tags &&
                                  emp.status_tags.map((tag) => {
                                    const isAmber = tag.includes('Needs input') || tag.includes('Hike pending');
                                    const isPurple = tag.includes('Open query');
                                    const isBlue = tag.includes('Leaving');

                                    let tagColor = '#9CA3AF';
                                    let tagBg = '#1F1F1F';
                                    let tagBorder = '#2A2A2A';

                                    if (isAmber) {
                                      tagColor = '#E3A008';
                                      tagBg = 'rgba(227, 160, 8, 0.15)';
                                      tagBorder = 'rgba(227, 160, 8, 0.3)';
                                    } else if (isPurple) {
                                      tagColor = '#A78BFA';
                                      tagBg = 'rgba(167, 139, 250, 0.15)';
                                      tagBorder = 'rgba(167, 139, 250, 0.3)';
                                    } else if (isBlue) {
                                      tagColor = '#5B8EE6';
                                      tagBg = 'rgba(91, 142, 230, 0.15)';
                                      tagBorder = 'rgba(91, 142, 230, 0.3)';
                                    }

                                    return (
                                      <span
                                        key={tag}
                                        data-testid={`status-tag-${emp.employee_id}-${tag.toLowerCase().replace(/\s+/g, '-')}`}
                                        style={{
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          padding: '1px 6px',
                                          fontSize: '10px',
                                          fontWeight: 500,
                                          borderRadius: '9999px',
                                          backgroundColor: tagBg,
                                          border: `1px solid ${tagBorder}`,
                                          color: tagColor,
                                          whiteSpace: 'nowrap',
                                        }}
                                      >
                                        {tag}
                                      </span>
                                    );
                                  })}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}

                    {footerText && (
                      <div
                        data-testid="employee-combobox-footer"
                        style={{
                          padding: '8px 12px',
                          fontSize: '11px',
                          color: '#9CA3AF',
                          borderTop: '1px solid #1F1F1F',
                          marginTop: '4px',
                        }}
                      >
                        {footerText}
                      </div>
                    )}
                  </>
                )}
              </>
            )}
          </div>
        )}
      </div>
    );
  }
);
EmployeeDropdownPicker.displayName = 'EmployeeDropdownPicker';
