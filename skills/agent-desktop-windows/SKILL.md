---
name: agent-desktop-windows
tags: windows-automation, accessibility, uia, ai-agent, gui-automation, cli
requirements:
  - agent-desktop
description: >
  Windows platform guide for the agent-desktop CLI. Lists per command group
  what works on Windows and what refuses, the first-contact gotchas
  (PowerShell ref quoting, minimized windows, headed-only input), and where
  to find shell surfaces, notifications, the cursor overlay, UIPI elevation,
  Chromium/Electron settle behavior and troubleshooting.
  Triggers on: "windows desktop automation", "UIA tree", "automate Windows app",
  "agent-desktop on Windows", "elevated window input blocked", "E_ACCESSDENIED",
  or any Windows GUI interaction task.
---

# agent-desktop-windows

This file covers only what differs on Windows. The observe-act loop, refs, JSON
envelope, sessions and tracing are the same on every platform.

Requires Windows 10 1809+ / Windows Server 2019+ (x64 or ARM64). Run it in the
interactive desktop session of the signed-in user. Session 0 (services and
SYSTEM tasks), Server Core, the secure desktop (UAC prompts, the sign-in
screen), a locked desktop and another user's session are not supported:
observation, actions and capture there fail or return nothing.

## Capability Table

| Group | Commands | Status on Windows |
|-------|----------|-------------------|
| Observation | `snapshot`, `find`, `get`, `is`, `screenshot` | Works. Surfaces are `window`, `focused`, a Chromium modal as `sheet`, and an open application menu as `menu` |
| Surfaces | `list-surfaces` | Works. Lists `window`, `focused` and `sheet` per process, plus `menu` with `item_count` while a menu is open |
| Shell surfaces | `open-system-surface` | Works for `start-menu`, `taskbar`, `system-tray`, `system-tray-overflow` and `action-center`, and returns the window `snapshot --surface <kind>` reads. `quick-settings` returns `INVALID_ARGS` naming `action-center` |
| Ref interaction | `click`, `right-click`, `type`, `set-value`, `clear`, `select`, `toggle`, `check`, `uncheck`, `expand`, `collapse`, `scroll`, `scroll-to` | Works, semantic in headless and `--headed` mode. `right-click` and `type` need `--headed` and return `POLICY_DENIED` headless |
| Multi-click and focus | `double-click`, `triple-click`, `focus` | Works with global `--headed` only |
| Keyboard and mouse | `press`, `hover`, `drag`, `mouse-click`, `mouse-move`, `mouse-wheel` | Works. Cursor-moving input needs `--headed`. First Contact covers `press --app` |
| Held input | `key-down`, `key-up`, `mouse-down`, `mouse-up` | Fails closed on every platform with `ACTION_NOT_SUPPORTED`. A headless `mouse-down` or `mouse-up` returns `POLICY_DENIED` first |
| App and window | `launch`, `close-app`, `list-windows`, `list-apps`, `focus-window`, `resize-window`, `move-window`, `minimize`, `maximize`, `restore` | Works. First Contact covers the name `launch` takes |
| Displays | `list-displays` | Works |
| Clipboard | `clipboard-get`, `clipboard-set`, `clipboard-clear` | Works; typed text and image content |
| Wait | `wait` | Works for ms, `--element`, `--window`, `--text`, `--menu`, `--menu-closed`, `--event` and `--notification` |
| Notifications | `list-notifications`, `dismiss-notification`, `dismiss-all-notifications`, `notification-action` | Works over the Action Center. Pass `--headed` when the center is closed |
| Cursor overlay | `cursor-overlay` | Works. `enable` returns `data.rendered: true` only after the renderer acknowledges over its pipe. See `references/shell-and-overlay.md` |
| System | `status`, `permissions`, `version`, `batch`, `skills`, `session`, `trace` | Works |

## First Contact

- **Quote every ref in PowerShell.** PowerShell reads a bare `@token` as its
  splatting operator and deletes the argument before the binary sees it, so
  `set-value @s8f3k2p9:e1 hi` fails `INVALID_ARGS`. Write
  `set-value '@s8f3k2p9:e1' hi`. cmd.exe and bash need no quoting.
- **A window behind another window is drivable. A minimized one is not.**
  Every element of a minimized window reports `offscreen` and ref actions
  fail. Run `restore --app <image>` and snapshot again. Do not use
  `focus-window` by reflex: it steals the user's foreground.
