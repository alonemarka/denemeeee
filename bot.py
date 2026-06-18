import os
from io import BytesIO
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import edge_tts

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ses seçenekleri
VOICES = {
    "kız1": "tr-TR-EmelNeural",
    "kız2": "tr-TR-ZehraNeural",
    "erkek1": "tr-TR-AhmetNeural",
    "erkek2": "tr-TR-EmreNeural",
    "ai": "tr-TR-YusufNeural"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
    "🎙 **Alone Ses Bot** aktif!\n\n"
    "Komutlar:\n"
    "/ses <metin> - Varsayılan kız\n"
    "/kiz1 <metin>\n"
    "/kiz2 <metin>\n"
    "/erkek1 <metin>\n"
    "/erkek2 <metin>\n"
    "/ai <metin>\n\n"
    "Örnek: /kiz1 Merhaba kanka nasılsın?"
)

async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE, voice_name="kız1"):
    if not context.args:
        await update.message.reply_text("Kullanım: `/kız1 Merhaba kanka`")
        return

    text = " ".join(context.args)
    voice = VOICES.get(voice_name, VOICES["kız1"])

    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_bytes = BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes.write(chunk["data"])

        audio_bytes.seek(0)
        await update.message.reply_voice(voice=audio_bytes, caption=f"Ses: {voice_name}")
    except Exception as e:
        await update.message.reply_text(f"Hata: {str(e)}")

# Komutlar
async def ses_kiz1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, "kız1")

async def ses_kiz2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, "kız2")

async def ses_erkek1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, "erkek1")

async def ses_erkek2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, "erkek2")

async def ses_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await text_to_speech(update, context, "ai")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
     app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ses", ses_kiz1))
    app.add_handler(CommandHandler("kiz1", ses_kiz1))   # kız1 → kiz1
    app.add_handler(CommandHandler("kiz2", ses_kiz2))   # kız2 → kiz2
    app.add_handler(CommandHandler("erkek1", ses_erkek1))
    app.add_handler(CommandHandler("erkek2", ses_erkek2))
    app.add_handler(CommandHandler("ai", ses_ai))
    
    print("🚀 Alone Ses Bot çalışıyor!")
    app.run_polling()

if __name__ == "__main__":
    main()
