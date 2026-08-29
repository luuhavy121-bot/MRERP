import type { Employee } from '../types'

export const rankLabels: Record<string, string> = {
  staff: 'Staff', captain: 'Captain', leader: 'Leader', manager: 'Manager', ceo: 'CEO',
}

export function initials(employee?: Employee) {
  const value = employee?.display_name || employee?.employee_code || 'MR'
  return value.split(' ').map((part) => part[0]).join('').slice(-2).toUpperCase()
}