- **No permission dialog exists.** `permissions` reports `automation` as
  `not_required`. Elevation boundaries are the only access control.
- **Chromium and Electron apps read thin before they settle.** Pass a longer
  `--timeout-ms` to `snapshot` instead of concluding the tree is empty.
- **Blocked shortcuts.** `alt+f4`, `win+l`, `win+d`, `alt+tab`, `win+r`,
  `win+x`, `win+e`, `ctrl+shift+esc` and their modifier supersets are refused
  without `--force`. In combos, `cmd` and `meta` are the Windows key, so
  `meta+c` is a shell shortcut. Write `ctrl+c` to copy.
- **`type` needs `--headed`.** It is keystroke synthesis through `SendInput`,
  so a strict-headless `type` returns `POLICY_DENIED`. Use `set-value`, or pass
  `--headed`. It ends `delivered_unverified` (`verification_scope:
  "unavailable"`) when the field exposes no readable Text selection, and can
  verify when one is readable: confirm with a fresh `get`.
- **`press --app` writes to the foreground queue** with no per-process
  targeting. A headless press to a non-frontmost app fails closed. A
  non-interactive caller (service, scheduled task, CI job) gets
  `delivered_unverified`.
- **`launch` takes an absolute path or a bare name** under System32 or the
  Windows directory, with or without `.exe` (`notepad` or `notepad.exe`), not
  a display name. Use `list-apps` to find a running app.
- **Notifications:** `list-notifications` with the Action Center closed needs
  `--headed`. Single-item `dismiss-notification` and `notification-action` need
  `--headed` and `--expected-app` or `--expected-title` for the entry at INDEX.
- **Surfaces:** an open or context menu is the `menu` surface. Windows does
  not advertise a `menubar` surface.
- **Commands that raise shell chrome take the foreground.** Strict headless
  refuses them with `POLICY_DENIED` before anything is raised.
- **Stateful actions run once, then verify by re-reading.** `delivered_verified`
  means the readback matched. `ACTION_FAILED` with
  `details.kind: "post_action_verification"` means the action landed but the
  readback differs: read `details.post_state` and do not retry. A `set-value`
  the app reformats reads as failed. See `references/troubleshooting.md`.
- **Unsigned binary warnings are expected.** See `references/troubleshooting.md`.

## What differs on Windows

- Ref actions are semantic UI Automation calls in headless and `--headed` mode, except `right-click`, `double-click`, `triple-click`, `type` and `focus`, which are physical or take focus and need `--headed`.
- A ref resolves only when it was the only element in the window its snapshot captured with its role, native id, name and description, and exactly one live element still matches. Uniqueness counts the whole window, not the shallow tree a `--skeleton` or `--max-depth` snapshot presents, so a twin below the cut still refuses the ref. Identical twins, such as several identical `Delete` buttons, are refused with `AMBIGUOUS_TARGET`, `details.kind: identity_not_unique`, before anything reaches the app; a live second match is `saved_ref_ambiguous`, and a removed element is `STALE_REF`, `saved_ref_absent`. Take a fresh snapshot after a list changes, and use `--headed mouse-click --xy` when you must pick one of two identical controls.
- The cursor overlay plays its per-action travel only for headless semantic actions. A `--headed` action moves the real cursor instead.

## References

- `references/shell-and-overlay.md`: open it for `open-system-surface`, tray
  and taskbar surfaces, notifications, the cursor overlay, hosted (UWP) window
  identity and menu detection coverage.
- `references/permissions-and-elevation.md`: integrity levels, UIPI, blocked
  combos, protected processes, the cross-process interaction lease.
- `references/chromium-and-electron.md`: settle timing, covered-window hazard,
  WPF wrong-provider trap, unnamed web content.
- `references/troubleshooting.md`: symptom-to-cause map, action verification
  outcomes, saving a document headless, install warnings.

Read any file from the binary:
`agent-desktop skills get agent-desktop-windows references/troubleshooting.md`.

--- references/permissions-and-elevation.md ---

# Permissions and Elevation

Windows has no TCC-style permission grant for UI Automation. What controls
access instead is **integrity level**: a Medium-integrity agent can observe and
act on same-integrity applications, and the OS gates what crosses the boundary
upward.

## Same-Integrity Targets Need No Grant

