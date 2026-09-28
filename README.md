# La Quinta Revolución

Aventura gráfica en pixel art, **táctil**, que recorre los apuntes de **Digitalización aplicada a los sectores productivos** de la UT1 a la UT5. Todo el juego está en un único archivo: [`la-quinta-revolucion.html`](la-quinta-revolucion.html).

Ada o Leo encuentran en el taller del instituto, con el Teide al fondo, el *Cronoprocesador*: una máquina que viaja por la historia de la digitalización. Le faltan cinco chips, uno por unidad. Solo con los cinco podrá responder a la pregunta del curso: *¿estamos en una 5ª revolución industrial?*

## Cómo se juega

- Abre `la-quinta-revolucion.html` en cualquier navegador: móvil, tablet u ordenador. No hace falta internet ni instalar nada.
- Toca el suelo para caminar y toca personas u objetos para interactuar. Arrastra la escena para mirar alrededor.
- Para usar un objeto, tócalo en el inventario y después toca algo de la escena. Si lo tocas dos veces, verás qué es.
- Botones de la barra superior:
  - la **chispa** muestra todo lo que se puede tocar;
  - la **bombilla** pide una pista a BIT;
  - el **libro** abre los apuntes;
  - el **menú** permite cambiar de unidad, quitar el sonido o volver a la portada.
- La partida se guarda sola en el navegador; en la portada aparece «Continuar».

## Qué recorre

| Unidad | Escenas | Contenidos |
| --- | --- | --- |
| UT1 · Digitalización de los sectores productivos | Inglaterra 1785, ciudad industrial 1880, centro de cálculo 1975, fábrica inteligente | Las cuatro revoluciones industriales; sistemas ciberfísicos y su ciclo (sensor, red, decisión, actuador); gemelo digital; IT y OT y su convergencia; digitalizar frente a sobredigitalizar |
| UT2 · Tecnologías Digitales Habilitadoras | Expo Habilita: plaza, pabellón de conectividad, pabellón de máquinas, simulador VR | Qué son las TDH; Big Data, 5G y GPS/GNSS (triangulación); IA, machine learning y deep learning; VR, AR y realidad mixta; cobots y robots autónomos; blockchain y DLT; chatbots y empleo |
| UT3 · Sistemas en la nube | Nubópolis: muelle, Restaurante La Nube, centro de datos submarino, Torre de las capas | Qué es la nube y su historia; almacenamiento y cloud computing; centros de datos; SaaS, PaaS e IaaS; cloud, fog, edge y mist; modelos de despliegue; ventajas y riesgos |
| UT4 · Aplicación de la inteligencia artificial | Museo de la Mente, laboratorio de aprendizaje, centro de emergencias 112 | IA débil y fuerte; de Turing a AlphaGo; cómo aprende la IA y sus sesgos; el prompt multimodal; modelos del mundo; robots sociables; IA en emergencias; RGPD y LOPDGDD; impacto en el empleo |
| UT5 · Evaluación de datos: Big Data | Lago de los datos, la Colmena, Pixelgram, observatorio | Las 5 V; data lake; procesamiento distribuido; datos explícitos e implícitos; análisis de patrones; dashboards; Big Data en emergencias; ventajas y riesgos |

Cada concepto que se descubre queda guardado como una ficha en los **Apuntes**. En total hay 73 fichas; las que faltan indican dónde se consiguen. Cada unidad termina con retos que repasan su contenido: ordenar, emparejar, clasificar, preguntas y minijuegos.

## Código de finalización

Al terminar la aventura, el Cronoprocesador da un **código al azar de una lista fija de 50** (por ejemplo `ABC-123`). El código queda guardado en la partida y se puede volver a ver desde el menú, así que si repiten el final les sale el mismo.

Para comprobar que alguien se ha pasado el juego, busca su código en tu lista de 50 o usa **«Profesorado: comprobar un código»** en la portada. La lista no está en este repositorio, para que no la vea el alumnado.

## En clase

- Desde la portada, **Elegir unidad** permite empezar directamente en cualquier UT, por ejemplo para repasar un tema concreto.
- Se juega bien en vertical y en horizontal. En un proyector conviene la pantalla completa del navegador.

## Detalles técnicos

- Todo el arte (fondos, personajes, efectos) se dibuja por código en un `canvas`. La música y los efectos se generan con WebAudio.
- El archivo no carga nada de internet. Lleva incrustadas las fuentes Pixelify Sans y VT323, ambas con licencia SIL Open Font License.
