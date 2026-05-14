# Render Director

Toma `visual-style.md` + `script.json` + assets → renderiza MP4 vía Remotion.

## Cuándo entrar

- "Renderiza"
- "Compón el video"
- El script-director acaba de generar un `script.json` validado
- El usuario itera sobre un render existente ("cambia X y rerenderiza")

## Pre-flight

Antes de tocar Remotion:

```bash
~/.claude/skills/autarqui-video-gen/scripts/doctor.sh
```

Verifica que estén listos: ffmpeg, node, remotion, el visual-style.md que pide el script, y la música referenciada.

Si algo falla, escala como blocker. No "fallback silencioso a otro style".

## Pasos

### 1. Setup del proyecto en compositions/

```bash
PROJECT_DIR=~/.claude/skills/autarqui-video-gen/compositions/src/projects/<project_id>
mkdir -p $PROJECT_DIR
cp <script.json> $PROJECT_DIR/script.json
```

Si hay assets locales (música, imágenes propias), cópialos a `$PROJECT_DIR/assets/` y a `~/.claude/skills/autarqui-video-gen/compositions/public/<project_id>/` (Remotion necesita que estén en `public/` para `staticFile()`).

### 2. Selección de scenes vs. custom

Para cada scene del `script.json`:
- Si `type` está en `scenes/index.ts` → usa la scene de la librería con sus props
- Si `type === "_custom"`:
  - Lee `component_path` del scene
  - Si existe el archivo, importarlo
  - Si NO existe, **escríbelo** (pareja: usar como referencia los componentes de OpenMontage que validamos esta sesión, pero **tokenizar** todos los valores leyendo del visual-style.md activo)
  - El componente custom debe importar de `lib/tokens.ts` para colores, fonts, layout

### 3. Generación del Composition

Crear `$PROJECT_DIR/Composition.tsx` que:
1. Carga el style con `loadStyle("<slug>")` de `lib/tokens.ts`
2. Itera sobre `script.scenes`, renderiza cada uno con su scene component, dentro de `<Sequence from={t_in*fps} durationInFrames={(t_out-t_in)*fps}>`
3. Renderiza el `<Audio>` con la mix curve calculada del `audio_mix`

### 4. Cálculo del trimBefore para música (alineación al final)

Si `audio_mix.music.trim_to_end === true`:
```python
audio_duration_s = ffprobe(music_path)
play_duration_s = end_at_s - fade_in_at_s
trim_before_s = audio_duration_s - play_duration_s
trim_before_frames = round(trim_before_s * fps)
```

Esto replica la lógica que validamos esta sesión (final natural de la música = momento del cierre, logo en silencio).

### 5. Registry update

Añade el composition al `compositions/src/Root.tsx` (el archivo tiene auto-discovery de `projects/*/Composition.tsx`, debería detectarlo solo).

### 6. Render

```bash
cd ~/.claude/skills/autarqui-video-gen/compositions
npx remotion render src/Root.tsx <project_id> ./out/<project_id>.mp4
```

O usa el wrapper:

```bash
~/.claude/skills/autarqui-video-gen/tools/render/remotion-render.sh <project_id>
```

Output va a `<output_folder>/<project_id>/final.mp4` (output_folder viene del config).

### 7. Verificación

- `ffprobe` del output: confirma `duration`, `width × height`, `fps`, presence de stream de audio
- Verifica que `duration` esté ±0.1s del `script.duration_s`
- Si hay subtítulos, confirma que se quemaron correctamente

### 8. Open + presentar

```bash
open <output_path>
```

Imprime resumen al usuario:
- Path
- Specs
- Cómo iterar (qué cambiar en script.json)

## Iteración rápida

Si el usuario pide un cambio menor ("cambia DELTA por DELTA en mayúsculas"):
1. Edit del scene prop o del componente custom (NO del archivo de la librería — eso afectaría otros videos)
2. Re-run `npx remotion render` (incremental, ~10-30s normalmente)

## Cuando escribir scene custom

**Solo cuando ninguna scene de la librería encaja.** Antes de empezar a escribir, comprueba:
- ¿Hay una scene similar que con props distintos hace el trabajo?
- ¿Se puede componer combinando 2 scenes con `Sequence`?

Si genuinamente es nuevo:
1. Escribe en `projects/<id>/<NameOfScene>.tsx`
2. **OBLIGATORIO**: importa tokens, NO hardcodees colores/fonts/sizes
3. Documenta en un comentario top: por qué no encaja en la librería
4. Si lo vas a usar 2+ veces, **promuévelo** a la librería (`compositions/src/scenes/<NameOfScene>.tsx`) y registra en `index.ts`

## Reglas de oro

1. **Tokens, siempre.** Cero hardcoded colors/fonts/sizes en componentes.
2. **No silent fallbacks.** Si una scene type no existe en la librería, error explícito — no "uso text-card en su lugar".
3. **Cache de fuentes.** Si el style pide una Google Font nueva, descárgala una vez a `cache/fonts/` y reúsala.
4. **Render.preview antes de full render.** Para iteración rápida usa `--frames 1-30` o `--still` para ver una frame antes de comprometer 60s de render.
