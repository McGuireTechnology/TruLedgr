import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '@/services/api';
export const useSecurityStore = defineStore('security', () => {
    const loading = ref(false);
    const error = ref(null);
    const metrics = ref(null);
    const events = ref([]);
    const accountLockouts = ref([]);
    const sessionAnalytics = ref([]);
    const recentEvents = computed(() => events.value.slice(0, 10));
    const criticalEvents = computed(() => events.value.filter((event) => event.severity === 'critical'));
    const activeAccountLockouts = computed(() => accountLockouts.value.filter((lockout) => lockout.is_active));
    const activeSessions = computed(() => sessionAnalytics.value.filter((session) => session.is_active));
    const fetchSecurityMetrics = async () => {
        loading.value = true;
        error.value = null;
        try {
            const response = await apiClient.get('/auth/security/metrics');
            metrics.value = response.data;
        }
        catch (err) {
            error.value = err?.message || 'Failed to fetch security metrics';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const fetchSecurityEvents = async (limit = 50, eventType) => {
        loading.value = true;
        error.value = null;
        try {
            const params = new URLSearchParams();
            params.append('limit', limit.toString());
            if (eventType)
                params.append('event_type', eventType);
            const response = await apiClient.get(`/auth/security/events?${params}`);
            events.value = response.data;
        }
        catch (err) {
            error.value = err?.message || 'Failed to fetch security events';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const fetchAccountLockouts = async () => {
        loading.value = true;
        error.value = null;
        try {
            const response = await apiClient.get('/auth/passwords/lockouts');
            accountLockouts.value = response.data;
        }
        catch (err) {
            error.value = err?.message || 'Failed to fetch account lockouts';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const fetchSessionAnalytics = async () => {
        loading.value = true;
        error.value = null;
        try {
            const response = await apiClient.get('/auth/sessions/analytics');
            sessionAnalytics.value = response.data;
        }
        catch (err) {
            error.value = err?.message || 'Failed to fetch session analytics';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const unlockAccount = async (lockoutId) => {
        loading.value = true;
        error.value = null;
        try {
            await apiClient.post(`/auth/passwords/lockouts/${lockoutId}/unlock`);
            // Refresh lockouts after unlocking
            await fetchAccountLockouts();
        }
        catch (err) {
            error.value = err?.message || 'Failed to unlock account';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const revokeSession = async (sessionId) => {
        loading.value = true;
        error.value = null;
        try {
            await apiClient.post(`/auth/sessions/${sessionId}/revoke`);
            // Refresh sessions after revoking
            await fetchSessionAnalytics();
        }
        catch (err) {
            error.value = err?.message || 'Failed to revoke session';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
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
    };
});