- UIA reads (snapshot, find, get, is, screenshot) and same-integrity input work
  from any terminal with no permission prompt.
- `agent-desktop permissions` probes UIA live rather than consulting a policy
  store: `accessibility` reports `granted` when UIA answers, `automation`
  reports `not_required`, and `screen_recording` reflects capture availability.
- There is no `--request` dialog to trigger; if `accessibility` reports
  `denied`, the cause is an integrity or policy boundary below, not a missing
  checkbox.

## The UIPI Boundary

User Interface Privilege Isolation blocks synthesized input from a
lower-integrity process into a higher-integrity one (Medium to High, such as an
elevated Notepad):

- **Reads cross the boundary.** From Medium, UIA resolves an elevated target's
  name, class, control type, pid, bounds and node count the same as a High
  caller, and `WM_GETTEXT` reads succeed. Observation is never refused across
  the boundary.
- **Writes do not.** The adapter compares the integrity levels of the two
  process tokens before it synthesizes anything, and a strictly higher target
  returns `PERM_DENIED` whose `platform_detail` reads
  `COM HRESULT 0x80070005 (E_ACCESSDENIED: Access is denied)`.
- **Fix:** run agent-desktop from a terminal elevated to the target's level,
  or act on elements that do not cross the boundary.

### Detection Is a Token Read, Never a SendInput Verdict

`SendInput`'s return value proves nothing: it reports success whether or not
the events landed. Only the token comparison above, or a re-read of the effect,
tells delivered from silently dropped. A target whose integrity level the
process cannot read is not assumed to be same-or-lower: the action proceeds
best-effort and is judged by re-reading its effect.

## Window Activation Crosses the Boundary

`focus-window` succeeds against a higher-integrity target.
`SetForegroundWindow` is gated by the Windows foreground-lock heuristic (recent
input, `AllowSetForegroundWindow`), not by integrity. When foreground cannot be
confirmed before the budget runs out, a strictly-higher target returns an
activation-worded `PERM_DENIED` and an equal-integrity target returns
`ACTION_FAILED`.

## Blocked Key Combos

`press` refuses dangerous shortcuts before synthesis. Every modifier order,
key alias (`meta`/`cmd`/`super` to `win`) and modifier superset is caught:

| Blocked | Why |
|---------|-----|
| `alt+f4` | closes the active window |
| `win+l` | locks the session |
| `win+d` | shows the desktop |
| `alt+tab` | steals the foreground mid-run |
| `win+r` | opens Run over the target |
| `win+x` | opens the Quick Link menu over the target |
| `win+e` | opens File Explorer over the target |
| `ctrl+shift+esc` | opens Task Manager over the target |

Supersets such as `alt+shift+tab` are blocked too. `--force` overrides the
guard. `ctrl+alt+delete` is not on the list, because `SendInput` cannot
synthesize the Secure Attention Sequence at all.

## Protected Processes

`close-app` refuses session- and shell-critical images by exact,
case-insensitive `.exe` name: `csrss.exe`, `wininit.exe`, `winlogon.exe`,
`services.exe`, `lsass.exe`, `smss.exe`, `lsaiso.exe`, `dwm.exe`,
`explorer.exe`. Other names close normally, including near-misses such as
`explorer++.exe`. A refusal is `INVALID_ARGS`.

## Cross-Process Interaction Lease

Interactive work holds an exclusive, token-derived lock file, so two concurrent
agent-desktop processes cannot interleave focus changes, clicks and typing on
the same desktop. An inherited-handle mode
(`AGENT_DESKTOP_INTERACTION_LEASE_HANDLE`) lets a parent pass its lease to a
child after re-verifying identity and exclusivity. If acquisition fails, wait
for the other process to finish. Do not bypass the lease.

## The Cursor Overlay's Control Pipe

The cursor overlay is a detached renderer process driven over a named pipe.

**What is protected:**

- Remote clients are rejected (`PIPE_REJECT_REMOTE_CLIENTS`).
- Another user's process is refused in both directions: each connection's
  token user SID must match.
- Before it sends a control, the client checks that the pipe server's
  executable is named `agent-desktop` (case-insensitive, with or without
  `.exe`). This is a file-name check, not a signature check. A mismatch makes
  `enable` report `rendered: false`.
- One renderer per session (`FILE_FLAG_FIRST_PIPE_INSTANCE`). A second renderer
  exits before it creates a window.

