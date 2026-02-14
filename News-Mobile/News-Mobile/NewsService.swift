//
//  NewsService.swift
//  News-Mobile
//

import Foundation

class NewsService {
    // FIXME: 自身のNews APIキーを設定してください
    private let apiKey = "eec9d227dcdf47b9bfa9b53a9f8d4042"
    private let baseURL = "https://newsapi.org/v2/everything"
    
    func fetchNews(query: String = "Apple") async throws -> [NewsArticle] {
        guard var components = URLComponents(string: baseURL) else {
            throw URLError(.badURL)
        }
        
        components.queryItems = [
            URLQueryItem(name: "q", value: query),
            URLQueryItem(name: "sortBy", value: "publishedAt"),
            URLQueryItem(name: "pageSize", value: "20"),
            URLQueryItem(name: "apiKey", value: apiKey)
        ]
        
        guard let url = components.url else {
            throw URLError(.badURL)
        }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            let statusCode = (response as? HTTPURLResponse)?.statusCode ?? -1
            print("News API error: Status Code \(statusCode)")
            throw URLError(.badServerResponse)
        }
        
        // デコード処理をバックグラウンドスレッドで実行
        return try await Task.detached(priority: .userInitiated) {
            let decoder = JSONDecoder()
            let result = try decoder.decode(NewsResponse.self, from: data)
            return result.articles
        }.value
    }
}
