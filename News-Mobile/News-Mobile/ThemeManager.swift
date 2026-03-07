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

enum AppLanguage: String, CaseIterable, Identifiable {
    case japanese = "ja"
    case english = "en"
    
    var id: String { self.rawValue }
    
    var displayName: String {
        switch self {
        case .japanese: return "日本語"
        case .english: return "English"
        }
    }
}

class ThemeManager: ObservableObject {
    @AppStorage("selectedThemeMode") var selectedTheme: ThemeMode = .system {
        willSet {
            objectWillChange.send()
        }
    }
    
    @AppStorage("selectedLanguage") var language: AppLanguage = .japanese {
        willSet {
            objectWillChange.send()
        }
    }

    static let shared = ThemeManager()

    private init() {}
}
