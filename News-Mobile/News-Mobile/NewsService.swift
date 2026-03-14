//
//  NewsService.swift
//  News-Mobile
//

import Foundation

class NewsService {
    private let baseURL = "\(AppConfig.flaskBaseURL)/api/update"
    
    func fetchNews(query: String = "Apple", lang: String = "ja") async throws -> [NewsArticle] {
        guard var components = URLComponents(string: baseURL) else {
            print("Invalid URL")
            throw URLError(.badURL)
        }
        
        components.queryItems = [
            URLQueryItem(name: "q", value: query),
            URLQueryItem(name: "lang", value: lang)
        ]
        
        guard let url = components.url else {
            throw URLError(.badURL)
        }
        
        let request = URLRequest(url: url)
        print("Fetching news from: \(url.absoluteString)")
        
        // Timeout時間を長めに設定しておく（外部API遅延対策）
        let sessionConfig = URLSessionConfiguration.default
        sessionConfig.timeoutIntervalForRequest = 30
        let session = URLSession(configuration: sessionConfig)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            print("Invalid response type")
            throw URLError(.badServerResponse)
        }
        
        guard httpResponse.statusCode == 200 else {
            print("Server API error: Status Code \(httpResponse.statusCode)")
            if let errorBody = String(data: data, encoding: .utf8) {
                print("Error body: \(errorBody)")
            }
            throw URLError(.badServerResponse)
        }
        
        // デコード処理
        return try await Task.detached(priority: .userInitiated) {
            let decoder = JSONDecoder()
            do {
                // デバッグ用に受信したJSONを文字列として出力（必要に応じて）
                if let jsonString = String(data: data, encoding: .utf8) {
                    print("Received JSON: \(jsonString.prefix(500))...")
                }
                
                let articles = try decoder.decode([NewsArticle].self, from: data)
                print("Successfully decoded \(articles.count) articles")
                return articles
            } catch let decodingError as DecodingError {
                switch decodingError {
                case .dataCorrupted(let context):
                    print("Decoding Error (Data Corrupted): \(context)")
                case .keyNotFound(let key, let context):
                    print("Decoding Error (Key Not Found): \(key) in \(context.debugDescription)")
                case .typeMismatch(let type, let context):
                    print("Decoding Error (Type Mismatch): \(type) in \(context.debugDescription)")
                case .valueNotFound(let type, let context):
                    print("Decoding Error (Value Not Found): \(type) in \(context.debugDescription)")
                @unknown default:
                    print("Decoding Error (Unknown): \(decodingError)")
                }
                throw decodingError
            } catch {
                print("General Error during decoding: \(error)")
                throw error
            }
        }.value
    }
}
