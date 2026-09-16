# Zentraly public Python API

Distribution and import name: **zentraly**. This document defines the public consumer contract for release `0.1.0`.

## Supported imports

Use package-root imports, for example:

```python
from zentraly import (
    NumberCapability,
    ZentralyApi,
    ZentralyNumberApi,
    ZentralyValidationError,
    create_device,
)
```

`zentraly.__all__` explicitly lists the exports. These are re-exports of the
original classes/functions, without wrappers, copied enums or new subclasses.
Existing module imports still work and retain class/exception identity. Future
internal reorganization must preserve root imports.

| Group | Public exports |
| --- | --- |
| Runtime | `ZentralyApi`, `ZentralyDevice`, `create_device` |
| Functional APIs | `ZentralyBinarySensorApi`, `ZentralyButtonApi`, `ZentralyClimateApi`, `ZentralyNumberApi`, `ZentralySelectApi`, `ZentralySensorApi`, `ZentralySwitchApi` |
| Capabilities | `BinarySensorCapability`, `ButtonCapability`, `ClimateCapability`, `NumberCapability`, `SelectCapability`, `SensorCapability`, `SwitchCapability` |
| Types | `ClimateConfiguration`, `ClimateOperationMode`, `DisplayMode`, `SelectOperationMode`, `ZentralyOutputType` |
| Models | `DeviceModel`, `get_device_model`, `get_device_commands`, `get_max_child_devices`, `is_allowed_child_device`, `supports_child_devices`, `supports_zeroconf_setup` |
| Errors | `ZentralyApiError`, `ZentralyAuthenticationError`, `ZentralyConnectionError`, `ZentralyConnectionBusyError`, `ZentralyInvalidResponseError`, `ZentralyCommandRejectedError`, `ZentralyValidationError` |

The contract covers the operations below and each functional API's public
`supports`, configuration accessors, state subscriptions and annotated read/write
or action methods. Only model-supported operations are valid. Being accessible as
a Python attribute is not by itself a compatibility promise. Private `_` fields,
transport tasks/queues, concrete model modules, mutable catalog dictionaries and
wire builders/parsers are implementation or model-extension details.
`get_device_commands` supports capability/configuration inspection; it does not
make every concrete model method an application contract.

Legacy client methods `async_update` and `async_get_device_info` are no-ops, not
supported refresh APIs. They remain available. Legacy client hardware/firmware
placeholders do not query the device.

## Compatibility policy

Patch releases preserve the public contract; minor releases add compatible
functionality. Necessary incompatible changes require changelog and migration
notes: a minor increment during 0.x, and a major increment from 1.0. Prefer a
deprecation period. Enums and the catalog may gain new capabilities/models; do not
assume their current members are exhaustive forever. Internal imports are retained
in this change; only the root is the long-term import contract.

## Lifecycle

- `ZentralyApi(host, port, password, device_id, mac="", *, session=None)` creates
  a client without connecting. The caller supplies address/identity; the package
  does not perform mDNS discovery.
- `await client.async_validate_password()` temporarily connects, authenticates,
  reads and returns the MAC, then closes that transport even on error.
- `create_device(client, device_id, mac)` creates a runtime sharing that client;
  it does not connect or validate hardware. Unknown models raise `ValueError`.
- `await client.async_connect()` starts the background connection loop without
  waiting for login. Register `add_connection_state_listener(callback)` before
  connecting and observe its boolean updates or `connected`.
- `add_authentication_error_listener(callback)` reports rejected credentials to
  the application, which decides how to request replacements.
- `await client.async_validate_child_device(device_id, mac)` uses the connected
  parent. Unknown models/invalid validation responses can raise `ValueError`;
  unavailable parent/no response produces connection errors. Callers also enforce
  allowed topology, duplicate IDs and capacity.
- `await client.async_execute_command(builder)` is a low-level escape hatch
  returning `(rid, response)` or `None`; saturation can raise a connection error.
  Prefer capability APIs for model-independent applications.
- `device.supports`, `available`, `connected` and `capability_enabled` expose
  capability/availability information. Shared parent/child clients retain separate
  MAC/runtime state. Number, select and switch APIs accept keyword `endpoint=1`;
  it identifies a channel, not a new device. Capabilities remain model-wide.
- State listener registration returns an unsubscribe callable. Callbacks are
  synchronous, must not block the event loop, have no promised ordering and do
  not promise initial state replay. Remove them on shutdown.
- Await `client.async_disconnect()` to cancel work and finish pending/queued
  requests without replay on the next connection.

A supplied `aiohttp.ClientSession` remains caller-owned through validation,
reconnect and disconnect. The library closes WebSockets, never that session.
Without injection the transport creates/closes its own sessions. Use objects on
their asyncio event loop; cross-thread sharing is not promised.

## Values, errors and updates

High-level APIs use semantic units. For ZTTIN/ZTTWZ,
`async_set_temperature_offset(-1.2)` takes degrees and the model writes -120;
callers must not scale again. `get_range` returns `(minimum, maximum, step)`.
Read `None` means no usable value, not zero/false. Action methods return their
annotated result after confirmation or raise an error; not every method has the
same return type.

Domain errors derive from `ZentralyApiError`. `ZentralyConnectionBusyError` also
derives from `ZentralyConnectionError`; catch busy first when handling it
separately. Action value errors use `ZentralyValidationError`, device rejection
uses `ZentralyCommandRejectedError` and malformed action responses use
`ZentralyInvalidResponseError`. Factory/configuration construction can raise
`ValueError`. HA exceptions and translation keys are not part of the library.

Capability listeners receive dictionaries keyed by the group's enum, containing
reported changes only. Consumers preserve omitted fields. Report routing retains
MAC and endpoint. Subscriptions do not add capabilities, create entities or start
periodic refreshes. HA schedules its own polling; other applications choose theirs.

## Catalog and HA boundary

`get_device_model` uses the first five case-sensitive ID characters, returning
`DeviceModel.UNKNOWN` if unrecognized. Topology/Zeroconf helpers return false or
zero for unknown devices; `get_device_commands` raises `ValueError` for an
unsupported model. Helpers inspect metadata, not the network or Excel.

HA imports these root exports to instantiate APIs, inspect capabilities, validate
topology and translate errors. Entities, DeviceInfo, config flow, UI units,
categories/translations and refresh scheduling stay in HA. The package runs with
asyncio/aiohttp alone. Concrete models remain independent in `devices/`.
