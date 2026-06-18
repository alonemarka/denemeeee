import os
import requests
from io import BytesIO
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Gerçekçi Ses ID'leri (ElevenLabs)
VOICES = {
    "kiz1": "EXAVITQu4vr4xnSDxMaL",   # Rachel (çok gerçekçi kız)
    "kiz2": "21m00Tcm4TlvDq8ikWAM",   # Bella
    "erkek1": "ErXwobaYiN019PkySvjV", # Adam
    "erkek2": "VR6AewLTigWG4xSOukaG", # Josh
    "ai": "EXAVITQu4vr4xnSDxMaL"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙 **Alone Gerçekçi Ses Bot** aktif!\n\n"
        "Komutlar:\n"
        "/kiz1 <metin> - En gerçekçi kız\n"
        "/kiz2 <metin>\n"
        "/erkek1 <metin>\n"
        "/erkek2 <metin>\n"
        "/ai <metin>\n\n"
        "Örnek: /kiz1 Merhaba kanka, nasılsın?"
    )

async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE, voice_id):
    if not context.args:
        await update.message.reply_text("Kullanım: `/kiz1 Merhaba`")
        return

    text = " ".join(context.args)

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.85}
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        audio_bytes = BytesIO(response.content)
        await update.message.reply_voice(voice=audio_bytes, caption="Gerçekçi Ses")
        
    except Exception as e:
        await update.message.reply_text(f"Hata: {str(e)}")

# Komutlar
async def kiz1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, VOICES["kiz1"])

async def kiz2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, VOICES["kiz2"])

async def erkek1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, VOICES["erkek1"])

async def erkek2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, VOICES["erkek2"])

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, VOICES["ai"])

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kiz1", kiz1))
    app.add_handler(CommandHandler("kiz2", kiz2))
    app.add_handler(CommandHandler("erkek1", erkek1))
    app.add_handler(CommandHandler("erkek2", erkek2))
    app.add_handler(CommandHandler("ai", ai))
    
    print("🚀 Gerçekçi Ses Bot çalışıyor!")
    app.run_polling()

if __name__ == "__main__":
    main()
