---
name: agent-desktop
tags: computer-use, desktop-automation, accessibility, ai-agent, gui-automation, cli
requirements:
  - agent-desktop
description: >
  Operate desktop applications on macOS, Windows and Linux through native accessibility trees,
  using the agent-desktop CLI. Use when an AI agent must see or act on a desktop GUI:
  click buttons, fill forms, read UI state, navigate menus, toggle checkboxes, scroll,
  drag, type text, press shortcuts, take screenshots, manage windows, use the clipboard,
  launch or close apps, read notifications.
  Triggers on: "click button", "fill form", "open app", "read UI", "computer use",
  "operate desktop", "accessibility tree", "snapshot app", "type into field", "navigate menu",
  "toggle checkbox", "take screenshot", "desktop automation", "agent-desktop",
  or any desktop GUI task on macOS, Windows or Linux.
---

# agent-desktop

agent-desktop is a CLI that reads and operates desktop apps through the OS accessibility tree. Every command prints one JSON envelope (`ok`, `data` or `error`). It is a tool, not an agent: the observe, act and verify loop runs in you.

## Shell syntax

Examples use a POSIX shell. In PowerShell, quote every ref (`'@s8f3k2p9:e1'`), because a bare `@token` is the splatting operator. Use `$env:NAME = 'value'` instead of `export`, and `| ConvertFrom-Json` instead of `$(...)` and `jq`. The Windows skill has the PowerShell forms.

## First run

1. Run `agent-desktop status`. It reports the platform, permissions and `supported_surfaces`.
2. Run `agent-desktop skills get platform`. It loads the skill for the OS the binary runs on (macOS, Windows or Linux).
3. For flags and syntax, run `agent-desktop <command> --help`. This skill does not repeat flag lists.

## The loop

Use `find` when you know the role or exact name. Otherwise map the app first and drill into one region.

```
agent-desktop snapshot --skeleton --app "Notes" -i --compact   # shallow map, children_count on cut branches
agent-desktop snapshot --root @s8f3k2p9:e3 -i --compact        # drill into one region
agent-desktop click @s8f3k2p9:e12                              # act on a qualified ref
agent-desktop snapshot --root @s8f3k2p9:e3 -i --compact        # verify: re-read the same region
```

- A small app needs no skeleton. Take a full `snapshot -i`.
- `-i` keeps interactive nodes only, so a row's static-text label is dropped. To tell which row a repeated button belongs to, drill that row's container with `--root` and leave out `-i`. On Windows and Linux that reads the row but does not make its button actionable: a button repeated in other rows is a twin in the window and its ref is refused (see Refs).
- A `--root` drill adds its refs to the same snapshot id. Refs outside the drilled subtree, and the drilled root itself, stay valid; refs that were already inside it are replaced, so an old ref there returns `STALE_REF`.
- Never skeleton a surface (`--surface menu`, `sheet`, `alert`). A surface is already focused.
- An action that opens a menu, sheet or alert lists it in `data.surfaces`. Target that overlay next.
- After an async step, use `wait` (see `commands-system.md`). A fixed sleep is a race.

## Refs

- Output refs are qualified: `@<snapshot_id>:e<N>`, for example `@s8f3k2p9:e1`. Pass them to later commands as they are.
- Refs are valid for one snapshot. After any UI change, re-drill the affected region or take a new snapshot.
- Only addressable elements get refs. Static text and inert containers do not.
- A command re-identifies the element before it acts. On macOS the ref carries the element's own address, so identical twins each keep their ref. On Windows and Linux a ref resolves only when it was the only element in the window its snapshot captured with its role, native id, name and description, counted even below a skeleton or depth cut, and exactly one live element still matches. Identical twins there have no ref path: only `--headed mouse-click --xy X,Y` can choose one, it takes the foreground, and a Linux Wayland session refuses it.
- `STALE_REF`: the element is gone or no longer matches. `details.kind` is `saved_ref_absent`, or `retained_object_stale` on macOS. Take a fresh snapshot and use the new ref.
- `AMBIGUOUS_TARGET`: an identical element appeared (`saved_ref_ambiguous`), or the ref was not proven unique at capture (`identity_not_unique`). Repeating the ref or re-snapshotting identical twins gives the same refusal; act on a control that is unique in the window. `identity_not_unique` also follows a snapshot that could not read the whole window in time: retake it with a larger `--timeout-ms`.
- `TIMEOUT` with `details.kind: resolution_identity_unknown`: a live read did not answer, so identity is unproven. Nothing was sent; retry.
- `SNAPSHOT_NOT_FOUND`: the snapshot id expired. Snapshot again.

## Delivery and retry

Action results carry `data.disposition` and errors carry `error.disposition`, each with `delivery` and `retry`. Observation commands such as `snapshot` have none on success; their errors, and every `INVALID_ARGS` refusal, carry `not_delivered` and `retry: safe`.

- Retry or substitute an action only when `disposition.retry` is `safe`. Only `not_delivered` is safe.
- Any other delivery value means the action may have landed. A repeat can click, type or submit twice, and `toggle` can undo itself.
- On a result that is not safe, read the live state (`get`, `is`, or a fresh snapshot) and decide from that. `details.post_state` helps when present.
- Branch on `error.code` and `error.disposition`. Message and suggestion text can change.
- `details.retryable: false` means waiting cannot change the outcome. Try a different approach.

## Headless and headed

Ref actions are headless by default. They use semantic accessibility calls and do not take focus, move the cursor, synthesize keys or use the clipboard. If no semantic path exists, the action fails closed. Use the global `--headed` flag only when the user explicitly permits physical input, such as double-click, hover, drag, or focus. Never switch to headed mode to recover from a headless failure. Raw coordinates (`--xy`) never imply focus. Which actions need `--headed` differs by OS: read the platform skill.

## References

Load one only when you need it: `agent-desktop skills get desktop <reference>`.

| Reference | Open it when |
|-----------|--------------|
| `commands-observation` | You need `snapshot`, `find`, `get`, `is`, `screenshot`, `list-surfaces` semantics, partial trees, or the `--root` rules |
| `commands-interaction` | You choose between click, type, set-value, select, toggle, scroll, press and mouse commands, or you debug an action error |
| `commands-system` | You launch or close apps, manage windows, use the clipboard, `wait`, `batch`, sessions, multi-agent cursors, tracing, or load skills |
| `workflows` | You want worked patterns (forms, menus, dialogs, waiting for a new window, scroll-find, drag) and the anti-patterns list |

--- references/commands-observation.md ---

# Observation Commands

Commands that read UI state and never change it. Run `agent-desktop <command> --help` for flags.

## snapshot

Captures the accessibility tree as JSON. Interactive elements get qualified refs (`@s8f3k2p9:e1`) that embed the snapshot id. A bare `@eN` fails with `INVALID_ARGS`.

```bash
agent-desktop snapshot --app "System Settings" -i --compact
agent-desktop snapshot --app "App" --skeleton -i --compact
agent-desktop snapshot --root @s8f3k2p9:e3 -i --compact
agent-desktop snapshot --app "App" --surface menu -i
agent-desktop snapshot --app "App" --window-id w-1234 -i
```

Output shape:

```json
{ "ok": true, "command": "snapshot",
  "data": { "app": "System Settings", "window": { "id": "w-4521", "title": "General" },
    "ref_count": 14, "snapshot_id": "s8f3k2p9", "complete": true,
    "tree": { "role": "window", "name": "General", "children": [
      { "ref_id": "@s8f3k2p9:e1", "role": "button", "name": "About", "states": ["focused"] } ] } } }
```

`data.window` is left out when macOS reads a windowless app through its process. On Windows and Linux the same app returns `WINDOW_NOT_FOUND`.

Each ref names the snapshot that owns it, so a ref keeps resolving against its own snapshot when you interleave several apps or windows.

Choose the scope:

