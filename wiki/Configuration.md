![](images/banner2.png)

# Configuration

Plugin Config is accessed via **Plugins → appleTV Plugin → Plugin Config**.

![Plugin Config](https://raw.githubusercontent.com/Ghawken/appleTV-indigoPlugin/master/Images/pluginConfig.png)

## Device discovery

| Field | Type | Default | Description |
|---|---|---|---|
| Force Discovery of all Devices | Checkbox | Off | Discovers every AirPlay device on the network, including non-Apple AirPlay 2 speakers. Required for Apple TV 4K gen 3+ and some newer models that appear as "Unknown" in a standard scan |
| Scan a single IP address | Checkbox | Off | Restricts the scan to one IP address using unicast. More reliable than multicast when a device is present but not found by the default network-wide scan |
| IP address | Text | — | The IP to scan when **Scan a single IP address** is enabled. Only visible when that checkbox is ticked |
| **Generate AppleTV Devices** | Button | — | Runs the network scan and creates Indigo devices for any newly discovered Apple TVs and HomePods. Safe to press again — existing devices are not duplicated; their IP address is updated if it has changed |

> **Tip:** If a device is not found with the default multicast scan, assign it a static/fixed IP in your router and use the **Scan a single IP address** option. A dynamic IP that changes will cause the plugin to lose the device on next restart.

## Debug options

| Field | Type | Default | Description |
|---|---|---|---|
| Debug pyatv Library (Verbose) | Checkbox | Off | Enables full pyatv library debug output. Written to the **log file only** — not the Indigo Event Log. Very high volume; enable only when diagnosing connection or protocol issues |
| Debug Artwork | Checkbox | Off | Logs artwork download, processing, and file-save operations to the Event Log |
| Indigo Log Debug level | Menu | Informational (20) | Controls verbosity shown in the Indigo Event Log |
| File Debug level | Menu | Detailed (5) | Controls verbosity written to the plugin's rotating log file |

### Log level reference

| Value | Label | Use for |
|---|---|---|
| 5 | Detailed Debugging | Maximum verbosity — everything |
| 10 | Debugging | Function-level tracing |
| 20 | Informational | Normal operation (default) |
| 30 | Warning Messages | Warnings and above only |
| 40 | Error Messages | Errors only |
| 50 | Critical Errors Only | Silence everything but crashes |

## Log file location

```
~/Library/Application Support/Perceptive Automation/Indigo <version>/Logs/com.GlennNZ.indigoplugin.appleTV/
```

This file captures everything, including pyatv library verbose output when Debug 1 is enabled. It rotates automatically so it does not grow unbounded.

---

← [Installation](Installation) → [Devices](Devices)
