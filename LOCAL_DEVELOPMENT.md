# Local HA extraction

This folder is an independent Git repository, ignored by the containing Core
checkout through `.git/info/exclude`. Do not add it to Core or vendor it inside
`homeassistant/components`. It has no remote and has not been published.

Core baseline: tag `zentraly-stable-before-library-2026-09-16`, commit
`4d254fd7a55021d974a5b27fa873e043aae76aeb`.
Core working branch: `codex/zentraly-library`.

## Install into the existing HA environment

From the Core checkout:

```sh
uv pip install --python /home/vscode/.local/ha-venv/bin/python3 --no-deps -e zentraly_library
UV_PROJECT_ENVIRONMENT=/home/vscode/.local/ha-venv uv run --no-sync pytest tests/components/zentraly -q
UV_PROJECT_ENVIRONMENT=/home/vscode/.local/ha-venv uv run --no-sync python3 -m script.hassfest --action validate --integration-path homeassistant/components/zentraly
```

The provisional manifest requirement is `zentraly==0.0.0.dev0`; it resolves only
because this local distribution is installed. It is not a published release.
A fresh CI runner cannot install it from PyPI. Do not submit this as a ready PR.
An environment sync/rebuild may require reinstalling the editable package.

The library has its own `.venv` and `pyproject.toml`; its tests do not load HA's
pytest fixtures. Run commands from this directory, not the Core test root.
No new secrets or default hardware credentials are provided.

## Scope of the extraction

- Protocol, transport, client, model catalog, models and capability APIs moved to
  `src/zentraly`. `devices/device.py` became `devices/catalog.py`.
- Runtime state moved to `zentraly.device`; HA subclasses it only for DeviceInfo
  and registry parent linkage in `models.py`.
- HA's `platforms.py` maps capability types to platforms. No HA platform enum
  exists in the library catalog. Adding a model with existing capabilities does
  not require a second HA model registration.
- HA refresh scheduling remains in HA `const.py`; device commands and timers
  retain their previous behavior. Dependencies remain device facts; HA decides
  how to display unavailable controls.
- Errors are defined once in the library; `actions.py` maps them to HA translation
  keys. Reads/actions retain their existing result and error semantics.
- The HA client receives the shared aiohttp session. Library-owned sessions are
  closed; caller-owned sessions are never closed by this package.

## Tests and packaging

270 existing test cases were retained across two suites: 190 in HA and 80 in the
library. Five new cases cover session ownership and the public API end-to-end
against a local WebSocket server. The extraction had 85 library cases. The public API adds one topology/factory
case and extends the existing WebSocket test; the total is now 86. The user has confirmed successful physical-device acceptance tests for this
extraction. The tested model/firmware matrix was not specified.

The source distribution builds a wheel in isolation. Both pass strict Twine
metadata checks. The wheel includes py.typed and was installed and tested in a
clean environment with no Home Assistant installed.

Core pre-commit's requirements generator adds a Zentraly entry to
`requirements_all.txt`. This generated change is necessary for eventual upstream
submission, but is intentionally excluded from the current local migration diff
because changes outside the integration/tests have not been authorized. The
scoped generator check passes when generated output is present. Regenerate and
review that file when the final published package name/version are known.

## Recovery and publishing

Preserve both repositories. A commit in Core does not back up this ignored
library. The initial library commit is a local migration checkpoint, not a
release. The unchanged stable tag contains the pre-extraction implementation.
Review Core changes before committing or publishing them.

To inspect the stable baseline without losing this working tree:

```sh
git -C /workspaces/Zentraly worktree add --detach /tmp/zentraly-stable zentraly-stable-before-library-2026-09-16
```

The standalone repository can later be moved outside Core without changing Python
imports. The package name is zentraly. Finalize owner and URLs before configuring publishing;
README.md describes the guarded manual release workflow. Never publish the local
placeholder version.

## Documentation and planned account migration

The current Spanish manuals are under `../zentraly_outputs/documentos/`, including
`arquitectura.tex/pdf`, `biblioteca.tex/pdf` and `pendientes_publicacion.md`. They
cover the extracted architecture. This relative location belongs to the local
workspace; it is not a runtime or packaging dependency.

The agreed sequence is documentation/review, a Core extraction commit and draft
PR, then transfer of the existing fork to a new GitHub account and creation of
separate library and documentation repositories. Destination and final names
are undecided. No remote or account transfer has been performed. The draft must
remain unmergeable until the dependency is published and tested from PyPI.

The public contract is implemented through root exports and documented in
PUBLIC_API.md. HA production code now imports only from the package root. Existing
module imports retain class/enum identity. The name is zentraly; version
0.0.0.dev0 remains local and must not be published. No protocol change was made.
