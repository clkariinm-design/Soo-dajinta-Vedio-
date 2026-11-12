# Soo-dajinta Vedio — Telegram Bot

Bot-ka Telegram wuxuu qabtaa laba shaqo:
- URL muuqaal ah → wuxuu ka soo saaraa cod MP3 ah isagoo adeegsanaya yt-dlp iyo FFmpeg.
- URL gallery ah → wuxuu soo dejinayaa sawirrada, kadibna ZIP ayuu ka sameeyaa isagoo adeegsanaya gallery-dl.

## Dejinta bot-ka
1. Telegram ka fur @BotFather oo samee bot cusub.
2. Nuqul ka qaado token-ka. Ha ku darin repository-ga ama fariin dadweyne.
3. Ku rakib Python 3.12, FFmpeg iyo dependencies-ka: pip install -r requirements.txt
4. Deji environment variable TELEGRAM_BOT_TOKEN.
5. Orod: python bot.py

## Deploy-ga Render
1. Render ka dooro New → Background Worker.
2. Ku xidh repository-gan: https://github.com/clkariinm-design/Soo-dajinta-Vedio-
3. Dooro Docker runtime; render.yaml wuxuu qeexayaa worker-ka.
4. Environment Variables ku dar TELEGRAM_BOT_TOKEN, kadib deploy samee.

Render worker-ku wuxuu u baahan yahay qorshe lacag leh oo ku habboon background workers; hubi qiimaha iyo xadka qorshaha ka hor intaadan deploy-gareyn.

## Xaddidaadaha
- Kaliya URL-yada HTTP/HTTPS ee dadweynaha.
- Ma dhaafo DRM, paywall, login ama xannibaadaha gelitaanka.
- Taageerada website-yadu way is beddeli kartaa; dhammaan link-yadu ma shaqaynayaan.
- Xadka caadiga ah waa 45 MB iyo 60 daqiiqo; waxaa lagu beddeli karaa MAX_FILE_MB iyo MAX_DURATION_SECONDS.
- Isticmaal kaliya waxyaabaha aad xaq u leedahay inaad soo dejiso.
- URL validation-ku waa difaac aasaasi ah. Adeegsi production ah wuxuu u baahan yahay network egress restrictions iyo SSRF controls dheeraad ah.

## Tests
Orod: python -m unittest discover -s tests -v
