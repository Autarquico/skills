# Asset Director

Esta sub-skill decide **qué tool invocar** para conseguir música, imágenes, video, voz o sound effects que necesita un script.

## Cuándo entrar

- El script-director marcó assets como "TBD"
- El render-director encuentra `music: null` o referencia a un asset que no existe
- El usuario pregunta directamente "necesito música para X"

## Order of preference (no invertir)

Para cualquier asset, busca en este orden:

### 1. User's library
Antes que nada, mira:
- `~/music_library/*.mp3` — música del usuario (gratis, sin metadata externa)
- `~/.claude/skills/autarqui-video-gen/cache/pixabay/` — assets ya descargados antes
- `~/.claude/skills/autarqui-video-gen/cache/pexels/`, `cache/unsplash/` — igual

Si encuentras candidatos, propón al usuario los nombres + un breve preview de duración/dimensiones.

### 2. Pixabay (cobertura amplia: música + imagen + video)
**API programmatic** (`tools/assets/pixabay/search.py`) cuando:
- Tienes claro qué buscar
- El usuario quiere arrancar rápido
- Es para asset funcional (no creativo crítico)

**Link curado** (`tools/assets/pixabay/link.py`) cuando:
- El usuario tiene buen ojo y quiere browsear
- El género es subjetivo (música emocional, imagen "que se sienta autarqui")
- Buscaste programmatic y no convence

### 3. Pexels (mejor que Pixabay para foto editorial)
Cuando el style requiere foto editorial limpia (lifestyle, hands-at-work, urbana minimalista). `tools/assets/pexels/search.py`.

### 4. Unsplash (lifestyle premium)
Cuando se necesita foto people/lifestyle de calidad alta. Usa el `link.py` también — Unsplash es más visual.

### 5. Freesound (sound effects, no música)
Para SFX puntuales: clicks UI, whoosh suaves, ambient room tone. CC license, ojo a la attribution requirement de algunos.

### 6. LottieFiles
Cuando el script especifica `lottie-play` scene. Buscar por keyword + descargar JSON.

## Voz (narración)

| Use case | Tool |
|---|---|
| Narración rápida, calidad aceptable | Piper (`tools/audio/piper-tts.sh`) |
| Calidad alta, voz expresiva | Coqui XTTS-v2 (`tools/audio/coqui-xtts.py`) |
| Voice cloning de un sample | Coqui XTTS-v2 con `--reference-voice` |
| Sin voz (typography only) | Skip — el style probablemente prefiere `prefer_voice: none` |

Defaults vienen del `audio.prefer_voice` del visual-style.md activo.

## Subtítulos

Siempre que haya voz (o video con audio hablado), genera subtítulos:

```bash
~/.claude/skills/autarqui-video-gen/tools/transcription/whisper-cpp.sh <audio> <output.ass>
```

Output ASS subtitle con timing word-level. El renderer los puede burnir vía Remotion `<Subtitles>` component o ffmpeg en post.

## Source media (footage real)

Si el guion necesita clips de YouTube/Vimeo de **contenido que el usuario tiene derecho a usar** (su propio canal, contenido CC, etc.):

```bash
~/.claude/skills/autarqui-video-gen/tools/source/yt-dlp-grab.sh <url> <output-dir>
```

**No descargues contenido protegido sin autorización.** Si dudas, pregunta al usuario.

## Animaciones complejas

| Necesidad | Tool |
|---|---|
| Animación matemática/educativa (3blue1brown style) | Manim (`tools/motion/manim-runner.sh`) |
| Lottie pre-hecho | LottieFiles search + `LottiePlay` scene |
| Kinetic typography | `KineticType` scene (GSAP) — no hace falta tool externo |
| 3D scene | `ThreeScene` scene (Three.js) — no hace falta tool externo |
| **Video clip generado por IA local** (b-roll, atmósfera) | LTX-Video local (`tools/video-gen/local-ltx.py`) + `LocalVideoClip` scene |

## Local AI video generation (LTX-Video)

Cuando un script declara un scene `local-video-clip` con un `prompt`, generas el clip antes de renderizar:

```bash
avg local-video generate \
  --prompt "[Cinematography] [Subject] [Action] [Context] [Style & Ambiance]" \
  --duration 5 --aspect 16:9 --resolution medium \
  --to compositions/public/<project>/<clip-name>.mp4
```

**Hardware**: Apple Silicon (MPS) o NVIDIA (CUDA) requerido. ~12-14 GB VRAM peak. CPU fallback es inviable.

**Tiempo**:
- Primera generación de la sesión: ~10 min (download modelo + carga)
- Subsiguientes: 3-5 min cada una @ 30-40 steps, resolución `small`/`medium`
- Cache por hash de prompt+config — mismo prompt no se regenera

**Calidad**: muy buena para b-roll editorial, atmósfera, objetos, texturas, paisajes. Mediocre para personas, lip-sync, escenas complejas con movimiento articulado.

**Prompt formula** (cinematic, alineada a Veo/LTX):
> [Cinematography (shot type, camera movement)] + [Subject] + [Action] + [Context (location, time, lighting)] + [Style & Ambiance (film stock, depth of field, mood)]

Ejemplo:
> *"Slow dolly forward, a leather notebook with handwritten numbers on a desk, pen rolling slowly across the page, late afternoon natural light through tall windows, shot on 35mm film, shallow depth of field, editorial photography, calm atmosphere"*

**Workflow declarativo desde script.json**:

```json
{
  "type": "local-video-clip",
  "t_in_s": 3,
  "t_out_s": 8,
  "props": {
    "video_src": "<project>/clip-leather.mp4",
    "prompt": "Slow dolly forward, leather notebook…",
    "overlay_eyebrow": "HECHO A MANO",
    "overlay_text": "Tirada limitada.",
    "overlay_position": "bottom-left",
    "overlay_dim": 0.35
  }
}
```

Antes de `avg render <project>`: si el `video_src` no existe, ejecuta `avg local-video generate --prompt "..." --to <video_src>` para generarlo. Después renderiza la composición.

## Audio post

| Necesidad | Tool |
|---|---|
| Mix voice + music con ducking | `tools/audio/ffmpeg-mix.py --preset voice-over-music` |
| Separar stems de canción (vocals/drums/...) | `tools/audio/demucs-stems.sh` |
| Curva de volumen editorial (fade slow) | `tools/audio/ffmpeg-mix.py --preset editorial` |
| Hard cut + silencio antes de logo | `tools/audio/ffmpeg-mix.py --preset hard-cut-trail` |

## Reglas de oro

1. **Cache antes que API.** Cada descarga se cachea en `cache/<source>/`. Próxima vez es local.
2. **Anuncia ANTES de gastar request.** "Voy a buscar en Pixabay 'calm piano cinematic 60-90s' — confirma." (esto siempre, no solo en APIs de pago — Pixabay tiene rate limits que merece la pena no quemar).
3. **Metadata sidecar.** Cada asset descargado se guarda con un `.json` adyacente con: `{source, query, author, url, license, downloaded_at}`. Para tu registro y para honor attribution si aplica.
4. **No descargas masivas especulativas.** Si el script tiene 5 imágenes, busca 5 — no 50 "por si acaso".
5. **Respeta licencias.** Pixabay/Pexels/Unsplash/LottieFiles son uso comercial libre sin attribution requerida (pero la metadata sidecar la guarda igualmente). Freesound es CC, mira la license de cada sound.
