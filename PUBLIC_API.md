# Zentraly public Python API

Distribution and import name: **zentraly**. This document defines the public consumer contract for release `0.4.0`.

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

### Child limits and new settings (unreleased)

`get_max_child_devices(device_id)` returns `int | None`: `None` means no limit
imposed by the integration, `0` means no children, and positive integers are
finite limits. Check parent/child compatibility separately with
`is_allowed_child_device`; an unlimited count does not allow unknown models.
Existing models keep their previous integer limits. Consumers supporting the new
gateways must handle `None` before doing numeric comparisons.

`ZentralySensorApi.async_get_battery_level()` returns an integer percentage from
0 to 100 (or `None` if unavailable), without sentinel values or scaling.
`ZentralyNumberApi.async_get_boiler_ignition_delay()` and
`async_get_boiler_shutdown_delay()` return minutes; their matching setters accept
whole minutes from 0 to 10. Zero has no special client-side behavior.
`ZentralySwitchApi.async_get_disconnect_on_error()` and its matching setter use
booleans. These configuration setters only write the selected parameter. They do
not change operating mode, switch outputs or start client-side timers.

### Connection lifecycle

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

## Device information and endpoints

`ZentralyDevice.supports_device_info` indicates whether at least one version can
be read. `await device.async_get_device_info()` returns `ZentralyDeviceInfo`,
a frozen result with optional `firmware_version` and `hardware_version` strings.
Unsupported, disconnected or malformed readings are `None`; a valid sibling
field is still returned. Connection-busy errors propagate as before. The method
does not change cached version properties: callers decide how to retain and
publish last-known values. Callers schedule refreshes; the library handles
builders, RID correlation and parsers.

`device.channel_endpoints` is the tuple of supported channel endpoints. It is
model metadata and supports any number of channels. Existing public factories
and capability APIs remain compatible.

## Periodic polling policy

`ZentralyDevice.supports_periodic_polling` exposes the model policy from the device
catalog. Clients must not schedule recurring reads (including version metadata)
when it is false. Initial reads, reconnection reads, explicit requests and writes
remain supported, as do incoming reports. This policy does not affect the gateway
connection keepalive. ZTTZB, ZTAAI, ZTHZB, ZTHG2 and ZTAAK disable periodic polling; all other current
models enable it. The value is explicit model metadata, not inferred at runtime
from the presence of a battery capability.


## Independent capability prerequisites (0.4.0)

Client platforms do not need to construct sensor or switch entities to initialize
shared prerequisites. Functional read/write APIs resolve their own prerequisites.
Before evaluating cached availability, clients can call
`await device.async_refresh_dependencies(capability, endpoint=1)`. This reads
only the switch dependency declared by the model, or the output type needed by
an OpenTherm capability. It never changes the device configuration.

The runtime shares in-flight reads per device, endpoint and prerequisite. A
successful result is reused for one second to coalesce adjacent entity updates;
there is no background timer and this is not a polling interval. The caller
continues to schedule updates and must respect `supports_periodic_polling`.
Explicit sensor/switch reads request a fresh value, sharing an in-flight request
if present. Reports and confirmed writes update the same state and supersede
older in-flight responses. Failed output-type reads return `None` while retaining
the last known output type, as before; failed switch prerequisites become unknown.

`await device.async_refresh_shared_state()` optionally initializes all declared
prerequisites for consumers that initialize devices before creating controls.
`async_get_shared_state(capability, endpoint=1)` reads a declared prerequisite
without constructing another functional API. Connection callbacks registered
through the device invalidate shared state and pending reads on disconnection;
consumers should subscribe for their runtime lifecycle. Removing the final state
and report subscriptions also releases pending shared reads.

The HA adapter requests prerequisites during each dependent entity's initial,
reconnect and standard HA updates. Boiler-reset buttons refresh only their
availability prerequisite; periodic updates never press a button. Reset-device
and refresh-device-info buttons do not gain periodic reads. Battery and gateway
models with periodic polling disabled retain initial, explicit and reconnect
reads, plus reports. Firmware/hardware refresh rules are unchanged.

### Delivery order for Home Assistant

Publish a new library version first. Submit the standalone dependency bump, then
the shared integration foundation. Once that common base is accepted, each
platform addition can branch from the same accepted commit; no platform PR
requires another platform PR. Each must include its own entity translations,
platform-specific tests and a representative supported model if the initial
thermostat lacks that platform. Shared helper changes belong in the foundation.
Review feedback must be propagated to the complete integration when applicable.
