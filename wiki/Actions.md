![](images/banner.png)

# Actions

All plugin actions are available via **Indigo → New Action Group → appleTV Plugin** (or inline in any action group).

---

## Send command to Apple TV

Sends any pyatv command to the selected device. The command list is built dynamically from the running connection — if pyatv gains new commands in a future library update they appear here automatically without a plugin update.

![Remote Commands](https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/remoteNew1.png)

| Parameter | Type | Description |
|---|---|---|
| Select Apple TV | Menu | The Indigo device to target |
| Command | Menu | Command to execute (see categories below) |
| Optional Arguments | Text | Arguments for commands that accept them — leave blank for most commands |
| Help to Log | Button | Logs the signature and documentation for the currently selected command to the Event Log |

### Command categories

| Category | Example commands |
|---|---|
| **Remote Commands** | `up`, `down`, `left`, `right`, `select`, `menu`, `home`, `play`, `pause`, `play_pause`, `stop`, `next`, `previous`, `volume_up`, `volume_down`, `set_position`, `set_repeat`, `set_shuffle`, `skip_forward`, `skip_backward` |
| **Simple Commands** | `TOP_MENU`, `APP_SWITCHER`, `SCREENSAVER`, `SKIP_FORWARD`, `SKIP_BACKWARD`, `SWIPE_LEFT`, `SWIPE_RIGHT`, `SWIPE_UP`, `SWIPE_DOWN`, `CHANNEL_UP`, `CHANNEL_DOWN` |
| **Power** | `turn_on`, `turn_off` |
| **Audio** | `set_volume`, `volume_up`, `volume_down`, `mute`, `toggle_mute` |
| **Streaming** | `play_url`, `stream_file` |
| **Metadata** | `artwork`, `playing` |
| **Apps** | `app_list`, `launch_app` |
| **Keyboard** | `text_input` |
| **Touch** | `swipe`, `tap` |
| **User Accounts** | `switch_account` |

### Optional argument encoding

Leave **Optional Arguments** blank for most commands. The following commands accept arguments:

| Command | Format | Values / example |
|---|---|---|
| `up` `down` `left` `right` `select` `menu` `home` | Integer | `0` = single tap (default), `1` = double tap, `2` = hold |
| `set_repeat` | Integer | `0` = off, `1` = repeat current track, `2` = repeat all |
| `set_shuffle` | Integer | `0` = off, `1` = shuffle album, `2` = shuffle song |
| `set_volume` | Float | `0.0`–`100.0`, e.g. `50.0` |
| `set_position` | Integer | Position in seconds, e.g. `120` |
| `play_url` | URL string | `https://example.com/audio.mp3` |
| `stream_file` | File path or URL | `/Users/indigo/Desktop/bell.mp3` or an HTTPS URL |

**Argument encoding:** The action concatenates the command and argument as `command=arg`. For example, to double-tap the home button, set Command to `home` and Optional Arguments to `1`. To seek to 2 minutes, set Command to `set_position` and Optional Arguments to `120`.

> **Common pitfall — TypeError:** Providing an argument for a command that takes none causes a `TypeError`. The Event Log will say "Optional Arguments for a command that should have none." Clear the Optional Arguments field and save the action.

> **Screensaver auto-dismiss:** If the screensaver is active when a remote command is sent, the plugin automatically sends `menu` to dismiss it, waits 0.5 s, then sends your command.

![Remote Commands detail](https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/remoteNew2.png)

---

## Launch App on AppleTV

Launches an app by its bundle identifier. The app list is fetched from the device when it connects.

![Launch App](https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/lauchApp.png)

| Parameter | Type | Description |
|---|---|---|
| Select Apple TV | Menu | Target device |
| App to Launch | Menu | App to launch — populated from the device's installed app list |

> **App list refresh:** The list is fetched once on connection. If you install new apps, restart the plugin (or disable/enable the device) to refresh it. App launching is supported on Apple TVs only — not HomePods or AirPlay 2 speakers.

---

## Speak Announcement

Converts text to speech using the macOS `say` command, converts the audio to MP3 via the bundled ffmpeg, and streams it to the selected device.

![Speak Announcement](https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/SpeakAnnoucement.png)

| Parameter | Type | Description |
|---|---|---|
| Select Apple TV | Menu | Target device (HomePod or AirPlay 2 speaker recommended) |
| Announce | Text | Text to speak. Supports Indigo variable and device state substitution |

### Indigo substitution syntax

```
%%v:VARID%%                 Variable by ID (find in Indigo's Variables window)
%%d:DEVID:STATEID%%         Device state — e.g. %%d:123456:currentlyPlaying_Title%%
```

> **macOS voice:** The system voice in **System Settings → Accessibility → Spoken Content → System Voice** is used. Change it there to change the announcement voice.

> **ffmpeg quarantine:** If announcements fail with a `CalledProcessError`, run the quarantine command from [Installation](Installation#install) once in Terminal.

> **Concurrency limit:** Only one announcement per device at a time. A second call to the same device while one is in progress is silently dropped. Sending to different devices simultaneously works fine.

---

## Save current Artwork

Fetches the artwork currently displayed on the device and saves it as a PNG.

| Parameter | Type | Default | Description |
|---|---|---|---|
| Select Apple TV | Menu | — | Source device |
| Width (optional) | Text | `512` | Output width in pixels. Height is auto-calculated to preserve aspect ratio. Leave blank for the default |

Saves to: `~/Pictures/Indigo-appleTV/<DeviceName>_Artwork.png`

If no artwork is available (device idle, app doesn't expose artwork, or device doesn't support artwork), the default thumbnail is saved instead.

> **Automatic saving:** For hands-free artwork updates, use the **Auto Save Artwork** checkbox in the device config — no action required.

---

## Save Progress Bar

Generates a transparent PNG image showing a media progress bar at the current playback position.

| Parameter | Type | Default | Description |
|---|---|---|---|
| Select Apple TV | Menu | — | Source device |
| Width (optional) | Text | `800` | Image width in pixels |
| Bar Colour | Menu | White | Fill colour for the completed portion of the bar |

Available colours: White, Black, Red, Green, Blue, Yellow, Cyan, Magenta, Orange, Purple, Pink, Brown, Gray, DarkGray, LightGray, Gold, Silver, Lime, Navy, Teal, Olive, Maroon.

Saves to: `~/Pictures/Indigo-appleTV/<DeviceName>_progressBar.png`

The bar image includes text labels: `0:00` at the left edge, current position centred on the fill edge, and remaining time at the right. Labels that would overlap are automatically hidden.

---

## Manually Update IP Address

Forces a device to a specific IP address and restarts its connection. Use this when a device's IP has changed and it can no longer be found automatically.

| Parameter | Type | Description |
|---|---|---|
| Select Apple TV | Menu | Device to update |
| IP | Text | New IP address (must be a valid IPv4 address) |

The device is disabled and re-enabled automatically after the IP is saved. If the new IP is invalid the action logs an error and does nothing.

---

← [Devices](Devices) → [Troubleshooting](Troubleshooting)
