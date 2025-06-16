from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal
import base64
import hashlib
import hmac
import requests
from Crypto.Cipher import AES
import mimetypes

app = FastAPI()

MEDIA_KEY_LABELS = {
    "audio": b"WhatsApp Audio Keys",
    "video": b"WhatsApp Video Keys",
    "image": b"WhatsApp Image Keys",
    "document": b"WhatsApp Document Keys"
}

class DecryptRequest(BaseModel):
    url: str
    mediaKey: str
    mediaType: Literal["audio", "video", "image", "document"]
    mimetype: str = None

def hkdf(key: bytes, length: int, app_info: bytes) -> bytes:
    prk = hmac.new(b"\0" * 32, key, hashlib.sha256).digest()
    key_stream = b""
    prev_block = b""
    for i in range(1, -(-length // 32) + 1):
        prev_block = hmac.new(prk, prev_block + app_info + bytes([i]), hashlib.sha256).digest()
        key_stream += prev_block
    return key_stream[:length]

def aes_unpad(data: bytes) -> bytes:
    return data[:-data[-1]]

@app.post("/decrypt-file")
def decrypt_media_file(req: DecryptRequest):
    if req.mediaType not in MEDIA_KEY_LABELS:
        raise HTTPException(status_code=400, detail="Unsupported mediaType")

    try:
        media_key = base64.b64decode(req.mediaKey)
        media_label = MEDIA_KEY_LABELS[req.mediaType]

        expanded_key = hkdf(media_key, 112, media_label)
        iv = expanded_key[:16]
        cipher_key = expanded_key[16:48]
        mac_key = expanded_key[48:80]

        response = requests.get(req.url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download media")

        enc_data = response.content
        file_data = enc_data[:-10]
        mac = enc_data[-10:]

        # Validate HMAC
        hmac_calc = hmac.new(mac_key, iv + file_data, hashlib.sha256).digest()
        if hmac_calc[:10] != mac:
            raise HTTPException(status_code=400, detail="HMAC validation failed")

        cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
        decrypted = aes_unpad(cipher.decrypt(file_data))

        # Determine extension and content type
        default_ext = {
            "audio": ".ogg",
            "video": ".mp4",
            "image": ".jpg",
            "document": ".bin"
        }.get(req.mediaType, ".bin")

        ext = default_ext
        content_type = "application/octet-stream"

        if req.mediaType == "document" and req.mimetype:
            guessed_ext = mimetypes.guess_extension(req.mimetype)
            if guessed_ext:
                ext = guessed_ext
            content_type = req.mimetype
        elif req.mediaType in ["audio", "video", "image"]:
            content_type = mimetypes.types_map.get(ext, "application/octet-stream")

        file_name = f"media{ext}"

        return StreamingResponse(
            iter([decrypted]),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting media: {str(e)}")
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "wpp-file-decrypt:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    )