- `-i --compact` keeps interactive elements only and drops empty wrappers. Use both by default.
- `-i` keeps interactive nodes and cut containers, so a row's static-text label is dropped. To tie a repeated button to its row, drill that row's container with `--root` and leave out `-i`. On Windows and Linux this identifies the row but a button repeated across rows stays a twin, so its ref is refused.
- `--skeleton` clamps depth to 3 and adds `children_count` to cut containers. Each cut branch exposes its deepest safely resolvable drill target, or its nearest resolvable ancestor when the boundary has no stable identity.
- `--root <REF>` starts from a ref found earlier. Re-drilling a root replaces the refs from that root's previous drill, and those of any drill made under it. Refs outside the drilled subtree keep working, skeleton refs inside it are replaced, and the new refs join the same snapshot id. A drill inherits the whole-window identity count of its snapshot, so its refs resolve like the skeleton's. `--root` cannot combine with `--surface` or `--wait-for`.
- `--max-depth` (default 10) limits depth. Reach deeper subtrees with `--root`.
- Use `--include-bounds` only when you need coordinates.
- With `--app` and no `--window-id`, `snapshot` and `find` take the app's only visible window, else its only focused window, and answer `AMBIGUOUS_TARGET` with the candidates when neither settles it. Pass `--window-id` when an app has several windows.

### Partial trees

`data.complete` is on every snapshot. When the observation budget runs out, the command still succeeds with `"complete": false`, `"truncated": true`, `"nodes_observed"`, and the tree it saw. Each node with cut descendants carries `"subtree_truncated": true`. Read `complete`; do not wait for a `TIMEOUT`. Raise `--timeout-ms` (default 3000) or drill with `--root` to finish the tree. A `--root` drill is all or nothing: an incomplete read returns `TIMEOUT`.

`"identity_unproven": true` means the snapshot could not read the whole window in time to prove its refs. On Windows and Linux, and on macOS for an element with no address, those refs fail with `identity_not_unique`, so retake the snapshot with a larger `--timeout-ms` before acting.

A cold Chromium or Electron app can take 10 to 25 seconds to expose its web tree. If a fresh snapshot comes back thin, raise `--timeout-ms` and snapshot again.

### Which refs exist

An element gets a ref when its role is interactive or it advertises a primary action. `scrollarea` and `disclosure` get refs because `scroll`, `expand` and `collapse` need them. Static text and inert containers stay in the tree without refs. Web content advertises focus, right-click and scroll-to on almost every node, so those alone do not earn a ref. `find` returns `bounds` for such matches. Drive them with `--xy` (right-click, hover, drag) or scroll the container.

### Ref re-identification

A command re-identifies the element from the ref before it acts. On macOS the ref carries the element's own address, so identical twins each keep their ref. On Windows and Linux a ref resolves only when it was the only element in the window its snapshot captured with its role, native id, name and description, and exactly one live element still matches. A skeleton, depth-limited or drilled capture counts against the whole window, so a shallow tree proves the same thing a full one does. Values and bounds never count as identity.

- `STALE_REF`, `details.kind: saved_ref_absent`: no live element matches the stored identity. Take a fresh snapshot. On macOS `retained_object_stale` means the recorded address is dead or no longer matches.
- `AMBIGUOUS_TARGET`, `details.kind: saved_ref_ambiguous`: an identical element appeared, so two live elements match. `identity_not_unique`: the ref was not proven unique at capture, so nothing was searched. That is an identical twin, which every snapshot refuses again, or a window the snapshot could not read whole in time, which a new snapshot with a larger `--timeout-ms` fixes.
- `TIMEOUT`, `details.kind: resolution_identity_unknown`: a live read did not answer, so identity is unproven. Nothing was sent; retry.

Off macOS, identical twins have no ref path: only `--headed mouse-click --xy X,Y` can choose one. It takes the foreground, and a Linux Wayland session refuses it.

### Surfaces

Surfaces are overlays: `menu`, `menubar`, `sheet`, `popover`, `alert`, `focused`, plus OS shell kinds on some platforms. Read `supported_surfaces` from `status` before you ask for one. A kind this OS does not have returns `INVALID_ARGS` with the supported list in `details`. A shell surface needs no `--app`; on macOS, `menu-bar-extras` with `--app` reads that app's own status item. When it is closed you get `WINDOW_NOT_FOUND`; raise it with `open-system-surface`.

Use a surface snapshot for dialogs and menus, not a window snapshot. To reach one item inside an overlay, use `find --surface` instead of a full dump.

## find

Searches by role, name, value, text, description or native id. Use it first when you know the target.

```bash
agent-desktop find --app "App" --role button --name "OK" --exact
agent-desktop find --root @s8f3k2p9:e4 --role textfield --first
agent-desktop find --app "App" --surface menubar --name "Save" --exact --first
agent-desktop find --app "App" --role button --count
```

- Scope before you widen. `--root` searches one ref's subtree. `--surface` searches an overlay. Both cost a few hundred bytes instead of a full dump. They cannot combine.
- `--name` and `--text` match fuzzily. Add `--exact` for case-insensitive equality. Use `--limit 2` before a mutation when you need to know the match is unique.
- `--text` also matches ancestors whose subtree text contains the text. Use `--name` to match the node itself.
- `--role` is case-insensitive; `textarea`, `textbox` and `searchfield` fold to `textfield`. When a role filter matches nothing, `data.roles_present` lists the roles in the searched tree. Use it to tell a wrong role name from an empty screen.
- Unnamed elements omit `name`. Their content is in `value`, so search it with `--value`.
- A large tree, such as a file dialog, can pass the 5000 ms default `--timeout-ms`. Raise it or narrow the search. A timeout here does not mean the app hangs.

Every non-count response returns the `snapshot_id` that owns its refs:

```json
{ "data": { "snapshot_id": "s8f3k2p9",
  "matches": [ { "ref_id": "@s8f3k2p9:e5", "role": "button", "name": "OK", "states": ["enabled"] } ] } }
```

A match without `ref_id` is a context match: readable text with no action target. It carries `bounds` when the platform reports them. A match with a `ref_id` never carries `bounds`; read them with `get --property bounds`.

## get

Reads one property of a ref: `text` (default), `value`, `title`, `bounds`, `role`, `states`.

- `title` is the accessible name. It answers "what does this button say".
- `text` is what a person reads. It is the content for `textfield`, `combobox`, `listbox`, `datefield` and `timefield`, and the name everywhere else. If the preferred half is empty, the other half answers. A checkbox answers its label, not `1`.
- `value` is the raw value regardless of role (text, slider position).
- `text`, `value`, `bounds` and `states` read live state when the adapter can. A missing live value or bounds returns `null`. When an optional live read is unavailable, `get` can fall back to the saved ref entry's value, name, bounds or states.
- Only `bounds` reports whether it is live, in `data.live`. When it is `false`, the rectangle came from the snapshot and may be out of date. Check it before you pass bounds to `mouse-click`.

## is

Checks one boolean: `visible` (default), `enabled`, `checked`, `focused`, `expanded`, `selected`. Output: `{ "ref", "property", "result" }`. For `enabled`, an unknown native value returns `result: false` with `applicable: false`. That means unknown, not disabled.

## screenshot

```bash
agent-desktop screenshot --app "Finder" out.png
agent-desktop screenshot --screen 0 display.png
```

With no path, the PNG returns as base64 in `data`. `--screen` takes a display index from `list-displays`; `0` is the primary display. A screenshot is evidence for you, not proof that an action worked. Permission denial returns `PERM_DENIED` (see the platform skill).

## list-displays

Lists displays as `{ id, bounds, is_primary, scale }`, primary first. Use the array index, not `id`, with `screenshot --screen`.

## list-surfaces

```bash
agent-desktop list-surfaces --app "Finder"
```

Lists the overlay surfaces an app presents now, the values `snapshot --surface` accepts. Shell surfaces belong to the OS and never appear here. If a window entry carries `"unclassified": ["sheet"]` or `["menu"]`, the check could not read that window (often a busy app). Treat the missing entry as unknown, not absent.

## open-system-surface

```bash
agent-desktop --headed open-system-surface --surface action-center
```

Raises an OS shell surface. On Windows and Linux it returns the window it presents, in the `w-<id>` form that `list-windows` uses; on macOS `data` is only `{"surface": "dock"}` and `window` is left out, because no window owns these surfaces. It takes the foreground, so on Windows and Linux strict headless is refused with `POLICY_DENIED`; pass `--headed`. On macOS, `dock` and `menu-bar-extras` are always on screen, so they return headless with no `--headed`. An already-present surface returns without being raised again. A kind the OS does not expose returns `INVALID_ARGS` naming the kinds to use instead. `start-menu` is a Windows kind and `action-center` exists on Windows and Linux (GNOME); neither is a macOS kind. On macOS use `dock` or `menu-bar-extras`, and open Control Center or Notification Center by clicking its `menu-bar-extras` item. See the platform skill for the kinds.

