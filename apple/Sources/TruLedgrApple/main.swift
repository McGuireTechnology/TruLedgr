import SwiftUI

@main
struct TruLedgrApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowResizability(.contentSize)
    }
}

struct ContentView: View {
    @State private var apiMessage = ""
    @State private var isLoading = false
    @State private var showError = false
    
    var body: some View {
        VStack(spacing: 30) {
            VStack(spacing: 10) {
                Text("TruLedgr")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
                
                Text("Bonjour!")
                    .font(.title)
                    .foregroundColor(.blue)
                
                Text("Personal Finance Application Suite")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            VStack(spacing: 15) {
                Button(action: testApiConnection) {
                    HStack {
                        if isLoading {
                            ProgressView()
                                .scaleEffect(0.8)
                        }
                        Text(isLoading ? "Testing..." : "Test API Connection")
                    }
                    .frame(minWidth: 200)
                }
                .disabled(isLoading)
                .buttonStyle(.borderedProminent)
                
                if !apiMessage.isEmpty {
                    Text(apiMessage)
                        .font(.body)
                        .foregroundColor(showError ? .red : .green)
                        .multilineTextAlignment(.center)
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(showError ? Color.red.opacity(0.1) : Color.green.opacity(0.1))
                        )
                }
            }
        }
        .padding(40)
        .frame(minWidth: 400, minHeight: 300)
    }
    
    private func testApiConnection() {
        isLoading = true
        apiMessage = ""
        showError = false
        
        guard let url = URL(string: "http://localhost:8000/") else {
            showApiError("Invalid API URL")
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    showApiError("Connection failed: \(error.localizedDescription)")
                    return
                }
                
                guard let data = data else {
                    showApiError("No data received from API")
                    return
                }
                
                do {
                    if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                       let message = json["message"] as? String {
                        apiMessage = message
                        showError = false
                    } else {
                        showApiError("Invalid response format")
                    }
                } catch {
                    showApiError("Failed to parse response")
                }
            }
        }.resume()
    }
    
    private func showApiError(_ message: String) {
        apiMessage = "\(message)\n\nMake sure the backend is running on port 8000"
        showError = true
        isLoading = false
    }
}

#Preview {
    ContentView()
}