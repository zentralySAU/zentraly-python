# Zentraly Python client (local development)

Independent asynchronous device library extracted from the Zentraly integration.
The distribution and import name are zentraly; the owner is not finalized. Version 0.0.0.dev0 is local only.
Python 3.14 or newer is required. No Home Assistant dependency.

## Installation and development

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

## Release checklist (not yet authorized)

1. Confirm PyPI availability of the chosen name zentraly and finalize owner,
   repository URL and project metadata.
   The Python import name and distribution name may differ; keep imports stable.
2. Review licensing and retained attribution. The extraction retains Apache-2.0.
3. Choose a release version, update pyproject.toml and changelog, run both library
   and HA tests, packaging checks and real-device acceptance tests.
4. Publish the reviewed source repository, configure the `pypi` GitHub environment
   with required approval, and register this workflow as a PyPI Trusted Publisher.
5. Set repository variables `PYPI_PROJECT_NAME` and `PYPI_PUBLISH_ENABLED=true`.
6. Tag the reviewed version as `v<version>`, then manually dispatch publish.yml
   against that tag. The CI build is required before publication. Release version
   0.0.0.dev0 is explicitly blocked. No credentials belong in this repository.
7. Pin the published version in HA's manifest and regenerate HA derived dependency
   files. Run HA CI before submitting the integration upstream.

The workflows are prepared for the future standalone repository. While this
folder is ignored inside the HA checkout they do not run on GitHub. There is no
remote or PyPI project configured yet. A TestPyPI rehearsal is optional and must
be configured separately before use; this workflow targets real PyPI.

## Project status and ownership

The user has reported successful physical-device tests after extraction; model
and firmware coverage were not specified. Automated evidence remains 190 HA
cases and 86 standalone library cases, also verified against built wheels.

A move to a new GitHub account is planned before publication. The existing HA
fork will be transferred, while this independent Git history will be published
in a separate library repository. Documentation/Excel/backups will have a
separate home; ignored files are not included in a Core push.

Root imports, results, errors, units and listener/session lifecycle are documented
in PUBLIC_API.md. Existing module imports remain available in this change.
This Python API requires no HTTP server or Home Assistant.
