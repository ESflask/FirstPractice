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
    
    private var authListener: AuthStateDidChangeListenerHandle?
    private let db = Firestore.firestore()
    
    init() {
        // 認証状態の監視
        authListener = Auth.auth().addStateDidChangeListener { [weak self] _, user in
            guard let self = self else { return }
            self.user = user
            if let user = user {
                Task {
                    await self.fetchUserProfile(uid: user.uid)
                }
            } else {
                self.userProfile = nil
            }
        }
    }
    
    deinit {
        if let listener = authListener {
            Auth.auth().removeStateDidChangeListener(listener)
        }
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
}
