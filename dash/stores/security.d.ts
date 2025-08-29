export interface SecurityEvent {
    id: string;
    event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
    user_id?: string;
    username?: string;
    ip_address: string;
    user_agent?: string;
    details: Record<string, unknown>;
    severity: 'low' | 'medium' | 'high' | 'critical';
    timestamp: string;
}
export interface SecurityMetrics {
    total_events: number;
    failed_logins_24h: number;
    successful_logins_24h: number;
    account_lockouts_24h: number;
    password_changes_24h: number;
    suspicious_activities_24h: number;
    oauth_logins_24h: number;
    top_failed_ips: Array<{
        ip: string;
        count: number;
    }>;
    recent_events: SecurityEvent[];
}
export interface AccountLockout {
    id: string;
    user_id: string;
    username: string;
    ip_address: string;
    locked_at: string;
    unlocked_at?: string;
    failed_attempts: number;
    is_active: boolean;
}
export interface SessionAnalytics {
    id: string;
    user_id: string;
    username: string;
    ip_address: string;
    user_agent: string;
    device_type: string;
    browser: string;
    location?: string;
    login_time: string;
    last_activity: string;
    is_active: boolean;
    duration_minutes?: number;
}
export declare const useSecurityStore: import("pinia").StoreDefinition<"security", Pick<{
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    metrics: import("vue").Ref<{
        total_events: number;
        failed_logins_24h: number;
        successful_logins_24h: number;
        account_lockouts_24h: number;
        password_changes_24h: number;
        suspicious_activities_24h: number;
        oauth_logins_24h: number;
        top_failed_ips: {
            ip: string;
            count: number;
        }[];
        recent_events: {
            id: string;
            event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
            user_id?: string | undefined;
            username?: string | undefined;
            ip_address: string;
            user_agent?: string | undefined;
            details: Record<string, unknown>;
            severity: 'low' | 'medium' | 'high' | 'critical';
            timestamp: string;
        }[];
    } | null, SecurityMetrics | {
        total_events: number;
        failed_logins_24h: number;
        successful_logins_24h: number;
        account_lockouts_24h: number;
        password_changes_24h: number;
        suspicious_activities_24h: number;
        oauth_logins_24h: number;
        top_failed_ips: {
            ip: string;
            count: number;
        }[];
        recent_events: {
            id: string;
            event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
            user_id?: string | undefined;
            username?: string | undefined;
            ip_address: string;
            user_agent?: string | undefined;
            details: Record<string, unknown>;
            severity: 'low' | 'medium' | 'high' | 'critical';
            timestamp: string;
        }[];
    } | null>;
    events: import("vue").Ref<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[], SecurityEvent[] | {
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    accountLockouts: import("vue").Ref<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[], AccountLockout[] | {
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[]>;
    sessionAnalytics: import("vue").Ref<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[], SessionAnalytics[] | {
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[]>;
    recentEvents: import("vue").ComputedRef<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    criticalEvents: import("vue").ComputedRef<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    activeAccountLockouts: import("vue").ComputedRef<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[]>;
    activeSessions: import("vue").ComputedRef<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[]>;
    fetchSecurityMetrics: () => Promise<void>;
    fetchSecurityEvents: (limit?: number, eventType?: string) => Promise<void>;
    fetchAccountLockouts: () => Promise<void>;
    fetchSessionAnalytics: () => Promise<void>;
    unlockAccount: (lockoutId: string) => Promise<void>;
    revokeSession: (sessionId: string) => Promise<void>;
}, "loading" | "error" | "events" | "metrics" | "accountLockouts" | "sessionAnalytics">, Pick<{
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    metrics: import("vue").Ref<{
        total_events: number;
        failed_logins_24h: number;
        successful_logins_24h: number;
        account_lockouts_24h: number;
        password_changes_24h: number;
        suspicious_activities_24h: number;
        oauth_logins_24h: number;
        top_failed_ips: {
            ip: string;
            count: number;
        }[];
        recent_events: {
            id: string;
            event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
            user_id?: string | undefined;
            username?: string | undefined;
            ip_address: string;
            user_agent?: string | undefined;
            details: Record<string, unknown>;
            severity: 'low' | 'medium' | 'high' | 'critical';
            timestamp: string;
        }[];
    } | null, SecurityMetrics | {
        total_events: number;
        failed_logins_24h: number;
        successful_logins_24h: number;
        account_lockouts_24h: number;
        password_changes_24h: number;
        suspicious_activities_24h: number;
        oauth_logins_24h: number;
        top_failed_ips: {
            ip: string;
            count: number;
        }[];
        recent_events: {
            id: string;
            event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
            user_id?: string | undefined;
            username?: string | undefined;
            ip_address: string;
            user_agent?: string | undefined;
            details: Record<string, unknown>;
            severity: 'low' | 'medium' | 'high' | 'critical';
            timestamp: string;
        }[];
    } | null>;
    events: import("vue").Ref<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[], SecurityEvent[] | {
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    accountLockouts: import("vue").Ref<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[], AccountLockout[] | {
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[]>;
    sessionAnalytics: import("vue").Ref<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[], SessionAnalytics[] | {
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[]>;
    recentEvents: import("vue").ComputedRef<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    criticalEvents: import("vue").ComputedRef<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    activeAccountLockouts: import("vue").ComputedRef<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[]>;
    activeSessions: import("vue").ComputedRef<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[]>;
    fetchSecurityMetrics: () => Promise<void>;
    fetchSecurityEvents: (limit?: number, eventType?: string) => Promise<void>;
    fetchAccountLockouts: () => Promise<void>;
    fetchSessionAnalytics: () => Promise<void>;
    unlockAccount: (lockoutId: string) => Promise<void>;
    revokeSession: (sessionId: string) => Promise<void>;
}, "recentEvents" | "criticalEvents" | "activeAccountLockouts" | "activeSessions">, Pick<{
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    metrics: import("vue").Ref<{
        total_events: number;
        failed_logins_24h: number;
        successful_logins_24h: number;
        account_lockouts_24h: number;
        password_changes_24h: number;
        suspicious_activities_24h: number;
        oauth_logins_24h: number;
        top_failed_ips: {
            ip: string;
            count: number;
        }[];
        recent_events: {
            id: string;
            event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
            user_id?: string | undefined;
            username?: string | undefined;
            ip_address: string;
            user_agent?: string | undefined;
            details: Record<string, unknown>;
            severity: 'low' | 'medium' | 'high' | 'critical';
            timestamp: string;
        }[];
    } | null, SecurityMetrics | {
        total_events: number;
        failed_logins_24h: number;
        successful_logins_24h: number;
        account_lockouts_24h: number;
        password_changes_24h: number;
        suspicious_activities_24h: number;
        oauth_logins_24h: number;
        top_failed_ips: {
            ip: string;
            count: number;
        }[];
        recent_events: {
            id: string;
            event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
            user_id?: string | undefined;
            username?: string | undefined;
            ip_address: string;
            user_agent?: string | undefined;
            details: Record<string, unknown>;
            severity: 'low' | 'medium' | 'high' | 'critical';
            timestamp: string;
        }[];
    } | null>;
    events: import("vue").Ref<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[], SecurityEvent[] | {
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    accountLockouts: import("vue").Ref<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[], AccountLockout[] | {
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[]>;
    sessionAnalytics: import("vue").Ref<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[], SessionAnalytics[] | {
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[]>;
    recentEvents: import("vue").ComputedRef<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    criticalEvents: import("vue").ComputedRef<{
        id: string;
        event_type: 'login_success' | 'login_failure' | 'password_change' | 'account_lockout' | 'oauth_login' | 'suspicious_activity';
        user_id?: string | undefined;
        username?: string | undefined;
        ip_address: string;
        user_agent?: string | undefined;
        details: Record<string, unknown>;
        severity: 'low' | 'medium' | 'high' | 'critical';
        timestamp: string;
    }[]>;
    activeAccountLockouts: import("vue").ComputedRef<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        locked_at: string;
        unlocked_at?: string | undefined;
        failed_attempts: number;
        is_active: boolean;
    }[]>;
    activeSessions: import("vue").ComputedRef<{
        id: string;
        user_id: string;
        username: string;
        ip_address: string;
        user_agent: string;
        device_type: string;
        browser: string;
        location?: string | undefined;
        login_time: string;
        last_activity: string;
        is_active: boolean;
        duration_minutes?: number | undefined;
    }[]>;
    fetchSecurityMetrics: () => Promise<void>;
    fetchSecurityEvents: (limit?: number, eventType?: string) => Promise<void>;
    fetchAccountLockouts: () => Promise<void>;
    fetchSessionAnalytics: () => Promise<void>;
    unlockAccount: (lockoutId: string) => Promise<void>;
    revokeSession: (sessionId: string) => Promise<void>;
}, "fetchSecurityMetrics" | "fetchSecurityEvents" | "fetchAccountLockouts" | "fetchSessionAnalytics" | "unlockAccount" | "revokeSession">>;
