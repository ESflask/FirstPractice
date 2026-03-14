import Foundation

struct NewsArticle: Codable, Identifiable {
    var id: String { url.isEmpty ? UUID().uuidString : url }
    
    let title_en: String?
    let title_ja: String?
    let description_en: String?
    let description_ja: String?
    
    let url: String 
    let urlToImage: String?
    let publishedAt: String? 
    let source: String?
    let lang: String?
}

let jsonString = """
[
    {
        "description_en": "When I hear \\"AI gadget\\", I can't help...",
        "description_ja": "AIガジェット...",
        "lang": "en",
        "publishedAt": "2026-03-01T04:00:00Z",
        "source": "ギズモード・ジャパン",
        "title_en": "Why I'm Not Getting My Hopes Up",
        "title_ja": "Appleが開発中...",
        "url": "https://www.gizmodo.jp/2026/",
        "urlToImage": "https://media.loom-app.com/"
    }
]
"""

do {
    let data = jsonString.data(using: .utf8)!
    let decoder = JSONDecoder()
    let articles = try decoder.decode([NewsArticle].self, from: data)
    print("Success! Decoded \(articles.count) articles.")
    print("Article 1 URL: \(articles[0].url)")
} catch {
    print("Error decoding: \\(error)")
}