## Chromium and Electron apps

The accessibility path is the default. It is the only path for an app that is already running and for native menus, dialogs and windows. For the web contents of an app you can launch fresh, `launch --cdp` plus a CDP client is faster than a skeleton walk. See `commands-system.md`.

--- references/commands-interaction.md ---

# Interaction Commands

Commands that change UI state. Run `agent-desktop <command> --help` for flags.

## Headless and headed

`--headed` is global (`agent-desktop --headed click @s8f3k2p9:e5`) and applies to every `batch` entry. A headed action may focus the exact source window first, and a pointer action needs a verified target point.

`press` is always physical keyboard input. `hover`, `drag`, `mouse-move`, `mouse-click` and `mouse-wheel` are physical cursor input and need `--headed`. Raw coordinates carry no window identity, so they never focus an app. `key-down`, `key-up`, `mouse-down` and `mouse-up` are reserved and never deliver input. They return `ACTION_NOT_SUPPORTED`, except that a headless `mouse-down` or `mouse-up` returns `POLICY_DENIED` first. Use `press`, `mouse-click` or `drag`.

Which gestures have a headless path:

| Command | Headless |
|---------|----------|
| `click`, `set-value`, `clear`, `select`, `check`, `uncheck`, `toggle`, `expand`, `collapse`, `scroll`, `scroll-to` | Yes, where the element advertises a semantic action (not `scroll` on Linux) |
| `type`, `right-click`, `focus` | OS-dependent. Read the platform skill for which need `--headed` |
| `double-click`, `triple-click`, `hover`, `drag`, `mouse-*` | No. They need `--headed` |

Native cross-app drag and drop may not start from synthetic events. It works for same-view drags and for web drag and drop.

## Read the result

A successful action reports what happened, not only that it ran.

| Field | Meaning |
|-------|---------|
| `data.steps` | Each mechanism tried, in order: `label`, `outcome` (`attempted`, `skipped`, `succeeded`), `mechanism` (`semantic_api` or `physical_synthetic`), `verified` |
| `data.disposition.delivery` | `delivered_verified` when the effect was observed, `delivered_unverified` when the app claimed success without an observable change |
| `data.post_state` | The target's state after the action, when it has one |
| `data.surfaces` | Overlays open once the action settled |

Stateful actions (`set-value`, `type`, `clear`, `check`, `uncheck`, `toggle`, `expand`, `collapse`) re-read state after they run. A readable contradiction returns `ACTION_FAILED` with `details.kind: "post_action_verification"`. A failed read keeps its own error code, so even `STALE_REF` or `TIMEOUT` can follow delivery. An unreadable postcondition does not fail the action. Missing evidence alone returns success with `delivered_unverified`, `details.verification_scope: "unavailable"` and `verification_reason: "insufficient_evidence"`.

- Secure text is redacted. A delivered write can return `delivered_unverified` with `verification_reason: "secure_field"`. This never turns a native delivery error into success.
- `set-value` and `type` verify the element value only (`verification_scope: element_value`, `application_commit: not_verified`). Confirm document-level effects, such as a table that should have resized, with an independent read.
- If `data.surfaces` lists a sheet, menu or alert, the app is waiting on it. Use `find --surface sheet` and answer it. A `delivered_unverified` result with an open surface usually means a confirmation is pending.

## Errors

Exit codes: `0` success, `1` structured error, `2` argument error. The `error` object can carry `details`, `recovery` and `disposition`. Ignore unknown keys.

| Code | Meaning | Recovery |
|------|---------|----------|
| `PERM_DENIED` | A required OS permission is missing | Read the platform skill |
| `ELEMENT_NOT_FOUND` | Ref cannot be resolved in the live UI | Snapshot again |
| `STALE_REF` | Ref no longer matches the live UI | Snapshot again, use the new ref |
| `AMBIGUOUS_TARGET` | Several live elements match the ref's identity, or it was not proven unique at capture | Act on a control unique in the window; identical twins need `--headed mouse-click --xy` (see `commands-observation.md`) |
| `SNAPSHOT_NOT_FOUND` | Snapshot id missing or expired | Snapshot again |
| `APP_NOT_FOUND` | App not running | `launch` it |
| `WINDOW_NOT_FOUND` | No matching window | Check the name, use `list-windows` |
| `ACTION_FAILED` | Action rejected, blocked, or contradicted by the result | Read `error.details`. A `checks[]` report names the blocking check. After delivery, read `disposition.retry` and `details.post_state` |
| `ACTION_NOT_SUPPORTED` | Element cannot do this | Use another command |
| `POLICY_DENIED` | A physical or headed path was blocked | Add `--headed` if physical input is intended. A dangerous key combo needs `--force` |
| `APP_UNRESPONSIVE` | A liveness probe also failed after an uncertain mutation | Take a fresh snapshot. Wait for recovery before you retry |
| `TIMEOUT` | Wait or actionability condition not met | Read `error.details.kind` |
| `INVALID_ARGS` | Bad arguments, or a protected system process was targeted for close | Check syntax |
| `PLATFORM_NOT_SUPPORTED` | The adapter lacks this method | Use another approach |
| `NOTIFICATION_NOT_FOUND` | Notification index or fingerprint no longer matches | List again |
| `INTERNAL` | Unexpected OS failure | Read `message`. Retry once only if `disposition.retry` is `safe` |

`TIMEOUT` `details.kind` values: `actionability_timeout` (the target never became actionable), `wait_timeout` (a `wait` condition; carries `predicate`, `timeout_ms`, `last_observed` or `last_error`), `chain_deadline` (an activation chain ran out of time; carries `value_before`, `value_at_timeout`, `target`, `mutated`). With `chain_deadline`, `mutated: true` or an unknown expanded state means re-read before you retry. `mutated: false` means a direct retry is safe.

## Actionability

Before a ref action dispatches, core checks the target under one bounded budget. `--timeout-ms` (default 5000) sets that budget. For `drag`, the same deadline also covers pickup, movement, drop delay and completion; gesture time is not added to it. The checks are `visible`, `stable`, `enabled`, `supported_action`, `policy`, `editable`, and `receives_events` for pointer delivery. Each is `pass`, `fail` or `unknown`. The full report is in `error.details`: `{ "actionable": false, "checks": [ { "check", "status", "reason" } ] }`.

- Transient checks (`visible`, `stable`, `enabled`, `receives_events`) are polled about every 100 ms until they pass. On expiry the result is `TIMEOUT` or `ACTION_FAILED`.
- A disabled target waits out the whole budget and ends `TIMEOUT` with `kind: actionability_timeout`; its `last_report` carries the failed `enabled` check. A target that is also off screen is not scrolled while it stays disabled, so the result does not depend on where the page was scrolled.
- A ref that matches nothing on a complete live read waits the whole budget and ends `STALE_REF` (`AMBIGUOUS_TARGET` if several match), not `TIMEOUT`. A `hover` or `drag` wait that ends on such a settled ref names that code too.
- Terminal checks (`supported_action`, `policy`, `editable`) cannot be healed by waiting. They fail at once with `ACTION_NOT_SUPPORTED` or `POLICY_DENIED`.
- `hover` and each ref endpoint of `drag` use a pointer resolver: live visibility and bounds, one scroll-into-view try, a second equal-bounds sample, then `receives_events`. They do not need an element action.
- `receives_events` runs only when the action reaches the target by pointer: a headed action, `hover`, `drag`, or a click with no semantic delivery. A headless click that dispatches by a semantic action skips it.
- `receives_events` fails with `reason: "occluded by <role>"` and an `occluder` of `{ role, name, bounds }` when another element is on top. Bring the target window to the front or dismiss the occluder, then retry. A blind retry fails the same way.
- `receives_events` fails open. An inconclusive hit test reports `unknown` and the action dispatches. A passing check is not proof that nothing covered the target.
- `details.kind: "live_read_incomplete"` with `retryable: false` means native reads failed on every poll. Take a fresh snapshot and use a fresh ref.
- Pick recovery from the failing check's `reason`: `wait --element <ref> --predicate actionable`, a fresh snapshot, or `--headed` when `policy` failed and physical input is intended.

Standard ref actions try a scroll into view first. If no scrollable ancestor exists, the result is `ACTION_FAILED` with `details.kind: "scroll_into_view_unsupported"` and `retryable: false`. Scroll the containing viewport with `scroll` instead. A scroll that may have moved but could not be confirmed carries `delivered_unverified`. Re-read the element before you assume no effect.

