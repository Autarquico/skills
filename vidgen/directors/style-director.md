# Style Director

Esta es una **sub-skill** del setup. Ayuda específicamente a crear, editar o navegar la galería de `visual-style.md`.

## Cuándo entrar

- El usuario quiere ver styles disponibles ("¿qué estilos tengo?")
- Editar un style existente ("cambia el color primario de autarqui-co a verde")
- Crear variante ("crea un autarqui-co-dark")
- Importar de otra fuente (URL, PDF, imagen de referencia)

## Operaciones

### List
```bash
ls ~/.claude/skills/autarqui-video-gen/styles/*.visual-style.md
```
Para cada uno, muestra `name`, `style_prompt_short`, y los colores primarios.

### View
Read del archivo, presenta los design tokens en tabla, y nota explicitly el `forbidden` y `verbatim_lines`.

### Edit
Edit puntual sobre el frontmatter YAML. Avisa al usuario que cambios en `colors`/`typography` afectan a TODOS los videos que usan ese style.

### Create

Hay dos paths:

**Desde fuente** (URL/PDF/imagen): delega a `setup-director.md` paso 2 y 3.

**Desde cero** (asistente conversacional): preguntas en orden:
1. Nombre y slug
2. Aesthetic shortcut: `editorial-mono | swiss | brutalist | lo-fi | cyberpunk | 3d-cinematic | flat-corporate | custom`
3. Si shortcut elegido: cargar template base; si custom: preguntar uno-a-uno.
4. Colores primarios (hex)
5. Acentos si los hay (hex)
6. Display font (Google Fonts name)
7. Body font
8. Pacing (`slow | medium | fast`)
9. Forbidden list (preguntar 3-5 cosas a evitar)
10. Verbatim lines: master, tagline (opcional)
11. ios_chrome: ¿se va a usar para UI mocks móviles?

Output al `styles/<slug>.visual-style.md` con la estructura completa de `setup-director.md`.

## Validación

Antes de guardar, verifica:
- Hex codes válidos (`/^#[0-9a-fA-F]{6}$/`)
- Fonts existen en Google Fonts (puedes verificar con un fetch a `https://fonts.googleapis.com/css2?family=<Name>` y ver si responde 200)
- Frontmatter parsea (YAML válido)

Si algo falla, edita y reintenta antes de presentar al usuario.

## Galería seed

Estos styles los crea el `scripts/install.sh` por defecto:
- `autarqui-co.visual-style.md` (canónico, copiado de OpenMontage/brand/)
- `mueller-brockmann-swiss.visual-style.md`
- `saul-bass-cinematic.visual-style.md`
- `lo-fi-handdrawn.visual-style.md`
- `brutalist.visual-style.md`
- `flat-corporate.visual-style.md`

Si alguno falta y el usuario lo pide, créalo con valores razonables del genre.
