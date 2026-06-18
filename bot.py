import os
import io
import wave
import logging
import base64
from pydub import AudioSegment

from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====================== CONFIG ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

TTS_VOICE = "Kore"   # Kore ve Puck en iyi kız sesleri

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

# ====================== DAHA GERÇEKÇİ TTS ======================
async def text_to_voice(text: str) -> bytes:
    """Gerçek genç kız gibi konuşsun diye prompt güçlendirdik"""
    # Gerçekçi prompt
    enhanced_prompt = f"""
    Gerçek bir Türk kızı gibi doğal, samimi ve duygusal bir ses tonuyla oku. 
    Nefes al, vurguları doğal yap, biraz duygusal ve sevimli ol. 
    Metin: {text}
    """

    response = client.models.generate_content(
        model="gemini-3.1-flash-tts-preview",
        contents=enhanced_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=TTS_VOICE
                    )
                )
            )
        )
    )

    pcm_data = response.candidates[0].content.parts[0].inline_data.data
    pcm_bytes = base64.b64decode(pcm_data)

    # WAV → OGG
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_bytes)
    wav_buffer.seek(0)

    audio = AudioSegment.from_wav(wav_buffer)
    ogg_buffer = io.BytesIO()
    audio.export(ogg_buffer, format="ogg", codec="libopus")
    ogg_buffer.seek(0)
    return ogg_buffer.read()

# ====================== HANDLERS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Tamam kanka! 👧 Bedava ve gerçekçi kız sesiyle çalışıyorum.\nMetin yaz, okuyayım."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.chat.send_action("record_voice")

    try:
        voice_bytes = await text_to_voice(text)
        await update.message.reply_voice(voice=voice_bytes, caption="Gerçekçi kız sesi ile ❤️")
    except Exception as e:
        await update.message.reply_text(f"Hata: {str(e)[:200]}")

# ====================== MAIN ======================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    port = int(os.getenv("PORT", 8080))
    if os.getenv("WEBHOOK_URL"):
        app.run_webhook(listen="0.0.0.0", port=port, url_path="webhook", webhook_url=os.getenv("WEBHOOK_URL"))
    else:
        app.run_polling()

if __name__ == "__main__":
    main()