## Click

```bash
agent-desktop click @s8f3k2p9:e5
agent-desktop --headed double-click @s8f3k2p9:e3
agent-desktop --headed triple-click @s8f3k2p9:e2
agent-desktop right-click @s8f3k2p9:e5
```

- `click` is the primary activation. Headless uses the activation the element publishes. `--headed` clicks physically first where that is possible and reports `physical_synthetic` in `data.steps`. The app is observed to judge delivery, not the accessibility return code.
- `double-click` and `triple-click` are physical gestures and fail closed headless. For raw coordinates use `--headed mouse-click --xy X,Y --count 2` (or `3`).
- `right-click` opens the context menu. Then take `snapshot --surface menu`. Use `select` for combo boxes and menu buttons instead.
- A right-click can return `APP_UNRESPONSIVE` with uncertain delivery after a modal menu opened. Look at the effect first. Do not retry.

## Text input

```bash
agent-desktop type @s8f3k2p9:e2 "hello@example.com"
agent-desktop type @s8f3k2p9:e2 "hello world" --interval-ms 60
agent-desktop set-value @s8f3k2p9:e2 "new value"
printf '%s' 'hello' | agent-desktop set-value @s8f3k2p9:e2 --stdin
agent-desktop clear @s8f3k2p9:e2
agent-desktop focus @s8f3k2p9:e2
```

- `type` inserts text and checks the result when value and selection are readable. A readable mismatch returns `ACTION_FAILED`, and an unreadable result succeeds as `delivered_unverified`. Text sent as keystrokes reaches the field through the app's event queue, so the check re-reads the field while it changes, inside the `--timeout-ms` budget. If it settles on other text, or never settles, the result is `delivered_unverified` with `verification_reason: postcondition_mismatch`. Headed typing that focuses an inactive field can change the selection, and the result then stays unverified. Read the field with `get` before you write again.
- The default `--timeout-ms` of `type` is 5000 plus 30 ms per character of the text. An explicit `--timeout-ms` wins.
- `type --interval-ms N` (1 to 2000) types one keystroke every N ms inside one command; `--timeout-ms` then applies to each keystroke, and `0` makes each keystroke try once. A keystroke keeps combining marks, emoji sequences and CR LF together. The first keystroke is a full ref action (headed, it also focuses the window), and the rest go to the same element, taking the interaction lease one keystroke at a time. A headed keystroke is posted only while the target's process and focused element are unchanged; if focus moves, the burst stops with an error. The result adds `keystrokes` and `interval_ms`, and `post_state` is the field after the last keystroke. It stays `delivered_verified` only when that read shows the whole text; otherwise it is `delivered_unverified` with `verification_reason` `postcondition_mismatch`, `insufficient_evidence` (typed part way through the field) or `final_read_failed` (no `post_state`). `--wait-for` waits once, after the last keystroke. A failure part way through adds `details.typed_keystrokes` and `details.keystrokes` and is `delivered_unverified`: read the field before you type again.
- `set-value` writes the value directly through the semantic value path. It is faster than `type`, but it may not fire every UI callback. Use it for text fields, text areas and sliders.
- Use `--stdin` with `type` or `set-value` to read text from a pipe or redirected file. Terminal input is rejected. Provide either `--stdin` or a command-line value.
- The action timeout starts after the input ends; it doesn't limit this wait. Empty input and all line breaks are kept, including a final newline. Use `printf '%s'` to avoid adding one. Input must be valid UTF-8 without NUL bytes (`\0`). The limits are 10,000 bytes for `type` and 128 KiB for `set-value`.
- Batch uses the JSON `text` or `value` field, which puts the text in process arguments. Run secret steps as separate `--stdin` commands.
- To enter the text `--stdin`, put it after `--`, as in `agent-desktop type @s8f3k2p9:e2 -- --stdin`.
- `--stdin` keeps text out of process arguments and omits observed `value` fields from JSON results, including `post_state.value`. Other app text and screenshot artifacts aren't redacted.
- A cell that exposes no value write is not directly editable. Activate it, take a fresh snapshot, and target the editor that appears. Some apps expose no editor and accept only keyboard input.
- `clear` empties the element. `focus` sets keyboard focus without clicking.

For a shared editor, such as a spreadsheet cell, the edit is a sequence: activate the cell, snapshot, target the editor, write, then commit. Run the whole sequence from one writer. The interaction lease serializes single actions, not your sequence.

## Selection, toggle, expand

```bash
agent-desktop select @s8f3k2p9:e4 "Option B"
agent-desktop check @s8f3k2p9:e6
agent-desktop toggle @s8f3k2p9:e6
agent-desktop expand @s8f3k2p9:e7
```

- `select` picks an option by display text in a list, dropdown or combobox. For menu-backed controls it opens the menu, activates the item and checks the control value. A missing item or an unchanged value returns a structured error.
- `check` and `uncheck` are idempotent and verify the final state. Prefer them over `toggle`. Use `toggle` only when the current state is unknown, and it needs readable before and after state.
- `expand` and `collapse` act on disclosure triangles, tree items and accordions, and verify the final state.

## Scroll

```bash
agent-desktop scroll @s8f3k2p9:e1 --direction down --amount 3
agent-desktop scroll-to @s8f3k2p9:e8
```

- `scroll` moves a scroll area. Headless uses native scroll paths, but on Linux `scroll` is physical wheel input and needs `--headed` and X11 (see the Linux skill). Headed sends a physical wheel gesture where possible. With no safe mechanism it returns a structured error.
- `scroll-to` brings an element into view. Success means a re-read found it visible. It needs a ref. When only `bounds` exist, scroll the container with `scroll` or use `--headed mouse-wheel`.
- `mouse-wheel --x --y [--dx] [--dy]` posts a raw wheel event at a screen point. Use it for canvases and custom scroll surfaces with no accessibility scroll action.

## Keyboard

```bash
agent-desktop press return
agent-desktop press ctrl+shift+z
agent-desktop press cmd+s --app "TextEdit" --wait-for "button:Save" --wait-timeout 5000
```

- Key names: `return`, `escape`, `tab`, `space`, `delete`, `up`, `down`, `left`, `right`, `f1` to `f12`. Modifiers: `cmd`/`meta`, `ctrl`, `alt`, `shift`, joined with `+`. Modifier names and blocked combos differ by OS. Read the platform skill.
- A bare uppercase letter adds Shift: `press H` sends `shift+h`.
- `--app` or `--window-id` targets one app. Use `--window-id` when several instances share a name and `--app` alone is `AMBIGUOUS_TARGET`. Unscoped `press` goes to the foreground app.
- `press` reports `delivered_unverified`, because delivery does not prove the shortcut did its job. Wait for the expected effect once with `--wait-for` or `--wait-for-gone`. A timeout keeps the delivered result and is unsafe to retry blindly.
- To open a window with a shortcut, keep the press and the wait in one `batch`, so the baseline is taken before delivery: `press`, then `wait --event window-opened`. A failed wait does not make the press safe to repeat.
- Dangerous shortcuts are refused with `POLICY_DENIED` by the adapter. `--force` sends one anyway. Adding a modifier to a blocked shortcut usually gives another blocked one.

## `--wait-for` and `--wait-for-gone`

Global flags that poll the tree until a selector matches (or stops matching) and then return a snapshot envelope.

```bash
agent-desktop snapshot --app Finder -w "button:OK"
agent-desktop click @s8f3k2p9:e5 -w ":Saved!"
agent-desktop click @s8f3k2p9:e5 --wait-for-gone "progressindicator" --wait-timeout 5000
```

- The selector is `role:text`, split on the first `:`. `"button"` is role only. `":Saved!"` is text only. Text searches name, value and description.
- They work on `snapshot`, `press` and every ref action. Other commands (`find`, `launch`, ...) return `INVALID_ARGS`. `--root` cannot combine with them. Batch entries never inherit an outer `-w`.
- `--wait-timeout` defaults to 30000. On expiry: exit `1`, `TIMEOUT`, `details.kind: "wait_timeout"`, `details.snapshot_id` of the last tree. A post-action timeout also embeds `details.after_action`.
- A ref action polls the acted-on ref's window. The action result is kept under `after_action`.
- `--wait-for-gone` succeeds with `{ "gone": true, "target_absent": true }` when the app or window itself closed.
- For `drag`, `--wait-for-scope to|from` picks which endpoint window to poll (default `to`).

