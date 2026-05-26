![](images/banner3.png)

# appleTV Plugin for Indigo

Control and monitor Apple TVs, HomePods, and AirPlay 2 speakers from [Indigo](https://www.indigodomo.com) home automation. Devices connect over your local network using the open-source [pyatv](https://pyatv.dev) library and maintain a persistent push-update connection — no polling, no delays.

## What it does

- **Real-time state** — play/pause/power changes appear in Indigo the instant they happen on the device
- **Full remote control** — every command pyatv exposes is available as an Indigo action; new commands in future library updates appear automatically
- **App launcher** — launch any installed app on an Apple TV by name
- **Text-to-speech** — speak announcements through HomePods using the macOS `say` voice with Indigo variable/device substitution
- **Artwork & progress bar** — auto-save current artwork and a playback progress PNG to `~/Pictures/Indigo-appleTV/` for use in Indigo Control Pages
- **AirPlay 2 speakers** — stream audio files to any AirPlay 2 device including Sonos speakers

## Supported devices

| Device type | Remote control | Push state updates | TTS playback |
|---|---|---|---|
| Apple TV (4K, HD) | ✅ | ✅ | — |
| HomePod / HomePod mini | ✅ | ✅ | ✅ |
| AirPlay 2 speakers (Sonos, etc.) | Stream only | — | ✅ |

## Quick start

1. Download and double-click the `.indigoPlugin` bundle to install
2. Open **Plugins → appleTV Plugin → Plugin Config**, press **Generate AppleTV Devices**
3. Open each newly created device, press **Start Connection**, enter the PIN if shown on the screen
4. Press **Save** — the device is now live and push-updating

→ See [Installation](Installation) for full details.

## Pages

| Page | Contents |
|---|---|
| [Installation](Installation) | Requirements, install steps, first run, upgrades |
| [Configuration](Configuration) | All Plugin Config settings explained |
| [Devices](Devices) | Device type, states, artwork/progress bar settings |
| [Actions](Actions) | Every action and its parameters |
| [Troubleshooting](Troubleshooting) | Debug logging, common errors, log locations |
| [FAQ](FAQ) | Network, pairing, artwork, TTS, rate limits |
| [Changelog](Changelog) | Full release history |
| [Support](Support) | Forum, GitHub Issues, what to include in a bug report |

---

→ [Installation](Installation)
