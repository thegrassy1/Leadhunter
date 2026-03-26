import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export async function fetchStats() {
  const { data } = await api.get('/leads/stats')
  return data
}

export async function fetchLeads(params) {
  const { data } = await api.get('/leads', { params })
  return data
}

export async function fetchLead(id) {
  const { data } = await api.get(`/leads/${id}`)
  return data
}

export async function patchLead(id, body) {
  const { data } = await api.patch(`/leads/${id}`, body)
  return data
}

export async function fetchScraperHistory() {
  const { data } = await api.get('/scraper/history')
  return data
}

export async function fetchScraperStatus() {
  const { data } = await api.get('/scraper/status')
  return data
}

export async function runScraper(source) {
  const { data } = await api.post('/scraper/run', { source })
  return data
}

export async function createDraft(leadId, templateType = 'initial_outreach') {
  const { data } = await api.post(`/outreach/draft/${leadId}`, null, {
    params: { template_type: templateType },
  })
  return data
}

export async function patchDraft(id, body) {
  const { data } = await api.patch(`/outreach/draft/${id}`, body)
  return data
}

export async function sendDraft(id) {
  const { data } = await api.post(`/outreach/send/${id}`)
  return data
}

export async function fetchOutreachLeads() {
  return fetchLeads({ page_size: 100, status: 'contacted' })
}

export async function fetchFollowUpLeads() {
  return fetchLeads({ page_size: 100, status: 'follow_up' })
}

export async function fetchInbox(page = 1) {
  const { data } = await api.get('/inbox/replies', { params: { page, page_size: 50 } })
  return data
}

export async function fetchUnreadCount() {
  const { data } = await api.get('/inbox/replies/unread')
  return data
}

export async function fetchThread(leadId) {
  const { data } = await api.get(`/inbox/thread/${leadId}`)
  return data
}

export async function markReplyRead(id) {
  await api.patch(`/inbox/reply/${id}/read`)
}
