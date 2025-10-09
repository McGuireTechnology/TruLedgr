//
//  ContentView.swift
//  TruLedgr
//
//  Created by Nathan McGuire on 10/9/25.
//

import SwiftUI

enum ApiStatus: Equatable {
    case notChecked
    case checking
    case up(message: String)
    case down(error: String)
}

struct ContentView: View {
    @State private var apiStatus: ApiStatus = .notChecked
    
    var body: some View {
        VStack(spacing: 20) {
            Spacer()
            
            Text("🎩 Bonjour!")
                .font(.system(size: 48, weight: .bold))
            
            Text("TruLedgr")
                .font(.title2)
                .foregroundStyle(.secondary)
            
            Spacer()
            
            // API Status Display
            VStack(spacing: 12) {
                switch apiStatus {
                case .notChecked:
                    Text("API Status: Not checked")
                        .font(.body)
                        .foregroundStyle(.secondary)
                    
                case .checking:
                    ProgressView()
                        .progressViewStyle(.circular)
                    Text("Checking API...")
                        .font(.body)
                        .foregroundStyle(.secondary)
                    
                case .up(let message):
                    Label("API is UP", systemImage: "checkmark.circle.fill")
                        .font(.title3)
                        .foregroundStyle(.green)
                    Text(message)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                    
                case .down(let error):
                    Label("API is DOWN", systemImage: "xmark.circle.fill")
                        .font(.title3)
                        .foregroundStyle(.red)
                    Text(error)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
            }
            .frame(minHeight: 100)
            
            Button(action: checkApiHealth) {
                Text("Check API Status")
                    .font(.headline)
                    .foregroundStyle(.white)
                    .padding(.horizontal, 32)
                    .padding(.vertical, 12)
                    .background(apiStatus == .checking ? Color.gray : Color.blue)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
            }
            .disabled(apiStatus == .checking)
            
            Text("API endpoint: https://api.truledgr.app/health")
                .font(.caption2)
                .foregroundStyle(.secondary)
                .padding(.top, 8)
            
            Spacer()
        }
        .padding()
    }
    
    private func checkApiHealth() {
        apiStatus = .checking
        
        guard let url = URL(string: "https://api.truledgr.app/health") else {
            print("❌ Invalid URL")
            apiStatus = .down(error: "Invalid URL")
            return
        }
        
        print("🔍 Checking API: https://api.truledgr.app/health")
        
        var request = URLRequest(url: url)
        request.timeoutInterval = 10
        request.cachePolicy = .reloadIgnoringLocalCacheData
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    let nsError = error as NSError
                    let errorMsg = "[\(nsError.domain):\(nsError.code)] \(error.localizedDescription)"
                    print("❌ API Error: \(errorMsg)")
                    apiStatus = .down(error: errorMsg)
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    print("❌ Invalid response type")
                    apiStatus = .down(error: "Invalid response")
                    return
                }
                
                print("✅ HTTP Status: \(httpResponse.statusCode)")
                
                if httpResponse.statusCode == 200, let data = data {
                    let responseString = String(data: data, encoding: .utf8) ?? ""
                    print("📡 Response: \(responseString)")
                    
                    if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                       let message = json["message"] as? String {
                        apiStatus = .up(message: message)
                    } else {
                        apiStatus = .up(message: "API is healthy")
                    }
                } else {
                    if let data = data, let errorBody = String(data: data, encoding: .utf8) {
                        print("❌ Error body: \(errorBody)")
                        apiStatus = .down(error: "HTTP \(httpResponse.statusCode): \(errorBody)")
                    } else {
                        apiStatus = .down(error: "HTTP \(httpResponse.statusCode)")
                    }
                }
            }
        }
        
        task.resume()
        print("🚀 API request started to: \(url.absoluteString)")
    }
}

#Preview {
    ContentView()
}
