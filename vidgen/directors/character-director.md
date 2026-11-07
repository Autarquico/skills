# Character Director

Trigger: el usuario invoca `/vidgen createchar <slug>` o `/vidgen animate <slug> "<prompt>"`, o pide "crear un personaje reusable" / "animar a <slug>".

Este director gobierna **dos flujos** sobre el inventario local de personajes en
`~/.claude/skills/vidgen/characters/<slug>/`. La idea: separar el personaje (creado una vez)
del clip (generado a demanda con Veo image-to-video).

---

## Inventario — estructura canónica por personaje

```
~/.claude/skills/vidgen/characters/<slug>/
├── bible.md            # canon textual: paleta, proporciones, wardrobe, banned
├── manifest.yml        # voice, default_ratio, accent_color, pose paths
├── poses/              # PNGs anchor pasadas a Veo como first frame
│   ├── neutral_front.png
│   ├── neutral_3q.png        # 3/4 turn — anchor preferido para acción
│   └── (opcional) expressions.png
└── references/         # imágenes que el usuario aportó como estilo (opcional)
```

El `manifest.yml` mínimo:

```yaml
slug: marco
name: Marco
voice:
  engine: piper
  model: es_ES-sharvard-medium
  pitch_semitones: 1
default_ratio: 9:16
accent_color: "#E5A82B"
paper_color: "#F5EFE0"
ink_color: "#1A1A1A"
anchor_default: poses/neutral_3q.png
```

---

## FLUJO 1 — `/vidgen createchar <slug>`

Input del usuario: descripción del personaje + (opcional) imágenes de referencia + (opcional) style hint.

1. **Confirmar slug y disponibilidad**: si `characters/<slug>/` ya existe, preguntar antes de sobrescribir.

2. **Escribir `bible.md`** directamente con Edit/Write. Estructura mínima:
   - `# <Nombre>` + concepto en 2-3 frases
   - `## Paleta` (tabla hex con tokens: ink, paper, accent)
   - `## Proporciones` (cabezas, brazos, piernas)
   - `## Wardrobe`
   - `## Cara`
   - `## Banned` (qué NO debe aparecer — copyright, estilos prohibidos)
   - `## Voice` (TTS sugerido si aplica)

3. **Escribir `manifest.yml`** con los tokens extraídos del bible.

4. **Generar pose anchors** con `/imgen` (`generate.py`). Generalmente 2 poses base:
   - `neutral_front.png` — pose frontal hero, full body, ratio 3:4
   - `neutral_3q.png` — 3/4 turn relajada, full body, ratio 3:4

   Cada call de `/imgen` debe incluir un bloque ANCHOR DESCRIPTION canon-locked
   (la misma descripción larga, copiada literal) y citar los hex de la paleta.
   Ejemplo de command:

   ```bash
   python3 /Users/alex/.claude/skills/imgen/scripts/generate.py \
     --prompt "$(cat <prompt-file>)" \
     --aspect-ratio 3:4 \
     --output ~/.claude/skills/vidgen/characters/<slug>/poses/neutral_front.png
   ```

5. **Reportar al usuario**: path del package + sugerencia de revisar el bible antes de animar.

**No generar lipsync sheets, no rigging, no SVG.** Veo no los necesita.

---

## FLUJO 2 — `/vidgen animate <slug> "<motion prompt>" [opciones]`

Opciones reconocidas (parseables del prompt o explícitas):
- `--duration 4|6|8` (default 4 para iterar barato, 8 para entrega final)
- `--ratio 9:16|16:9` (default: el `default_ratio` del manifest)
- `--pose <name>` (default: `anchor_default` del manifest)
- `--model fast|standard` (default fast; standard solo si el usuario pide calidad)
- `--output <path>` (default: `out/<slug>-<timestamp>.mp4`)

1. **Cargar contexto**: leer `bible.md` y `manifest.yml` de `characters/<slug>/`.
   Si no existe, ofrecer correr `createchar` primero.

2. **Seleccionar pose anchor**:
   - Si `--pose` explícito: usar ese.
   - Heurística por defecto: acciones manuales (cocinar, escribir, saludar) → `neutral_3q`;
     intros, planos estáticos → `neutral_front`.

3. **Componer prompt Veo** (motion-only + style guard). Patrón:

   > `<motion prompt del usuario>`. Static camera, locked-off shot.
   > Preserve original style: `<paper_color>` paper background, `<ink_color>` ink outlines,
   > single `<accent_color>` accent only. Hand-drawn cel animation feel,
   > 1930s Fleischer rubber-hose tradition (si aplica al personaje). No camera movement.

   **Reglas:**
   - El prompt describe **el gesto**, no la escena (el anchor ya tiene la escena).
   - Reafirma siempre la paleta del manifest, en hex.
   - Cualquier `banned` del bible que sea visual ("no realistic joints", "no gradient shading")
     se reexpresa positivo: "joints stay as continuous curves", "flat fills only".

4. **Llamar Veo** vía `veo_generate.py` del veo skill:

   ```bash
   python3 ~/src/claude-code-video-toolkit/tools/veo_generate.py \
     --image <pose-anchor-path> \
     --prompt "<composed prompt>" \
     --aspect-ratio <ratio> \
     --resolution 720p \
     --duration <duration> \
     --model veo-3.1-fast-generate-preview \
     --output <output-path>
   ```

   - `720p + duration 4|6|8` con fast model = ~$0.05-0.15. Iteración por defecto.
   - `1080p` requiere `duration 8`. Solo si el usuario pide "entrega final" o similar.

5. **Reportar**: path del MP4 + duración + coste estimado. Si el usuario quiere más
   clips para componer un video largo, encadenar varias llamadas y concatenar con
   Remotion (ver `render-director.md`).

---

## Clips largos (>8s)

Veo está limitado a 4/6/8s. Para historias más largas:

1. Descomponer el prompt en N beats de ≤8s cada uno.
2. Generar el primer clip desde `anchor_default`.
3. Para los clips 2..N: extraer el último frame del clip anterior con ffmpeg y pasarlo
   como `--image` (mejora continuidad), o regenerar desde el mismo anchor si la
   acción cambia drásticamente.
4. Concatenar con Remotion o `ffmpeg -f concat`.

Patrón ya validado: ver `MarcoFlan.tsx` en OpenMontage (storybook) — el mismo formato
sirve si sustituyes los PNGs estáticos por MP4s de Veo.

---

## Coste y guardrails

- Cada call de Veo cuesta. **Confirma con el usuario antes de la primera call de pago**
  en una sesión. Después, asume autorización implícita salvo que el usuario suba el modelo
  a `standard` (más caro).
- Para iterar prompt antes de gastar: usa `/imgen` (Nano Banana, ~$0.04) para visualizar
  el end-state como still y validar dirección artística.
- Logueá cada generación con `cost_tracker.py` del imgen/veo skill si está disponible.

---

## Banderas de calidad

Cuando el clip de Veo vuelve, mira:
- ¿La identidad del personaje se preserva? (proporciones, paleta, accent intacto)
- ¿El acento color sigue siendo único? (no proliferó a otras zonas)
- ¿La pose final es coherente con el gesto pedido?
- ¿Hay morphing/AI artifacts visibles?

Si falla cualquiera: reformular el prompt enfatizando lo que se rompió, o cambiar el pose
anchor a uno más cercano a la acción.
