# Zentraly Python client

Independent asynchronous device library extracted from the Zentraly integration.
The distribution and import name are zentraly. The repository owner is zentralySAU.
The first release is 0.1.0.
Python 3.14 or newer is required. No Home Assistant dependency.

## Installation

```sh
python3 -m pip install zentraly==0.1.0
```

## Development

```sh
python3 -m venv .venv
.venv/bin/python3 -m pip install -e '.[dev]'
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/zentraly
.venv/bin/python3 -m build
.venv/bin/python3 -m twine check --strict dist/*
```

The `src` layout ensures tests use the installed package. The CI additionally
installs the built wheel into a fresh environment and reruns the tests without HA.
`py.typed` is included. Tests require no real device and do not send commands to hardware.

## Public API

```python
import asyncio
import os

from aiohttp import ClientSession
from zentraly import ZentralyApi, ZentralyNumberApi, create_device


async def main():
    async with ClientSession() as session:
        client = ZentralyApi(
            os.environ["ZENTRALY_HOST"],
            80,
            os.environ["ZENTRALY_PASSWORD"],
            os.environ["ZENTRALY_DEVICE_ID"],
            session=session,
        )
        # Temporary authentication and model-specific MAC discovery.
        mac = await client.async_validate_password()
        device = create_device(client, client.device_id, mac)
        number = ZentralyNumberApi(device)
        connected = asyncio.Event()
        remove_connection = client.add_connection_state_listener(
            lambda online: connected.set() if online else connected.clear()
        )
        remove_updates = number.add_state_listener(print)
        try:
            # Starts a background reconnect loop; does not wait for a login.
            await client.async_connect()
            await asyncio.wait_for(connected.wait(), timeout=30)
            print(await number.async_get_temperature_offset())
            # An explicit write, only if the application requests it:
            # await number.async_set_temperature_offset(-1.2)
        finally:
            remove_updates()
            remove_connection()
            await client.async_disconnect()


asyncio.run(main())
```

Capability enums and command contracts live under `zentraly.device_classes`.
Device implementations and topology live under `zentraly.devices`; catalog
helpers are in `zentraly.devices.catalog`. The root exports client/runtime, capability APIs/enums, semantic types, model
helpers and errors. Use these imports; see [PUBLIC_API.md](PUBLIC_API.md) for the
compatibility and lifecycle contract. Home Assistant entity classes are not part of this package.

Children use `create_device(parent_client, child_id, child_mac)` and share the
parent connection. `async_validate_child_device` validates them on that connection;
applications must also enforce catalog parent/child compatibility and limits.
Number/select/switch APIs accept `endpoint=` for supported channels. Reports retain
MAC and endpoint, and missing attributes do not erase previously received fields.

Read helpers may return `None` when no valid response is available. Action failures
raise exceptions from `zentraly.exceptions`; UI translation belongs to the caller.
The raw `async_execute_command(builder)` returns `(rid, response)` or `None`.
Listener registration returns an unsubscribe callable. Unsubscribe and disconnect
on shutdown. No background work starts merely by importing or creating a device.

A supplied `ClientSession` remains owned by its caller, including on failed
validation, reconnect and disconnect. Without injection, transports create and
close their own sessions. HA always supplies its shared session.

## Preserved behavior

- 20 in-flight requests per physical connection; FIFO wait, warning at capacity.
- Response timeout 30 seconds; maximum queue wait 60 seconds.
- Queue threshold 10 logs an error but does not reject requests by queue size.
- Keepalive uses the same queue, with no priority. Disconnect resolves outstanding
  requests without replaying them on the next connection.
- Device models preserve scales, ranges, independent implementations and action
  sequences. Display dependencies expose control availability; they do not add a
  new protocol write restriction.
- HA owns entity refresh scheduling, registry data, entity names, UI categories,
  unit constants, translations and timer presentation.

## Releasing

The GitHub Actions workflow `publish.yml` uses PyPI Trusted Publishing. The `pypi`
environment requires release approval and accepts version tags. Repository
variables are `PYPI_PROJECT_NAME=zentraly` and `PYPI_PUBLISH_ENABLED=true`.

1. Update pyproject.toml and CHANGELOG.md for the reviewed release.
2. Run library and HA tests, type/format checks, build and strict Twine validation.
   Build into an empty output directory so previous versions are not uploaded.
3. Commit the reviewed release and tag it as `v<version>`.
4. Dispatch `publish.yml` manually against that tag. CI must pass before publishing;
   approve the `pypi` environment deployment for the reviewed commit.
5. Verify the PyPI files and install the published version in a clean environment.
6. Pin the published release in HA, regenerate dependency files and validate CI.

The release guard checks project name, repository URL and tag/version agreement;
it rejects the former local version 0.0.0.dev0. No API token is stored in this
repository. A TestPyPI rehearsal needs separate configuration; this workflow
publishes to production PyPI. Never replace a version already uploaded to PyPI.

## Project status and ownership

The user has reported successful physical-device tests after extraction; model
and firmware coverage were not specified. Automated evidence remains 190 HA
cases and 86 standalone library cases, also verified against built wheels.

The HA fork belongs to zentralySAU. This library lives in the separate
zentraly-python repository; its sibling zentraly-documentos contains private
documentation and the Excel. Neither is included in a Core push. See
LOCAL_DEVELOPMENT.md for the multi-repository workspace and editable installation.

Root imports, results, errors, units and listener/session lifecycle are documented
in PUBLIC_API.md. Existing module imports remain available in this change.
This Python API requires no HTTP server or Home Assistant.