## Mouse

```bash
agent-desktop --headed hover @s8f3k2p9:e5
agent-desktop --headed drag --from @s8f3k2p9:e1 --to @s8f3k2p9:e5
agent-desktop --headed drag --from-xy 100,200 --to-xy 400,500 --drop-delay 800
agent-desktop --headed mouse-click --xy 500,300 --count 2
agent-desktop --headed mouse-move --xy 100,200
```

- `hover` moves the cursor to an element center or to `--xy`. A positive `--duration` is rejected, because a stateless process cannot own the cursor during a dwell. Hover, then `wait <ms>`.
- With `--headed`, a ref endpoint must focus its exact window first. If focus cannot be confirmed, the command fails before delivery. Coordinate-only input never focuses.
- `drag` accepts refs, coordinates, or a mix. The destination app is never pre-focused, because raising it could cover the source point. For a cross-app drag, keep the destination visible. Both endpoints still pass visibility, stability and hit-test checks.
- `drag --timeout-ms` covers the whole gesture as well as target preparation. An explicit `--duration` plus `--drop-delay` at or above the budget returns `INVALID_ARGS` before target work. Leave additional room for platform pickup/default delays, resolution and completion: for a 5000 ms movement, use `--duration 5000 --timeout-ms 10000`. A valid request can still return `TIMEOUT` if preparation consumes the remaining gesture budget. Optional `--wait-for`/`--wait-for-gone` verification has its own separate wait budget.
- A drop target often needs the item to dwell over it. The default `--drop-delay` is 500 ms (150 ms on Linux, where a longer hold opens a hovered Files folder). Raise it (800 to 1200) for list reorders and cross-window drops.
- `mouse-click` takes `--button left|right|middle`, `--count`, and `--modifiers`.

## Choose the command

| Goal | Use | Fall back to |
|------|-----|--------------|
| Click a button | `click @ref` | `--headed mouse-click --xy X,Y` |
| Fill a text field | `set-value @ref "text"` | `clear` then `type` |
| Set a checkbox | `check` / `uncheck` | `toggle` when state is unknown |
| Pick a dropdown option | `select @ref "Option"` | open the menu, then `snapshot --surface menu` |
| Open a context menu | `right-click @ref` | `--headed mouse-click --button right` |
| Move between fields | `press tab` | `focus @ref` |
| Copy text out of a field | `get @ref --property value` | `press` the copy shortcut, then `clipboard-get` |
| Find an off-screen item | `scroll @area`, then `find` | `scroll-to @ref` |

## Agent cursor

A visible cursor overlay is optional presentation. Enable it once per session (see `commands-system.md`). It shows where each action lands and never changes what the action does.

--- references/commands-system.md ---

# System Commands

App lifecycle, windows, notifications, clipboard, wait, batch, sessions, health. Run `agent-desktop <command> --help` for flags.

## launch

```bash
agent-desktop launch "System Settings"       # macOS display name
agent-desktop launch "TextEdit" --activate
agent-desktop launch "MyTool" --arg /tmp/notes.txt --env KEY=VALUE --no-attach
agent-desktop launch "Obsidian" --cdp
```

`launch` returns once the process runs. The identifier differs by OS: the examples use macOS display names, and the platform skill names the form for its OS. By default it attaches to a running instance. `--no-attach` starts a fresh instance instead of attaching: on Windows it returns `ACTION_FAILED` if a matching app is already running; on macOS it launches a second instance alongside the running one. For an `--arg` value that starts with `-`, use `--arg=<value>`.

The process running and the app showing a window are separate facts:

```json
{ "app": "TextEdit", "pid": 611, "window": { "id": "w-110407", "title": "Open", "visible": true } }
```

- `window` is present when the app already has one, and omitted when it has none. Its absence is not a failure. `launch` still returns `ok: true`.
- A document-based app may open its first window only when brought forward. Use `--activate`: it asks the app to present a window and waits for it up to `--timeout` (default 30000). This brings the app forward, so it is not headless. Or trigger the window yourself and use `wait --event window-opened`.
- A process that exits before it shows a window returns `APP_UNRESPONSIVE`.
- Windowless and menu-bar-only apps report no `window`. Use `list-apps` and read `presentation`.
- An app built on Chromium may return `renderer: "chromium"` and a `suggestion`. These are hints. The accessibility path still works. A missing `renderer` never proves the app is native.

### Web contents of a Chromium app (`--cdp`)

Use `--cdp` for Electron and Chromium apps whose web contents are dense or slow to walk (Slack, VS Code, Discord, Obsidian, Notion). It launches the app fresh with a loopback-only debugging port, polls until the endpoint answers, then returns. Pass a port, or omit it to let the OS pick a free one.

```json
{ "app": "Obsidian", "pid": 4821, "cdp": { "port": 9229, "http_endpoint": "http://127.0.0.1:9229",
  "websocket_url": "ws://127.0.0.1:9229/devtools/browser/<id>", "product": "Chrome/142.0.7444.265" } }
```

The port exists only for a fresh process. `launch` never quits a running app for you, because that loses the user's state. A running target returns `ACTION_FAILED` with `details.kind: "cdp_requires_fresh_launch"`. Run `close-app`, confirm the exit, then launch again with `--cdp`.

| `details.kind` | Meaning | Recovery |
|----------------|---------|----------|
| `cdp_requires_fresh_launch` | App already running | `close-app`, confirm exit, relaunch |
| `cdp_port_in_use` (`INVALID_ARGS`) | The named port is bound | Name another port, or omit it |
| `cdp_switch_conflict` (`INVALID_ARGS`) | `--arg` carried a `--remote-debugging-*` or `--remote-allow-origins` switch | Drop that `--arg` |
| `cdp_endpoint_unavailable` | No endpoint answered before the deadline | The app stays running. Use the accessibility path |

Handoff: agent-desktop never talks to the port itself. Check `command -v agent-browser`. If it exists, run `agent-browser connect <port>` and use its snapshot, click and type workflow (`agent-browser skills get electron` has the guide). Playwright, Puppeteer and other CDP clients also work. Do not write raw CDP by hand or call app-internal APIs. If no client exists, ask the user to run `npm install -g agent-browser`, or stay on the accessibility path.

Keep these on agent-desktop even with CDP connected: the native menu bar, file dialogs and sheets, window management, notifications, screenshots, and any app you did not launch. While the port is open, any local process of the same user can control the app's web contents. Request `--cdp` only for the step that needs it. `close-app` ends the exposure.

## close-app

`close-app` closes the app and all its windows. There is no `close-window`
command. To close one of several windows, snapshot the intended `--window-id`
and click its own Close button ref, then confirm the close with a `batch` of the
click and `wait --event window-closed`. Answer any save prompt through its
sheet. For the last window, use `close-app` if you intend to exit the app.
Ctrl+W may close only a tab or document, leaving the window open.
The Linux windows reference includes a Bash recipe that selects a fresh Close ref.

```bash
agent-desktop close-app "TextEdit"
agent-desktop close-app "TextEdit" --force
```

Success is reported only after the process is seen gone: `{ "method": "graceful" | "force", "disposition": { "delivery": "delivered_unverified" | "delivered_verified" | "not_delivered" }, "target": { "kind": "app", ... } }`. `not_delivered` means the app had already exited. Read `disposition`, not `ok`, to learn what was proved. If a save dialog appears, snapshot it and answer it. `--force` ends the process. Protected system processes return `INVALID_ARGS` with `not_delivered`, not `PERM_DENIED`.

## list-apps

Lists running GUI apps as `{ name, pid, bundle_id, presentation }`. `--app` filters by name substring. `presentation` is `foreground` (ordinary windows), `background` (no Dock entry, such as menu-bar items and hotkey overlays), or omitted (helper processes). Apps with no UI are excluded.

## Windows (OS windows)

```bash
agent-desktop list-windows --app "Finder"
agent-desktop focus-window --window-id w-4521
agent-desktop resize-window --app "TextEdit" --width 800 --height 600
agent-desktop move-window --app "TextEdit" --x 0 --y 0
agent-desktop minimize --app "TextEdit"   # maximize, restore likewise
```

