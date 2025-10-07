// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "TruLedgrApple",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .executable(name: "TruLedgrApple", targets: ["TruLedgrApple"])
    ],
    targets: [
        .executableTarget(
            name: "TruLedgrApple",
            dependencies: []
        )
    ]
)