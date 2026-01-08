# BrkRaw Hook Template

This repository is a template for implementing a BrkRaw dataset hook (rules/specs/transforms + Python hook entry points).

## Maintainer workflow (developers)
- Copy this template into a new repository, then update `pyproject.toml` metadata (name, entry point, dependencies) before publishing to PyPI.
- Implement the dataset-specific hook in `src/brkraw_hook_template/hook.py`. BrkRaw expects a `HOOK` dict that exposes `get_dataobj` and `get_affine` (and optionally `convert` for a richer workflow).
- Declare hook assets in `src/brkraw_hook_template/brkraw_hook.yaml`, which references package-local directories like `src/brkraw_hook_template/docs/`, `src/brkraw_hook_template/rules/`, `src/brkraw_hook_template/specs/`, and `src/brkraw_hook_template/transforms/`.
- Use `src/brkraw_hook_template/docs/` as a writing template: define scope, document the rule/spec/transform flow, and record conversion notes and limitations.
- Keep `build-backend` on `setuptools`/`wheel`. BrkRaw still has fragile file-fetch paths when hooks rely on hatch-based installers.
- Optional maintainer tooling: `.vscode/tasks.json` contains release task placeholders, `.github/workflows/` contains CI/publish placeholders, and `tests/` contains a minimal hook install test.

## Hook architecture and data flow
- BrkRaw loads datasets via `from brkraw import load` (see `brkraw/src/brkraw/__init__.py`). The loader exposes `get_scan(scan_id)`; hook code should operate on BrkRaw `Scan` objects.
- `get_dataobj(scan, **kwargs)` and `get_affine(scan, **kwargs)` are called during conversion and should return the CLI-compatible types (typically numpy arrays, or tuples of arrays).
- If conversion is multi-stage (trajectory reconstruction, RSS, caching, etc.), implement `convert(scan, metadata, **kwargs)` and expose it via `HOOK` so callers can opt into the richer workflow.
- Always accept `**kwargs`. `brkraw convert` (see `brkraw/src/brkraw/cli/commands/convert.py`) forwards `--hook-arg name:key=value` into `hook_args_by_name={...}` and ultimately into your hook functions (e.g., `--hook-arg template:offset=5`).
- Keep responsibilities separated: `rules/*.yaml` for detection/routing, `specs/*.yaml` for metadata mapping, `transforms/*.py` for sanitisation helpers. Document shared transforms in `src/brkraw_hook_template/docs/` (see `src/brkraw_hook_template/docs/rule_spec_transform.md`).

## Working with an AI agent
This section is for teams using an AI agent to help implement or extend a hook.

- In your prompt, point the agent to this repository (`git@github.com:BrkRaw/brkraw-hook.git`) and to at least one real hook example (e.g., `brkraw-mrs` or `brkraw-sordino`).
- Call out the non-negotiables: BrkRaw loads scans via `load()`, hook code should operate on `Scan`, and the hook must expose `HOOK = {'get_dataobj': ..., 'get_affine': ...}` (plus `convert` if needed).

  ```python
  from brkraw import load

  loader = load("/path/to/source")
  scan = loader.get_scan(scan_id)
  metadata = scan.get_metadata(reco_id=1)
  dataobj = scan.get_dataobj(reco_id=1)
  affine = scan.get_affine(reco_id=1)
  ```

- Tell the agent to wire options through `--hook-arg` (kwargs), not by inventing new CLI flags. Ask it to implement a real `convert()` (not a placeholder) when the workflow needs more than `get_dataobj`/`get_affine`.
- Example prompt: `"Use git@github.com:BrkRaw/brkraw-hook.git as the base hook. Mimic brkraw-mrs: implement HOOK={'get_dataobj': ..., 'get_affine': ..., 'convert': ...} in hook.py, operate on Scan objects from brkraw.load(...).get_scan(scan_id), and use hook args (from --hook-arg) to enable optional preprocessing. Provide rule/spec/transform files that match the detection logic, and include a complete convert() implementation."`

## Notes
- BrkRaw's file-fetch path is fragile in some scenarios, so keep data local to the hook package or repository instead of relying on fragile remote bootstrapping paths.
- Rules should be the first line of defense: keep them focused on scan identifiers, modality flags, or Bruker sequence/method markers, then route to the right spec/hook.
- `info_spec` drives the BrkRaw info parser (what appears in `brkraw info`), while `metadata_spec` feeds `get_metadata` and sidecar generation. Both should map raw headers to BrkRaw metadata keys and call into `transforms/` helpers for sanitisation (trim strings, convert units, inject constants).
- Document transforms that are shared between specs so future hooks can reuse them; check `src/brkraw_hook_template/docs/rule_spec_transform.md` for a general flow chart and template snippets.
- Tests should exercise the hook integration path (install the hook, ensure rules/specs/transforms register) rather than only unit-testing isolated helpers.