- `list-windows` returns `{ id, title, app_name, pid, bounds, is_focused, accessible }`. Use a `w-<id>` with `--window-id` when an app has several windows.
- `accessible: false` means semantic commands cannot reach that window. Targeting it returns `ACTION_NOT_SUPPORTED` with `kind: "window_without_accessibility_element"`. It still accepts screenshots and coordinate input. Choose another window.
- `focus-window` needs at least one identifier. It confirms the OS reports that window as focused. Otherwise it returns `ACTION_FAILED`.
- `restore` undoes a minimize and returns the window to its earlier placement. It does not promise to un-maximize.

## Notifications

Commands: `list-notifications`, `dismiss-notification`, `dismiss-all-notifications`, `notification-action`, `wait --notification`. They drive the OS notification surface: Notification Center on macOS, Action Center on Windows, the GNOME Shell message list on Linux. Command shapes and JSON fields are the same on each. The platform skill states its limits.

- Output is verbatim. Titles and bodies are not redacted. Treat anything you route onward as sensitive.
- On macOS and Windows, headless listing works only when the surface is already open. When it is closed, a strict-headless call returns `POLICY_DENIED`. Use `--headed`, which may open the surface and restore the earlier foreground app. Linux lists headless even when the list is closed.
- Every mutation needs `--headed`. A single-notification mutation also needs a fingerprint from the same listing: `--expected-app` or `--expected-title`. Notifications reorder between listings. When the row at the index no longer matches, the call returns `NOTIFICATION_NOT_FOUND` and presses nothing. Without a fingerprint, `INVALID_ARGS`.
- `list-notifications` returns `{ index, app_name, title, body, actions }`, with 1-based indexes. `--app`, `--text`, `--limit` filter.
- `notification-action INDEX "Reply"` clicks a named button. An action the entry lacks returns `ACTION_NOT_SUPPORTED` and changes nothing.
- `dismiss-all-notifications` returns `{ dismissed_count, failures, failed_count }`. A failure to close the surface afterward is not reported as an error.
- `wait --notification` detects a new entry against a baseline taken at wait start. Transient errors retry within `--timeout`. On macOS and Windows, a headless wait sees only an already-open surface.

## Clipboard

```bash
agent-desktop clipboard-get --format auto
agent-desktop clipboard-get --format image --out /tmp/clip.png
agent-desktop clipboard-set "Hello"
printf '%s' 'Hello' | agent-desktop clipboard-set --stdin
agent-desktop clipboard-set --image /tmp/a.png
agent-desktop clipboard-set --file-url /tmp/a.txt --file-url /tmp/b.txt
agent-desktop clipboard-clear
```

- Formats: `text` (default), `auto` (file references, then image, then text), `image`, `file-urls`. Output is `{ "type": "text", "text": ... }`, `{ "type": "file_urls", ... }`, or `{ "type": "image", "path", "width", "height" }`. When the clipboard has nothing in that form: `{ "type": "<format>", "found": false }`.
- Image bytes go to `--out`, or to a private file under the active session directory (or `~/.agent-desktop/tmp`).
- `clipboard-set` writes one representation per call. `--file-url` and `--image` win over the positional text. Every `--file-url` path must exist, or `INVALID_ARGS`.
- Use `clipboard-set --stdin` to read up to 128 KiB from a pipe or redirected file without putting it in process arguments. Terminal input is rejected. It cannot be combined with a command-line value, `--image`, or `--file-url`.
- The command waits until the input ends. Empty input and all line breaks are kept, including a final newline. Use `printf '%s'` to avoid adding one. Input must be valid UTF-8 without NUL bytes (`\0`).
- Batch uses the JSON `text` field, which puts the text in process arguments. Run secret steps as separate `--stdin` commands. To copy the text `--stdin`, use `agent-desktop clipboard-set -- --stdin`.
- A write that loses clipboard ownership mid-way reports `delivered_unverified`, not a false success.

## wait

```bash
agent-desktop wait 1000
agent-desktop wait --element @s8f3k2p9:e5 --predicate actionable --action type --timeout 5000
agent-desktop wait --element @s8f3k2p9:e5 --predicate value --value "Done"
agent-desktop wait --window "Save As" --app "TextEdit"
agent-desktop wait --text "Loading complete" --app "Safari"
agent-desktop wait --menu --app "Finder"
agent-desktop wait --event window-opened --app "Finder"
```

Use `wait`, not a fixed sleep. `--timeout` defaults to 30000 ms. Modes:

- **Time.** `wait <ms>` pauses.
- **Element.** `--predicate` is `exists` (default), `enabled`, `visible`, `actionable`, or `value` (with `--value`). `actionable` checks readiness for `--action` (`click` default, `type`, `set-value`, `clear`). Use `--action type` before a wait-then-type flow. The editability check runs only for editing actions. `--element` takes a qualified ref (`@<snapshot_id>:eN`); the wait polls the snapshot embedded in the ref.
- **Window.** Waits for a window whose title contains the text. `--app` narrows. On timeout, `details.last_observed` lists the scoped window count and up to eight titles.
- **Text.** Selects one app window, then waits for text in that tree. `--count N` waits until exactly N nodes match, and the result carries `count`. Several eligible windows, such as a document and its save dialog, return `AMBIGUOUS_TARGET` before any text check. `--window-id` does not narrow a text wait. To recover, find the target with `list-windows --app <app>` and inspect it with `snapshot --app <app> --window-id <id> -i`. For a dialog, use `wait --window <title> --app <app>`, then `snapshot --surface sheet` (see the dialog workflow). `--window` and `--text` are separate modes and cannot combine.
- **Menu.** `--menu` waits for a menu surface to open. `--menu-closed` waits for it to close.
- **Event.** `--event` is one of `window-opened`, `window-closed`, `app-launched`, `app-terminated`, `focus-changed`, `surface-appeared`, `surface-dismissed`. It diffs a baseline taken at wait start against fresh reads, so you need no window id up front. `--window-id` and `--window` narrow it.

For `wait --event` only, `--app` resolves once, at wait start, to one process instance. (`wait --window` filters by app name on every poll.) A later process of the same name is invisible to the wait. Two running instances return `AMBIGUOUS_TARGET`. When no app matches:

- `app-launched`, `window-opened`, `surface-appeared`: keep polling until the timeout. Use these when you race a launch.
- `app-terminated`, `window-closed`, `surface-dismissed`: return `"found": true` with `"target_unresolved": true` at once. A misspelled `--app` gives the same answer, so check the name.
- `focus-changed`: returns `APP_NOT_FOUND`.

On macOS and Windows, an existing window can still satisfy `--window` while its app is unresponsive. A wait can return top-level `APP_UNRESPONSIVE` before its timeout; handle that error directly. `wait --event` keeps polling after retryable read failures and includes the latest failure in `details.last_error` if it times out. A non-retryable error ends the event wait immediately.

The platform skills state the event and menu wait rules that differ by OS.

A `TIMEOUT` from `wait` carries `details.kind: "wait_timeout"`, `last_observed` or `last_error`, and `baseline_counts` for events.

## batch

```bash
agent-desktop batch '[
  {"command":"click","args":{"ref_id":"@s8f3k2p9:e1"}},
  {"command":"wait","args":{"ms":200}},
  {"command":"type","args":{"ref_id":"@s8f3k2p9:e2","text":"hello"}}
]' --stop-on-error

agent-desktop batch '[
  {"command":"click","args":{"ref_id":"@s8f3k2p9:e1"}},
  {"command":"wait","args":{"event":"window-opened","app":"TextEdit","timeout":5000}}
]' --stop-on-error
```

Batch runs entries in order in one process. It is not a transaction. Entries use the same typed commands, policy checks and dispatch as the CLI. Use `args`, not `params`. Unknown fields are rejected, and nested `batch` is rejected. Pass `--stop-on-error` to halt at the first failure. Each entry may carry `"session": "id"`, otherwise it inherits the top-level session. An entry whose session ended before dispatch is `not_started` with reason `session_ended`. An ended top-level session refuses the whole batch with `INVALID_ARGS` (`details.kind: session_ended`) before any entry runs. Snapshot args use `skeleton`, `root`, `interactive_only`.

Wait entries use flat JSON keys matching the wait argument fields. For event waits, use `event` and optional `app`, `timeout` (milliseconds; defaults to 30000), `window`, and `window_id`. For example, the batch above waits up to five seconds for a new TextEdit window. `window` and `window_id` narrow only window lifecycle events (`window-opened`, `window-closed`, `focus-changed`); they do not scope text waits. In an action-then-event sequence, the batch captures the event baseline before the action, and does not start the action if that baseline read fails.

