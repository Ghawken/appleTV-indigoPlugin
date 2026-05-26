![](images/banner3.png)

# Installation

## Requirements

| Requirement | Minimum |
|---|---|
| Indigo | 2023.2 (API 3.4) |
| macOS | Ventura or later recommended |
| Network | Apple TV / HomePod on the same local network segment as the Indigo server |
| Internet | Not required — all communication is local LAN only |

## Install

1. Download the latest release from [GitHub Releases](https://github.com/Ghawken/appleTV-indigoPlugin/releases)
2. Double-click the `appleTV.indigoPlugin` bundle
3. Indigo will prompt you to install — confirm

All required Python libraries (pyatv, Pillow, ffmpeg) are bundled. No manual `pip install` is needed.

> **macOS quarantine note** — on a fresh install, macOS may quarantine the bundled ffmpeg binary used for text-to-speech. If Speak Announcement actions fail, run this once in Terminal (adjust the path to match your Indigo version):
> ```bash
> sudo xattr -rd com.apple.quarantine '/Library/Application Support/Perceptive Automation/Indigo 2025.1/Plugins'
> ```

## First run — generating devices

1. Go to **Plugins → appleTV Plugin → Plugin Config**

   ![Plugin Config](https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/pluginConfig.png)

2. Optionally configure discovery (see [Configuration](Configuration) for details):
   - Tick **Force Discovery of all Devices** if you have an Apple TV 4K gen 3+ or if devices are not found by default
   - Or tick **Scan a single IP address** and enter the device's IP if multicast discovery fails on your network
3. Press **Generate AppleTV Devices**

Indigo creates a device for each discovered Apple TV, HomePod, and (if Force Discovery is on) AirPlay 2 speaker. Devices are placed in the main Devices folder — move them wherever you like. Re-pressing Generate is safe; existing devices are not duplicated.

## Pairing a device

Each Apple TV must be paired before it can push state updates. HomePods typically do not require pairing but still need the connection step.

1. Open the device in Indigo (**Edit Device Details**)

   ![Device Config](https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/DeviceConfig.png)

2. Press **Start Connection** and watch the Indigo Event Log
3. If a PIN is shown on the Apple TV screen:
   - Enter it in the **PinCode** field
   - Press **Submit PinCode (if requested)**
4. If no PIN is needed the log says so — skip straight to step 5
5. Press **Save**

Credentials are stored in the Indigo device properties and survive plugin restarts. Pairing is a one-time step per device.

> **HomePods:** Simply press Start Connection, wait for the log to confirm success, then Save.

> **Force Connection button:** If a tvOS / macOS update changed the device's MAC address (common after iOS/tvOS 18+), use this button to re-pair against the current IP address even if the stored identifier no longer matches.

## Upgrading

1. Download the new `.indigoPlugin` bundle from [GitHub Releases](https://github.com/Ghawken/appleTV-indigoPlugin/releases)
2. Double-click to install — Indigo replaces the plugin in-place
3. Existing devices and their pairing credentials are preserved
4. If the release notes mention a quarantine command, run it once after install

---

← [Home](Home) → [Configuration](Configuration)
