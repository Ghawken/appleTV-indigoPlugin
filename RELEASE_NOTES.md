# appleTV Plugin – Release Notes

## 1.8.6 – 1.8.8

Support for the new **Apple TV 4K (4th generation)** and **tvOS 27**, a much more reliable connection layer, and an easy way to replace an Apple TV.

### Why a custom pyatv build?

The plugin is built on [pyatv](https://pyatv.dev). Upstream pyatv hasn't had a commit or release since **19 June 2026 (v0.18.0)**. Since then, the community has submitted dozens of fixes that are still waiting to be merged, including support for new hardware and tvOS 27.

From 1.8.7 the plugin installs pyatv from [Ghawken/pyatv – `indigo` branch](https://github.com/Ghawken/pyatv/tree/indigo). That branch is upstream pyatv 0.18.0 plus a selected set of those pending fixes. All of them pass pyatv's full test suite: 1325 passed, 6 skipped. The current version is **`0.18.0.post2`**. If upstream starts releasing again, the plugin will move back to the official package.

Indigo installs the new library automatically when you update the plugin.

---

### Library improvements (pyatv)

#### New hardware & tvOS 27
| Improvement | What it means for you | Upstream PR |
|---|---|---|
| **Apple TV 4K (4th generation) recognised** | The new `AppleTV18,1` model shows as "Apple TV 4K (gen 4)" running tvOS, not "Unknown". | [#2949](https://github.com/postlund/pyatv/pull/2949) |
| **AirPlay PIN pairing fixed on tvOS 27** | tvOS 27 could stop the pairing PIN from appearing on screen. pyatv now sends the client name tvOS 27 expects, so the PIN appears. | [#2894](https://github.com/postlund/pyatv/pull/2894) |
| **Pairing errors reported instead of hanging** | If a device rejects pairing, you now get an immediate error. Previously it hung for about 10 seconds and then failed with a confusing error. | [#2920](https://github.com/postlund/pyatv/pull/2920) |
| **Clearer authentication errors** | AirPlay remote-control authentication failures now show the real reason. | [#2924](https://github.com/postlund/pyatv/pull/2924) |

#### Connection reliability
| Improvement | What it means for you | Upstream PR |
|---|---|---|
| **No leaked connections on failed connects** | When a connection attempt failed part-way, pyatv left network connections open. The plugin retries automatically, so a device that was offline or asleep could pile these up. Failed attempts now clean up fully. | [#2945](https://github.com/postlund/pyatv/pull/2945) |
| **Companion protocol errors raised properly** | Error replies from the Apple TV are now treated as errors, not as successful responses. | [#2939](https://github.com/postlund/pyatv/pull/2939) |

#### Discovery (finding your devices)
| Improvement | What it means for you | Upstream PR |
|---|---|---|
| **Unicast (by-IP) scans wait for all services** | The plugin scans by IP address first. These scans used to stop early, which could miss services that are slow to appear (e.g. Companion just after the Apple TV wakes). Missing Companion affects power state and app launching. | [#2911](https://github.com/postlund/pyatv/pull/2911) |
| **Fallback scan asks for every service type** | The backup scan method now looks for all of a device's services, not just some of them. | [#2930](https://github.com/postlund/pyatv/pull/2930) |
| **Unusual device names no longer abort a scan** | A device name the network library refuses is now skipped instead of stopping the whole scan. | [#2936](https://github.com/postlund/pyatv/pull/2936) |
| **Malformed network packets ignored** | Truncated or malformed mDNS packets on the network no longer upset discovery. | [#2926](https://github.com/postlund/pyatv/pull/2926) |
| **Multi-VLAN / mDNS-reflector networks** | If your Apple TVs are on a different subnet behind an mDNS reflector (UniFi, Firewalla, Avahi), devices were mixed up: wrong models were shown, or every device appeared to be in deep sleep. Each device is now tracked separately. | [#2931](https://github.com/postlund/pyatv/pull/2931) |

#### Playback & device state
| Improvement | What it means for you | Upstream PR |
|---|---|---|
| **Playback position NaN fixed** | Some apps report an invalid elapsed time, which broke the position and remaining-time calculations. | [#2897](https://github.com/postlund/pyatv/pull/2897) |
| **No bogus volume updates** | When the device doesn't report a volume, pyatv no longer sends a false value. | [#2935](https://github.com/postlund/pyatv/pull/2935) |
| **HomePod stereo pairs show as On** | The lead HomePod in a stereo pair reported power Off while playing. | [#2917](https://github.com/postlund/pyatv/pull/2917) |
| **Audio streaming deadlock fixed** | Streaming some URLs/internet streams to AirPlay devices could stall and fail with "failed to init decoder". | [#2850](https://github.com/postlund/pyatv/pull/2850) |
| **AirPlay feature detection for third-party receivers** | Fixes wrong capability detection on some receivers, e.g. LG TVs. | [#2942](https://github.com/postlund/pyatv/pull/2942) |

Also included: [#2907](https://github.com/postlund/pyatv/pull/2907) (typing fix) and [#2909](https://github.com/postlund/pyatv/pull/2909) (test fixes for newer zeroconf).

---

### Plugin improvements

**1.8.8**
- Uses pyatv `0.18.0.post2`, which adds Apple TV 4K (4th generation) support.

**1.8.7**
- **Fixed connections constantly dropping and reconnecting after re-pairing.** Stopping a device during start-up could leave an orphaned connection running in the background. It then fought with the new connection, and each knocked the other off in a loop. Old connections now always shut down properly, and a device can only ever have one connection.
- Switched to the custom pyatv build above.

**1.8.6**
- **New "Reset Device" button** in the device config dialog, for when you replace an Apple TV (e.g. a new unit on the same IP address). It stops the current connection and clears the saved pairing credentials, identifier and MAC address. It keeps the IP address and removes the old Apple TV's saved pairing data.
- **Start Connection** now pairs with whatever Apple TV is at the device's IP after a reset.
- A log message now explains when no matching Apple TV is found. Previously it failed silently.

---

### Replacing an Apple TV

1. Open the Indigo device → **Edit Device Settings**.
2. Press **Reset Device**.
3. Press **Start Connection**, enter the PIN shown on the TV, and press **Submit PinCode**.
4. Press **Save**.

If the connection keeps cycling after re-pairing on an older version, restart the plugin. 1.8.7 and later prevent this.
