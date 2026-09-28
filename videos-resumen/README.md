# Vídeos resumen · Digitalización aplicada a los sectores productivos

Cinco vídeos de unos **2 minutos** que resumen los apuntes de cada unidad, con el mismo estilo gráfico, voz de narrador en español, música motivadora y subtítulos.

| Unidad | Vídeo | Duración | Guion | Subtítulos |
|---|---|---|---|---|
| **UT1** · Digitalización de los sectores productivos | [UT1_Digitalizacion_de_los_sectores_productivos.mp4](UT1_Digitalizacion_de_los_sectores_productivos.mp4) (27 MB) | 1:59 | [guion](guiones/UT1.md) | [.srt](UT1_Digitalizacion_de_los_sectores_productivos.srt) |
| **UT2** · Tecnologías digitales habilitadoras | [UT2_Tecnologias_digitales_habilitadoras.mp4](UT2_Tecnologias_digitales_habilitadoras.mp4) (26 MB) | 2:00 | [guion](guiones/UT2.md) | [.srt](UT2_Tecnologias_digitales_habilitadoras.srt) |
| **UT3** · Sistemas en la nube | [UT3_Sistemas_en_la_nube.mp4](UT3_Sistemas_en_la_nube.mp4) (27 MB) | 2:00 | [guion](guiones/UT3.md) | [.srt](UT3_Sistemas_en_la_nube.srt) |
| **UT4** · Aplicación de la inteligencia artificial | [UT4_Aplicacion_de_la_inteligencia_artificial.mp4](UT4_Aplicacion_de_la_inteligencia_artificial.mp4) (27 MB) | 2:00 | [guion](guiones/UT4.md) | [.srt](UT4_Aplicacion_de_la_inteligencia_artificial.srt) |
| **UT5** · Big data | [UT5_Big_data.mp4](UT5_Big_data.mp4) (28 MB) | 2:01 | [guion](guiones/UT5.md) | [.srt](UT5_Big_data.srt) |

## Características

- **Formato:** MP4 (H.264 + AAC), 1920×1080, 30 fps. Se reproduce en cualquier móvil, ordenador, Moodle, Classroom o YouTube.
- **Narración:** voz masculina en español generada con el modelo Supertonic 3; cada frase se verificó automáticamente con reconocimiento de voz (Whisper).
- **Música:** pista *uplifting* original compuesta y sintetizada por código para cada vídeo (misma instrumentación, distinta tonalidad), sin derechos de autor. Baja automáticamente cuando habla el narrador.
- **Gráficos:** estilo unificado (fondo tecnológico animado, tarjetas, iconos, líneas de tiempo, diagramas) con un color distinto por unidad. Cada elemento aparece justo cuando el narrador lo menciona.
- **Subtítulos:** pista de subtítulos en español dentro del MP4 (se activa desde el reproductor) y archivo `.srt` con el mismo nombre del vídeo (VLC y la mayoría de reproductores lo cargan solo).

## Contenido de cada vídeo

- **UT1 · Digitalización de los sectores productivos:** Las revoluciones industriales · Las tecnologías que lo cambian todo · No es lo mismo digitizar que digitalizar · Sobredigitalización · Sistemas ciberfísicos · Convergencia IT / OT.
- **UT2 · Tecnologías digitales habilitadoras:** Tecnologías digitales habilitadoras · Las tecnologías que lo sostienen · Realidad inmersiva y robótica · Blockchain · ¿Destruyen o crean empleo?
- **UT3 · Sistemas en la nube:** La nube · De idea a servicio global · La usamos sin darnos cuenta · La nube, como un restaurante · Cloud, fog y edge · Ventajas e inconvenientes.
- **UT4 · Aplicación de la inteligencia artificial:** Inteligencia artificial · IA débil frente a IA fuerte · De los datos a la predicción · Ya está en todas partes · De Turing a AlphaGo · Dónde brilla y dónde no · Una IA responsable.
- **UT5 · Big data:** ¿Cuántos datos generamos? · Las 5 V del big data · Del dato al conocimiento · Explícitos frente a implícitos · Aplicaciones reales · Usar los datos con inteligencia.

Los datos de «cada minuto en internet» de la UT5 proceden de la infografía de LocaliQ (2023) incluida en la presentación.

## Regenerar o modificar los vídeos

La carpeta [`generador/`](generador/) contiene todo el código: guion (`content.py`), voz, música, mezcla y motor gráfico. Para cambiar un texto basta con editar `content.py` y volver a ejecutar el proceso (ver [generador/README.md](generador/README.md)).
