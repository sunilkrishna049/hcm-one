export const USER_NAME_MAP: Record<string, { name: string; role: string }> = {
  HR01: { name: 'Anita Desai', role: 'HR Admin' },
  HR02: { name: 'Kiran Patel', role: 'HR Sales' },
  'USER-E01': { name: 'Priya Sharma', role: 'Employee' },
  E01: { name: 'Priya Sharma', role: 'Employee' },
  'USER-E02': { name: 'Arjun Rao', role: 'Employee' },
  E02: { name: 'Arjun Rao', role: 'Employee' },
  'USER-E03': { name: 'Kavya Iyer', role: 'Employee' },
  E03: { name: 'Kavya Iyer', role: 'Employee' },
  'USER-E05': { name: 'Neha Gupta', role: 'Employee' },
  E05: { name: 'Neha Gupta', role: 'Employee' },
  'USER-E06': { name: 'Siddharth Jain', role: 'Employee' },
  E06: { name: 'Siddharth Jain', role: 'Employee' },
  'USER-E09': { name: 'Meera Nair', role: 'Employee' },
  E09: { name: 'Meera Nair', role: 'Employee' },
  'USER-E10': { name: 'Rahul Verma', role: 'Employee' },
  E10: { name: 'Rahul Verma', role: 'Employee' },
  'USER-E11': { name: 'Lakshmi Reddy', role: 'Employee' },
  E11: { name: 'Lakshmi Reddy', role: 'Employee' },
  'USER-E12': { name: 'Imran Khan', role: 'Employee' },
  E12: { name: 'Imran Khan', role: 'Employee' },
  'USER-E16': { name: 'Pooja Das', role: 'Employee' },
  E16: { name: 'Pooja Das', role: 'Employee' },
};

export function getUserDisplayName(userId: string, includeRole = false): string {
  const info = USER_NAME_MAP[userId];
  if (!info) return userId;
  return includeRole ? `${info.name} · ${info.role}` : info.name;
}
