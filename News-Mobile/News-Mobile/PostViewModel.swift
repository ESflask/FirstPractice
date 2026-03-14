//
//  PostViewModel.swift
//  News-Mobile
//

import Foundation
import SwiftUI
import FirebaseFirestore
import UIKit
import Combine
import FirebaseAuth

@MainActor
class PostViewModel: ObservableObject {
    @Published var posts: [Post] = []
    @Published var isLoading = false

    private let db = Firestore.firestore()

    func fetchPosts() async {
        isLoading = true
        do {
            let snapshot = try await db.collection("posts")
                .order(by: "timestamp", descending: true)
                .getDocuments()

            // Base64デコードはメインスレッドをブロックしないようバックグラウンドで実行
            let decodedPosts: [Post] = await Task.detached(priority: .userInitiated) {
                var result: [Post] = []
                for doc in snapshot.documents {
                    guard var post = try? doc.data(as: Post.self) else { continue }
                    if let base64 = post.image_base64,
                       let data = Data(base64Encoded: base64) {
                        post.uiImage = UIImage(data: data)
                    }
                    result.append(post)
                }
                return result
            }.value

            self.posts = decodedPosts
        } catch {
            print("Error fetching posts: \(error)")
        }
        isLoading = false
    }

    func createPost(title: String, description: String, image: UIImage?, user: User?) async -> Bool {
        guard let user = user else { return false }
        isLoading = true

        var base64String: String? = nil
        if let image = image {
            // Firestoreの1MB制限を考慮してリサイズと圧縮を行う
            if let resizedImage = image.resized(to: CGSize(width: 800, height: 800)),
               let imageData = resizedImage.jpegData(compressionQuality: 0.5) {
                base64String = imageData.base64EncodedString()
            }
        }

        let newPost = [
            "title": title,
            "description": description,
            "image_base64": base64String as Any,
            "user_email": user.email ?? "",
            "user_id": user.uid,
            "timestamp": FieldValue.serverTimestamp()
        ] as [String : Any]

        do {
            try await db.collection("posts").addDocument(data: newPost)
            await fetchPosts() // 投稿後に再取得
            isLoading = false
            return true
        } catch {
            print("Error creating post: \(error)")
            isLoading = false
            return false
        }
    }
}

// UIImageのリサイズ用拡張
extension UIImage {
    func resized(to targetSize: CGSize) -> UIImage? {
        let widthRatio  = targetSize.width  / size.width
        let heightRatio = targetSize.height / size.height

        // アスペクト比を維持してリサイズ（Aspect Fit）
        // 元の画像より大きくならないように scaleFactor は最大 1.0
        let scaleFactor = min(min(widthRatio, heightRatio), 1.0)

        // 新しいサイズを計算
        let newSize = CGSize(width: size.width * scaleFactor, height: size.height * scaleFactor)

        UIGraphicsBeginImageContextWithOptions(newSize, false, 0.0)
        draw(in: CGRect(origin: .zero, size: newSize))
        let resizedImage = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext()
        return resizedImage
    }
}
