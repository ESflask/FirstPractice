//
//  NewsArticle.swift
//  News-Mobile
//

import Foundation

struct NewsResponse: Codable {
    let status: String
    let totalResults: Int?
    let articles: [NewsArticle]
}

struct NewsArticle: Codable, Identifiable {
    var id: String { url }
    let title: String
    let description: String?
    let url: String
    let urlToImage: String?
    let publishedAt: String
    let source: NewsSource?
    
    struct NewsSource: Codable {
        let name: String?
    }
}
