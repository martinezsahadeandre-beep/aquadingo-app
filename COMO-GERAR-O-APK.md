# Como gerar o AquaDingo.apk (passo a passo)

Este pacote tem o app completo em Kivy (Python para mobile) + um workflow do
GitHub Actions que compila o `.apk` automaticamente na nuvem — você não
precisa instalar Android Studio nem nada pesado no seu PC.

## O que tem aqui dentro

```
aquadingo_apk/
├── main.py                          <- o app (interface)
├── data_logic.py                    <- lógica de XP, streak, conquistas
├── buildozer.spec                   <- receita de como empacotar o APK
└── .github/workflows/build-apk.yml  <- robô que compila o APK sozinho
```

## Passo a passo

### 1. Crie uma conta no GitHub (se ainda não tiver)
https://github.com/signup — é grátis.

### 2. Crie um repositório novo
- Vá em https://github.com/new
- Dê um nome, ex: `aquadingo-app`
- Deixe como **público** (repositórios privados também funcionam, mas
  público é mais simples pro plano grátis)
- Clique em "Create repository"

### 3. Suba os arquivos deste pacote para o repositório
Na página do repositório recém-criado, clique em **"uploading an existing
file"** (ou "Add file" → "Upload files") e arraste **todos os arquivos e
pastas** deste pacote (`main.py`, `data_logic.py`, `buildozer.spec`, e a
pasta `.github` inteira — mantenha essa estrutura de pastas!).

> Importante: a pasta `.github/workflows/build-apk.yml` precisa ficar
> exatamente nesse caminho para o GitHub reconhecer o workflow. Se o site
> não deixar arrastar pastas, você pode instalar o GitHub Desktop
> (https://desktop.github.com) e arrastar a pasta toda de uma vez, ou usar
> o `git` pela linha de comando:
> ```
> git init
> git add .
> git commit -m "AquaDingo app"
> git branch -M main
> git remote add origin https://github.com/SEU_USUARIO/aquadingo-app.git
> git push -u origin main
> ```

### 4. Aguarde a build automática
Assim que os arquivos forem enviados (commit feito na branch `main`), o
GitHub já dispara a build sozinho. Para acompanhar:
- Vá na aba **"Actions"** do seu repositório
- Você verá "Build AquaDingo APK" rodando (bolinha amarela = em andamento)
- A primeira build demora entre **15 e 25 minutos** (baixa o Android SDK/NDK
  do zero). Builds seguintes são bem mais rápidas.

### 5. Baixe o APK
Quando o círculo ficar verde (✅ sucesso):
- Clique na execução concluída
- Role até **"Artifacts"** no final da página
- Baixe **"AquaDingo-apk"** (vem como um `.zip` contendo o `.apk` dentro)

### 6. Instale no celular
- Copie o `.apk` para o celular (Google Drive, cabo USB, WhatsApp Web, etc.)
- No Android, abra o arquivo `.apk` pelo gerenciador de arquivos
- Se aparecer aviso de "instalar apps de fontes desconhecidas", permita —
  isso é normal para apps fora da Play Store
- Pronto, o AquaDingo vai aparecer na sua tela de apps

## Se a build falhar

Erros de build do Buildozer costumam ser por causa de versões. Se der erro,
me mostre o log da aba "Actions" (clique no passo que falhou em vermelho)
que eu ajusto o `buildozer.spec` ou o `main.py` pra você.

## Sobre os lembretes de beber água no Android

O app usa a biblioteca `plyer` para mandar notificações nativas do Android
enquanto está aberto. Para notificações mesmo com o app fechado/minimizado
por muito tempo, o Android pode "congelar" o app em segundo plano (é o
comportamento padrão do sistema para economizar bateria) — isso é uma
limitação de apps simples como este, não um bug. Se quiser lembretes
garantidos o dia todo, a forma mais confiável é deixar o app aberto em
segundo plano e configurar o Android para não otimizar a bateria dele
(Ajustes → Apps → AquaDingo → Bateria → Sem restrições).
