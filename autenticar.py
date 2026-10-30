"""Execute LOCALMENTE uma vez para obter o refresh token da Twitch."""
import http.server
import secrets
import threading
import urllib.parse
import urllib.request
import json
import webbrowser

REDIRECT = "http://localhost:3000"
CLIENT_ID = input("Client ID do seu aplicativo Twitch: ").strip()
CLIENT_SECRET = input("Client Secret do seu aplicativo Twitch: ").strip()
STATE = secrets.token_urlsafe(32)
event = threading.Event()
resultado = {}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if qs.get("state", [None])[0] != STATE:
            self.send_error(400, "State inválido")
            return
        if "code" in qs:
            resultado["code"] = qs["code"][0]
            mensagem = "Autorizado! Volte ao terminal."
        else:
            resultado["error"] = qs.get("error", ["Acesso negado"])[0]
            mensagem = "A autorização falhou. Volte ao terminal."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(mensagem.encode())
        event.set()

    def log_message(self, *args):
        pass

server = http.server.HTTPServer(("127.0.0.1", 3000), Handler)
url = "https://id.twitch.tv/oauth2/authorize?" + urllib.parse.urlencode({
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT,
    "scope": "user:write:chat",
    "state": STATE,
})
print("Abrindo o navegador para autorizar sua conta...")
webbrowser.open(url)
server.handle_request()
server.server_close()
if "code" not in resultado:
    raise SystemExit(f"Erro: {resultado.get('error')}")
body = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code": resultado["code"],
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT,
}).encode()
request = urllib.request.Request("https://id.twitch.tv/oauth2/token", data=body)
with urllib.request.urlopen(request, timeout=30) as resp:
    auth = json.load(resp)
print("\nCopie cada valor apenas para GitHub Actions Secrets:")
print("TWITCH_CLIENT_ID:", CLIENT_ID)
print("TWITCH_CLIENT_SECRET:", CLIENT_SECRET)
print("TWITCH_REFRESH_TOKEN:", auth["refresh_token"])
print("\nNÃO compartilhe esses valores nem os publique no repositório.")
