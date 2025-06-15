# WhatsApp Media Decrypt Microservice

Este microserviço em Python permite descriptografar mídias recebidas via webhook do WhatsApp Web. Ele é compatível com arquivos de áudio, vídeo, imagem e documentos, realizando a verificação HMAC e retornando o arquivo descriptografado via download direto.

## ✅ Funcionalidades

- 📥 Download de arquivos `.enc` via URL pública do WhatsApp
- 🔐 Descriptografia usando `mediaKey` (HKDF + AES-CBC)
- 🛡️ Validação do HMAC antes da descriptografia
- 🧾 Suporte a `audio`, `video`, `image`, `document`
- 📦 Retorno da mídia como download com o `mimetype` correto
- 🔄 Compatível com execução via `pm2`, `Docker`, ou manual

---

## 🚀 Requisitos

- Python 3.8+
- pip

### Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## ▶️ Executando manualmente

```bash
python wpp-file-decrypt.py
```

> O microserviço ficará disponível em: http://localhost:8001/decrypt-file

---

## 🔄 Usando com PM2

Instale o PM2:

```bash
npm install -g pm2
```

Inicie o microserviço com PM2:

```bash
pm2 start wpp-file-decrypt.py --interpreter=python3 --name=wpp-file-decrypt
pm2 save
pm2 startup
```

> Isso garante que o microserviço reinicie automaticamente após reboots.

---

## 📨 Endpoint

### `POST /decrypt-file`

**JSON esperado:**

```json
{
  "url": "https://mmg.whatsapp.net/v/...",
  "mediaKey": "base64-media-key",
  "mediaType": "document",
  "mimetype": "application/pdf"  
}
```

Retorna o arquivo descriptografado como download.

---

## 🧪 Testado com mídias reais do WhatsApp Web ✅
