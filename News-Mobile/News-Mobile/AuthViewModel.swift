//
//  AuthViewModel.swift
//  News-Mobile
//

import Foundation
import SwiftUI
import FirebaseAuth
import FirebaseFirestore
import Combine

@MainActor
class AuthViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var userProfile: [String: Any]?
    @Published var isEmailVerified = false

    private var authListener: AuthStateDidChangeListenerHandle?
    private let db = Firestore.firestore()

    init() {
        // 認証状態の監視
        authListener = Auth.auth().addStateDidChangeListener { [weak self] _, user in
            guard let self = self else { return }
            self.user = user
            if let user = user {
                self.isEmailVerified = user.isEmailVerified
                Task {
                    await self.fetchUserProfile(uid: user.uid)
                }
            } else {
                self.userProfile = nil
                self.isEmailVerified = false
            }
        }
    }

    func reloadUser() async {
        do {
            try await Auth.auth().currentUser?.reload()
            self.user = Auth.auth().currentUser
            self.isEmailVerified = self.user?.isEmailVerified ?? false
        } catch {
            print("Error reloading user: \(error)")
        }
    }

    func sendEmailVerification() async {
        guard let user = Auth.auth().currentUser else { return }
        isLoading = true
        errorMessage = nil
        do {
            try await user.sendEmailVerification()
        } catch {
            errorMessage = "確認メールの送信に失敗しました: \(error.localizedDescription)"
        }
        isLoading = false
    }
    
    // 再認証
    private func reauthenticate(password: String) async throws {
        guard let user = Auth.auth().currentUser, let email = user.email else {
            throw NSError(domain: "Auth", code: -1, userInfo: [NSLocalizedDescriptionKey: "ユーザーが見つかりません"])
        }
        let credential = EmailAuthProvider.credential(withEmail: email, password: password)
        try await user.reauthenticate(with: credential)
    }
    
    // メールアドレス変更 (新しいアドレスに確認メールを送信)
    func updateEmail(newEmail: String, password: String) async {
        isLoading = true
        errorMessage = nil
        do {
            try await reauthenticate(password: password)
            // Swift SDKでは async/await 向けの updateEmail(to:) を使用します
            try await Auth.auth().currentUser?.updateEmail(to: newEmail)
        } catch {
            errorMessage = "メールアドレスの変更に失敗しました: \(error.localizedDescription)"
        }
        isLoading = false
    }
    
    // アカウント削除
    func deleteAccount(password: String) async {
        isLoading = true
        errorMessage = nil
        do {
            try await reauthenticate(password: password)
            
            // Firestoreのユーザーデータも削除
            if let uid = Auth.auth().currentUser?.uid {
                try await db.collection("users").document(uid).delete()
            }
            
            try await Auth.auth().currentUser?.delete()
            self.user = nil
        } catch {
            errorMessage = "アカウントの削除に失敗しました: \(error.localizedDescription)"
        }
        isLoading = false
    }

    func fetchUserProfile(uid: String) async {
        do {
            let snapshot = try await db.collection("users").document(uid).getDocument()
            self.userProfile = snapshot.data()
        } catch {
            print("Error fetching user profile: \(error)")
        }
    }
    
    func signIn(email: String, password: String) async {
        isLoading = true
        errorMessage = nil
        do {
            try await Auth.auth().signIn(withEmail: email, password: password)
        } catch {
            errorMessage = "ログインに失敗しました: \(error.localizedDescription)"
        }
        isLoading = false
    }
    
    func signUp(email: String, password: String) async {
        isLoading = true
        errorMessage = nil
        do {
            let result = try await Auth.auth().createUser(withEmail: email, password: password)
            // 新規登録時、Firestoreに初期ドキュメントを作成 (Web版と合わせる)
            try await db.collection("users").document(result.user.uid).setData([
                "email": email,
                "created_at": FieldValue.serverTimestamp(),
                "icon": ""
            ])
        } catch {
            errorMessage = "登録に失敗しました: \(error.localizedDescription)"
        }
        isLoading = false
    }
    
    func signOut() {
        do {
            try Auth.auth().signOut()
        } catch {
            print("Error signing out: \(error)")
        }
    }
    
    func sendPasswordReset() async {
        guard let email = user?.email else { return }
        isLoading = true
        errorMessage = nil
        do {
            try await Auth.auth().sendPasswordReset(withEmail: email)
            // 成功時はerrorMessageではなく、UI側で成功メッセージを出すためのフラグを持たせることも検討できますが、
            // 今回はシンプルにエラーがなければ成功とみなします。
        } catch {
            errorMessage = "メール送信に失敗しました: \(error.localizedDescription)"
        }
        isLoading = false
    }
}
