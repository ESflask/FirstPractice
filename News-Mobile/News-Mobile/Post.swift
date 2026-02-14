//
//  Post.swift
//  News-Mobile
//

import Foundation
import FirebaseFirestore
import UIKit

struct Post: Codable, Identifiable {
    @DocumentID var id: String?
    var title: String
    var description: String
    var image: String?          // Web版のローカルパス用 (/static/...)
    var image_base64: String?   // iOS版の画像データ用
    var user_email: String
    var user_id: String?
    var timestamp: Timestamp?
    
    // UI表示用にデコード済みの画像を保持 (Codableからは除外)
    var uiImage: UIImage? = nil
    
    enum CodingKeys: String, CodingKey {
        case id, title, description, image, image_base64, user_email, user_id, timestamp
    }
    
    // UI表示用の型識別
    var isUserPost: Bool { true }
}
