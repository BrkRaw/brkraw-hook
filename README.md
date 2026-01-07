# BrkRaw Hook Template

## Instruction
- Copy this template into a new repository, then update `pyproject.toml` metadata (name, entry point, dependencies) before publishing to PyPI.
- Define the dataset-specific hook inside `src/brkraw_hook_template/hook.py`, returning `(dataobj, order, metadata)` once the rule/spec layer has validated the scan.
- Declare the hook assets in `src/brkraw_hook_template/brkraw_hook.yaml`, point to user-oriented docs in `docs/`, rules in `rules/`, specs in `specs/`, and transforms in `transforms/`.
- Use the docs in `src/brkraw_hook_template/docs/` as an example for explaining the hook's scope, the rule/spec/transform flow, and any conversion notes.
- Avoid switching to hatchling (or other hatch-based backends) in `build-backend` because BrkRaw still has buggy file-fetching paths when hooks rely on hatch installers; stick with `setuptools`/`wheel` as configured here.
- Developer support extras: `.vscode/tasks.json` includes release-oriented task placeholders, `.github/workflows/` includes CI/publish placeholders, and `tests/` includes a minimal hook install test so maintainers can validate hook integration in CI.

## Hook workflow
- Load a dataset via `from brkraw import load` (see `brkraw/src/brkraw/__init__.py`). The loader exposes `get_scan(scan_id)` so you always work with BrkRaw `Scan` objects when populating metadata or producing outputs.
- Implement `get_dataobj(scan, **kwargs)` and `get_affine(scan, **kwargs)` inside your hook module. BrkRaw calls those helpers directly during conversion, so they should return the same data types the CLI expects (e.g., numpy arrays or tuples of arrays). When a conversion demands multi-stage processing (trajectory reconstruction, RSS combination, caching, etc.), wrap that logic in `convert(scan, metadata, **kwargs)` and keep it available for callers that need the extra workflow.
- Accept `**kwargs` throughout your helpers. `brkraw convert` (see `brkraw/src/brkraw/cli/commands/convert.py`) forwards CLI `--hook-arg name:key=value` into `loader.convert(..., hook_args_by_name={...})`, which eventually supplies the same dictionary to `scan.convert(...)` and to your hook functions. That lets you expose options like `--hook-arg template:offset=5` without hardcoding CLI bindings.
- Keep `rules/*.yaml` focused on detection logic, `specs/*.yaml` on metadata mapping, and `transforms/*.py` on sanitisation helpers. Document reusable transforms inside `docs/` (see `docs/rule_spec_transform.md`) and reference them in your AI prompts so collaborators understand the flow.

## AI friendly prompt (with BrkRaw API)
- When you iterate with an AI agent, point it to this repository (`git@github.com:BrkRaw/brkraw-hook.git`) and mention that BrkRaw loads scans via `load()` before invoking hooks. The core requirement is to expose a `HOOK` dict with `get_dataobj` and `get_affine` (plus `convert` if you need a custom workflow), just like `brkraw-mrs` or `brkraw-sordino`.

  ```python
  from brkraw import load

  loader = load("/path/to/source")
  scan = loader.get_scan(scan_id)
  metadata = scan.get_metadata(reco_id=1)
  dataobj = scan.get_dataobj(reco_id=1)
  affine = scan.get_affine(reco_id=1)
  ```

- This clarifies that AI-generated code should operate on `Scan` objects, implement `get_dataobj`/`get_affine`, and optionally expose a richer `convert` workflow that consumes kwargs from `hook_args_by_name`. Mention the repo URL so the model can inspect the template structure and docs, and prompt it to add dataset-specific options tied to CLI `--hook-arg` keys.
- Example prompt for AI: `"Use git@github.com:BrkRaw/brkraw-hook.git as the base hook. Mimic brkraw-mrs: build HOOK={'get_dataobj': ..., 'get_affine': ..., 'convert': ...} in hook.py, parse a Scan from brkraw.load(...).get_scan(scan_id), and use hook args (from --hook-arg) to enable optional preprocessing. Provide rule/spec/transform files that match the detection logic, and include the actual convert() implementation code (not just a placeholder) that performs the intended conversion."`

## Note
- BrkRaw's file-fetch path is fragile in some scenarios, so keep data local to the hook package or repository instead of relying on fragile remote bootstrapping paths.
- Rules should be the first line of defense: keep them focused on scan identifiers, modality flags, or Bruker sequence/method markers and then route to the right spec/hook.
- `info_spec` drives the BrkRaw info parser (what appears in `brkraw info`), while `metadata_spec` feeds `get_metadata` and sidecar generation. Both should map raw headers to BrkRaw metadata keys and call into `transforms/` helpers for sanitisation (trim strings, convert units, inject constants).
- Document transforms that are shared between specs so future hooks can reuse them; check `docs/rule_spec_transform.md` for a general flow chart and template snippets.
- Tests should exercise the hook integration path (install the hook, ensure rules/specs/transforms register) rather than only unit-testing isolated helpers.
