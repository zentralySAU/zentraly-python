# Changelog

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
