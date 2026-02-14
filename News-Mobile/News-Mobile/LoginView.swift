//
//  LoginView.swift
//  News-Mobile
//

import SwiftUI

struct LoginView: View {
    @StateObject private var viewModel = AuthViewModel()
    @State private var email = ""
    @State private var password = ""
    @State private var isSignUp = false
    
    var body: some View {
        ZStack {
            // 背景
            LinearGradient(colors: [.purple.opacity(0.3), .blue.opacity(0.3)],
                           startPoint: .topLeading,
                           endPoint: .bottomTrailing)
                .ignoresSafeArea()
            
            VStack(spacing: 25) {
                Text(isSignUp ? "新規登録" : "ログイン")
                    .font(.system(size: 32, weight: .bold, design: .rounded))
                    .padding(.bottom, 20)
                
                VStack(spacing: 15) {
                    TextField("メールアドレス", text: $email)
                        .padding()
                        .background(.ultraThinMaterial)
                        .cornerRadius(12)
                        .textInputAutocapitalization(.none)
                        .keyboardType(.emailAddress)
                    
                    SecureField("パスワード", text: $password)
                        .padding()
                        .background(.ultraThinMaterial)
                        .cornerRadius(12)
                }
                .padding(.horizontal)
                
                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }
                
                Button {
                    Task {
                        if isSignUp {
                            await viewModel.signUp(email: email, password: password)
                        } else {
                            await viewModel.signIn(email: email, password: password)
                        }
                    }
                } label: {
                    if viewModel.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text(isSignUp ? "登録する" : "ログインする")
                            .fontWeight(.bold)
                            .frame(maxWidth: .infinity)
                    }
                }
                .padding()
                .background(Color.blue.opacity(0.7))
                .foregroundColor(.white)
                .cornerRadius(12)
                .padding(.horizontal)
                
                Button {
                    isSignUp.toggle()
                } label: {
                    Text(isSignUp ? "既にアカウントをお持ちの方はこちら" : "新しくアカウントを作成する")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                }
            }
            .padding(30)
            .background(.ultraThinMaterial)
            .cornerRadius(24)
            .overlay(
                RoundedRectangle(cornerRadius: 24)
                    .stroke(Color.white.opacity(0.4), lineWidth: 1)
            )
            .padding()
        }
    }
}

#Preview {
    LoginView()
}
