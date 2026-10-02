# Changelog

## 0.3.0 — 2026-10-02

- Expose a per-model periodic polling policy, disabled for ZTTZB, ZTAAI, ZTHZB, ZTHG2 and ZTAAK.
  Initial, reconnect and explicit reads remain supported.

## 0.2.0 — 2026-10-01

- Add independent models for ZTHZB, ZTHG2, ZTAAK, ZTTZB, ZTAAI, ZTMWZ,
  ZTBZB, ZTBZH and ZTEIE, including discovery and child validation.
- Add battery percentage, boiler ignition/shutdown delay and disconnect-on-error
  capability APIs. Configuration writes change only their own parameter.
- Return `None` from `get_max_child_devices` for unlimited gateways. Consumers
  must check for `None` before comparing child counts; existing limits retain
  their integer values. This API extension requires a minor release during 0.x.
- Keep battery polling and Wi-Fi signal behavior unchanged in this release work.

## 0.1.1 — 2026-09-16

- Add public device information reads and immutable ZentralyDeviceInfo results.
- Keep protocol construction and version parsing inside the library.
- Expose channel_endpoints as public device metadata.
- Preserve existing commands, units, transport and capability APIs.

## 0.1.0 — 2026-09-16

- Extract Zentraly transport, client, commands, device catalog, runtime and
  capability APIs from Home Assistant without changing the device protocol.
- Support caller-owned aiohttp sessions and independent credential redaction.
- Move communication and model configuration regression tests out of HA.
- Prepare typed wheels, source distributions, independent CI and guarded release.
- Define root exports for capability APIs/enums, types, model helpers and errors;
  preserve existing module imports and class identity.
- Document units, errors/results, listener/session lifecycle and compatibility
  policy in PUBLIC_API.md; choose zentraly as the package name.
