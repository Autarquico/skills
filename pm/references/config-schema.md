# Schema: `.pm/config.yaml`

Fuente de verdad sobre **qué proyecto soy**.

## Estructura

```yaml
codename: <string>              # required, lowercase, no spaces
display_name: <string>          # optional, default = codename capitalizado

github:
  repo: <owner>/<repo_name>     # required
  project:
    owner: <string>             # required
    owner_type: org | user      # required
    number: <integer>           # required
  field_ids:                    # required, los 4
    status: <integer>
    priority: <integer>
    size: <integer>
    ticket_type: <integer>

paths:
  specs: <string>                # required, e.g. "docs/specs/"
  specs_archive: <string>        # required, e.g. "docs/specs/archive/"
  tracking:
    status: <string>             # required, e.g. "docs/STATUS.md"
    todo: <string>               # optional
    roadmap: <string>            # optional

agent:
  language: es | en              # required
  conventions: <string>          # required, e.g. "AGENT.md"

mcp:
  server: <string>               # required, e.g. "github-autarquico"

sync:
  archive_on_ship: <bool>        # optional, default false
  default_since_days: <integer>  # optional, default 7
  status_markers:                # optional, defaults below
    done_this_week: "pm-sync:done-this-week"
    in_progress: "pm-sync:in-progress"
    blocked: "pm-sync:blocked"
```

## Validación

1. YAML parseable
2. Required fields presentes
3. Types correctos (integers, enums)
4. Paths existen en el repo
5. `codename` lowercase sin espacios

## Decisiones

- **option_ids NO en config**: se resuelven en runtime (evita drift si alguien edita opciones desde UI)
- **owner_type explícito**: GitHub API trata org y user projects con endpoints distintos
- **paths configurables**: flexibilidad sin código condicional