**What is not protected: a same-user process on the same machine.** The pipe
has no security descriptor, and its name derives from the state root, the
session id and the protocol generation. A same-user process can:

- hold the name first, so `enable` answers `rendered: false` while it does
  (a missing overlay, never a fake one);
- connect to a live renderer and move the drawn cursor or put any text in the
  label card.

The overlay is presentation-only. It never performs or fails an action and
carries no credential. On a host where other people run processes as your
account, do not trust what the overlay draws, and leave it disabled.

--- references/chromium-and-electron.md ---

# Chromium and Electron Trees

Chromium-based apps (Electron or browser) are the most common source of a false
"the tree is empty" conclusion on Windows. The tree is real. The renderer builds
it after the first UIA client connects.

## Exposure Needs No Flag on Modern Chromium

Chromium 138 and later exposes a full UIA tree to any UIA client with no
`--force-renderer-accessibility` flag. The settled tree is the same with and
without the flag. Do not relaunch a running app to add accessibility flags.
Connect to what is there.

## First Contact Is Thin; Wait for Settle

The first read after connecting starts the renderer's accessibility build, so it
returns about a thirteenth of the settled tree. On a cold launch the settle
takes 10 to 25 seconds.

- Pass `--timeout-ms` to `snapshot` so its budget covers the settle. The
  adapter connects, lets the tree settle and re-walks within that budget.
- A grown tree is visible to a **fresh** read. The client that started the
  build can keep serving the shell it saw first. If one command still reports
  a thin tree after the settle, run a new snapshot instead of retrying in the
  same process.
- The renderer flag does not remove the need to settle. With it, first contact
  is a race that returns anything from a fraction of the tree to nearly all of it.

## A Thin Tree With Boundary Groups Is a Depth Effect, Not Settling

Chromium nests its controls under a long chain of unnamed pass-through groups,
so a settled tree can show no buttons, textfields or links at the default
`--max-depth 10`. The groups at the depth boundary carry `children_count` and
refs, so you can drill into them.

When a settled snapshot has refs but no operable controls, and its boundary
nodes carry `children_count`, do not wait longer or raise `--timeout-ms`. Raise
`--max-depth`, or drill into a boundary ref with `snapshot --root <ref>`.

## Covered Windows Hold First-Contact Counts Indefinitely

A Chromium window that other windows fully cover can keep its first-contact
node count through the whole settle. Do not park another window over the target
during launch and settle. If the count looks frozen at a small number, bring the
target to the foreground or minimize the covering windows, then snapshot again.

## WPF: Reading Too Early Binds the Wrong Provider

A UIA client that reads a WPF window before its automation peer exists binds the
generic HWND provider **permanently**. The window then reports
`ClassName HwndWrapper[...]` with zero children, and no in-process retry
recovers it. A read a few seconds after launch gets the real tree.

Take a new snapshot, so the adapter resolves from a new handle. Retrying the same
read cannot fix it. After you launch a WPF application, use
`wait --event window-opened` or a short `wait` before the first snapshot.

## Unnamed Web Content

A ref to web content with **no accessible name** is identified by its role plus
any AutomationId or description it carries, and resolves only if that
combination was unique in the window when you took it and still is. Bounds are
never identity. A ref to one of several unnamed elements that share role,
AutomationId and description returns `AMBIGUOUS_TARGET`; use headed coordinate
input from a parent's bounds, or a CDP client (`launch --cdp`).

--- references/troubleshooting.md ---

# Troubleshooting

Symptom-to-cause map for the Windows adapter. Each entry names the observable
symptom first.

## Empty or Tiny Tree

| Symptom | Cause | Fix |
|---------|-------|-----|
| Chromium/Electron app returns far fewer nodes than the UI shows | The first read came before the renderer's accessibility build settled | Run `snapshot --timeout-ms 30000`. The settle can take 10 to 25 s cold. See `chromium-and-electron.md` |
| Node count frozen at a small number however long you wait | Other windows fully cover the target during the settle | Bring the target to the foreground or minimize the covering windows, then snapshot again |
| WPF app: one node, `ClassName` like `HwndWrapper[...]`, zero children | A read before the automation peer existed bound the generic HWND provider permanently | Take a fresh snapshot. In-process retries never recover |
| Custom-rendered UI or a game returns nothing meaningful | No accessibility exposure at all | Out of scope. Use screenshots for verification only |

