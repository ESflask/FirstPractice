import SwiftUI
import Combine

enum ThemeMode: String, CaseIterable, Identifiable {
    case light = "Light"
    case dark = "Dark"
    case system = "System"

    var id: String { self.rawValue }

    var colorScheme: ColorScheme? {
        switch self {
        case .light: return .light
        case .dark: return .dark
        case .system: return nil
        }
    }
}

class ThemeManager: ObservableObject {
    @AppStorage("selectedThemeMode") var selectedTheme: ThemeMode = .system {
        willSet {
            objectWillChange.send()
        }
    }

    static let shared = ThemeManager()

    private init() {}
}
