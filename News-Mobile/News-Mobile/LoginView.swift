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
            Color(.systemGroupedBackground)
                .ignoresSafeArea()

            VStack(spacing: 25) {
                Text(isSignUp ? "新規登録" : "ログイン")
                    .font(.system(size: 32, weight: .bold))
                    .padding(.bottom, 20)

                VStack(spacing: 15) {
                    TextField("メールアドレス", text: $email)
                        .padding()
                        .background(.thickMaterial)
                        .cornerRadius(12)
                        .textInputAutocapitalization(.none)
                        .keyboardType(.emailAddress)

                    SecureField("パスワード", text: $password)
                        .padding()
                        .background(.thickMaterial)
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
                            .progressViewStyle(CircularProgressViewStyle(tint: .primary))
                    } else {
                        Text(isSignUp ? "登録する" : "ログインする")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                    }
                }
                .padding()
                .background(.thickMaterial)
                .foregroundColor(.primary)
                .cornerRadius(12)
                .padding(.horizontal)

                Button {
                    isSignUp.toggle()
                } label: {
                    Text(isSignUp ? "既にアカウントをお持ちの方はこちら" : "新しくアカウントを作成する")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                }
                .padding(.horizontal)
                .padding(.vertical, 10)
            }
            .padding(30)
            .background(.regularMaterial)
            .cornerRadius(24)
            .padding()
        }
    }
}

#Preview {
    LoginView()
}
