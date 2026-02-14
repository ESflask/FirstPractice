//
//  Post.swift
//  News-Mobile
//

import Foundation
import FirebaseFirestore

struct Post: Codable, Identifiable {
    @DocumentID var id: String?
    var title: String
    var description: String
    var image: String?          // Web版のローカルパス用 (/static/...)
    var image_base64: String?   // iOS版の画像データ用
    var user_email: String
    var user_id: String?
    var timestamp: Timestamp?
    
    // UI表示用の型識別
    var isUserPost: Bool { true }
}
