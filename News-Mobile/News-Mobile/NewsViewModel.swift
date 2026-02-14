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
        isLoading = true
        errorMessage = nil
        
        do {
            articles = try await newsService.fetchNews(query: query)
        } catch {
            errorMessage = "ニュースの取得に失敗しました: \(error.localizedDescription)"
            print("Error loading news: \(error)")
        }
        
        isLoading = false
    }
}
