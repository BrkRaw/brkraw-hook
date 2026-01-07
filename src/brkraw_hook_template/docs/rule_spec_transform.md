# Rule / Spec / Transform Guide

## Purpose of each layer

- **Rules** decide when a spec or hook applies. Keep the conditionals near the top
  of the detection chain, prefer `when` (source lookups) + `if` (logical tests).
- **Specs** map raw metadata to BrkRaw-friendly keys. Each spec should declare
  a `__meta__` block, list `sources`, and delegate sanitisation to transforms.
- **Transforms** live in `transforms/` and centralise normalization helpers
  (string trimming, unit conversion, list casting, constant injection).

## Best-practice checklist

1. Describe what the rule detects and which spec(s) it drives.
2. Keep spec field definitions short: one or two `sources` + a `transform` chain.
3. Reuse transforms across specs instead of repeating logic.
4. Document any expectations (required keys, units, triggers) in `docs/`.

## Example mapping flow

1. `rules/template_rule.yaml` matches scans that start with `TEMPLATE-`.
2. It binds to `specs/info_template.yaml` / `specs/metadata_template.yaml`.
3. Each spec field defers cleansed values to `transforms/template.py`, e.g.: 

```yaml
SequenceName:
  sources:
    - file: method
      key: Method
  transform: strip_enclosed
```

4. The `strip_enclosed` transform returns a trimmed string with angled brackets removed.
5. Once the metadata dict is ready, BrkRaw calls `brkraw_hook_template.hook`, which
   either reuses `first_value`, `ensure_list`, etc., or implements more complex
   dimension inference.

By keeping detection, sanitisation, and conversion distinct, the template
remains readable and easy to extend.