## PERM_DENIED with an E_ACCESSDENIED Detail

```json
"code": "PERM_DENIED",
"platform_detail": "COM HRESULT 0x80070005 (E_ACCESSDENIED: Access is denied)"
```

Cause: the target runs at a strictly higher integrity level, typically an
elevated app driven from a Medium terminal. UIPI blocks synthesized input across
that boundary, while reads still succeed.

Fix: run your terminal elevated to the target's level. See
`permissions-and-elevation.md`.

## COM Apartment Error

```json
"message": "... COM multithreaded apartment ..."
```

Cause: UIA needs the calling thread to belong to a COM apartment. The CLI joins
the multithreaded apartment itself, so this error means an embedding host's
threading conflicts with it.

Fix: in an FFI consumer, initialize through the library's bootstrap entrypoints
instead of calling UIA from arbitrary threads. The error's `suggestion` names
joining the multithreaded apartment. The defect is in the calling process, not
in the target application.

## DPI-Scaled Coordinates

Symptom: headed coordinate actions (`mouse-click --xy`, drag endpoints) land
offset from the visible element on scaled or multi-monitor setups.

Cause: without per-monitor awareness, Windows reports virtualized coordinates.
The adapter applies `Per-Monitor V2` at startup, so bounds and `--xy` values are
physical pixels.

- A host that already set an incompatible awareness context is tolerated
  (`ERROR_ACCESS_DENIED` on the second call means it is already set).
- If startup reports `INTERNAL` with a `SetProcessDpiAwarenessContext` Win32
  error detail, the hosting process locked the context first. Run from a plain
  terminal instead of an embedded host.
- Prefer refs to raw coordinates.

## The Binary Will Not Start

agent-desktop ships unsigned on Windows. Three execution controls treat that
differently:

- **SmartScreen:** a browser download carries Mark-of-the-Web, so
  double-clicking it can show "Windows protected your PC". Choose More info,
  then Run anyway. The npm package bundles the binary and downloads nothing,
  so npm installation attaches no mark and fires no mark-gated prompt.
- **Antivirus quarantine:** Defender or another scanner may quarantine a new
  unsigned executable however it was obtained. Restore or allow-list it after
  you verify the published SHA-256 checksum.
- **Smart App Control:** on a clean Windows 11 install it blocks unknown
  unsigned executables at process creation, including command-line launches.
  No download path or launch mode avoids it. Turn Smart App Control off or use
  a signed build.

## POLICY_DENIED from a Shell-Surface or Notification Command

Symptom: `open-system-surface`, `list-notifications`, `wait --notification` or a
notification mutation returns `POLICY_DENIED` without touching the desktop.

Cause: the command raises shell chrome and so takes the foreground, which strict
headless refuses before anything is raised.

Fix: pass global `--headed`, or raise the surface yourself first.
`snapshot --surface <kind>` reads an already-present shell surface headless, and
`list-notifications` and `wait --notification` adopt an already-open Action
Center.

## wait --notification Times Out While Toasts Are Being Posted

Cause: the Action Center collects a toast only while it is open, and the wait
opens and closes the center on each poll, so a toast posted between polls is
lost.

Fix: hold the center open yourself across the staging window, so the polls
adopt it without closing it, or confirm the toast with a `list-notifications`
taken while the center is open.

## A Hosted (UWP) App Reads as ApplicationFrameHost

Symptom: `focused_window` or `list-windows` reports a hosted UWP app (Settings
and its peers) under the frame host's identity, or an identity verified against
the app's pid stops resolving.

Cause: the app is suspended, which drops its `CoreWindow` while the frame
survives. See "Hosted (UWP) Window Identity" in `shell-and-overlay.md`.

Fix: activate the app so it resumes, then list again.

## INTERNAL: "private file parent is owned by a foreign principal"

```json
"code": "INTERNAL",
"message": "private file parent is owned by a foreign principal, not this
process's token user, token owner, or an owner-eligible token group; if a
different principal owns this path intentionally, relocate the state root with
AGENT_DESKTOP_HOME instead of reusing it"
```

Cause: a process with a different token owner created the state root
(`~/.agent-desktop`). On Windows this is almost always an elevated (Run as
administrator) shell that reuses a directory a non-elevated session created, or
the reverse. The ownership check protects refmaps and trace segments from a
pre-planted path.

