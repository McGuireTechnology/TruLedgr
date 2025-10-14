//
//  IdentifierFirstLoginView.swift
//  TruLedgr
//
//  Created on 10/10/25.
//

import SwiftUI

struct IdentifierFirstLoginView: View {
    @StateObject private var viewModel = AuthenticationViewModel()
    @State private var showApiDialog = false
    @State private var apiUrlInput = ""
    @State private var debounceTask: Task<Void, Never>?
    @AppStorage("customApiUrl") private var customApiUrl: String?
    
    private let defaultApiUrl = "https://api.truledgr.app"
    
    private var currentApiUrl: String {
        customApiUrl ?? defaultApiUrl
    }
    
    private var displayUrl: String {
        currentApiUrl
            .replacingOccurrences(of: "https://", with: "")
            .replacingOccurrences(of: "http://", with: "")
    }
    
    private var appVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "0.1.0"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(spacing: 24) {
                    // Logo and title
                    VStack(spacing: 16) {
                        Text("🎩")
                            .font(.system(size: 72))
                        
                        Text("Log in to TruLedgr")
                            .font(.title)
                            .fontWeight(.bold)
                    }
                    .padding(.top, 60)
                    .padding(.bottom, 24)
                    
                    // Error message
                    if let error = viewModel.error {
                        HStack {
                            Text(error)
                                .font(.subheadline)
                                .foregroundStyle(.red)
                            Spacer()
                        }
                        .padding()
                        .background(Color.red.opacity(0.1))
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                    
                    // Step 1: Email identifier
                    if viewModel.step == .identifier {
                        identifierStep
                    }
                    
                    // Step 2: Login options
                    if viewModel.step == .password {
                        passwordStep
                    }
                }
                .padding(.horizontal, 24)
            }
            
