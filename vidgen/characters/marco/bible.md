---
name: Marco
style: 1930s rubber-hose cartoon (Fleischer / early Disney tradition)
status: draft v1
---

# Marco — Chef Character Bible

## Concept

Marco es un cocinero alto y desgarbado en sus veintitantos, dibujado en el lenguaje rubber-hose de los años 30. Carismático, ligeramente torpe, siempre con una sonrisa amable. Estética monocroma con un único acento mostaza que ancla la marca visualmente sin romper la pureza del cel art.

**Naming alternatives** si Marco no encaja: *Beto*, *Tito*, *Lalo*, *Otto*. Mantener nombre corto, 2 sílabas, sonoridad italiana/latina suave.

## Model sheets

| Lámina | Archivo | Uso |
|---|---|---|
| Front pose (turnaround base) | `01_front_pose.png` | Animation base, T-pose de referencia |
| Side profile | `02_profile.png` | Caminata lateral, perfil hablando |
| Expressions sheet | `03_expressions.png` | Lip-sync / mood library |
| Cooking action pose | `04_cooking_pose.png` | Hero pose, key art de portada |

## Paleta (estricta)

| Token | Hex | Uso |
|---|---|---|
| `ink` | `#1A1A1A` | Contorno principal, hatching, sombras |
| `paper` | `#F5EFE0` | Fondo crema envejecido (NUNCA blanco puro) |
| `paper-grain` | `#E8DFC8` | Variación sutil del paper para textura |
| `mustard` | `#E5A82B` | Único acento de color — apron ribbon, neckerchief |
| `pure-white` | `#FFFFFF` | Solo dentro de la silueta (uniforme, guantes, toque) |

**Regla de oro:** el mustard nunca aparece en más de un elemento por toma. Si la cinta del delantal está visible, no pongas mustard en nada más.

## Proporciones (rubber-hose)

- Altura total: ~8 cabezas (lankier que el clásico 6-7 cabezas de Mickey/Felix)
- Cabeza: pequeña, redonda, ligeramente ovalada
- Torso: 2 cabezas, esbelto
- Brazos: 3 cabezas de largo, sin codo definido — curva continua tipo manguera
- Piernas: 4 cabezas, sin rodilla definida
- Manos: guantes de 4 dedos, ~1.2x el tamaño de la cabeza
- Pies: zapatos negros bulbosos, ~1.5x el tamaño de la cabeza

## Wardrobe (canon)

- Toque de chef blanco, alto, con base rígida
- Chaquetilla doble botonadura blanca (6 botones visibles de frente, 6 de perfil)
- Pantalón de cocinero blanco, ligeramente abolsado, vuelta arriba en el tobillo
- Delantal blanco hasta la rodilla
- **Cinta mostaza** anudada en el centro del delantal (firma del personaje)
- Guantes blancos cartoon de 4 dedos
- Zapatos negros bulbosos (estilo Mickey clásico)
- **Barba de tres días:** stippling de puntos negros pequeños distribuidos por mentón y mandíbula. NO líneas, NO sombra sólida — solo puntos.

## Cara

- Ojos: almendrados, blancos del ojo visibles, pupilas pin-dot negras sólidas
- **Gafas**: redondas wire-frame finas. Dos círculos negros perfectos conectados por un puente recto sobre la nariz, varillas finas hacia las orejas. Las pupilas pin-dot se ven a través de los lentes.
- Cejas: dos arcos negros simples por encima de las gafas
- Nariz: bolita redonda, sombreada con hatching
- Boca: línea simple, expresiva, capaz de estirarse en squash-and-stretch
- Pelo: capucha negra sólida visible bajo el toque, raya al lado izquierdo

## Animation notes

- **Línea madre:** Fleischer Studios, Max Fleischer "Out of the Inkwell" (1918-1929), early Disney "Plane Crazy" (1928)
- **Movement language:** rubber-hose pure — brazos y piernas se curvan como mangueras de jardín, no como huesos articulados
- **Walk cycle:** 12 frames, pasos exagerados, brazos contrarios oscilando en arco amplio
- **Cooking actions:** squash al agacharse sobre la olla, stretch al levantar la cuchara, anticipation antes de cada movimiento grande
- **Frame rate sugerido:** 12fps animation on 2s (24fps display) — auténtico al periodo
- **Steam puffs / FX:** curlicue clásico de 3 vueltas, salen de la olla, expanden y desaparecen en 8 frames

## Voice (cuando se anime con TTS)

- Tono: barítono cálido, ligeramente nasal, energético
- Estilo: locutor de radio años 30, sin ser caricatura. Pausa para puntuar.
- Idioma sugerido: español neutro con cadencia ligeramente italiana
- Piper voice candidate: `es_ES-sharvard-medium` o equivalente con pitch +1 semitono

## Banned (NO hacer)

- NO añadir más colores aparte del mustard
- NO sombrear con gradientes — solo hatching paralelo
- NO articulaciones realistas en codos/rodillas
- NO fondo blanco puro — siempre crema con grano
- NO copiar rasgos identificables de personajes con copyright (Bimbo, Bosko, Felix, Mickey, Oswald, Koko). Si surge un parecido accidental, regenerar.

## Próximos pasos

1. **Validar visual** con el usuario — ¿el personaje es lo que esperabas?
2. **Si se aprueba:** definir 8-12 viñetas para el video de flan (script-director)
3. **Generación de poses adicionales** por receta (cortar, batir, mezclar, sacar del horno, probar, sonreír al cliente)
4. **Composición Remotion** estilo "libro ilustrado animado": cross-fades + ken burns sutil entre poses + narración Piper + jazz de Pixabay
