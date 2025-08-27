import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/services/api'

export interface SecurityEvent {
  id: string
  event_type:
    | 'login_success'
    | 'login_failure'
    | 'password_change'
    | 'account_lockout'
    | 'oauth_login'
    | 'suspicious_activity'
  user_id?: string
  username?: string
  ip_address: string
  user_agent?: string
  details: Record<string, unknown>
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: string
}

export interface SecurityMetrics {
  total_events: number
  failed_logins_24h: number
  successful_logins_24h: number
  account_lockouts_24h: number
  password_changes_24h: number
  suspicious_activities_24h: number
  oauth_logins_24h: number
  top_failed_ips: Array<{ ip: string; count: number }>
  recent_events: SecurityEvent[]
}

export interface AccountLockout {
  id: string
  user_id: string
  username: string
  ip_address: string
  locked_at: string
  unlocked_at?: string
  failed_attempts: number
  is_active: boolean
}

export interface SessionAnalytics {
  id: string
  user_id: string
  username: string
  ip_address: string
  user_agent: string
  device_type: string
  browser: string
  location?: string
  login_time: string
  last_activity: string
  is_active: boolean
  duration_minutes?: number
}

export const useSecurityStore = defineStore('security', () => {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const metrics = ref<SecurityMetrics | null>(null)
  const events = ref<SecurityEvent[]>([])
  const accountLockouts = ref<AccountLockout[]>([])
  const sessionAnalytics = ref<SessionAnalytics[]>([])

  const recentEvents = computed(() => events.value.slice(0, 10))
  const criticalEvents = computed(() => events.value.filter((event) => event.severity === 'critical'))
  const activeAccountLockouts = computed(() => accountLockouts.value.filter((lockout) => lockout.is_active))
  const activeSessions = computed(() => sessionAnalytics.value.filter((session) => session.is_active))

  const fetchSecurityMetrics = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/auth/security/metrics')
      metrics.value = response.data
    } catch (err) {
      error.value = (err as Error)?.message || 'Failed to fetch security metrics'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSecurityEvents = async (limit = 50, eventType?: string) => {
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams()
      params.append('limit', limit.toString())
      if (eventType) params.append('event_type', eventType)
      
      const response = await apiClient.get(`/auth/security/events?${params}`)
      events.value = response.data
    } catch (err) {
      error.value = (err as Error)?.message || 'Failed to fetch security events'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchAccountLockouts = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/auth/passwords/lockouts')
      accountLockouts.value = response.data
    } catch (err) {
      error.value = (err as Error)?.message || 'Failed to fetch account lockouts'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSessionAnalytics = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/auth/sessions/analytics')
      sessionAnalytics.value = response.data
    } catch (err) {
      error.value = (err as Error)?.message || 'Failed to fetch session analytics'
      throw err
    } finally {
      loading.value = false
    }
  }

  const unlockAccount = async (lockoutId: string) => {
    loading.value = true
    error.value = null
    
    try {
      await apiClient.post(`/auth/passwords/lockouts/${lockoutId}/unlock`)
      // Refresh lockouts after unlocking
      await fetchAccountLockouts()
    } catch (err) {
      error.value = (err as Error)?.message || 'Failed to unlock account'
      throw err
    } finally {
      loading.value = false
    }
  }

  const revokeSession = async (sessionId: string) => {
    loading.value = true
    error.value = null
    
    try {
      await apiClient.post(`/auth/sessions/${sessionId}/revoke`)
      // Refresh sessions after revoking
      await fetchSessionAnalytics()
    } catch (err) {
      error.value = (err as Error)?.message || 'Failed to revoke session'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    metrics,
    events,
    accountLockouts,
    sessionAnalytics,
    recentEvents,
    criticalEvents,
    activeAccountLockouts,
    activeSessions,
    fetchSecurityMetrics,
    fetchSecurityEvents,
    fetchAccountLockouts,
    fetchSessionAnalytics,
    unlockAccount,
    revokeSession,
  }
})
