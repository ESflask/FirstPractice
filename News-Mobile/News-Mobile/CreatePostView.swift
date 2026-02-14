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
        NavigationView {
            ZStack {
                LinearGradient(colors: [.blue.opacity(0.1), .white],
                               startPoint: .topLeading,
                               endPoint: .bottomTrailing)
                    .ignoresSafeArea()
                
                VStack(spacing: 20) {
                    // 画像選択エリア
                    PhotosPicker(selection: $selectedItem, matching: .images) {
                        ZStack {
                            if let selectedImage = selectedImage {
                                Image(uiImage: selectedImage)
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(height: 200)
                                    .cornerRadius(12)
                            } else {
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(.ultraThinMaterial)
                                    .frame(height: 200)
                                    .overlay(
                                        VStack {
                                            Image(systemName: "photo.on.rectangle.angled")
                                                .font(.largeTitle)
                                            Text("画像を選択")
                                        }
                                        .foregroundColor(.secondary)
                                    )
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
                    
                    VStack(alignment: .leading, spacing: 8) {
                        TextField("タイトル", text: $title)
                            .padding()
                            .background(.ultraThinMaterial)
                            .cornerRadius(10)
                        
                        TextEditor(text: $description)
                            .padding(8)
                            .frame(minHeight: 120)
                            .background(.ultraThinMaterial)
                            .cornerRadius(10)
                            .overlay(
                                Group {
                                    if description.isEmpty {
                                        Text("内容を入力してください...")
                                            .foregroundColor(.secondary.opacity(0.5))
                                            .padding(.horizontal, 12)
                                            .padding(.vertical, 16)
                                    }
                                },
                                alignment: .topLeading
                            )
                    }
                    
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
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text("投稿する")
                                .fontWeight(.bold)
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .padding()
                    .background(title.isEmpty ? Color.gray : Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
                    .disabled(title.isEmpty || postViewModel.isLoading)
                    
                    Spacer()
                }
                .padding()
            }
            .navigationTitle("新規投稿")
            .navigationBarTitleDisplayMode(.inline)
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