Keys are the command's own field names, so a positional argument is named after itself rather than after its placeholder: `press COMBO` is `{"combo":"cmd+s"}`, `click REF` is `{"ref_id":"@s8f3k2p9:e1"}`, and `type REF TEXT` takes `ref_id` and `text`. A flag drops its leading `--` and writes `-` as `_`, so `--timeout-ms` is `timeout_ms`.

## Sessions and traces

A session is an on-disk container under `<state root>/sessions/<id>/` with a manifest, snapshot refmaps and, when tracing is on, a `trace/` directory. The state root is `~/.agent-desktop`. `AGENT_DESKTOP_HOME` relocates it. It must be an absolute path, or the command fails with `INVALID_ARGS`. `status` reports it as `state_root`.

```bash
export AGENT_DESKTOP_SESSION="$(agent-desktop session start --name "invoice-bot" | jq -r '.data.session_id')"
agent-desktop session end "$AGENT_DESKTOP_SESSION"
```

- `session start` creates the session and prints `{ session_id, name, trace, created_at }`. `--name` must be 1 to 128 bytes with no control characters, or `session start` returns `INVALID_ARGS`. `session start` does not activate later processes. Pass the id with global `--session <id>` or `AGENT_DESKTOP_SESSION`. `--session` wins over the variable. With neither, commands use the global namespace.
- A session owns its trace and its latest-snapshot namespace. Lookup never searches another session. A session-owned ref still requires the same `--session` or `AGENT_DESKTOP_SESSION` scope, even though a qualified ref embeds its snapshot id.
- Tracing needs a manifest with `trace: on` (the default). `--no-trace`, or a bare `--session <id>` without a manifest, gives a namespace with no trace files. `--trace <path>` overrides to one file. `--trace-strict` fails on trace setup errors. `version` and `skills` write no trace events when run from the command line.
- `--screenshots` records pre and post PNGs and refmap copies. They are unredacted and sensitive. They need tracing on.
- Several agents may share one session id. Each should use qualified refs from its own snapshot.
- `session list`, `session end [id]` and `session gc` list, seal and reclaim sessions. `session end` is repeatable, including when the active scope has already ended; other commands refuse an ended scope, except `version` and `skills` when run from the command line. `session gc --ended` removes every ended session that no running command holds (only those older than `--older-than <secs>`, when given), trace segments included; plain `session gc` also keeps a session that wrote a snapshot or trace segment in the last 5 minutes.
- `trace show [--limit N] [--event PREFIX]` returns the merged event timeline (default tail 500, `0` for all). `trace export [--out path.html]` writes a self-contained HTML viewer. Without `--out` it writes `trace-<session>.html` inside the session directory, and `data.path` names the file. Both need no OS permission. Readers reject input beyond 32 MiB, 100,000 events, or 4,096 directory entries, regardless of the output limit. Session writers share a recording budget across processes and stop before those limits, reserving 16 directory entries for artifacts and bookkeeping. Start a new session to continue recording; existing events remain readable. Failed writes may consume reserved capacity. Older or externally modified traces beyond the limits must be split before reading. Only regular segment files are read; lines over 8 MiB are skipped with bounded buffering.
- Trace lines redact sensitive fields (`text`, `value`, `name`, `title`, `url`, ...) to `{ "redacted": true }`.
- `status` shows `session_id`, `tracing` and `artifacts`.

### Cursor overlay

`cursor-overlay enable` draws an agent cursor and ripple for actions. It affects presentation only. `enable` returns `data.rendered`: `false` means the setting was saved but nothing was drawn. `session start --cursor` enables it at start. `agent-desktop cursor-overlay enable --help` lists the style, image and motion flags with their ranges and defaults. Settings persist in the session and in per-agent profiles. After an upgrade, run `cursor-overlay disable`, then `enable`, to restart the renderer with the new settings.

On macOS:

- `--travel-ms MIN,MAX` needs `30 ≤ MIN ≤ MAX`. Travel max plus `--dwell-ms` must be at most 700 ms, or the command returns `INVALID_ARGS`.
- Reduce Motion skips travel and dwell. Physical headed drags keep their own motion.

On macOS and Windows:

- The label is a black pill with white text in the system font (SF Pro on macOS, Segoe UI on Windows), sized to the text and set below and right of the cursor's tip. A label wider than 360 pt is cut with an ellipsis, and an empty label shows no pill.
- `--accent` colours the cursor body as well as the ripple, the element outline and the caret; `--fill` gives the body a different colour.
- `--image` and `--pointer-image` take a PNG of at most 2 MiB and 1024 pixels per side, drawn at `--size` with the hotspot on the point the cursor targets. Relative paths resolve at `enable`. `--fill` and `--rim` conflict with `--image`. A missing or invalid image falls back to the arrow. With `--image`, `enable` draws no greeting.
- The pointer image shows on arrival at a pressable control. Text fields keep the arrow.

Windows accepts the motion settings but keeps its built-in motion.

On macOS and Windows, after `type` or `set-value` lands, the overlay draws the agent's caret, a thin bar in the accent color, at the field's insertion point and leaves the element outline off. `type --interval-ms` moves the caret with each keystroke while the cursor stays put. A field that reports no insertion point keeps the outline and gets no caret. The caret goes away when the cursor sets off for somewhere else, and stays for another `type` into the same field. After `press` delivers, a caret that is showing moves to the focused field's new insertion point, or disappears when the focused element has none. `type` plays the click ripple only when its field does not already have keyboard focus.

Multi-agent cursors (macOS and Windows): start with `session start --cursor --multi-agent`, then pass the returned session id to every subagent.

- Desktop UI actions then require an agent id: global `--agent-id <id>` or `AGENT_DESKTOP_AGENT_ID`. The flag wins. Observations, clipboard commands and session administration do not need one.
- An id has 1 to 64 letters, digits, `-` or `_`. It is scoped by session. Each distinct id gets its own cursor, and a reused id reuses its cursor.
- A headless action moves its cursor before it takes the interaction lease, so several agents' cursors travel at the same time. The actions still take turns, and commands that draw the same cursor take turns from its travel to its click effect.
- `--agent-id <id> cursor-overlay enable` saves a style for that agent. Do not add `--multi-agent` to it.
- `cursor-overlay disable` and `session end` stop every cursor in the session, even when you pass an agent id.

## status, permissions, version

- `status` returns adapter health, platform, the permission report, `supported_surfaces`, the latest snapshot (`snapshot_id`, `ref_count`), `session_id`, `tracing`, `state_root`.
- `permissions` returns `accessibility`, `screen_recording` and `automation`, each as `{ "state": "granted" | "denied" | "not_required" | "unknown" }`, with a `suggestion` when denied. It is cached per process. `permissions --request` asks the OS to prompt, through a bounded isolated helper so a stalled prompt cannot hang the command. It is the only path that prompts. On macOS, `permissions --guide` opens System Settings at the missing permission with an on-screen guide, adds `"guide": "started" | "already_running" | "not_needed"` to the result, and returns without waiting. Other platforms return `PLATFORM_NOT_SUPPORTED` for `--guide`. What to grant is in the platform skill.
- `version` returns `{ version, target, os }`.

## skills

Skills ship inside the binary. The JSON envelope holds the markdown in `data.content`.

```bash
agent-desktop skills                            # list skills and references
agent-desktop skills get desktop                # this skill
agent-desktop skills get desktop workflows      # one reference
agent-desktop skills get platform               # skill for the current OS
```

--- references/workflows.md ---

# Common Workflows

Patterns for multi-step desktop automation. Every ref comes from the latest snapshot output.

## First-Time Setup

Check the platform and permissions before any automation.

```bash
agent-desktop status
agent-desktop permissions
```

- On macOS, the terminal needs Accessibility permission, and Screen Recording for screenshots. If `permissions` reports `denied`, run `agent-desktop permissions --guide`. It opens System Settings at the missing permission with a panel that shows the user which app to drag into the list.
- On Windows, there is no permission dialog for same-integrity targets. Input into an elevated target needs an equally elevated terminal.
- On Linux, there is no permission dialog. The session needs a running AT-SPI bus and `status` must report `accessibility` as `granted`. Run the tool in the same desktop session as the target app. If `status` reports it denied, read the bus section of the Linux skill.

