//
//  LoginView.swift
//  TruLedgr
//
//  Created by AI Assistant on 10/10/25.
//

import SwiftUI

struct LoginView: View {
    @State private var showApiDialog = false
    @State private var apiUrlInput = ""
    @AppStorage("customApiUrl") private var customApiUrl: String?
    
    private let defaultApiUrl = "https://api.truledgr.app"
    
    // Get current API URL
    private var currentApiUrl: String {
        customApiUrl ?? defaultApiUrl
    }
    
    // Display URL without protocol
    private var displayUrl: String {
        currentApiUrl
            .replacingOccurrences(of: "https://", with: "")
            .replacingOccurrences(of: "http://", with: "")
    }
    
    // Get app version from Info.plist
    private var appVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "0.1.0"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            Spacer()
            
            // Top section with logo and title
            VStack(spacing: 16) {
                Text("🎩")
                    .font(.system(size: 72))
                
                Text("TruLedgr")
                    .font(.system(size: 44, weight: .bold))
                    .foregroundStyle(.primary)
                
                Text("Personal Finance Management")
                    .font(.body)
                    .foregroundStyle(.secondary)
            }
            
            Spacer()
            
            // Middle section with login buttons
            VStack(spacing: 16) {
                // Sign Up button (primary)
                Button(action: {
                    // TODO: Navigate to signup
                }) {
                    Text("Sign Up")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(Color.blue)
                        .foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                
                // Login button (secondary)
                Button(action: {
                    // TODO: Navigate to login
                }) {
                    Text("Log In")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(Color.clear)
                        .foregroundStyle(.blue)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.blue, lineWidth: 2)
                        )
                }
                
                // OAuth section
                VStack(spacing: 16) {
                    Text("Or continue with")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    
                    HStack(spacing: 12) {
                        // Google OAuth
                        Button(action: {
                            // TODO: Google OAuth
                        }) {
                            Text("Google")
                                .font(.subheadline)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(Color.clear)
                                .foregroundStyle(.primary)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                                )
                        }
                        
                        // Apple OAuth
                        Button(action: {
                            // TODO: Apple OAuth
                        }) {
                            Text("Apple")
                                .font(.subheadline)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(Color.clear)
                                .foregroundStyle(.primary)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                                )
                        }
                        
                        // Microsoft OAuth
                        Button(action: {
                            // TODO: Microsoft OAuth
                        }) {
                            Text("Microsoft")
                                .font(.subheadline)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(Color.clear)
                                .foregroundStyle(.primary)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                                )
                        }
                    }
                }
                .padding(.top, 8)
            }
            .padding(.horizontal, 24)
            
            Spacer()
            
            // Bottom section with API settings and version
            VStack(spacing: 8) {
                Divider()
                    .padding(.horizontal, 24)
                
                // Inconspicuous API URL button
                Button(action: {
                    showApiDialog = true
                }) {
                    HStack(spacing: 8) {
                        Image(systemName: "gearshape")
                            .font(.caption2)
                        
                        Text(displayUrl)
                            .font(.caption2)
                    }
                    .foregroundStyle(.secondary)
                    .padding(.vertical, 4)
                }
                
                // Version number (separate, non-clickable)
                Text("v\(appVersion)")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .padding(.vertical, 4)
            }
            .padding(.bottom, 16)
        }
        .sheet(isPresented: $showApiDialog) {
            ApiConfigurationDialog(
                apiUrlInput: $apiUrlInput,
                customApiUrl: $customApiUrl,
                currentDisplayUrl: displayUrl,
                defaultApiUrl: defaultApiUrl
            )
        }
    }
}

struct ApiConfigurationDialog: View {
    @Environment(\.dismiss) var dismiss
    @Binding var apiUrlInput: String
    @Binding var customApiUrl: String?
    let currentDisplayUrl: String
    let defaultApiUrl: String
    
    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Text("Default: \(defaultApiUrl)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    
                    Text("Current: \(currentDisplayUrl)")
                        .font(.body)
                }
                
                Section(header: Text("Custom API URL")) {
                    #if os(iOS)
                    TextField("Custom API URL", text: $apiUrlInput)
                        .textContentType(.URL)
                        .autocapitalization(.none)
                        .autocorrectionDisabled(true)
                    #else
                    TextField("Custom API URL", text: $apiUrlInput)
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
                        dismiss()
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
        
        // Add https:// if no protocol specified
        if !newUrl.isEmpty &&
            !newUrl.hasPrefix("http://") &&
            !newUrl.hasPrefix("https://") {
            newUrl = "https://\(newUrl)"
        }
        
        // Save to UserDefaults via @AppStorage
        customApiUrl = newUrl.isEmpty ? nil : newUrl
        
        // Clear input and dismiss
        apiUrlInput = ""
        dismiss()
    }
}

#Preview {
    LoginView()
}
