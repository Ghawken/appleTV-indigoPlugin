![](images/banner2.png)

# Troubleshooting

## Enabling debug logging

1. Go to **Plugins → appleTV Plugin → Plugin Config**
2. Set **Indigo Log Debug level** to `Debugging` (10) or `Detailed Debugging` (5) to see more in the Event Log
3. Tick **Debug pyatv Library** to capture raw protocol traffic — written to the log **file** only, not the Event Log (very high volume)
4. Tick **Debug Artwork** if artwork is not saving correctly

Return the level to `Informational` (20) when done.

## Log file location

```
~/Library/Application Support/Perceptive Automation/Indigo <version>/Logs/com.GlennNZ.indigoplugin.appleTV/
```

---

## Common errors

### Device not found during Generate

**Symptom:** Pressing Generate AppleTV Devices creates no new devices.

**Fixes (try in order):**
1. Confirm the device is powered on and on the same local network segment as the Indigo server
2. Tick **Force Discovery of all Devices** and press Generate again — required for Apple TV 4K gen 3+
3. Find the device's IP address in your router's DHCP table, tick **Scan a single IP address**, enter the IP, press Generate
4. Assign a static IP in your router so discovery is reliable going forward

---

### "Connection Failed. Retrying…" in device status

**Symptom:** The device shows `Connection Failed. Retrying…` and an error badge in Indigo.

**What the plugin does:** Retries automatically. After 3 consecutive unicast failures it switches to multicast discovery and back. The retry interval grows from 10 s to a cap of 60 s.

**Fixes:**
1. Confirm the Apple TV is on and reachable (ping its IP from the Indigo server)
2. Power-cycle the Apple TV
3. Open the device, press **Start Connection** again

---

### tvOS / iOS 18 — device stops connecting after update

**Symptom:** A device that was working stops connecting after a tvOS update.

**Cause:** iOS/tvOS 18 can reassign device MAC addresses, causing the stored identifier to become stale.

**Fix:**
1. Open the device in Indigo (Edit Device Details)
2. Press **Force Connection to this IP**
3. The plugin updates the stored identifier to match the current address
4. Alternatively, use **Actions → Manually Update IP Address** to force an IP refresh

---

### Speak Announcement fails — CalledProcessError

**Symptom:** Event Log says "Have you run the UnQuarantine terminal Command?"

**Fix:** Run once in Terminal (adjust path to your Indigo version):
```bash
sudo xattr -rd com.apple.quarantine '/Library/Application Support/Perceptive Automation/Indigo 2025.1/Plugins'
```

---

### Speak Announcement fails — TimeoutExpired

**Symptom:** "Speak command failed, because of timeout."

**Cause:** macOS `say` or ffmpeg took longer than 10 seconds. Usually caused by very long text or a heavily loaded machine.

**Fix:** Shorten the announcement text. For long content, pre-generate MP3 files offline and stream them with **Send Command → stream_file**.

---

### Artwork not updating

**Symptom:** `_Artwork.png` is stale, missing, or always shows the default thumbnail.

**Checks:**
1. Confirm **Auto Save Artwork** is ticked in the device config (section only appears after pairing)
2. Check `~/Pictures/Indigo-appleTV/` exists and the Indigo process can write to it
3. Enable **Debug Artwork** in Plugin Config and watch the Event Log for the reason
4. Verify the device is an Apple TV, not a HomePod or AirPlay 2 speaker — most non-Apple-TV devices do not expose artwork via pyatv

---

### TypeError when sending a command

**Symptom:** Event Log says "Optional Arguments for a command that should have none."

**Fix:** Open the action, clear the **Optional Arguments** field, save.

---

### "MRP Protocol disabled" warning in the log

**Symptom:** `<DeviceName> has MRP Protocol disabled on this device. This will impact PowerState reporting.`

**Cause:** The MRP protocol is disabled on this specific device (uncommon). Power state changes will be less reliable or absent.

**Not a crash** — the plugin continues operating. Use `currentlyPlaying_PlayState` or `currentlyPlaying_DeviceState` for trigger conditions instead of power state.

---

### App list is empty in Launch App action

**Symptom:** The App to Launch dropdown is empty or missing apps.

**Cause:** The app list is fetched once when the device connects. Newly installed apps are not picked up until the next connection.

**Fix:** Disable and re-enable the Indigo device (or restart the plugin) to force a reconnect and re-fetch the app list.

---

## Menu diagnostics

**Plugins → appleTV Plugin → Device Further Info**

| Option | Output |
|---|---|
| Scan and Display Info on Device | Full pyatv scan result for the selected device (protocols, ports, services) |
| List supported Commands | All commands the connected device currently supports |
| Detailed Info on Each Command | Signature and docstring for every command on the device |
| List supported Features | Feature availability: Available / Unavailable / Unknown / Unsupported |

**Plugins → appleTV Plugin → Scan for Devices and Log results** — rescans the whole network and logs a table of discovered devices. Use this to confirm a device is visible before attempting to pair.

**Plugins → appleTV Plugin → Rerun Ffmpeg Call for logging** — re-runs the last ffmpeg command with visible output to the Event Log. Use this when TTS is failing silently.

---

## Filing a useful bug report

Include all of the following in your post or issue:

| Item | Where to find it |
|---|---|
| Plugin version | Plugin Config dialog header |
| Indigo version | Indigo → About Indigo |
| macOS version | Apple menu → About This Mac |
| Device model and tvOS version | Settings → General → About on the device |
| Event Log with debug enabled | Set debug level to 10, reproduce, copy the log |
| Plugin log file | Path above — attach or paste the relevant section |
| Steps to reproduce | Exactly what you did before the problem appeared |

→ See [Support](Support) for where to post.

---

← [Actions](Actions) → [FAQ](FAQ)
