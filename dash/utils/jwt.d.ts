/**
 * JWT utility functions
 */
export interface JWTPayload {
    sub: string;
    exp: number;
    iat: number;
    [key: string]: any;
}
/**
 * Decode a JWT token without verification
 * @param token The JWT token to decode
 * @returns The decoded payload or null if invalid
 */
export declare function decodeJWT(token: string): JWTPayload | null;
/**
 * Check if a JWT token is expired
 * @param token The JWT token to check
 * @returns True if the token is expired, false otherwise
 */
export declare function isTokenExpired(token: string): boolean;
/**
 * Get the expiration time of a JWT token
 * @param token The JWT token
 * @returns The expiration date or null if invalid
 */
export declare function getTokenExpiration(token: string): Date | null;
