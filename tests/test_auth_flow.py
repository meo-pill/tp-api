# test_auth_flow.py

import requests

BASE_URL = "http://localhost:8000"

def test_complete_auth_flow():
    """Test du flow complet : register → login → refresh → logout"""
    
    print("=" * 70)
    print("TEST DU FLOW D'AUTHENTIFICATION")
    print("=" * 70)
    
    # 1. Register
    print("\n1️⃣ Register...")
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "testflow@example.com",
        "username": "testflow",
        "password": "SecurePass123",
        "full_name": "Test Flow"
    })
    print(f"   Status: {response.status_code}")
    assert response.status_code == 201
    print(f"   ✅ Utilisateur créé : {response.json()['username']}")
    
    # 2. Login
    print("\n2️⃣ Login...")
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": "testflow",
        "password": "SecurePass123"
    })
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    print(f"   ✅ Access token : {access_token[:30]}...")
    print(f"   ✅ Refresh token: {refresh_token[:30]}...")
    
    # 3. Get current user
    print("\n3️⃣ Get /me avec access token...")
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    user = response.json()
    print(f"   ✅ Utilisateur : {user['username']} ({user['email']})")
    
    # 4. Refresh token
    print("\n4️⃣ Refresh access token...")
    response = requests.post(
        f"{BASE_URL}/auth/refresh-token",
        json={"refresh_token": refresh_token}
    )
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    
    new_access_token = response.json()["access_token"]
    print(f"   ✅ Nouveau access token : {new_access_token[:30]}...")
    
    # 5. Utiliser le nouveau token
    print("\n5️⃣ Get /me avec nouveau token...")
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    print(f"   ✅ Token valide")
    
    # 6. Logout
    print("\n6️⃣ Logout...")
    response = requests.post(
        f"{BASE_URL}/auth/logout",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    print(f"   ✅ Déconnexion réussie")
    
    # 7. Tenter de refresh après logout (doit échouer)
    print("\n7️⃣ Tentative de refresh après logout (doit échouer)...")
    response = requests.post(
        f"{BASE_URL}/auth/refresh-token",
        json={"refresh_token": refresh_token}
    )
    print(f"   Status: {response.status_code}")
    assert response.status_code == 401
    print(f"   ✅ Refresh token révoqué correctement")
    
    print("\n" + "=" * 70)
    print("✅ TOUS LES TESTS RÉUSSIS !")
    print("=" * 70)


if __name__ == "__main__":
    test_complete_auth_flow()
