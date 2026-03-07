//
//  NewsService.swift
//  News-Mobile
//

import Foundation

class NewsService {
    // FlaskサーバーのベースURL (開発環境)
    // 実機テスト時はPCのIPアドレス、またはRenderなどのデプロイ済みURLに変更してください
    private let baseURL = "http://localhost:5001/api/update"
    
    func fetchNews(query: String = "Apple", lang: String = "ja") async throws -> [NewsArticle] {
        guard var components = URLComponents(string: baseURL) else {
            throw URLError(.badURL)
        }
        
        components.queryItems = [
            URLQueryItem(name: "q", value: query),
            URLQueryItem(name: "lang", value: lang)
        ]
        
        guard let url = components.url else {
            throw URLError(.badURL)
        }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            let statusCode = (response as? HTTPURLResponse)?.statusCode ?? -1
            print("Server API error: Status Code \(statusCode)")
            throw URLError(.badServerResponse)
        }
        
        // デコード処理
        return try await Task.detached(priority: .userInitiated) {
            let decoder = JSONDecoder()
            // サーバーからのレスポンスは[NewsArticle]の配列であることを想定
            let articles = try decoder.decode([NewsArticle].self, from: data)
            return articles
        }.value
    }
}
