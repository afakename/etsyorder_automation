import http.server
import socketserver
import webbrowser
import requests
import secrets
import hashlib
import base64
from urllib.parse import urlparse, parse_qs

# === REPLACE WITH YOUR CREDENTIALS ===
CLIENT_ID = "1bsfw0s4klwjm2hvie9zb4cr"
CLIENT_SECRET = "jk5rekr9jp"
REDIRECT_URI = "http://localhost:8080"

# === Generate PKCE code_verifier and code_challenge ===
def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode("utf-8")
    return code_verifier, code_challenge

code_verifier, code_challenge = generate_pkce_pair()
STATE = secrets.token_urlsafe(16)

# === Etsy OAuth URL ===
AUTH_URL = (
    f"https://www.etsy.com/oauth/connect"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=transactions_r listings_r profile_r email_r shops_r"
    f"&state={STATE}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
)

# === Local server handler ===
class EtsyOAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query = parse_qs(parsed_url.query)

        if "error" in query:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed.")
            print("Error:", query.get("error_description", ["Unknown error"])[0])
            return

        if query.get("state", [None])[0] != STATE:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid state. Aborting.")
            print("Invalid state received.")
            return

        code = query.get("code", [None])[0]
        if not code:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization code missing.")
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Authorization successful. You can close this window.")
        print(f"\nAuthorization code received: {code}")
        self.server.auth_code = code

# === Step 1: Launch Etsy auth ===
def get_auth_code():
    print("Opening Etsy authorization URL in your browser...")
    webbrowser.open(AUTH_URL)
    with socketserver.TCPServer(("localhost", 8080), EtsyOAuthHandler) as httpd:
        print("Waiting for Etsy authorization response...")
        httpd.handle_request()
        return getattr(httpd, 'auth_code', None)

# === Step 2: Exchange code for access token ===
def get_access_token(code):
    token_url = "https://api.etsy.com/v3/public/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "code_verifier": code_verifier
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    print("Exchanging code for access token...")
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code == 200:
        print("\nAccess token received:")
        print(response.json())
    else:
        print("Failed to retrieve access token:")
        print(response.status_code, response.text)

# === Run the full OAuth process ===
if __name__ == "__main__":
    print("Starting OAuth process...")
    code = get_auth_code()
    if code:
        get_access_token(code)
    else:
        print("No authorization code received.")
