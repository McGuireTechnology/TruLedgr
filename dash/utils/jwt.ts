/**
 * JWT utility functions
 */

export interface JWTPayload {
  sub: string
  exp: number
  iat: number
  [key: string]: any
}

/**
 * Decode a JWT token without verification
 * @param token The JWT token to decode
 * @returns The decoded payload or null if invalid
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) {
      return null
    }

    const payload = parts[1]
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decoded)
  } catch (error) {
    console.error('Failed to decode JWT:', error)
    return null
  }
}

/**
 * Check if a JWT token is expired
 * @param token The JWT token to check
 * @returns True if the token is expired, false otherwise
 */
export function isTokenExpired(token: string): boolean {
  const payload = decodeJWT(token)
  if (!payload || !payload.exp) {
    return true
  }

  const now = Math.floor(Date.now() / 1000)
  return payload.exp < now
}

/**
 * Get the expiration time of a JWT token
 * @param token The JWT token
 * @returns The expiration date or null if invalid
 */
export function getTokenExpiration(token: string): Date | null {
  const payload = decodeJWT(token)
  if (!payload || !payload.exp) {
    return null
  }

  return new Date(payload.exp * 1000)
}
