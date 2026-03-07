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
    
    func loadNews(query: String = "Apple", lang: String = "ja") async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil
        
        do {
            let fetchedArticles = try await newsService.fetchNews(query: query, lang: lang)
            self.articles = fetchedArticles
        } catch {
            errorMessage = "ニュースの取得に失敗しました: \(error.localizedDescription)"
            print("Error loading news: \(error)")
        }
        
        isLoading = false
    }
}
