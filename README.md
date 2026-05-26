![appleTV Plugin for Indigo](https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/banner3.png)

# appleTV Plugin for Indigo

[![Version](https://img.shields.io/badge/version-1.8.0-blue)](https://github.com/Ghawken/appleTV-indigoPlugin/releases/latest)
[![Indigo](https://img.shields.io/badge/Indigo-2023.2%2B-green)](https://www.indigodomo.com)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/github/license/Ghawken/appleTV-indigoPlugin)](LICENSE)

Control and monitor **Apple TVs**, **HomePods**, and **AirPlay 2 speakers** from [Indigo](https://www.indigodomo.com) home automation. Devices connect over your local network using the open-source [pyatv](https://pyatv.dev) library and maintain a persistent push-update connection — no polling, no delays.

---

## Features

- 📡 **Real-time push updates** — play/pause/power state changes appear in Indigo the instant they happen; no polling
- 🎮 **Full remote control** — every pyatv command available as an Indigo action; new commands in future library updates appear automatically
- 📱 **App launcher** — launch any installed app on an Apple TV by name
- 🔊 **Text-to-speech** — speak announcements through HomePods using the macOS system voice, with Indigo variable and device substitution
- 🖼 **Artwork & progress bar** — auto-save current artwork and a playback progress PNG to disk for use in Indigo Control Pages
- 📻 **AirPlay 2 streaming** — stream audio files to any AirPlay 2 device including Sonos speakers

## Supported devices

| Device | Remote control | Push state updates | TTS playback |
|---|---|---|---|
| Apple TV (4K, HD) | ✅ | ✅ | — |
| HomePod / HomePod mini | ✅ | ✅ | ✅ |
| AirPlay 2 speakers (Sonos, etc.) | Stream only | — | ✅ |

---

## Quick start

1. Download the [latest release](https://github.com/Ghawken/appleTV-indigoPlugin/releases/latest) and double-click the `.indigoPlugin` bundle to install
2. Open **Plugins → appleTV Plugin → Plugin Config**, press **Generate AppleTV Devices**
3. Open each new device, press **Start Connection**, enter the PIN if shown on the Apple TV screen
4. Press **Save** — the device is now live and push-updating

> All Python libraries (pyatv, Pillow, ffmpeg) are bundled. No manual `pip install` required.

---

## Screenshots

<table>
<tr>
<td><img src="https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/pluginConfig.png" width="260" alt="Plugin Config"/><br><sub>Plugin Config — device discovery</sub></td>
<td><img src="https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/DeviceConfig.png" width="260" alt="Device Config"/><br><sub>Device setup &amp; pairing</sub></td>
<td><img src="https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/DeviceStates.png" width="260" alt="Device States"/><br><sub>Device states in Indigo</sub></td>
</tr>
<tr>
<td><img src="https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/remoteNew1.png" width="260" alt="Remote Commands"/><br><sub>Send Command action</sub></td>
<td><img src="https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/SpeakAnnoucement.png" width="260" alt="Speak Announcement"/><br><sub>Speak Announcement action</sub></td>
<td><img src="https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/Paused-Example.png" width="260" alt="Paused artwork example"/><br><sub>Artwork with pause overlay</sub></td>
</tr>
</table>

---

## Documentation

Full documentation is in the [GitHub Wiki](https://github.com/Ghawken/appleTV-indigoPlugin/wiki):

| Page | Description |
|---|---|
| [Installation](https://github.com/Ghawken/appleTV-indigoPlugin/wiki/Installation) | Requirements, install steps, first run, pairing, upgrades |
| [Configuration](https://github.com/Ghawken/appleTV-indigoPlugin/wiki/Configuration) | Every Plugin Config setting explained |
| [Devices](https://github.com/Ghawken/appleTV-indigoPlugin/wiki/Devices) | Device states, artwork settings, Control Page integration |
| [Actions](https://github.com/Ghawken/appleTV-indigoPlugin/wiki/Actions) | Every action and its parameters |
| [Troubleshooting](https://github.com/Ghawken/appleTV-indigoPlugin/wiki/Troubleshooting) | Common errors, debug logging, diagnostic menus |
| [FAQ](https://github.com/Ghawken/appleTV-indigoPlugin/wiki/FAQ) | Network, pairing, artwork, TTS, rate limits |
| [Changelog](https://github.com/Ghawken/appleTV-indigoPlugin/wiki/Changelog) | Full release history |
| [Support](https://github.com/Ghawken/appleTV-indigoPlugin/wiki/Support) | Forum, Issues, what to include in a bug report |

---

## Requirements

- **Indigo** 2023.2+ (API 3.4)
- **macOS** Ventura or later recommended
- Apple TV / HomePod on the **same local network** as the Indigo server

---

## Support

- **Forum:** [Indigo community — appleTV Plugin](https://forums.indigodomo.com/viewforum.php?f=382)
- **Bugs / feature requests:** [GitHub Issues](https://github.com/Ghawken/appleTV-indigoPlugin/issues)

---

## Acknowledgements

Built on the excellent [pyatv](https://pyatv.dev) library by [postlund](https://github.com/postlund/pyatv).