            // Footer with API settings
            footer
        }
        .sheet(isPresented: $showApiDialog) {
            apiConfigurationDialog
        }
    }
    
    // MARK: - Identifier Step
    
    private var identifierStep: some View {
        VStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 8) {
                Text("Email")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                TextField("name@example.com", text: $viewModel.email)
                    .textFieldStyle(.roundedBorder)
                    .textContentType(.emailAddress)
                #if os(iOS)
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)
                    .autocorrectionDisabled(true)
                    .submitLabel(.next)
                #endif
                    .disabled(viewModel.loading)
            }
            
            Button(action: {
                Task {
                    await viewModel.handleIdentifierSubmit()
                }
            }) {
                HStack {
                    if viewModel.loading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        Text("Checking...")
                    } else {
                        Text("Next")
                    }
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 16)
                .background(viewModel.email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? Color.gray : Color.blue)
                .foregroundStyle(.white)
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .disabled(viewModel.email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || viewModel.loading)
            
            // Info message about JIT signup
            HStack(spacing: 8) {
                Image(systemName: "info.circle")
                    .font(.caption)
                
                Text("New to TruLedgr? We'll create your account automatically.")
                    .font(.caption)
            }
            .foregroundStyle(.secondary)
            .padding()
            .background(Color.secondary.opacity(0.1))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
    }
    
    // MARK: - Password Step
    
    private var passwordStep: some View {
        VStack(spacing: 20) {
            // User identifier display
            HStack {
                Text(viewModel.email)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Spacer()
                
                Button("Change") {
                    viewModel.goBackToIdentifier()
                }
                .font(.subheadline)
                .foregroundStyle(.blue)
            }
            .padding()
            .background(Color.secondary.opacity(0.1))
            .clipShape(RoundedRectangle(cornerRadius: 8))
            
            // Biometric authentication (if available)
            if viewModel.biometricAvailable {
                Button(action: {
                    Task {
                        await viewModel.handleBiometricAuth()
                    }
                }) {
                    HStack {
                        Image(systemName: viewModel.biometricType.icon)
                        Text("Sign in with \(viewModel.biometricType.displayName)")
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(Color.blue)
                    .foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }
            }
            
            // OAuth buttons
            VStack(spacing: 12) {
                oauthButton(title: "Google", action: viewModel.handleGoogleLogin)
                oauthButton(title: "Apple", action: viewModel.handleAppleLogin)
                oauthButton(title: "Microsoft", action: viewModel.handleMicrosoftLogin)
            }
            
            // OR divider
            HStack {
                Rectangle()
                    .frame(height: 1)
                    .foregroundStyle(.secondary.opacity(0.3))
                Text("OR")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Rectangle()
                    .frame(height: 1)
                    .foregroundStyle(.secondary.opacity(0.3))
            }
            
            // Password form
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text("Password")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    Spacer()
                    
                    Button(action: {
                        viewModel.showPassword.toggle()
                    }) {
                        Text(viewModel.showPassword ? "Hide" : "Show")
                            .font(.subheadline)
                            .foregroundStyle(.blue)
                    }
                }
                
                Group {
                    if viewModel.showPassword {
                        TextField("Enter your password", text: $viewModel.password)
                    } else {
                        SecureField("Enter your password", text: $viewModel.password)
                    }
                }
                .textFieldStyle(.roundedBorder)
                .textContentType(.password)
                .disabled(viewModel.loading)
                #if os(iOS)
                .submitLabel(.go)
                #endif
                
                Button("Forgot your password?") {
                    // TODO: Navigate to password reset
                }
                .font(.subheadline)
                .foregroundStyle(.blue)
                
                // Terms text
                Text("By continuing, you acknowledge that you understand and agree to our terms, privacy policy, and cookie policy.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                
                Button(action: {
                    Task {
                        await viewModel.handlePasswordSubmit()
                    }
                }) {
                    HStack {
                        if viewModel.loading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            Text("Logging in...")
                        } else {
                            Text("Log in")
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(Color.blue)
                    .foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .disabled(viewModel.loading)
            }
        }
    }
    
    // MARK: - Helper Views
    
    private func oauthButton(title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 16)
                .background(Color.clear)
                .foregroundStyle(.primary)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.secondary.opacity(0.3), lineWidth: 2)
                )
        }
        .disabled(viewModel.loading)
    }
    
    private var footer: some View {
        VStack(spacing: 8) {
            Divider()
                .padding(.horizontal, 24)
            
            Button(action: {
                apiUrlInput = customApiUrl ?? ""
                showApiDialog = true
            }) {
                HStack(spacing: 8) {
                    // Health status dot
                    Circle()
                        .fill(viewModel.healthStatus.color)
                        .frame(width: 8, height: 8)
                        .opacity(viewModel.healthStatus == .checking ? 0.5 : 1.0)
                    
                    Text(displayUrl)
                        .font(.caption2)
                }
                .foregroundStyle(.secondary)
                .padding(.vertical, 4)
            }
            
            Text("v\(appVersion)")
                .font(.caption2)
                .foregroundStyle(.secondary)
                .padding(.vertical, 4)
        }
        .padding(.bottom, 16)
    }
    
    private var apiConfigurationDialog: some View {
        NavigationStack {
            Form {
                Section {
                    Text("Default: \(defaultApiUrl)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    
                    HStack {
                        Text("Current Status:")
                            .font(.body)
                        Spacer()
                        HStack(spacing: 6) {
                            Circle()
                                .fill(viewModel.healthStatus.color)
                                .frame(width: 10, height: 10)
                            Text(viewModel.healthStatus.displayText)
                                .font(.body)
                                .foregroundStyle(viewModel.healthStatus.color)
                        }
                    }
                }
                
                Section(header: Text("Custom API URL")) {
                    #if os(iOS)
                    TextField("Custom API URL", text: $apiUrlInput)
                        .textContentType(.URL)
                        .autocapitalization(.none)
                        .autocorrectionDisabled(true)
                        .onChange(of: apiUrlInput) { oldValue, newValue in
                            checkHealthWithDebounce(for: newValue)
                        }
                    #else
                    TextField("Custom API URL", text: $apiUrlInput)
                        .onChange(of: apiUrlInput) { oldValue, newValue in
                            checkHealthWithDebounce(for: newValue)
                        }
                    #endif
                    
                    Text("Leave empty to reset to default")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("API Configuration")
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        apiUrlInput = ""
                        showApiDialog = false
                    }
                }
                
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        saveApiUrl()
                    }
                }
            }
        }
        .presentationDetents([.medium])
    }
    
    private func saveApiUrl() {
        var newUrl = apiUrlInput.trimmingCharacters(in: .whitespacesAndNewlines)
        
        if !newUrl.isEmpty &&
            !newUrl.hasPrefix("http://") &&
            !newUrl.hasPrefix("https://") {
            newUrl = "https://\(newUrl)"
        }
        
        customApiUrl = newUrl.isEmpty ? nil : newUrl
        apiUrlInput = ""
        showApiDialog = false
        
        // Restart health check with new URL
        viewModel.startHealthCheck()
    }
    
    private func checkHealthWithDebounce(for url: String) {
        // Cancel previous task
        debounceTask?.cancel()
        
        // Create new debounced task
        debounceTask = Task {
            try? await Task.sleep(nanoseconds: 500_000_000) // 500ms debounce
            
            if !Task.isCancelled {
                let urlToCheck = url.trimmingCharacters(in: .whitespacesAndNewlines)
                if urlToCheck.isEmpty {
                    await viewModel.checkHealth()
                } else {
                    var checkUrl = urlToCheck
                    if !checkUrl.hasPrefix("http://") && !checkUrl.hasPrefix("https://") {
                        checkUrl = "https://\(checkUrl)"
                    }
                    let status = await viewModel.checkHealthForUrl(checkUrl)
                    await MainActor.run {
                        viewModel.healthStatus = status
                    }
                }
            }
        }
    }
}

#Preview {
    IdentifierFirstLoginView()
}
