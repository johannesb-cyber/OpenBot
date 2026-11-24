# YouTube Downloader

Kleine lokale Web-App zum Herunterladen von YouTube-Videos als **MP4** oder nur den Ton als **MP3**.
Läuft komplett auf deinem Rechner und nutzt [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Starten

Voraussetzung: **Python 3.9 oder neuer** ([python.org](https://www.python.org/downloads/)).

- **Windows:** Doppelklick auf `start.bat`
- **macOS / Linux:** `./start.sh` im Terminal

Beim ersten Start werden die Abhängigkeiten installiert, danach öffnet sich der Browser
auf <http://127.0.0.1:5000>. ffmpeg wird über `imageio-ffmpeg` mitgeliefert, du musst es nicht extra installieren.

## Bedienung

1. YouTube-Link einfügen und **Laden** klicken
2. **Video (MP4)** mit gewünschter Auflösung oder **Nur Ton (MP3)** wählen
3. **Herunterladen** – die Datei wird im Browser gespeichert und liegt zusätzlich im Ordner `downloads/`

## Einstellungen (optional)

| Variable     | Bedeutung                           | Standard      |
|--------------|-------------------------------------|---------------|
| `PORT`       | Port der App                        | `5000`        |
| `YTDL_DIR`   | Ordner für die Downloads            | `./downloads` |
| `NO_BROWSER` | `1` = Browser nicht automatisch öffnen | –          |

## Wenn ein Download plötzlich nicht mehr geht

YouTube ändert regelmäßig etwas; dann hilft fast immer ein Update von yt-dlp.
Das passiert automatisch bei jedem Start über `start.bat` / `start.sh`.

## Hinweis

Lade nur Inhalte herunter, an denen du die Rechte hast oder deren Download erlaubt ist
(z. B. eigene Videos oder Creative-Commons-Inhalte). Die Nutzungsbedingungen von YouTube schränken Downloads ein.
