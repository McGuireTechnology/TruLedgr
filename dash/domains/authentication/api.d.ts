export interface LoginCredentials {
    username: string;
    password: string;
}
export interface LoginResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
    user: {
        id: string;
        username: string;
        email: string;
    };
    session_id: string;
    totp_enabled: boolean;
}
export interface AuthUser {
    id: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
    is_active: boolean;
    is_verified: boolean;
    email_verified: boolean;
    last_login?: string;
    created_at?: string;
    role_id?: string;
}
export declare const authApi: {
    login: (credentials: LoginCredentials) => Promise<LoginResponse>;
    logout: (allSessions?: boolean) => Promise<void>;
    me: () => Promise<AuthUser>;
    refresh: () => Promise<LoginResponse>;
    register: (userData: {
        username: string;
        email: string;
        password: string;
        first_name?: string;
        last_name?: string;
    }) => Promise<{
        message: string;
        user_id: string;
    }>;
};
