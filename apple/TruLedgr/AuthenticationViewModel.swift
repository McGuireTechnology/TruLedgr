//
//  AuthenticationViewModel.swift
//  TruLedgr
//
//  Created on 10/10/25.
//

import SwiftUI
import LocalAuthentication

@MainActor
class AuthenticationViewModel: ObservableObject {
    @Published var step: AuthStep = .identifier
    @Published var email = ""
    @Published var password = ""
    @Published var showPassword = false
    @Published var error: String?
    @Published var loading = false
    @Published var biometricAvailable = false
    @Published var biometricType: BiometricType = .none
    @Published var healthStatus: HealthStatus = .unknown
    
    @AppStorage("customApiUrl") private var customApiUrl: String?
    private let defaultApiUrl = "https://api.truledgr.app"
    private var healthCheckTask: Task<Void, Never>?
    
    var currentApiUrl: String {
        customApiUrl ?? defaultApiUrl
    }
    
    enum HealthStatus {
        case healthy
        case degraded
        case unhealthy
        case checking
        case unknown
        
        var color: Color {
            switch self {
            case .healthy: return .green
            case .degraded: return .yellow
            case .unhealthy: return .red
            case .checking: return .gray
            case .unknown: return .gray
            }
        }
        
        var displayText: String {
            switch self {
            case .healthy: return "Healthy"
            case .degraded: return "Degraded"
            case .unhealthy: return "Unhealthy"
            case .checking: return "Checking..."
            case .unknown: return "Unknown"
            }
        }
    }
    
    enum AuthStep {
        case identifier
        case password
    }
    
    enum BiometricType {
        case none
        case faceID
        case touchID
        case opticID
        
        var displayName: String {
            switch self {
            case .none: return "Biometric"
            case .faceID: return "Face ID"
            case .touchID: return "Touch ID"
            case .opticID: return "Optic ID"
            }
        }
        
        var icon: String {
            switch self {
            case .none: return "person.badge.key"
            case .faceID: return "faceid"
            case .touchID: return "touchid"
            case .opticID: return "opticid"
            }
        }
    }
    
    init() {
        checkBiometricAvailability()
        startHealthCheck()
    }
    
    deinit {
        healthCheckTask?.cancel()
    }
    
    func checkBiometricAvailability() {
        let context = LAContext()
        var error: NSError?
        
        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            biometricAvailable = true
            
            switch context.biometryType {
            case .faceID:
                biometricType = .faceID
            case .touchID:
                biometricType = .touchID
            case .opticID:
                biometricType = .opticID
            default:
                biometricType = .none
                biometricAvailable = false
            }
        } else {
            biometricAvailable = false
            biometricType = .none
        }
    }
    
    func handleIdentifierSubmit() async {
        error = nil
        
        guard !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            error = "Please enter your email address"
            return
        }
        
        guard email.contains("@") else {
            error = "Please enter a valid email address"
            return
        }
        
        loading = true
        defer { loading = false }
        
        do {
            // Check if user exists
            let exists = try await checkEmailExists(email)
            
            if exists {
                // User exists - proceed to login options
                step = .password
            } else {
                // JIT signup - user doesn't exist
                // In a real app, navigate to signup
                print("JIT Signup: Redirect to signup with email: \(email)")
                // For now, just proceed to password (TODO: Implement navigation)
                step = .password
            }
        } catch {
            // On error, default to login flow
            print("Email check failed: \(error.localizedDescription)")
            step = .password
        }
    }
    
    func handlePasswordSubmit() async {
        error = nil
        
        guard !password.isEmpty else {
            error = "Please enter your password"
            return
        }
        
        loading = true
        defer { loading = false }
        
        do {
            // TODO: Implement actual login API call
            try await Task.sleep(nanoseconds: 1_000_000_000)
            print("Login successful for: \(email)")
            // Navigate to main app
        } catch {
            self.error = "Invalid email or password"
        }
    }
    
    func handleBiometricAuth() async {
        let context = LAContext()
        var error: NSError?
        
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            self.error = "Biometric authentication not available"
            return
        }
        
        do {
            let reason = "Log in to TruLedgr"
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            
            if success {
                // TODO: Retrieve and use saved credentials
                print("Biometric authentication successful")
                // Navigate to main app
            }
        } catch {
            self.error = "Biometric authentication failed"
        }
    }
    
    func handleGoogleLogin() {
        print("Google OAuth login")
        // TODO: Implement Google OAuth
    }
    
    func handleAppleLogin() {
        print("Apple OAuth login")
        // TODO: Implement Sign in with Apple
    }
    
    func handleMicrosoftLogin() {
        print("Microsoft OAuth login")
        // TODO: Implement Microsoft OAuth
    }
    
    func goBackToIdentifier() {
        step = .identifier
        password = ""
        error = nil
    }
    
    // MARK: - Health Check Methods
    
    func startHealthCheck() {
        stopHealthCheck()
        healthCheckTask = Task {
            while !Task.isCancelled {
                await checkHealth()
                try? await Task.sleep(nanoseconds: 30_000_000_000) // 30 seconds
            }
        }
    }
    
    func stopHealthCheck() {
        healthCheckTask?.cancel()
        healthCheckTask = nil
    }
    
    func checkHealth() async {
        healthStatus = .checking
        
        do {
            let status = try await performHealthCheck(url: currentApiUrl)
            healthStatus = status
        } catch {
            healthStatus = .unhealthy
        }
    }
    
    func checkHealthForUrl(_ url: String) async -> HealthStatus {
        do {
            return try await performHealthCheck(url: url)
        } catch {
            return .unhealthy
        }
    }
    
    private func performHealthCheck(url: String) async throws -> HealthStatus {
        guard let healthUrl = URL(string: "\(url)/health") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: healthUrl)
        request.httpMethod = "GET"
        request.timeoutInterval = 5
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            return .unhealthy
        }
        
        if httpResponse.statusCode == 200 {
            struct HealthResponse: Codable {
                let status: String
            }
            
            if let healthResponse = try? JSONDecoder().decode(HealthResponse.self, from: data) {
                switch healthResponse.status.lowercased() {
                case "healthy":
                    return .healthy
                case "degraded":
                    return .degraded
                default:
                    return .unhealthy
                }
            }
            return .healthy
        } else {
            return .unhealthy
        }
    }
    
    // MARK: - API Methods
    
    private func checkEmailExists(_ email: String) async throws -> Bool {
        guard let url = URL(string: "\(currentApiUrl)/auth/check-email") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 5
        
        let body = ["email": email]
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        struct CheckEmailResponse: Codable {
            let exists: Bool
            let authMethods: [String]?
            
            enum CodingKeys: String, CodingKey {
                case exists
                case authMethods = "auth_methods"
            }
        }
        
        let result = try JSONDecoder().decode(CheckEmailResponse.self, from: data)
        return result.exists
    }
}
