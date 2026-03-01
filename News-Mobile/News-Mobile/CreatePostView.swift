//
//  CreatePostView.swift
//  News-Mobile
//

import SwiftUI
import PhotosUI

struct CreatePostView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var authViewModel: AuthViewModel
    @ObservedObject var postViewModel: PostViewModel

    @State private var title = ""
    @State private var description = ""
    @State private var selectedItem: PhotosPickerItem?
    @State private var selectedImage: UIImage?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // 画像選択エリア
                    PhotosPicker(selection: $selectedItem, matching: .images) {
                        ZStack {
                            if let selectedImage = selectedImage {
                                Image(uiImage: selectedImage)
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(height: 200)
                                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                            } else {
                                VStack(spacing: 8) {
                                    Image(systemName: "photo.on.rectangle.angled")
                                        .font(.largeTitle)
                                    Text("画像を選択")
                                        .font(.subheadline)
                                }
                                .foregroundStyle(.secondary)
                                .frame(maxWidth: .infinity)
                                .frame(height: 200)
                                .glassEffect(.regular, in: .rect(cornerRadius: 16))
                            }
                        }
                    }
                    .onChange(of: selectedItem) { newItem in
                        Task {
                            if let data = try? await newItem?.loadTransferable(type: Data.self),
                               let image = UIImage(data: data) {
                                selectedImage = image
                            }
                        }
                    }

                    // 入力フィールド
                    VStack(alignment: .leading, spacing: 12) {
                        TextField("タイトル", text: $title)
                            .padding()
                            .glassEffect(.regular, in: .rect(cornerRadius: 12))

                        ZStack(alignment: .topLeading) {
                            TextEditor(text: $description)
                                .padding(8)
                                .frame(minHeight: 120)
                                .scrollContentBackground(.hidden)

                            if description.isEmpty {
                                Text("内容を入力してください...")
                                    .foregroundStyle(.secondary.opacity(0.5))
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 16)
                                    .allowsHitTesting(false)
                            }
                        }
                        .glassEffect(.regular, in: .rect(cornerRadius: 12))
                    }

                    // 投稿ボタン
                    Button {
                        Task {
                            let success = await postViewModel.createPost(
                                title: title,
                                description: description,
                                image: selectedImage,
                                user: authViewModel.user
                            )
                            if success {
                                dismiss()
                            }
                        }
                    } label: {
                        if postViewModel.isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .primary))
                                .frame(maxWidth: .infinity)
                                .padding()
                        } else {
                            Text("投稿する")
                                .fontWeight(.semibold)
                                .frame(maxWidth: .infinity)
                                .padding()
                        }
                    }
                    .glassEffect(.regular.interactive(), in: .capsule)
                    .disabled(title.isEmpty || postViewModel.isLoading)
                }
                .padding()
            }
            .scrollDismissesKeyboard(.interactively)
            .onTapGesture {
                UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
            }
            .scrollContentBackground(.hidden)
            .background(.clear)
            .navigationTitle("新規投稿")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(.hidden, for: .navigationBar)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("キャンセル") {
                        dismiss()
                    }
                }
            }
        }
    }
}
