import secrets
import webbrowser


# Placeholder implementation for OAuth2 login flow
def perform_login(client_id: str, redirect_port: int = 8080):
    state = secrets.token_urlsafe(16)
    redirect_uri = f"http://localhost:{redirect_port}/callback"
    auth_url = (
        f"https://api.restream.io/login?response_type=code&client_id={client_id}"
    ) + f"&redirect_uri={redirect_uri}&state={state}"
    print(f"Open this URL in your browser: {auth_url}")
    webbrowser.open(auth_url)
    # Simplified listener stub; real implementation needs to capture code and exchange for tokens.
    print(
        "[stub] Listening on localhost for redirect and capturing authorization code..."
    )
