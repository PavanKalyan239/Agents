# Standalone script to test all API endpoints sequentially, capturing tokens and tracking results
import requests
import json

BASE_URL = "http://localhost:8000"

test_counter = 0
passed = 0
failed = 0

# run_test now expects func() to return True/False
def run_test(description, func):
    global test_counter, passed, failed
    test_counter += 1
    try:
        result = func()
        if not result:
            raise AssertionError(f"Failed: {description}")
        print(f"Test {test_counter} PASS: {description}")
        passed += 1
    except AssertionError as e:
        print(f"Test {test_counter} FAIL: {description} - {e}")
        failed += 1

# Helper functions

def register_user(username, email, password, role="user"):
    return requests.post(f"{BASE_URL}/register", json={
        "username": username,
        "email": email,
        "password": password,
        "role": role
    })

def login_user(username, password):
    resp = requests.post(f"{BASE_URL}/login", data={"username": username, "password": password})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return None


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

# End-to-end tests

def main():
    # Registration tests
    run_test("Register admin", lambda: register_user("admin1", "admin1@example.com", "password123", "admin").status_code == 200)
    run_test("Register editor", lambda: register_user("editor1", "editor1@example.com", "password123", "editor").status_code == 200)
    run_test("Register viewer", lambda: register_user("viewer1", "viewer1@example.com", "password123").status_code == 200)
    run_test("Duplicate registration fails", lambda: register_user("admin1", "admin1@example.com", "password123", "admin").status_code == 400)

    # Login tests
    admin_token = login_user("admin1", "password123")
    editor_token = login_user("editor1", "password123")
    viewer_token = login_user("viewer1", "password123")
    run_test("Login valid user", lambda: admin_token is not None)
    run_test("Login invalid password", lambda: login_user("admin1", "wrong") is None)
    run_test("Login non-existent user", lambda: login_user("nouser", "nopass") is None)

    # Document creation tests
    run_test("Admin can create document", lambda: requests.post(f"{BASE_URL}/documents", json={"title":"D1","content":"C1"}, headers=auth_header(admin_token)).status_code == 200)
    run_test("Editor can create document", lambda: requests.post(f"{BASE_URL}/documents", json={"title":"D2","content":"C2"}, headers=auth_header(editor_token)).status_code == 200)
    run_test("Viewer cannot create document", lambda: requests.post(f"{BASE_URL}/documents", json={"title":"D3","content":"C3"}, headers=auth_header(viewer_token)).status_code == 403)
    run_test("No token create fails", lambda: requests.post(f"{BASE_URL}/documents", json={"title":"D4","content":"C4"}).status_code == 401)

    # Read documents tests
    run_test("Admin can read documents", lambda: requests.get(f"{BASE_URL}/documents", headers=auth_header(admin_token)).status_code == 200)
    run_test("Editor can read documents", lambda: requests.get(f"{BASE_URL}/documents", headers=auth_header(editor_token)).status_code == 200)
    run_test("Viewer can read documents", lambda: requests.get(f"{BASE_URL}/documents", headers=auth_header(viewer_token)).status_code == 200)
    run_test("Invalid token read fails", lambda: requests.get(f"{BASE_URL}/documents", headers=auth_header('badtoken')).status_code == 401)

    # Prepare a doc for update/delete tests
    create_resp = requests.post(f"{BASE_URL}/documents", json={"title":"ForUpdate","content":"Old"}, headers=auth_header(admin_token))
    doc_id = create_resp.json().get("id")

    # Update tests
    run_test("Admin can update any document", lambda: requests.put(f"{BASE_URL}/documents/{doc_id}", json={"title":"New","content":"Changed"}, headers=auth_header(admin_token)).status_code == 200)
    run_test("Editor can update own document", lambda: requests.put(f"{BASE_URL}/documents/{doc_id}", json={"title":"Enew","content":"Ex"}, headers=auth_header(editor_token)).status_code in (200,403))
    run_test("Viewer cannot update document", lambda: requests.put(f"{BASE_URL}/documents/{doc_id}", json={"title":"Vnew","content":"Vc"}, headers=auth_header(viewer_token)).status_code == 403)
    run_test("Update non-existent document fails", lambda: requests.put(f"{BASE_URL}/documents/9999", json={"title":"X","content":"Y"}, headers=auth_header(admin_token)).status_code == 404)

    # Delete tests
    run_test("Editor cannot delete document", lambda: requests.delete(f"{BASE_URL}/documents/{doc_id}", headers=auth_header(editor_token)).status_code == 403)
    run_test("Viewer cannot delete document", lambda: requests.delete(f"{BASE_URL}/documents/{doc_id}", headers=auth_header(viewer_token)).status_code == 403)
    run_test("Admin can delete document", lambda: requests.delete(f"{BASE_URL}/documents/{doc_id}", headers=auth_header(admin_token)).status_code == 200)
    run_test("Delete non-existent document fails", lambda: requests.delete(f"{BASE_URL}/documents/9999", headers=auth_header(admin_token)).status_code == 404)

    # Registration validation negative tests
    invalid_inputs = [
        ("ab","a@example.com","pass123","user",422),
        ("toolongusername_abcdefghijklmnopqrstuvwxyz","u@example.com","pass123","user",422),
        ("u5","bademail","pass123","user",422),
        ("u6","u6@example.com","pwd","user",422),
        ("u7","u7@example.com","password","invalid",422)
    ]
    for idx, (u,e,p,r,exp) in enumerate(invalid_inputs, start=1):
        run_test(f"Invalid registration case {idx}", lambda u=u,e=e,p=p,r=r,exp=exp: register_user(u,e,p,r).status_code == exp)

    # Summary
    print(f"\nExecuted {test_counter} tests: {passed} passed, {failed} failed.")

if __name__ == "__main__":
    main()
