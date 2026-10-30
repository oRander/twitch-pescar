"""Envia uma mensagem por execução via API Helix da Twitch."""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

CANAL = "casalskills"
MENSAGEM = "$pescar"


def requisicao(url, *, token=None, client_id=None, dados=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if client_id:
        headers["Client-Id"] = client_id
    if dados is not None:
        if isinstance(dados, dict):
            body = json.dumps(dados).encode()
            headers["Content-Type"] = "application/json"
        else:
            body = urllib.parse.urlencode(dados).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
    else:
        body = None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def main():
    client_id = os.environ["TWITCH_CLIENT_ID"]
    client_secret = os.environ["TWITCH_CLIENT_SECRET"]
    refresh_token = os.environ["TWITCH_REFRESH_TOKEN"]
    gh_token = os.environ["GH_PAT"]
    repo = os.environ["GITHUB_REPOSITORY"]

    # Pedir um access token novo usando o refresh token salvo.
    refreshed = requisicao(
        "https://id.twitch.tv/oauth2/token",
        dados={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    access_token = refreshed["access_token"]
    new_refresh_token = refreshed["refresh_token"]

    # IMPORTANTE: atualizar o segredo antes de fazer qualquer outra coisa.
    # Twitch pode rotacionar o refresh token a cada renovação.
    subprocess.run(
        ["gh", "secret", "set", "TWITCH_REFRESH_TOKEN", "--repo", repo],
        input=new_refresh_token,
        text=True,
        env={**os.environ, "GH_TOKEN": gh_token},
        check=True,
        capture_output=True,
    )
    print("Autenticação renovada e segredo atualizado.")

    usuario = requisicao(
        "https://api.twitch.tv/helix/users",
        token=access_token,
        client_id=client_id,
    )["data"][0]
    canal = requisicao(
        "https://api.twitch.tv/helix/users?" + urllib.parse.urlencode({"login": CANAL}),
        token=access_token,
        client_id=client_id,
    )["data"]
    if not canal:
        raise RuntimeError(f"Canal #{CANAL} não encontrado")

    resultado = requisicao(
        "https://api.twitch.tv/helix/chat/messages",
        token=access_token,
        client_id=client_id,
        dados={
            "broadcaster_id": canal[0]["id"],
            "sender_id": usuario["id"],
            "message": MENSAGEM,
        },
    )
    resposta = resultado["data"][0]
    if not resposta.get("is_sent", False):
        raise RuntimeError("Twitch rejeitou a mensagem: " + json.dumps(resposta.get("drop_reason")))
    print(f"Mensagem {MENSAGEM} enviada ao chat de #{CANAL}.")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, urllib.error.HTTPError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"Erro: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
