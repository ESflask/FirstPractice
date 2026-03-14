//
//  NewsArticle.swift
//  News-Mobile
//

import Foundation

struct NewsArticle: Codable, Identifiable {
    var id: String { url.isEmpty ? UUID().uuidString : url }
    
    // Backend returns both English and Japanese versions
    let title_en: String?
    let title_ja: String?
    let description_en: String?
    let description_ja: String?
    
    let url: String // url should usually be there, but let's be careful
    let urlToImage: String?
    let publishedAt: String? // Make this optional just in case
    let source: String?
    let lang: String?
    
    var title: String {
        return title_ja ?? title_en ?? "No Title"
    }
    
    var description: String? {
        return description_ja ?? description_en
    }
}

// NewsResponse is not used since the API returns a direct array of articles
