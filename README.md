# Twitch Pescar via GitHub Actions

Envia `$pescar` ao chat de `casalskills`, usando sua conta Twitch, em execuções agendadas de 10 em 10 minutos. É necessário que a automação seja permitida pelo canal. O GitHub pode atrasar ou perder agendamentos.

## Configurar Twitch

1. Acesse https://dev.twitch.tv/console/apps e registre um aplicativo (pode exigir 2FA).
2. Em **OAuth Redirect URLs**, use exatamente `http://localhost:3000`; escolha **Confidential** como categoria de cliente.
3. Anote **Client ID** e crie/copiei o **Client Secret**.
4. No seu computador com Python 3, execute `python autenticar.py` e autorize o acesso `user:write:chat`.
5. Copie o `TWITCH_REFRESH_TOKEN` mostrado no terminal. Não compartilhe nenhum token.

## Configurar GitHub

1. Crie um repositório e envie `pescar.py` e a pasta `.github/workflows/` mantendo os caminhos. NÃO envie dados secretos e NÃO precisa enviar `autenticar.py` (mas ele não contém senhas salvas).
2. Em **Settings → Secrets and variables → Actions → New repository secret**, crie `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET` e `TWITCH_REFRESH_TOKEN` com os valores gerados.
3. Crie um token GitHub fine-grained em https://github.com/settings/personal-access-tokens/new limitado **somente a esse repositório**, permissão **Secrets: Read and write**, com validade apropriada. Ele é necessário porque o refresh token da Twitch pode mudar, e o workflow precisa atualizar o segredo. Salve esse token como `GH_PAT` nos mesmos Actions Secrets.
4. Vá a **Actions → Pescar na Twitch → Run workflow** para testar.
5. Nos logs, procure `Mensagem $pescar enviada ao chat de #casalskills.`

**Atenção:** nunca copie tokens para arquivos versionados; se algum token vazar, revogue-o. Quando o PAT do GitHub expirar, atualize `GH_PAT`. Se ocorrer erro 401, pode ser necessário refazer a autorização Twitch. O projeto não verifica se a transmissão está online. Para parar: desative o workflow na aba Actions.
