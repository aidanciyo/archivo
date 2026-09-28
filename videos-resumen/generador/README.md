# Generador de los vídeos resumen

Todo el vídeo se genera por código, sin plantillas de pago ni material con derechos:

| Paso | Archivo | Qué hace |
|---|---|---|
| Guion | `content.py` | Texto narrado de cada escena y datos de los gráficos. Las marcas `{0}`, `{L}`, `{c1}`… indican el instante en que aparece cada elemento visual. |
| Voz | `narration.py` | Sintetiza cada frase con **Supertonic 3** (voz masculina, español), genera 4 tomas, las comprueba con **Whisper** y conserva la mejor. Monta la pista de voz y `timeline.json`. |
| Música | `music.py` | Compone y sintetiza desde cero una pista *uplifting* (pads, arpegio, bajo, batería, risers) ajustada a la duración exacta; el acorde final cae en el cierre. |
| Mezcla | `mix.py` | EQ y compresión de voz, *ducking* de la música bajo la voz, efectos de transición, normalización a −16 LUFS y subtítulos `.srt`. |
| Gráficos | `engine/engine.js`, `engine/engine.css` | Plantillas animadas (GSAP) con estilo común; `renderFrame(t)` deja la página en el instante exacto `t`. |
| Render | `render.js`, `produce.py`, `finalize.py` | Captura fotograma a fotograma con Chromium (Playwright) a 1920×1080, 30 fps, y codifica H.264 + AAC + subtítulos. |

## Requisitos

- Python 3.11: `pip install numpy scipy numba soundfile librosa pyloudnorm sherpa-onnx`
- Node 22 con Playwright (Chromium) y `npm install` en esta carpeta (GSAP, fuentes Montserrat/Inter, iconos Lucide)
- ffmpeg
- Modelos (en la carpeta indicada por `TTS_MODELS`, por defecto `../voices/`), de las *releases* de [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx/releases):
  - `tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2`
  - `asr-models/sherpa-onnx-whisper-small.tar.bz2`

## Control de calidad

- `qa.sh` crea una hoja de contactos del MP4 y muestra sus pistas.
- `asr_check.py UTx` transcribe el audio final (voz + música) con Whisper y calcula el porcentaje de palabras reconocidas.

## Uso

```bash
npm install
python3 narration.py UT1,UT2,UT3,UT4,UT5 1.05   # voz (velocidad 1.05)
python3 produce.py UT1,UT2,UT3,UT4,UT5          # mezcla + render + MP4 en out/<UT>/
python3 export_guiones.py ../guiones             # guiones en Markdown
python3 finalize.py                              # subtítulos .srt, MP4 finales y README en la carpeta superior
```

Para revisar fotogramas concretos sin renderizar todo: `node preview.js engine/UT1.html out/prev 12.5 40`.

## Licencias de terceros

- Modelo de voz Supertonic 3 (Supertone Inc.): licencia OpenRAIL-M. Whisper (OpenAI): MIT.
- Fuentes Montserrat e Inter: SIL Open Font License. Iconos Lucide: ISC. GSAP: licencia estándar gratuita de GSAP.
- La música se sintetiza en `music.py`: es original y no usa samples.
