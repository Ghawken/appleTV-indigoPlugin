![](images/banner3.png)

# FAQ

## Setup & discovery

**Q: Generate AppleTV Devices found nothing. What should I try?**

First tick **Force Discovery of all Devices** and press Generate again — this is required for Apple TV 4K gen 3+ devices that appear as "Unknown" in a standard scan. If still nothing, find the device's IP in your router's DHCP list, tick **Scan a single IP address**, enter the IP, and press Generate. If unicast finds it but multicast doesn't, assign a static IP in your router to ensure reliable future discovery.

---

**Q: Do I need to re-pair after every plugin restart?**

No. Pairing credentials are stored in the Indigo device's plugin properties and loaded automatically on each connection. Re-pairing is only necessary if credentials become invalid (rare) or after certain tvOS updates that change device identifiers.

---

**Q: Can I manage multiple Apple TVs?**

Yes — one Indigo device per physical device. Run Generate AppleTV Devices once; it creates a device for each one found. Devices can be moved to any Indigo folder after creation.

---

**Q: My AirPlay 2 speaker (Sonos, etc.) was created but commands don't work.**

AirPlay 2 speakers support audio streaming only. Remote control and push state updates are not available for non-Apple AirPlay 2 devices — this is a protocol limitation, not a plugin bug. Use **Send Command → stream_file** or **Speak Announcement** to play audio to them.

---

**Q: How do I remove a device I no longer need?**

Delete the Indigo device as normal. If you want to prevent it being re-created on the next Generate run, make sure the physical device is off or unreachable during that scan.

---

## Network & connectivity

**Q: Does the plugin require internet access?**

No. All communication is local LAN only via pyatv. No cloud services, no API keys, no external endpoints.

---

**Q: My Apple TV keeps dropping and reconnecting. Is that normal?**

Occasional disconnects are expected — Apple TVs go into deep sleep and the protocol connection drops. The plugin reconnects automatically, alternating between unicast (IP-based) and multicast discovery. If disconnects are very frequent, check that the Apple TV has a stable IP (assign a static one), and that the network does not block mDNS/Bonjour between the Indigo server and the device.

---

**Q: The log says it switched to "Multicast Discovery" — what does that mean?**

After 3 consecutive unicast failures the plugin falls back to a network-wide multicast scan to find the device. It alternates back to unicast after 3 more attempts. If multicast succeeds and unicast doesn't, the device's IP is probably changing — assign a static IP.

---

**Q: Do I need to open any firewall ports?**

No. The plugin makes outbound connections to devices; it does not listen on any ports itself.

---

## Pairing & authentication

**Q: The Apple TV showed a PIN but I dismissed it before entering it. What now?**

Press **Start Connection** in the device config to restart the pairing process from the beginning.

---

**Q: The log says "Pairing is Unsupported" or "Pairing is Not Needed". Is that an error?**

No. HomePods and some older AirPlay devices do not require AirPlay pairing. The plugin connects without credentials. Press **Save** when prompted.

---

**Q: tvOS 18 updated and now my Apple TV won't connect.**

iOS/tvOS 18 can reassign device MAC addresses. Use **Force Connection to this IP** in the device edit screen to update the stored identifier to the current one. See [Troubleshooting](Troubleshooting#tvos--ios-18--device-stops-connecting-after-update) for the full procedure.

---

## Artwork & images

**Q: Where are artwork and progress bar files saved?**

`~/Pictures/Indigo-appleTV/` on the machine running the Indigo server. Files are named `<DeviceName>_Artwork.png` and `<DeviceName>_progressBar.png`.

---

**Q: Can I use a custom default artwork image?**

Yes. Replace `~/Pictures/Indigo-appleTV/apple-tv-default-thumb.png` with your own PNG (same filename). Delete the file and restart the plugin to restore the built-in default.

---

**Q: Artwork isn't showing for HomePods or AirPlay speakers.**

Most non-Apple-TV devices do not expose artwork via pyatv. This is an Apple / protocol limitation. The plugin logs a debug message when artwork is not supported — it is not an error.

---

**Q: The progress bar only updates every 10 seconds. Can I make it faster?**

The bar updates on every push event from the device (which is immediate) and also every 10 seconds from the plugin's internal tick loop. You cannot make the tick interval shorter from within the plugin. For near-real-time position display, trigger **Save Progress Bar** from an Indigo trigger on `currentlyPlaying_PlayState` changes.

---

## Text-to-speech

**Q: What voice is used for announcements?**

The macOS system voice configured in **System Settings → Accessibility → Spoken Content → System Voice**.

---

**Q: Can I pre-generate audio files instead of using the Speak Announcement action?**

Yes. In Terminal:
```bash
say "Your announcement text" -o output.aiff
ffmpeg -i output.aiff -f mp3 -acodec libmp3lame -ab 192000 -ar 44100 output.mp3
```
Then use **Send Command → stream_file** with the full path to `output.mp3`.

---

**Q: Can I speak to multiple HomePods at the same time?**

Yes — add multiple Speak Announcement actions to an Indigo action group, one per device. Each runs in its own thread so they start nearly simultaneously. Sending two announcements to the *same* device simultaneously will drop the second one.

---

## Rate limits & performance

**Q: Are there any rate limits?**

No API rate limits — it is all local. Practical limits: only one TTS announcement per device at a time (the second is silently dropped). Artwork processing at large widths is CPU-bound on the Indigo server.

---

**Q: How quickly do play/pause state changes appear in Indigo?**

Essentially instant. pyatv uses push updates — the Apple TV sends an event to the plugin the moment the state changes. There is no polling delay.

---

← [Troubleshooting](Troubleshooting) → [Changelog](Changelog)
