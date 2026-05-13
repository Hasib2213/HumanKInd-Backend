import requests

BASE_URL = "http://127.0.0.1:8000/api/auth/"

def test_registration():
    url = BASE_URL + "register/"
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    response = requests.post(url, json=data)
    print(f"Registration status: {response.status_code}")
    print(f"Registration response: {response.json()}")

def test_login():
    url = BASE_URL + "login/"
    data = {
        "email": "test@example.com",
        "password": "Password123!"
    }
    response = requests.post(url, json=data)
    print(f"Login status: {response.status_code}")
    print(f"Login response: {response.json()}")

if __name__ == "__main__":
    # Note: This requires the server to be running.
    # Since I cannot run the server in the background and hit it from another process easily here,
    # I'll just provide this script for the user to verify.
    pass