Fix: run from one elevation level, or set `AGENT_DESKTOP_HOME` to a fresh
absolute directory for the elevated session. Do not take ownership of the
existing directory or open its ACL to work around the error, because that
defeats the check.

## Action Verification

Every stateful action (`set-value`, `clear`, `type`, `toggle`, `check`,
`uncheck`, `expand`, `collapse`) runs **exactly once**, then re-reads live
state. The settle loop polls every 50 ms up to a 400 ms cap and stops as soon as
the postcondition holds. It never runs the action again.

The three outcomes are not interchangeable:

- The readback matches: `disposition.delivery` is `delivered_verified`. A value
  write also carries `details.verification_scope: "element_value"` with
  `application_commit: "not_verified"`: the control holds your value, but it
  cannot say whether the application committed it.
- The readback contradicts the request: `ACTION_FAILED` with
  `details.kind: "post_action_verification"` and `details.post_state`. **Read
  `post_state` before anything else.** The action was delivered, so
  `disposition.retry` is `unsafe`.
- The evidence was never observed: the action succeeds as
  `delivered_unverified` with `details.verification_scope: "unavailable"`. This
  is not a failure and not proof that nothing changed. The element lacks the
  UIA property the check needs, such as a TogglePattern or
  ExpandCollapsePattern, or the read failed. **`type` is verified only when the
  focused field exposes a readable Text pattern selection.** Without one, `type`
  lands here. Confirm the value with a fresh `get` if it matters.

**A `set-value` that the application reshapes reads as failed.** If the app
trims whitespace, reformats a date or normalizes a number, the readback differs
from what you wrote, and the envelope says `ACTION_FAILED` although the write
landed. The `SetValue` check captures no before-state, so it cannot tell
"nothing happened" from "accepted and reshaped". Compare
`details.post_state.value` with what you sent: your value in the app's own
format means the write succeeded. Numeric tolerance is role-scoped: only
`slider`, `incrementor`, `scrollbar` and `handle` compare numerically, so a
`textfield` that stores `42.0` after you wrote `42` fails this way.

## Saving a document, headless, without keyboard input

No `save` command exists. Saving is a menu path plus a dialog, and the whole
chain is semantic, so it needs no `--headed` and no keystrokes. The same shape
fits any app whose save flow is File, then Save As.

The script runs as written against an open Notepad. Each ref comes from the JSON
of the step before it, so the sequence stays correct when the tree shifts.

```powershell
$out = "$env:TEMP\notepad-save-demo.txt"

agent-desktop restore --app notepad.exe                 # only if minimized; behind is fine
$doc = (agent-desktop find --app notepad.exe --role textfield | ConvertFrom-Json).data.matches[0]
agent-desktop set-value $doc.ref_id "the document body"

$file = (agent-desktop find --app notepad.exe --role menuitem --name "File" | ConvertFrom-Json).data.matches[0]
agent-desktop expand $file.ref_id
agent-desktop wait --menu --app notepad.exe             # the open menu is its own surface
$menu = (agent-desktop snapshot --app notepad.exe --surface menu | ConvertFrom-Json).data.tree
agent-desktop click ($menu.children | Where-Object name -eq 'Save As...').ref_id

agent-desktop wait --window "Save As" --app notepad.exe # the dialog is a new window
$dialog = (agent-desktop list-windows --app notepad.exe | ConvertFrom-Json).data |
    Where-Object title -eq 'Save As'
$name = (agent-desktop find --name "File name" --window-id $dialog.id | ConvertFrom-Json).data.matches |
    Where-Object role -eq 'textfield'
agent-desktop set-value $name.ref_id $out               # full path goes in the name field

$save = (agent-desktop find --role button --name "Save" --window-id $dialog.id | ConvertFrom-Json).data.matches[0]
agent-desktop click $save.ref_id
agent-desktop wait --window "notepad-save-demo - Notepad" --app notepad.exe
Get-Content $out
```

Three things that surprise a first-time caller:

- **`find --name "File name"` returns three matches:** a `statictext` label, a
  `combobox`, and the `textfield` inside the combobox. Only the textfield
  accepts `set-value`, so match on `role` as well as name.
- **The full path in the name field selects the directory.** There is no
  separate folder step, and navigating the file list by ref is far more fragile.
