import asyncio
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from bot_utils import safe_zip_name, validate_public_url

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("video-downloader")
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
MAX_BYTES = int(os.getenv("MAX_FILE_MB", "45")) * 1024 * 1024
MAX_DURATION = int(os.getenv("MAX_DURATION_SECONDS", "3600"))

HELP = (
    "Ii soo dir URL-ga muuqaal ama gallery.\n"
    "• Video: waxaan ka soo saarayaa cod MP3 ah.\n"
    "• Gallery: sawirrada waxaan kuugu soo dirayaa ZIP.\n"
    "Kaliya URL-yada dadweynaha ee HTTP/HTTPS; ma taageerno DRM ama xannibaadaha gelitaanka."
)

def run_command(args, timeout=900):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True)

def ensure_size(path: Path):
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError("Wax fayl ah lama helin.")
    if path.stat().st_size > MAX_BYTES:
        raise RuntimeError(f"Faylku wuu ka weyn yahay xadka {MAX_BYTES // (1024*1024)} MB.")

def download_audio(url: str, folder: Path) -> Path:
    template = str(folder / "%(title).80B.%(ext)s")
    run_command(["yt-dlp", "--no-playlist", "--max-filesize", str(MAX_BYTES),
        "--match-filter", f"duration <= {MAX_DURATION}", "-f", "bestaudio/best",
        "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", template, url])
    files = list(folder.glob("*.mp3"))
    if not files:
        raise RuntimeError("MP3 lama soo saarin.")
    result = max(files, key=lambda p: p.stat().st_mtime)
    ensure_size(result)
    return result

def download_gallery(url: str, folder: Path) -> Path:
    run_command(["gallery-dl", "--directory", str(folder), url])
    files = [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in
        {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".avif"}]
    if not files:
        raise RuntimeError("Gallery sawirro ah lama helin.")
    if sum(p.stat().st_size for p in files) > MAX_BYTES:
        raise RuntimeError(f"ZIP-gu wuxuu dhaafayaa xadka {MAX_BYTES // (1024*1024)} MB.")
    archive_base = folder.parent / safe_zip_name(urlsplit(url).hostname or "gallery")
    archive = Path(shutil.make_archive(str(archive_base), "zip", root_dir=folder))
    ensure_size(archive)
    return archive

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ku soo dhawoow Soo-dajinta Vedio Bot.\n\n" + HELP)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = validate_public_url((update.message.text or "").strip())
    except ValueError as exc:
        await update.message.reply_text(f"URL sax ah geli: {exc}")
        return
    status = await update.message.reply_text("Waan soo dejinayaa, fadlan sug...")
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    with tempfile.TemporaryDirectory(prefix="tg-downloader-") as temp:
        folder = Path(temp) / "downloads"
        folder.mkdir()
        try:
            try:
                output = await asyncio.to_thread(download_audio, url, folder)
                kind, caption = "audio", "Codka MP3-gaaga."
            except Exception as audio_error:
                log.info("yt-dlp failed; trying gallery-dl: %s", audio_error)
                shutil.rmtree(folder)
                folder.mkdir()
                output = await asyncio.to_thread(download_gallery, url, folder)
                kind, caption = "document", "Sawirrada gallery-ga oo ZIP ah."
            with output.open("rb") as stream:
                if kind == "audio":
                    await update.message.reply_audio(audio=stream, filename=output.name, caption=caption)
                else:
                    await update.message.reply_document(document=stream, filename=output.name, caption=caption)
            await status.delete()
        except subprocess.TimeoutExpired:
            await status.edit_text("Waqtigu wuu dhammaaday. Isku day URL kale.")
        except Exception as exc:
            log.exception("Download failed")
            await status.edit_text((str(exc) or "Soo dejintu way fashilantay.")[:900])

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.exception("Unhandled Telegram error", exc_info=context.error)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_error_handler(error_handler)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
