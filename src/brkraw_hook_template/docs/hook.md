# Hook Template Overview

This package ships a starter hook that mirrors the brkraw-mrs layout.
The key assets that BrkRaw looks for are declared in `brkraw_hook.yaml`:

```yaml
docs: docs/hook.md
specs:
  - specs/info_template.yaml
  - specs/metadata_template.yaml
rules:
  - rules/template_rule.yaml
transforms:
  - transforms/template.py
```

When the hook is installed via `brkraw hook install template`, the CLI loads
those files, evaluates the rules to pick specs/transforms, and finally calls
`brkraw_hook_template.hook:HOOK` to convert any supported scan.

## Hook usage example

```bash
pip install .
brkraw hook install template
brkraw convert /path/to/source --output /path/to/output
```

Replace the stub conversion in `src/brkraw_hook_template/hook.py` with logic
that reads `scan` attributes, builds the output array, and returns
`(dataobj, order, metadata)`.

## Rule / spec / transform example

The bundled rule file focuses on a placeholder metadata key. The rule maps
validation to the info + metadata specs before invoking the hook itself:

```yaml
converter_hook:
  - name: "template"
    when:
      scan_id:
        sources:
          - key: ScanIdentifier
    if:
      regex: ["$scan_id", "^TEMPLATE"]
    use: "template"
```

Keep your `rules/*.yaml` focused on detection logic. Keep `specs/*.yaml` as
source-to-target mappings, and keep all text/number sanitisation inside
`transforms/*.py`.