- **The file does not exist when the Save click returns.** The shell took
  10.9 s between the click's envelope and the file on disk. Wait for the title
  change with `wait --window`. A fixed sleep of a second or two reads as a
  missing file.

The dialog's Save button returns `delivered_unverified`, because a synthesized
invoke cannot confirm what the shell dialog did with it. Verify by reading the
file back from disk.

--- references/shell-and-overlay.md ---

# Shell surfaces, notifications and cursor overlay

Open this file to raise shell surfaces, read or drive notifications, use the cursor overlay, or handle hosted (UWP) window identity and menu detection.

## Shell Surfaces

`open-system-surface --surface <kind>` raises a shell surface and returns the
`w-<hwnd>` identity of the window it presents. Windows kinds: `start-menu`,
`taskbar`, `system-tray`, `system-tray-overflow`, `action-center`. Read the
surface with `snapshot --surface <kind>`. `snapshot --window-id` refuses that
handle with `WINDOW_NOT_FOUND`, because the window inventory excludes shell
windows.

- **The command takes the foreground.** Strict headless refuses it with
  `POLICY_DENIED` before anything is raised. Pass global `--headed`. An
  already-present surface is returned without being raised again.
- **`snapshot --surface <kind>` needs no `--app` and works headless.** A closed
  surface returns `WINDOW_NOT_FOUND` with a suggestion that names
  `open-system-surface`.
- **`quick-settings` returns `INVALID_ARGS`** and names
  `action-center`, where the quick actions live.
- **`start-menu` is whatever the Win key raises.** Before Windows 11 that is a
  search overlay whose root holds a `SearchTextBox`, not a tile grid. Drive it
  as a search surface.
- **Tray items use the generic commands.** There are no Windows-specific tray
  commands. `snapshot --surface system-tray` returns the promoted
  notification-area items; zero items is a correct answer on a machine with no
  tray icons. `snapshot --surface taskbar` gives refs to the notification
  area's tray `button`s. `snapshot --surface system-tray-overflow` gives refs to
  the overflow items: raise the flyout first with
  `open-system-surface --surface system-tray-overflow`, or a click fails the
  occlusion check. A click on a `system-tray` item reports
  `delivered_unverified` with `retry: unsafe`, because a synthesized click
  cannot confirm what the owning app did with it. A click on an overflow item
  is untested.

## Notifications

The notification commands read and drive the Action Center through UI
Automation. The WinRT `UserNotificationListener` is never used, so its
per-machine consent setting cannot fail a call. The reader keys on landmark
`AutomationId`s: `MainListView` when notifications are present, an empty-state
shape when none are, and a top-level `ClearAllButton`.

- **The center must be open for a read.** `list-notifications` reads an
  already-open center headless. When the center is closed, strict headless
  returns `POLICY_DENIED` before raising it, and `--headed` raises it and
  restores the desktop afterwards. `dismiss-notification`,
  `dismiss-all-notifications` and `notification-action` always need
  `--headed`, and `wait --notification` refuses on its first poll under the
  same rule.
- **An empty center lists zero entries.** A center that shows neither the
  notification list nor the empty-state landmarks returns
  `PLATFORM_NOT_SUPPORTED` with a `platform_detail` that names the missing
  landmark. An unrecognized tree is an error, never an empty answer.
- **The index is not the identity.** Every mutation re-reads the center and
  compares the entry at the index with `--expected-app` and
  `--expected-title`. A mismatch is `NOTIFICATION_NOT_FOUND`. An action name the
  entry does not offer is `ACTION_NOT_SUPPORTED`.
- **A dismiss that does nothing fails.** The shell can accept an entry's
  `DismissButton` without acting on it. When the target is the only entry, the
  verified clear-all control runs instead. Otherwise the call reports
  `ACTION_FAILED` (`delivered_unverified`). `dismiss-all-notifications` is
  judged against the entries captured before the clear, so entries that arrive
  while it runs are not failures.
- **`wait --notification` opens and closes the center per poll**, as on macOS.
  Each poll adopts an already-open center and restores the entry state after.
  Measured cost: 1243.5 ms per poll at the minimum, 1254.2 ms at the median.
  The wait also sleeps up to 500 ms between polls, so size `--timeout` for
  both. A notification that appears and is dismissed inside one interval can be
  missed. A toast joins the center only while the center is open, so toasts
  posted between polls never land. To stage arrivals, hold the center open
  yourself; the polls adopt it without closing it.
