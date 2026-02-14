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
        VStack(spacing: 0) {
            HeaderView()
            
            ZStack {
                // 背景
                LinearGradient(colors: [.blue.opacity(0.1), .purple.opacity(0.05), .white],
                               startPoint: .topLeading,
                               endPoint: .bottomTrailing)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    Picker("カテゴリ", selection: $selectedTab) {
                        Text("ニュース").tag(0)
                        Text("投稿").tag(1)
                    }
                    .pickerStyle(.segmented)
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                    
                    if selectedTab == 0 {
                        NewsListView(viewModel: newsViewModel)
                    } else {
                        PostListView(viewModel: postViewModel)
                    }
                }
                
                // 投稿ボタン
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        Button {
                            showingCreatePost = true
                        } label: {
                            Image(systemName: "plus")
                                .font(.title.bold())
                                .foregroundColor(.white)
                                .padding(16)
                                .background(Circle().fill(Color.blue))
                                .shadow(color: .black.opacity(0.15), radius: 4, x: 0, y: 2)
                        }
                        .padding(20)
                    }
                }
            }
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

struct NewsListView: View {
    @ObservedObject var viewModel: NewsViewModel
    
    var body: some View {
        if viewModel.isLoading && viewModel.articles.isEmpty {
            ProgressView()
        } else {
            ScrollView {
                LazyVStack(spacing: 16) {
                    ForEach(viewModel.articles) { article in
                        NewsCard(article: article)
                    }
                }
                .padding()
            }
            .refreshable {
                await viewModel.loadNews()
            }
        }
    }
}

struct PostListView: View {
    @ObservedObject var viewModel: PostViewModel
    
    var body: some View {
        if viewModel.isLoading && viewModel.posts.isEmpty {
            ProgressView()
        } else {
            ScrollView {
                LazyVStack(spacing: 16) {
                    ForEach(viewModel.posts) { post in
                        UserPostCard(post: post)
                    }
                }
                .padding()
            }
            .refreshable {
                await viewModel.fetchPosts()
            }
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
            
            if let uiImage = post.uiImage {
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
                .font(.system(size: 22, weight: .bold, design: .rounded))
            Spacer()
            
            Menu {
                Button(role: .destructive) {
                    authViewModel.signOut()
                } label: {
                    Label("ログアウト", systemImage: "rectangle.portrait.and.arrow.right")
                }
            } label: {
                Image(systemName: "person.circle.fill")
                    .font(.title2)
                    .foregroundColor(.blue)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.white.opacity(0.9))
        .overlay(Divider(), alignment: .bottom)
    }
}

struct NewsCard: View {
    let article: NewsArticle
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if let imageUrl = article.urlToImage, let url = URL(string: imageUrl) {
                AsyncImage(url: url, transaction: Transaction(animation: .easeInOut)) { phase in
                    switch phase {
                    case .success(let image):
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(height: 180)
                            .clipped()
                            .transition(.opacity)
                    case .failure(_):
                        Image(systemName: "photo")
                            .font(.largeTitle)
                            .foregroundColor(.gray.opacity(0.3))
                            .frame(height: 180)
                            .frame(maxWidth: .infinity)
                            .background(Color.gray.opacity(0.1))
                    case .empty:
                        Rectangle()
                            .fill(Color.gray.opacity(0.1))
                            .frame(height: 180)
                            .overlay(ProgressView())
                    @unknown default:
                        EmptyView()
                    }
                }
                .cornerRadius(12)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text(article.title)
                    .font(.headline)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                if let desc = article.description {
                    Text(desc)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .lineLimit(3)
                }
                
                HStack {
                    Text(article.source?.name ?? "Unknown")
                        .font(.caption)
                        .fontWeight(.bold)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(4)
                    
                    Spacer()
                    
                    Text(formatDate(article.publishedAt))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 4)
            }
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
