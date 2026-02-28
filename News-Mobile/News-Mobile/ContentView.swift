//
//  ContentView.swift
//  News-Mobile
//
//  Created by 遠藤省吾 on R 8/01/31.
//

import SwiftUI
import Firebase
import FirebaseCore
import FirebaseAuth

struct ContentView: View {
    @StateObject private var newsViewModel = NewsViewModel()
    @StateObject private var postViewModel = PostViewModel()
    @EnvironmentObject var authViewModel: AuthViewModel

    var body: some View {
        Group {
            if authViewModel.user == nil {
                LoginView()
            } else {
                AppTabView(newsViewModel: newsViewModel, postViewModel: postViewModel)
            }
        }
    }
}

struct AppTabView: View {
    @ObservedObject var newsViewModel: NewsViewModel
    @ObservedObject var postViewModel: PostViewModel

    init(newsViewModel: NewsViewModel, postViewModel: PostViewModel) {
        self.newsViewModel = newsViewModel
        self.postViewModel = postViewModel

        let appearance = UITabBarAppearance()
        appearance.configureWithDefaultBackground()
        appearance.backgroundEffect = UIBlurEffect(style: .systemUltraThinMaterial)
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
    }

    var body: some View {
        TabView {
            HomeView(newsViewModel: newsViewModel, postViewModel: postViewModel)
                .tabItem {
                    Label("ホーム", systemImage: "house")
                }

            SettingsView()
                .tabItem {
                    Label("設定", systemImage: "gearshape")
                }
        }
        .accentColor(.primary)
    }
}

// 統合フィード用のアイテム定義
enum FeedItem: Identifiable {
    case article(NewsArticle)
    case post(Post)

    var id: String {
        switch self {
        case .article(let article): return article.url ?? UUID().uuidString
        case .post(let post): return post.id ?? UUID().uuidString
        }
    }

    var date: Date {
        let isoFormatter = ISO8601DateFormatter()
        switch self {
        case .article(let article):
            return isoFormatter.date(from: article.publishedAt) ?? Date.distantPast
        case .post(let post):
            return post.timestamp?.dateValue() ?? Date.distantPast
        }
    }
}

struct HomeView: View {
    @ObservedObject var newsViewModel: NewsViewModel
    @ObservedObject var postViewModel: PostViewModel

            @State private var showingCreatePost = false
            @State private var searchText = ""
            @FocusState private var isFocused: Bool