- **This output is sensitive.** The notification-area surface shows the names
  of installed background agents, including security and remote-access
  products, and `list-notifications` returns titles and bodies verbatim.
  Nothing is redacted.

## Cursor Overlay

`cursor-overlay enable` renders on Windows: a detached renderer process paints a
presentation-only cursor in a click-through, topmost, non-activating window.

```powershell
$env:AGENT_DESKTOP_HOME = "$env:TEMP\ad-scratch"
$start = agent-desktop session start --cursor | ConvertFrom-Json
$env:AGENT_DESKTOP_SESSION = $start.data.session_id
agent-desktop cursor-overlay enable --label "Opening menu" --accent "#FF3B7B"
agent-desktop cursor-overlay disable
```

- **Start the session before you snapshot.** The overlay needs a session, and a
  snapshot taken outside it lands in the global namespace, where a
  session-scoped action cannot see it (`SNAPSHOT_NOT_FOUND`). Run
  `session start`, `cursor-overlay enable`, `snapshot`, then act.
- **`data.rendered` is the renderer's acknowledgement.** `enable` returns `true`
  only after a renderer connects to the session's control pipe and acknowledges
  the control. It returns `false` when no renderer could be reached, spawned or
  heard from in time. `disable` carries no `rendered` field. `session start
  --cursor` also enables the overlay and echoes only `cursor_overlay`.
- **Headed actions skip the travel animation.** A `--headed` action moves the
  real cursor, so the overlay does not animate travel or the click for it. An
  enabled overlay still paints its resting cursor.
- **It costs about 355 ms per action.** A headless `click` took 427 ms without
  the overlay and 782 ms with it. Enabling costs about 50 ms once. A hundred
  overlaid clicks add about 35 seconds.
- **It starts at the centre of the primary monitor's work area**, not over the
  app you drive. The first frame lands shortly after `enable` returns, so poll
  for the pixels before you take a screenshot.
- **It draws above the taskbar and other topmost shell chrome.**
- **It ignores the "Show animations in Windows" setting.** Windows reports
  animations off by default on a stock Windows Server host, so the explicit
  `enable` counts as the opt-in. macOS honours Reduce Motion instead.
- **The label is a black pill with white Segoe UI text**, sized to the text.
  `--fill` and `--rim` colour only the cursor, not the label.
- **The label shows only when there is something to say.** `enable` without
  `--label` greets once, and with `--image` it does not greet. After that,
  only an action that carries a description draws the label. Each `enable`
  and each action replaces the label text.
- **It fades out after 6 s with no instruction** and comes straight back on the
  next command.
- **The caret comes from the Text pattern.** After text entry, the agent's caret
  sits where the field's Text pattern places the insertion point, in a window
  of its own, and goes when the cursor sets off for somewhere else. A field
  without the Text pattern keeps the element outline.
- **It draws in physical pixels**, the space element bounds are reported in,
  so it is not scaled again for the monitor's DPI. Multi-monitor placement is
  unit-tested only and not verified on a live multi-monitor desktop.
- **A harness job object takes the overlay with it.** A job with
  `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, which CI runners and some agent
  harnesses use, ends the detached renderer when the job closes. A vanished
  overlay there is not a renderer defect, and actions are unaffected.
- **Its control pipe trusts any process that runs as you.** See "The Cursor
  Overlay's Control Pipe" in `references/permissions-and-elevation.md`.
- **Teardown.** `cursor-overlay disable` ends the renderer for its session, and
  `session end` closes it too. When a session ends another way (a crash,
  `session gc`), the renderer reclaims itself within 3000 ms.

## Hosted (UWP) Window Identity

An app hosted in `ApplicationFrameHost` is reported through its frame:
`focused_window` and `list-windows` give the frame's handle as the window `id`,
which every window operation targets, while `app` and `pid` name the hosted
app, read from its `Windows.UI.Core.CoreWindow`. A suspended hosted app drops
its `CoreWindow`, so until it resumes the entry reads as its frame host, and
identities checked against the hosted pid fail closed.

## Menu Detection Coverage

The `menu` surface detector covers classic Win32 menus, WPF context menus and
menu-bar dropdowns, and Chromium/Electron DOM context menus drawn inside the
app's own window. WinUI3 and MSIX hosts are not evaluated. For an app outside
these families, read "no menu is open" as "not detected", not as proof that the
menu is closed.
