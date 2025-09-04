# 🤖 TruLedgr Android

**Native Android application for the TruLedgr financial platform**

[![Kotlin](https://img.shields.io/badge/Kotlin-1.9+-7F52FF.svg?style=flat-square)](https://kotlinlang.org)
[![Android](https://img.shields.io/badge/Android-API%2024+-3DDC84.svg?style=flat-square)](https://developer.android.com)
[![Jetpack](https://img.shields.io/badge/Jetpack-Compose-4285F4.svg?style=flat-square)](https://developer.android.com/jetpack/compose)
[![Material](https://img.shields.io/badge/Material-Design%203-6200EA.svg?style=flat-square)](https://m3.material.io/)

> 📱 **Modern Android experience** with Jetpack Compose, Material Design 3, and seamless TruLedgr integration.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/mcguiretechnology/truledgr-android.git
cd truledgr-android

# Open in Android Studio
# File > Open > truledgr-android
```

**🛠️ Requirements:** Android Studio Hedgehog+, Kotlin 1.9+, Android API 24+

## ✨ Key Features

- **🏦 Secure Banking** with Plaid integration and biometric authentication
- **📊 Real-Time Data** synced with TruLedgr API using Retrofit and Coroutines
- **🎨 Material Design 3** with dynamic theming and TruLedgr brand colors
- **📲 Android Features** including App Widgets, Shortcuts, and Notifications
- **🔐 Biometric Auth** with fingerprint and face unlock support
- **🌙 Adaptive UI** with automatic dark/light theme switching

## 🏗️ Tech Stack

- **Language:** Kotlin with Coroutines for async programming
- **UI Framework:** Jetpack Compose with Material Design 3
- **Architecture:** MVVM with Repository pattern and Clean Architecture
- **Networking:** Retrofit with OkHttp for API communication
- **Database:** Room for local data storage with offline support
- **DI:** Hilt for dependency injection
- **Security:** Android Keystore for secure credential storage

## 📱 Android Features

- **📊 Dashboard** with account overview and transaction management
- **📈 Analytics** with spending insights and budget tracking
- **🔔 Push Notifications** for transaction alerts and important updates
- **📲 App Widgets** for home screen balance and quick actions
- **🔗 App Shortcuts** for frequent actions from launcher
- **📤 Sharing** integration for transaction exports and reports
- **♿ Accessibility** full TalkBack and large text support

## 🔧 Development

```bash
# Build debug APK
./gradlew assembleDebug

# Run tests
./gradlew test

# Run instrumented tests
./gradlew connectedAndroidTest

# Generate release APK
./gradlew assembleRelease
```

## 🧪 Testing

- **Unit Tests** with JUnit and MockK
- **UI Tests** with Espresso and Compose Testing
- **Integration Tests** with Android Test framework
- **Screenshot Tests** for UI regression testing

## 🏗️ Architecture

Modern Android development patterns:

- **MVVM Architecture** with ViewModels and LiveData/StateFlow
- **Repository Pattern** for data layer abstraction
- **Clean Architecture** with clear separation of concerns
- **Dependency Injection** with Hilt for testability
- **Reactive Programming** with Kotlin Coroutines and Flow

## 🎨 Design System

Implements TruLedgr brand within Material Design 3:

- **🎨 Brand Colors** adapted to Material You color system
- **📝 Typography** using Material Design type scale
- **🎭 Theming** with dynamic colors and brand consistency
- **📱 Components** custom components following Material guidelines

## 📖 Documentation

- **[Development Guide](./docs/development.md)** - Setup and contribution guide
- **[Architecture](./docs/architecture.md)** - App structure and patterns
- **[Design System](./docs/design-system.md)** - Android-specific design guidelines
- **[API Integration](./docs/api-integration.md)** - TruLedgr API client documentation

## 🔒 Security & Privacy

- **🔐 Biometric Auth** - Fingerprint and face authentication
- **🛡️ Android Keystore** - Hardware-backed security for credentials
- **📊 Local Encryption** - All financial data encrypted at rest
- **🔒 Network Security** - Certificate pinning and secure communication
- **🕵️ Privacy Controls** - Granular permissions and data controls

---

**Part of the [TruLedgr Platform](https://github.com/mcguiretechnology/truledgr) | Built by [McGuire Technology](https://mcguire.technology)**