Then run `agent-desktop skills get platform` for the details of your OS.

## Dense app: skeleton, drill, act, verify

Use this for Electron apps and any app with more than about 50 interactive elements.

```bash
agent-desktop snapshot --skeleton --app "Slack" -i --compact
# group "Channels" @s8f3k2p9:e2 (children_count: 42)
agent-desktop snapshot --root @s8f3k2p9:e2 -i --compact
agent-desktop click @s8f3k2p9:e18
agent-desktop snapshot --root @s8f3k2p9:e2 -i --compact
```

- Re-drilling a root replaces that root's refs and the refs of drills made under it. Skeleton refs elsewhere, and drills in other regions, stay valid.
- Interactive elements inside skeleton depth already have normal refs.
- If you know the role or exact name, skip the map and run `find` with `--role --name --exact`.

## Fill a form

```bash
agent-desktop snapshot --app "System Settings" -i --compact
agent-desktop set-value @s8f3k2p9:e3 "My MacBook Pro"
agent-desktop click @s8f3k2p9:e8
agent-desktop snapshot --app "System Settings" -i --compact
```

- Prefer `set-value`. Use `clear` then `type` when the field needs real key events.
- Read the result: `delivered_verified` confirms the field value only, not that the app accepted it. Verify the outcome in the UI.
- To move field to field without a ref for each, use `press tab` and `type`.

## Navigate menus

```bash
agent-desktop find --app "TextEdit" --surface menubar --name "Save As…" --exact --first
agent-desktop click @s8f3k2p9:e5
agent-desktop wait --window "Save" --app "TextEdit"
agent-desktop snapshot --app "TextEdit" --surface sheet -i
```

- `find --surface menubar` returns one ref instead of the whole menu bar.
- To walk a menu by hand: click the menu bar item, `wait --menu`, `snapshot --surface menu -i`, click the item, `wait --menu-closed`.
- A headless `press` never runs a menu item. Find the item and `click` it instead.

## Dialogs, sheets and alerts

```bash
agent-desktop wait --window "Save As" --app "TextEdit" --timeout 5000
agent-desktop snapshot --app "TextEdit" --surface sheet -i
agent-desktop set-value @s8f3k2p9:e2 "my-document.txt"
agent-desktop click @s8f3k2p9:e5
agent-desktop snapshot --app "TextEdit" -i
```

Snapshot the surface (`sheet`, `alert`, `popover`), not the window, while an overlay is open. Never use `--skeleton` on a surface. After the dialog closes, snapshot the window again for fresh refs. When an action leaves `data.surfaces` non-empty, answer that overlay next.

## Right-click context menu

```bash
agent-desktop right-click @s8f3k2p9:e3
agent-desktop snapshot --app "Finder" --surface menu -i
agent-desktop click @s8f3k2p9:e7
agent-desktop wait --menu-closed --app "Finder" --timeout 2000
```

If `right-click` returns `APP_UNRESPONSIVE`, the menu may have opened. Look at the screen state first. Do not retry blindly. Some OSes need `--headed` for right-click (platform skill).

## Scroll to find an item

```bash
agent-desktop snapshot --skeleton --app "App" -i --compact
agent-desktop snapshot --root @s8f3k2p9:e2 -i --compact
agent-desktop scroll @s8f3k2p9:e8 --direction down --amount 5
agent-desktop find --app "App" --name "Target Item" --exact
```

Repeat `scroll` and `find` until `find` returns a ref. Then `click` it. If a list is virtualized and the row never appears, scroll the container instead of `scroll-to`.

## Wait for async UI

```bash
agent-desktop click @s8f3k2p9:e5
agent-desktop wait --text "Download complete" --app "App" --timeout 30000
agent-desktop wait --element @s8f3k2p9:e10 --predicate actionable --timeout 10000
```

Use the wait primitive that matches the signal: text, element, window, menu or event. After `launch`, a dialog trigger or a menu click, wait before you snapshot.

## Check before act

```bash
agent-desktop is @s8f3k2p9:e6 --property checked
agent-desktop check @s8f3k2p9:e6
```

`check` and `uncheck` are idempotent. Use them instead of `toggle`. If a toggle result is `delivered_unverified`, read the state with `is` before you act again.

## Copy text from an element

Read it directly: `agent-desktop get @s8f3k2p9:e5 --property value`. If the element does not expose its text, focus it, select all, copy with the OS shortcut through `press`, then run `clipboard-get`.

## Drag and drop

```bash
agent-desktop --headed drag --from @s8f3k2p9:e3 --to @s8f3k2p9:e8
agent-desktop --headed drag --from-xy 100,200 --to-xy 500,400 --drop-delay 800
```

Drag is physical and needs `--headed`. Confirm the drop by reading the destination state, not the command's `ok`.

## Multiple windows

```bash
agent-desktop list-windows --app "Finder"
agent-desktop focus-window --window-id w-5678
agent-desktop snapshot --app "Finder" --window-id w-5678 -i
```

## Launch, automate, close

```bash
agent-desktop launch "Calculator"       # macOS name; on Windows use "calc.exe" or an absolute path
agent-desktop snapshot --app "Calculator" -i
agent-desktop close-app "Calculator"
```

Read `data.window` in the launch result. If it is absent and you need a window, use `launch --activate` or `wait --event window-opened`. The launch identifier rules differ by OS (platform skill).

## Chromium app: two tools

Slack, VS Code, Discord and similar apps are Chromium based. Use agent-desktop for native surfaces and a CDP client for dense web contents.

```bash
agent-desktop launch "Slack"       # macOS name; on Windows use the absolute path to slack.exe
agent-desktop close-app "Slack"
agent-desktop wait --event app-terminated --app "Slack" --timeout 10000
agent-desktop launch "Slack" --cdp 9222
agent-browser connect 9222
```

`--cdp` needs a fresh launch, so close a running app first. Drive the web contents with the CDP client. Keep menus, file dialogs, windows, notifications and screenshots on agent-desktop. If no CDP client exists, skip `--cdp` and use the skeleton workflow on the accessibility path. It always works.

## Notifications

```bash
agent-desktop --headed list-notifications --app "Slack"
agent-desktop --headed notification-action 1 "Reply" --expected-app Slack --expected-title "#general"
agent-desktop --headed dismiss-notification 1 --expected-app Slack
```

macOS (Notification Center), Windows (Action Center) and Linux (GNOME Shell) support these commands. List first and copy the fingerprint from the listing. Notifications reorder, so a stale index fails with `NOTIFICATION_NOT_FOUND` instead of pressing the wrong row.

## Batch

```bash
agent-desktop batch '[
  {"command":"click","args":{"ref_id":"@s8f3k2p9:e1"}},
  {"command":"wait","args":{"ms":200}},
  {"command":"press","args":{"combo":"return"}}
]' --stop-on-error
```

Batch saves process starts. It is not a transaction. Entries after a failure run unless you pass `--stop-on-error`.

## Trace a multi-step run

This example uses `jq` to read the session id returned by `session start`.

```bash
session_start=$(agent-desktop session start --name "invoice-bot")
AGENT_DESKTOP_SESSION=$(printf '%s\n' "$session_start" | jq -er '.data.session_id')
export AGENT_DESKTOP_SESSION
agent-desktop status
agent-desktop trace show --limit 50
agent-desktop session end "$AGENT_DESKTOP_SESSION"
```

`status` confirms `session_id` and `tracing`. Use one session per run. Concurrent agents set the same variable and use qualified refs from their own snapshots.

## Anti-patterns

The core skill already states the rules on refs, waits, headed mode and retries. These are the other common mistakes:

1. **Full snapshots of a dense app.** Use `--skeleton` and `--root`, and re-drill only the region that changed. A full tree costs far more tokens.
2. **Coordinates when a ref exists.** Semantic actions are more reliable than coordinate clicks.
3. **Skipping `status` and `permissions`.** A missing permission looks like an empty tree.
4. **Window snapshot while an overlay is open.** Snapshot the surface instead.
5. **Hand-rolled CDP.** Use a real CDP client. Raw WebSocket scripts and app-internal APIs break silently and verify nothing.
6. **Parallel writers on one editor.** Click-to-edit, type and commit are not atomic. Serialize the sequence, and after an uncertain delivery read the state before you act.
