//
//  NewsViewModel.swift
//  News-Mobile
//

import Foundation
import SwiftUI
import Combine

@MainActor
class NewsViewModel: ObservableObject {
    @Published var articles: [NewsArticle] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let newsService = NewsService()
    
    func loadNews(query: String = "Apple") async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil
        
        // 取得処理自体は非同期で行われるが、明示的にバックグラウンド優先度を意識
        let task = Task(priority: .userInitiated) {
            do {
                return try await newsService.fetchNews(query: query)
            } catch {
                throw error
            }
        }
        
        do {
            let fetchedArticles = try await task.value
            self.articles = fetchedArticles
        } catch {
            errorMessage = "ニュースの取得に失敗しました: \(error.localizedDescription)"
            print("Error loading news: \(error)")
        }
        
        isLoading = false
    }
}