            var body: some View {
                ZStack {
                    // 背景
                    Color(.systemGroupedBackground)
                        .ignoresSafeArea()

                    VStack(spacing: 0) {
                        HeaderView()
                            .padding(.top, 8)

                        // 検索バーエリア
                        HStack(spacing: 12) {
                            HStack {
                                Image(systemName: "magnifyingglass")
                                    .foregroundColor(.secondary)

                                TextField("検索...", text: $searchText)
                                    .focused($isFocused)
                                    .submitLabel(.search)

                                if !searchText.isEmpty {
                                    Button {
                                        searchText = ""
                                    } label: {
                                        Image(systemName: "xmark.circle.fill")
                                            .foregroundColor(.secondary)
                                    }
                                }
                            }
                            .padding(10)
                            .background(.ultraThinMaterial)
                            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))

                            if isFocused {
                                Button("キャンセル") {
                                    withAnimation {
                                        searchText = ""
                                        isFocused = false
                                    }
                                }
                                .foregroundColor(.primary)
                                .transition(.move(edge: .trailing).combined(with: .opacity))
                            }
                        }
                        .padding(.horizontal)
                        .padding(.bottom, 8)
                        .animation(.spring(), value: isFocused)

                        // 統合タイムライン
                        UnifiedFeedView(
                            newsViewModel: newsViewModel,
                            postViewModel: postViewModel,
                            searchText: searchText
                        )
                    }            // 投稿ボタン (Floating Glass Action Button)
            VStack {
                Spacer()
                HStack {
                    Spacer()
                    Button {
                        showingCreatePost = true
                    } label: {
                        Image(systemName: "plus")
                            .font(.system(size: 24, weight: .semibold))
                            .foregroundColor(.primary)
                            .frame(width: 56, height: 56)
                            .background(.ultraThinMaterial)
                            .clipShape(Circle())
                            .shadow(color: .black.opacity(0.1), radius: 10)
                    }
                    .padding(.trailing, 20)
                    .padding(.bottom, 20)
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

struct UnifiedFeedView: View {
    @ObservedObject var newsViewModel: NewsViewModel
    @ObservedObject var postViewModel: PostViewModel
    var searchText: String

    var combinedFeed: [FeedItem] {
        let articles = newsViewModel.articles.map { FeedItem.article($0) }
        let posts = postViewModel.posts.map { FeedItem.post($0) }
        let allItems = (articles + posts).sorted { $0.date > $1.date }

        if searchText.isEmpty {
            return allItems
        } else {
            return allItems.filter { item in
                switch item {
                case .article(let article):
                    return article.title.localizedCaseInsensitiveContains(searchText) ||
                           (article.description?.localizedCaseInsensitiveContains(searchText) ?? false)
                case .post(let post):
                    return post.title.localizedCaseInsensitiveContains(searchText) ||
                           post.description.localizedCaseInsensitiveContains(searchText)
                }
            }
        }
    }

    var body: some View {
        if newsViewModel.isLoading && postViewModel.isLoading && combinedFeed.isEmpty {
            ProgressView()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else {
            ScrollView {
                LazyVStack(spacing: 20) {
                    ForEach(combinedFeed) { item in
                        switch item {
                        case .article(let article):
                            NewsCard(article: article)
                        case .post(let post):
                            UserPostCard(post: post)
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 10)
                .padding(.bottom, 100)
            }
            .refreshable {
                await newsViewModel.loadNews()
                await postViewModel.fetchPosts()
            }
        }
    }
}

struct SettingsView: View {
    @EnvironmentObject var authViewModel: AuthViewModel

    var body: some View {
        NavigationView {
            List {
                Section(header: Text("アカウント")) {
                    if let user = authViewModel.user {
                        HStack {
                            Text("メールアドレス")
                            Spacer()
                            Text(user.email ?? "")
                                .foregroundColor(.secondary)
                        }
                    }
                    Button("パスワード変更") {
                        // TODO: Implement
                    }
                    Button("ログアウト", role: .destructive) {
                        authViewModel.signOut()
                    }
                }

                Section(header: Text("アプリ設定")) {
                    Text("テーマ設定 (Coming Soon)")
                        .foregroundColor(.secondary)
                }

                Section(header: Text("情報")) {
                    HStack {
                        Text("バージョン")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .navigationTitle("設定")
            .listStyle(.insetGrouped)
        }
    }
}

// ユーザー投稿用のカードコンポーネント (Crystal Glass Style)
struct UserPostCard: View {
    let post: Post

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Image(systemName: "person.crop.circle.fill")
                    .font(.title3)
                    .foregroundColor(.primary)
                Text(post.user_email)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.primary)
                Spacer()
                if let timestamp = post.timestamp {
                    Text(timestamp.dateValue(), style: .date)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.secondary)
                }
            }

            if let uiImage = post.uiImage {
                Image(uiImage: uiImage)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(height: 220)
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            } else if let imageUrl = post.image, !imageUrl.isEmpty {
                let baseURL = "http://localhost:5000"
                AsyncImage(url: URL(string: baseURL + imageUrl)) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } placeholder: {
                    Rectangle()
                        .fill(.ultraThinMaterial)
                        .overlay(ProgressView())
                }
                .frame(height: 220)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            }

            VStack(alignment: .leading, spacing: 6) {
                Text(post.title)
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundColor(.primary)

                Text(post.description)
                    .font(.system(size: 14))
                    .foregroundColor(.secondary)
                    .lineLimit(3)
            }
        }
        .padding(16)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

struct HeaderView: View {
    @EnvironmentObject var authViewModel: AuthViewModel

    var body: some View {
        HStack {
            Text("News-Mobile")
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(.primary)
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
                    .foregroundColor(.primary)
                    .padding(8)
                    .background(.ultraThinMaterial)
                    .clipShape(Circle())
            }
        }
        .padding(.horizontal, 24)
        .padding(.vertical, 12)
    }
}

struct NewsCard: View {
    let article: NewsArticle

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let imageUrl = article.urlToImage, let url = URL(string: imageUrl) {
                AsyncImage(url: url, transaction: Transaction(animation: .spring())) { phase in
                    switch phase {
                    case .success(let image):
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(height: 200)
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                            .transition(.opacity.combined(with: .scale(scale: 0.95)))
                    case .failure(_):
                        Image(systemName: "photo.fill")
                            .font(.largeTitle)
                            .foregroundColor(.secondary)
                            .frame(height: 200)
                            .frame(maxWidth: .infinity)
                            .background(.ultraThinMaterial)
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    case .empty:
                        Rectangle()
                            .fill(.ultraThinMaterial)
                            .frame(height: 200)
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                            .overlay(ProgressView())
                    @unknown default:
                        EmptyView()
                    }
                }
            }

            VStack(alignment: .leading, spacing: 10) {
                Text(article.title)
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundColor(.primary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)

                if let desc = article.description {
                    Text(desc)
                        .font(.system(size: 14))
                        .foregroundColor(.secondary)
                        .lineLimit(3)
                }

                HStack {
                    Text(article.source?.name ?? "Unknown")
                        .font(.system(size: 11, weight: .bold))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(.ultraThinMaterial)
                        .clipShape(Capsule())
                        .foregroundColor(.secondary)

                    Spacer()

                    Text(formatDate(article.publishedAt))
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.secondary)
                }
                .padding(.top, 4)
            }
        }
        .padding(16)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
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
