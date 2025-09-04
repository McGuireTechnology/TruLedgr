# 🍎 TruLedgr Apple

**Native iOS and macOS applications for the TruLedgr financial platform**

[![Swift](https://img.shields.io/badge/Swift-5.9+-FA7343.svg?style=flat-square)](https://swift.org)
[![iOS](https://img.shields.io/badge/iOS-17.0+-000000.svg?style=flat-square)](https://developer.apple.com/ios/)
[![macOS](https://img.shields.io/badge/macOS-14.0+-000000.svg?style=flat-square)](https://developer.apple.com/macos/)
[![SwiftUI](https://img.shields.io/badge/SwiftUI-5.0+-007AFF.svg?style=flat-square)](https://developer.apple.com/swiftui/)

> 📱 **Native Apple experiences** with SwiftUI, Combine, and deep iOS/macOS integration.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/mcguiretechnology/truledgr-apple.git
cd truledgr-apple

# Open in Xcode
open TruLedgr.xcodeproj
```

**🛠️ Requirements:** Xcode 15.0+, iOS 17.0+, macOS 14.0+

## ✨ Key Features

- **🏦 Native Banking** with Plaid integration and secure account linking
- **📊 Real-Time Sync** with the TruLedgr API using Combine framework
- **🔐 Biometric Auth** with Face ID, Touch ID, and Keychain integration
- **📱 iOS Features** including Widgets, Shortcuts, and Siri integration
- **💻 macOS Features** with Menu Bar app and Notification Center widgets
- **🌙 Platform Design** following Apple's Human Interface Guidelines

## 🏗️ Tech Stack

- **Language:** Swift 5.9+ with modern concurrency
- **UI Framework:** SwiftUI with UIKit bridging where needed
- **Architecture:** MVVM with Combine for reactive programming
- **Networking:** URLSession with async/await and custom API client
- **Storage:** Core Data with CloudKit sync for cross-device data
- **Security:** Keychain Services for secure credential storage

## 📱 Target Platforms

### iOS App Features
- **📊 Dashboard** with account overview and transaction history
- **📈 Analytics** with spending insights and budget tracking
- **🔔 Notifications** for transaction alerts and budget updates
- **📲 Widgets** for home screen balance and recent transactions
- **🗣️ Siri Shortcuts** for quick balance checks and payments

### macOS App Features
- **📊 Full Dashboard** with multi-window support
- **📋 Menu Bar** quick access to balances and recent activity
- **🖥️ Desktop Widgets** for Notification Center integration
- **⌨️ Keyboard Shortcuts** for power user workflows

## 🔧 Development

```bash
# Install dependencies (if using Swift Package Manager)
# Dependencies are managed in Xcode

# Run tests
cmd+U in Xcode

# Build for device
cmd+R in Xcode

# Archive for distribution
Product > Archive in Xcode
```

## 🧪 Testing

- **Unit Tests** with XCTest framework
- **UI Tests** with XCUITest for automation
- **Snapshot Tests** for UI regression testing
- **Performance Tests** for API and Core Data operations

## 🚀 Architecture

Built with modern Swift patterns:

- **MVVM Architecture** with ObservableObject view models
- **Combine Framework** for reactive data flow
- **Async/Await** for modern concurrency
- **Swift Packages** for modular code organization
- **Protocol-Oriented** design for testability

## 📖 Documentation

- **[Development Guide](./docs/development.md)** - Setup and contribution guide
- **[Architecture](./docs/architecture.md)** - App structure and patterns
- **[Design System](./docs/design-system.md)** - iOS/macOS specific design guidelines
- **[API Integration](./docs/api-integration.md)** - TruLedgr API client documentation

## 🔒 Privacy & Security

- **📊 Privacy First** - All financial data encrypted locally
- **🔐 Biometric Auth** - Face ID/Touch ID for app access
- **🛡️ Keychain** - Secure credential storage
- **🔒 Network Security** - Certificate pinning and request signing

---

**Part of the [TruLedgr Platform](https://github.com/mcguiretechnology/truledgr) | Built by [McGuire Technology](https://mcguire.technology)**
