//
//  ContentView.swift
//  News-Mobile
//
//  Created by 遠藤省吾 on R 8/01/31.
//

import SwiftUI
import Firebase
import FirebaseCore

struct ContentView: View {
    @StateObject private var newsViewModel = NewsViewModel()
    @StateObject private var postViewModel = PostViewModel()
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        Group {
            if authViewModel.user == nil {
                LoginView()
            } else {
                MainFeedView(newsViewModel: newsViewModel, postViewModel: postViewModel)
            }
        }
    }
}

struct MainFeedView: View {
    @ObservedObject var newsViewModel: NewsViewModel
    @ObservedObject var postViewModel: PostViewModel
    @EnvironmentObject var authViewModel: AuthViewModel
    
    @State private var selectedTab = 0
    @State private var showingCreatePost = false
    
    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            // 背景のグラデーション
            LinearGradient(colors: [.blue.opacity(0.2), .purple.opacity(0.1), .white],
                           startPoint: .topLeading,
                           endPoint: .bottomTrailing)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                HeaderView()
                
                // タブセレクター
                Picker("Tab", selection: $selectedTab) {
                    Text("ニュース").tag(0)
                    Text("投稿").tag(1)
                }
                .pickerStyle(.segmented)
                .padding()
                
                if selectedTab == 0 {
                    // ニュースフィード
                    if newsViewModel.isLoading {
                        ProgressView().frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else {
                        ScrollView {
                            LazyVStack(spacing: 16) {
                                ForEach(newsViewModel.articles) { article in
                                    NewsCard(article: article)
                                }
                            }
                            .padding()
                        }
                    }
                } else {
                    // ユーザー投稿フィード
                    if postViewModel.isLoading && postViewModel.posts.isEmpty {
                        ProgressView().frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else {
                        ScrollView {
                            LazyVStack(spacing: 16) {
                                ForEach(postViewModel.posts) { post in
                                    UserPostCard(post: post)
                                }
                            }
                            .padding()
                        }
                        .refreshable {
                            await postViewModel.fetchPosts()
                        }
                    }
                }
            }
            
            // 新規投稿ボタン (Floating Action Button)
            Button {
                showingCreatePost = true
            } label: {
                Image(systemName: "plus")
                    .font(.title.bold())
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.blue)
                    .clipShape(Circle())
                    .shadow(radius: 5)
            }
            .padding(24)
        }
        .task {
            if newsViewModel.articles.isEmpty {
                await newsViewModel.loadNews()
            }
            if postViewModel.posts.isEmpty {
                await postViewModel.fetchPosts()
            }
        }
        .sheet(isPresented: $showingCreatePost) {
            CreatePostView(postViewModel: postViewModel)
        }
    }
}

// ユーザー投稿用のカードコンポーネント
struct UserPostCard: View {
    let post: Post
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "person.circle.fill")
                    .foregroundColor(.blue)
                Text(post.user_email)
                    .font(.caption)
                    .fontWeight(.bold)
                Spacer()
                if let timestamp = post.timestamp {
                    Text(timestamp.dateValue(), style: .date)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            if let imageBase64 = post.image_base64,
               let data = Data(base64Encoded: imageBase64),
               let uiImage = UIImage(data: data) {
                Image(uiImage: uiImage)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(height: 200)
                    .clipped()
                    .cornerRadius(12)
            } else if let imageUrl = post.image, !imageUrl.isEmpty {
                // FIXME: Flaskサーバーの実際のURLに置き換えてください (例: https://your-app.render.com)
                let baseURL = "http://localhost:5000" 
                AsyncImage(url: URL(string: baseURL + imageUrl)) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } placeholder: {
                    Rectangle()
                        .fill(Color.gray.opacity(0.1))
                        .overlay(ProgressView())
                }
                .frame(height: 200)
                .clipped()
                .cornerRadius(12)
            }
            
            Text(post.title)
                .font(.headline)
            
            Text(post.description)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .lineLimit(3)
        }
        .padding()
        .background(.ultraThinMaterial)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.white.opacity(0.4), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.05), radius: 8, x: 0, y: 4)
    }
}

struct HeaderView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        HStack {
            Text("News-Mobile")
                .font(.system(size: 24, weight: .bold, design: .rounded))
            Spacer()
            
            Menu {
                Button(role: .destructive) {
                    authViewModel.signOut()
                } label: {
                    Label("ログアウト", systemImage: "rectangle.portrait.and.arrow.right")
                }
            } label: {
                Image(systemName: "person.circle")
                    .font(.title2)
                    .foregroundColor(.primary)
            }
        }
        .padding()
        .background(.ultraThinMaterial)
    }
}

struct NewsCard: View {
    let article: NewsArticle
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if let imageUrl = article.urlToImage, let url = URL(string: imageUrl) {
                AsyncImage(url: url) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(height: 180)
                        .clipped()
                        .cornerRadius(12)
                } placeholder: {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 180)
                        .cornerRadius(12)
                }
            }
            
            Text(article.title)
                .font(.headline)
                .lineLimit(2)
            
            if let desc = article.description {
                Text(desc)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(3)
            }
            
            HStack {
                Text(article.source?.name ?? "Unknown Source")
                    .font(.caption)
                    .fontWeight(.bold)
                Spacer()
                Text(formatDate(article.publishedAt))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(.ultraThinMaterial) // Liquid Glass 効果
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.white.opacity(0.4), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.1), radius: 10, x: 0, y: 5)
    }
    
    func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        guard let date = formatter.date(from: dateString) else { return dateString }
        
        let displayFormatter = DateFormatter()
        displayFormatter.dateStyle = .medium
        displayFormatter.timeStyle = .short
        return displayFormatter.string(from: date)
    }
}

#Preview {
    ContentView()
}
