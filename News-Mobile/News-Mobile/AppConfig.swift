//
//  AppConfig.swift
//  News-Mobile
//

import Foundation

enum AppConfig {
    /// FlaskサーバーのベースURL
    /// 実機テスト時はMacのローカルIPアドレスに合わせて変更してください。
    #if DEBUG
    static let flaskBaseURL = "http://172.20.10.2:5001"
    #else
    static let flaskBaseURL = "https://your-production-server.com"
    #endif
}
