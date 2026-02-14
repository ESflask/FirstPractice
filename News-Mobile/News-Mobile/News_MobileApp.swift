//
//  News_MobileApp.swift
//  News-Mobile
//
//  Created by 遠藤省吾 on R 8/01/31.
//

import SwiftUI

import FirebaseCore

import FirebaseAppCheck



class AppDelegate: NSObject, UIApplicationDelegate {

  func application(_ application: UIApplication,

                   didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {

    

    // デバッグ環境用のAppCheckプロバイダー設定

    #if DEBUG

    let providerFactory = AppCheckDebugProviderFactory()

    AppCheck.setAppCheckProviderFactory(providerFactory)

    #endif



    FirebaseApp.configure()



    return true

  }

}



@main
struct News_MobileApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate
    @StateObject private var authViewModel = AuthViewModel()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authViewModel)
        }
    }
}
