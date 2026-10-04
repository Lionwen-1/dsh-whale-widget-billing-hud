# DSH Whale Widget Billing HUD

[中文说明](README.md) · [Implementation notes (Chinese)](NOTES.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

This package adds a balance display, per-call charge indicators, and movable bubble controls to the DSH desktop whale widget. It patches two separately installed community plugins. The repository contains only our patch scripts and injected code; it does not redistribute the plugins or artwork.

This is an independent community patch and is not affiliated with DSH or the maintainers of either dependency.

## What it is for

| Feature | Use |
| --- | --- |
| Persistent balance panel | Keep the account balance and today's usage visible below the character. Move, resize, or hide the panel. |
| Per-call charge indicators | Show each model call's charge near the character, including cache hit, cache miss, and output costs when the event provides a breakdown. |
| Bubble controls | Adjust the bubble's text size, overall scale, and position. Save settings in browser storage and a local DSH configuration file. |
| Installer checks | Verify plugin versions and source anchors before modifying either plugin. Keep original-file backups for rollback. |

## Requirements and compatibility

- DSH desktop must have run at least once, creating a profile under `~/.dsh/profiles/`.
- Install `dsh-whale-widget` **0.3.12** and `dsh-damage-pulse` **4.0.11** in the same DSH profile.
- Python 3.8 or newer. Node.js is optional but enables JavaScript syntax checks during installation.
- The complete workflow was tested on Windows with DSH **0.1.7-rc.2**. A newer DSH runtime, including **0.2.0-rc.2**, has not been verified end to end. A passing `--check` confirms plugin versions and source anchors only; it does not prove runtime compatibility.

## Install

Run from the repository root:

```bash
python install.py --check
python install.py
```

If several profiles contain both plugins, choose one explicitly:

```bash
python install.py --check --plugin-root "/path/to/profile/node_modules"
python install.py --plugin-root "/path/to/profile/node_modules"
```

The installer checks both plugins before writing either one. On first use, it saves original files under `payload/whale-widget-backup-0.3.12/` and `payload/damage-pulse-backup-4.0.11/`. Subsequent runs restore those originals before applying the patches, avoiding stacked edits. The backup directories are ignored by Git. A failed preflight or patch returns a nonzero exit code; if a failure occurs after patching starts, inspect the plugins and restore the backups before retrying.

**Fully restart DSH after installation.** Reloading the desktop window does not reload the injected front-end script.

## Verify

After restarting DSH:

1. Open the widget's `☰` menu and look for the balance panel and bubble controls.
2. Confirm the balance panel appears below the character and responds to drag and resize actions.
3. Make a model call and confirm that a charge indicator appears. This needs `dsh-damage-pulse` to be running and recording charge events.

For a developer check, run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q install.py payload tests
node --check payload/balbox_patch.js
```

## Changes and rollback

The package patches the whale widget's host and front-end files, plus the billing plugin's host and client files. The patches add DSH account-balance fallback, enable billing for the DSH account provider, display charge events in the widget, and persist display settings. They do not modify DSH itself.

To roll back, copy the saved original files from the two backup directories into the matching plugin paths, or reinstall both community plugins through DSH. A plugin upgrade overwrites the patches. The installer rejects unsupported plugin versions rather than applying old backups to new code.

## Repository contents

```text
install.py                    Installer and preflight
payload/patch_whale_widget.py Widget host and front-end patch
payload/patch_damage_pulse.py Billing host and client patch
payload/balbox_patch.js       Injected balance panel and menu code
tests/test_install.py         Installer behavior tests
README.md                     Chinese guide
NOTES.md                      Chinese implementation notes
LICENSE                       MIT license for this project's original code
THIRD_PARTY_NOTICES.md        Dependency credits and licenses
```

The original code in this repository is released under the [MIT License](LICENSE). See [third-party notices](THIRD_PARTY_NOTICES.md) for dependency credits. DSH, the two community plugins, and any character artwork retain their own licenses.
