import { useQuery } from '@tanstack/react-query'
import { fetchLeads } from '../api/client'

/**
 * @param {Record<string, unknown>} filters
 */
export function useLeads(filters = {}) {
  return useQuery({
    queryKey: ['leads', filters],
    queryFn: () => fetchLeads(filters),
  })
}
