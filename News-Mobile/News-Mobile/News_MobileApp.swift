//
//  News_MobileApp.swift
//  News-Mobile
//
//  Created by 遠藤省吾 on R 8/01/31.
//

import SwiftUI
import Combine
import FirebaseCore





class AppDelegate: NSObject, UIApplicationDelegate {

  func application(_ application: UIApplication,

                   didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {

    FirebaseApp.configure()



    return true

  }

}





@main
struct News_MobileApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate
    @StateObject private var authViewModel = AuthViewModel()
    @StateObject private var themeManager = ThemeManager.shared
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authViewModel)
                .environmentObject(themeManager)
                .preferredColorScheme(themeManager.selectedTheme.colorScheme)
        }
    }
}
