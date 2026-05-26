![](images/banner2.png)

# Support

## Getting help

### Indigo forum

The primary support channel is the Indigo community forum:

**[appleTV Plugin — Indigo forum](https://forums.indigodomo.com/viewforum.php?f=382)**

Search existing threads first — most common questions have already been answered. When posting, include the information in the checklist below.

### GitHub Issues

For confirmed bugs or feature requests:

**[https://github.com/Ghawken/appleTV-indigoPlugin/issues](https://github.com/Ghawken/appleTV-indigoPlugin/issues)**

---

## What to include in a bug report

| Item | Where to find it |
|---|---|
| Plugin version | Plugin Config dialog header |
| Indigo version | Indigo → About Indigo |
| macOS version | Apple menu → About This Mac |
| Device model | Settings → General → About on the Apple TV or HomePod |
| tvOS / audioOS version | Settings → General → About on the device |
| Event Log excerpt | Indigo Event Log with debug level set to `Debugging` (10) or lower |
| Plugin log file | `~/Library/Application Support/Perceptive Automation/Indigo <version>/Logs/com.GlennNZ.indigoplugin.appleTV/` |
| Steps to reproduce | Exactly what you did before the problem occurred |

### Before you post

1. Check [Troubleshooting](Troubleshooting) and [FAQ](FAQ) — the most common issues are covered there
2. Set **Indigo Log Debug level** to `Debugging` (10) in Plugin Config, reproduce the problem, and copy the relevant Event Log section
3. For connection issues, also enable **Debug pyatv Library** (checkbox in Plugin Config) and attach the plugin log file — it captures the raw protocol traffic
4. For TTS / audio issues, run **Plugins → appleTV Plugin → Rerun Ffmpeg Call for logging** and include that output

---

## pyatv library

This plugin is built on [pyatv](https://pyatv.dev) by postlund. For questions about specific device behaviour, protocol limitations, or supported features, the [pyatv FAQ](https://pyatv.dev/support/faq/) and [pyatv GitHub](https://github.com/postlund/pyatv) are useful references.

---

← [Changelog](Changelog)
