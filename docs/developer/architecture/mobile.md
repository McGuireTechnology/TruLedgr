# Mobile Applications Architecture

## iOS/macOS Application

Built with SwiftUI using Apple's Multiplatform approach, allowing code sharing between iOS and macOS.

### Technology Stack
- **SwiftUI**: Declarative UI framework
- **Swift Package Manager**: Dependency management
- **Combine**: Reactive programming
- **URLSession**: Network requests

### Project Structure
```
truledgr_apple/
├── Sources/
│   └── TruLedgrApple/
│       ├── Views/           # SwiftUI views
│       ├── Models/          # Data models
│       ├── Services/        # API services
│       ├── ViewModels/      # MVVM view models
│       └── main.swift       # App entry point
├── Package.swift            # SPM configuration
└── README.md
```

### Key Features
- Native iOS and macOS support
- SwiftUI navigation and lifecycle
- Async/await for API calls
- ObservableObject for state management

## Android Application

Built with Jetpack Compose using modern Android development practices.

### Technology Stack
- **Jetpack Compose**: Modern UI toolkit
- **Kotlin**: Primary programming language
- **Material Design 3**: Design system
- **Retrofit**: HTTP client
- **ViewModel**: MVVM architecture
- **StateFlow**: Reactive state management

### Project Structure
```
truledgr_android/
├── src/main/
│   ├── java/com/truledgr/android/
│   │   ├── ui/
│   │   │   ├── components/      # Reusable Compose components
│   │   │   ├── screens/         # Screen-level composables
│   │   │   └── theme/           # Material Design theme
│   │   ├── data/
│   │   │   ├── models/          # Data classes
│   │   │   ├── repository/      # Repository pattern
│   │   │   └── network/         # API interfaces
│   │   ├── viewmodel/           # ViewModels
│   │   └── MainActivity.kt      # Main activity
│   ├── res/                     # Resources
│   └── AndroidManifest.xml      # App manifest
├── build.gradle                 # Module build config
└── proguard-rules.pro          # ProGuard rules
```

### Key Features
- Material Design 3 theming
- Compose navigation
- Coroutines for async operations
- StateFlow for reactive UI updates
- Dependency injection (planned)

## Shared Patterns

### API Communication
Both mobile apps communicate with the same FastAPI backend:
- RESTful API calls
- JSON serialization/deserialization
- Error handling and retry logic
- Authentication token management

### Architecture Patterns
- **MVVM**: Model-View-ViewModel architecture
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: Loose coupling
- **Reactive Programming**: State management

### Data Models
Both apps use similar data structures that mirror the API models:
- Account information
- Transaction data
- User preferences
- Monthly reports

## Development

### iOS/macOS
```bash
cd truledgr_apple
swift run                    # Run on macOS
open Package.swift           # Open in Xcode
```

### Android
1. Open Android Studio
2. Open `truledgr_android` directory
3. Wait for Gradle sync
4. Run on emulator or device

## Platform-Specific Features

### iOS/macOS
- Keychain integration for secure storage
- CloudKit sync (planned)
- Shortcuts app integration (planned)
- Apple Pay integration (planned)

### Android
- Biometric authentication
- Android Auto support (planned)
- Google Pay integration (planned)
- Widgets for quick access (planned)
