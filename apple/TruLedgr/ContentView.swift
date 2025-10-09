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
            
            Text("API endpoint: http://localhost:8000/health")
                .font(.caption2)
                .foregroundStyle(.secondary)
                .padding(.top, 8)
            
            Spacer()
        }
        .padding()
    }
    
    private func checkApiHealth() {
        apiStatus = .checking
        
        guard let url = URL(string: "http://localhost:8000/health") else {
            apiStatus = .down(error: "Invalid URL")
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    apiStatus = .down(error: error.localizedDescription)
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    apiStatus = .down(error: "Invalid response")
                    return
                }
                
                if httpResponse.statusCode == 200, let data = data {
                    if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                       let message = json["message"] as? String {
                        apiStatus = .up(message: message)
                    } else {
                        apiStatus = .up(message: "API is healthy")
                    }
                } else {
                    apiStatus = .down(error: "HTTP \(httpResponse.statusCode)")
                }
            }
        }
        
        task.resume()
    }
}

#Preview {
    ContentView()
}
