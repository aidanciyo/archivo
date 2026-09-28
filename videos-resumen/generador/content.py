# -*- coding: utf-8 -*-
"""Guiones y escenas de los vídeos resumen (UT1-UT5).

Cada escena tiene un tipo de plantilla gráfica y unas líneas de narración.
Las marcas {clave} dentro del texto indican el instante en que aparece el
elemento visual con esa clave (0, 1, 2... para listas; L/R, c0, f, etc.).
"""

MODULE = "Digitalización aplicada a los sectores productivos"

VIDEOS = [
# ─────────────────────────────────────────────────────────────── UT1
{
  "id": "UT1", "num": "1",
  "title": "Digitalización de los sectores productivos",
  "accent": "#22D3EE", "accent2": "#3B82F6", "icon": "factory",
  "next": "UT2 · Tecnologías digitales habilitadoras",
  "scenes": [
    {"type": "intro", "lines": [
        "Unidad 1: digitalización de los sectores productivos.",
        "En dos minutos, lo esencial. ¡Vamos allá!"]},
    {"type": "timeline", "kicker": "01 · De dónde venimos", "title": "Las revoluciones industriales",
     "items": [
        {"year": "1780", "tag": "1.ª revolución", "label": "Vapor y mecanización", "desc": "Del campo a la fábrica", "icon": "factory"},
        {"year": "1870", "tag": "2.ª revolución", "label": "Electricidad y petróleo", "desc": "Producción en serie", "icon": "zap"},
        {"year": "Años 70", "tag": "3.ª revolución", "label": "Electrónica e informática", "desc": "Automatización e internet", "icon": "cpu"},
        {"year": "2011", "tag": "4.ª revolución", "label": "Datos y conectividad", "desc": "Industria 4.0", "icon": "network"}],
     "footer": "La cuarta no añade máquinas: añade información sobre ellas.",
     "lines": [
        "Todo empieza con las revoluciones industriales.",
        "{0}La primera, en el siglo XVIII, trajo la máquina de vapor.",
        "{1}La segunda, la electricidad y la producción en serie.",
        "{2}La tercera, la informática e internet.",
        "{3}Y la cuarta, desde 2011, es la industria 4.0: datos, conectividad y robótica.",
        "{f}La cuarta no añade máquinas: añade información sobre ellas."]},
    {"type": "grid", "kicker": "02 · Industria 4.0", "title": "Las tecnologías que lo cambian todo", "cols": 3,
     "items": [
        {"icon": "cloud", "label": "Nube", "desc": "Datos y potencia de cálculo"},
        {"icon": "radio-tower", "label": "Internet de las cosas", "desc": "Sensores conectados"},
        {"icon": "brain", "label": "Inteligencia artificial", "desc": "Aprendizaje automático"},
        {"icon": "glasses", "label": "Realidad virtual y aumentada", "desc": "Interacción persona-máquina"},
        {"icon": "bot", "label": "Robótica", "desc": "Automatización y vehículos autónomos"},
        {"icon": "printer", "label": "Fabricación aditiva", "desc": "Impresión 3D"}],
     "chips": ["Cadenas de suministro eficientes", "Menos desperdicio", "Más sostenibilidad"],
     "lines": [
        "Sus tecnologías clave: {0}la nube, {1}el internet de las cosas, {2}la inteligencia artificial, {3}la realidad virtual y aumentada, {4}la robótica {5}y la impresión 3D.",
        "¿El resultado? {c0}Cadenas de suministro más eficientes, {c1}menos desperdicio {c2}y más sostenibilidad."]},
    {"type": "flow", "kicker": "03 · Conceptos clave", "title": "No es lo mismo digitizar que digitalizar", "numbered": True,
     "items": [
        {"icon": "file-scan", "label": "Digitización", "desc": "Del papel a lo digital. El proceso sigue igual."},
        {"icon": "workflow", "label": "Digitalización", "desc": "Se rediseña el proceso: trabajo en línea, alertas…"},
        {"icon": "rocket", "label": "Transformación digital", "desc": "Cambia el modelo de negocio y la organización."}],
     "note": "Regla práctica: si al quitar la tecnología el proceso funciona igual, era digitización.",
     "lines": [
        "Pero cuidado: no es lo mismo digitizar que digitalizar.",
        "{0}Digitizar es pasar del papel a lo digital: el proceso sigue igual.",
        "{1}Digitalizar es rediseñar el proceso.",
        "{2}Y la transformación digital cambia el modelo de negocio.{n}"]},
    {"type": "quote", "kicker": "04 · Ojo con…", "quote": "Digitalizar no es comprar tecnología.",
     "term": "Sobredigitalización", "icon": "scale",
     "definition": "Cuando la complejidad, los costes o la exclusión superan a los beneficios reales.",
     "lines": [
        "Y recuerda: digitalizar no es comprar tecnología.",
        "Si un proceso es innecesariamente complicado, digitalizarlo solo lo hace complicado… y además digital.",
        "{t}Eso es la sobredigitalización: cuando los costes y la complejidad superan a los beneficios."]},
    {"type": "cycle", "kicker": "05 · Lo físico y lo digital", "title": "Sistemas ciberfísicos", "center": "CPS", "parts": ["Hardware", "Software", "Redes"],
     "items": [
        {"icon": "thermometer", "label": "Sensor", "desc": "Mide una magnitud real"},
        {"icon": "wifi", "label": "Red", "desc": "Transporta el dato"},
        {"icon": "brain", "label": "Decisión", "desc": "Compara, calcula o predice"},
        {"icon": "cog", "label": "Actuador", "desc": "Ejecuta en el mundo físico"}],
     "extra": {"icon": "copy", "title": "Gemelo digital", "text": "Réplica virtual viva, alimentada con datos en tiempo real: simula y predice sin tocar el original."},
     "lines": [
        "El corazón de todo son los sistemas ciberfísicos, que unen hardware, software y redes.",
        "Funcionan en ciclo: {0}un sensor mide, {1}la red transporta el dato, {2}el sistema decide {3}y un actuador ejecuta.",
        "{x}Y si creamos una réplica virtual alimentada con datos en tiempo real, tenemos un gemelo digital."]},
    {"type": "compare", "kicker": "06 · Dos mundos que convergen", "title": "Convergencia IT / OT", "mode": "merge",
     "left": {"abbr": "IT", "icon": "server", "label": "Tecnología de la información", "desc": "Gestiona los datos"},
     "right": {"abbr": "OT", "icon": "factory", "label": "Tecnología operativa", "desc": "Controla las máquinas"},
     "center": "IT + OT",
     "chips": ["Menos costes", "Más eficiencia", "Trazabilidad", "Ciberseguridad reforzada"],
     "lines": [
        "Por último, dos mundos que hoy convergen: {L}IT, la tecnología de la información, que gestiona datos, {R}y OT, la tecnología operativa, que controla máquinas.",
        "{M}Juntos {c0}reducen costes, {c1}ganan eficiencia {c2}y trazabilidad… {c3}siempre que se refuerce la ciberseguridad."]},
    {"type": "outro", "title": "Ideas clave",
     "items": ["La 4.ª revolución añade información a las máquinas",
               "Digitalizar es rediseñar procesos, no comprar tecnología",
               "Sensor → red → decisión → actuador",
               "IT + OT: datos y máquinas trabajando juntos"],
     "lines": [
        "En resumen: tecnología, sí, pero con sentido.",
        "{end}¡Nos vemos en la próxima unidad!"]},
  ]},

# ─────────────────────────────────────────────────────────────── UT2
{
  "id": "UT2", "num": "2",
  "title": "Tecnologías digitales habilitadoras",
  "accent": "#A78BFA", "accent2": "#E879F9", "icon": "layers",
  "next": "UT3 · Sistemas en la nube",
  "scenes": [
    {"type": "intro", "lines": [
        "Unidad 2: tecnologías digitales habilitadoras.",
        "¡Empezamos!"]},
    {"type": "definition", "kicker": "01 · Qué son", "term": "Tecnologías digitales habilitadoras", "abbr": "TDH", "icon": "layers",
     "text": "Herramientas que permiten a las empresas transformarse digitalmente y entrar en el modelo de negocio de la industria 4.0.",
     "chips": ["Innovación en procesos y productos", "Nuevos negocios y mercados", "Más productividad", "También para pymes"],
     "lines": [
        "Las tecnologías digitales habilitadoras son las herramientas que permiten a una empresa transformarse digitalmente y competir en la industria 4.0.",
        "Son transversales: {c0}impulsan la innovación, {c1}abren nuevos mercados {c2}y mejoran la productividad, {c3}también en las pymes."]},
    {"type": "grid", "kicker": "02 · El catálogo", "title": "Las tecnologías que lo sostienen", "cols": 4,
     "items": [
        {"icon": "database", "label": "Big data", "desc": "Información útil a partir de enormes volúmenes de datos"},
        {"icon": "signal", "label": "Redes 5G", "desc": "Más rápidas y con menos latencia que el 4G"},
        {"icon": "satellite", "label": "GPS · GNSS", "desc": "Posición, velocidad y hora exacta por triangulación"},
        {"icon": "brain", "label": "Inteligencia artificial", "desc": "Machine learning y deep learning"}],
     "lines": [
        "Veamos las principales.",
        "{0}El big data analiza enormes volúmenes de datos para tomar mejores decisiones.",
        "{1}Las redes 5G son más rápidas y con menor latencia que el 4G, y conectan vehículos, sensores y realidad virtual.",
        "{2}Los satélites GPS nos dan posición, velocidad y hora exacta en cualquier parte del mundo.",
        "{3}Y la inteligencia artificial aprende de los datos: el machine learning detecta patrones, y el deep learning aprende incluso de datos sin estructurar."]},
    {"type": "grid", "kicker": "03 · Nuevas formas de interactuar", "title": "Realidad inmersiva y robótica", "cols": 4,
     "items": [
        {"icon": "glasses", "label": "Realidad virtual", "desc": "Te sumerge en un entorno 100 % digital"},
        {"icon": "scan-eye", "label": "Realidad aumentada y mixta", "desc": "Combina lo virtual con el mundo real"},
        {"icon": "hand-helping", "label": "Robots colaborativos", "desc": "Trabajan junto a personas, de forma segura"},
        {"icon": "car", "label": "Robots autónomos", "desc": "Perciben, deciden y actúan sin ayuda humana"}],
     "lines": [
        "{0}La realidad virtual nos sumerge por completo en un entorno digital; {1}la aumentada y la mixta combinan lo virtual con el mundo real.",
        "{2}Los cobots trabajan junto a las personas de forma segura y asumen las tareas más peligrosas, {3}y los robots autónomos perciben su entorno y deciden sin intervención humana."]},
    {"type": "chain", "kicker": "04 · Confianza digital", "title": "Blockchain",
     "pillars": [{"icon": "eye", "label": "Transparencia"}, {"icon": "shield-check", "label": "Seguridad"}, {"icon": "handshake", "label": "Sin intermediarios"}],
     "examples": ["Bitcoin", "IBM Food Trust", "UNICEF"],
     "lines": [
        "{b}El blockchain es como un libro de cuentas compartido: guarda la información en bloques encadenados que nadie puede alterar sin que todos lo vean.",
        "Aporta {p0}transparencia, {p1}seguridad {p2}y confianza sin intermediarios.",
        "{e}Se usa en Bitcoin, en IBM Food Trust para rastrear alimentos o en UNICEF para seguir donaciones."]},
    {"type": "compare", "kicker": "05 · Negocio y empleo", "title": "¿Destruyen o crean empleo?", "mode": "versus",
     "left": {"icon": "trending-down", "label": "Tareas que se automatizan", "tone": "warn",
              "items": ["Atención telefónica → chatbots", "Montaje y empaquetado", "Procesamiento manual de datos"]},
     "right": {"icon": "trending-up", "label": "Perfiles que nacen", "tone": "good",
               "items": ["Científicos de datos", "Técnicos de robótica", "Administradores cloud"]},
     "center": "VS",
     "lines": [
        "Todo esto reorganiza los negocios: {L}un chatbot ya atiende a clientes como lo haría un teleoperador, y la formación se vuelve imprescindible.",
        "¿Destruyen empleo? Algunas tareas desaparecen, {R}pero nacen nuevos perfiles: científicos de datos, técnicos de robótica o administradores cloud."]},
    {"type": "outro", "title": "Ideas clave",
     "items": ["Las TDH impulsan la transformación digital",
               "Big data, 5G, GPS e inteligencia artificial",
               "Realidad inmersiva, robótica y blockchain",
               "Cambian el empleo: la formación es clave"],
     "lines": [
        "Conócelas bien: te abrirán muchas puertas.",
        "{end}¡Nos vemos en la próxima unidad!"]},
  ]},

# ─────────────────────────────────────────────────────────────── UT3
{
  "id": "UT3", "num": "3",
  "title": "Sistemas en la nube",
  "accent": "#34D399", "accent2": "#22D3EE", "icon": "cloud",
  "next": "UT4 · Aplicación de la inteligencia artificial",
  "scenes": [
    {"type": "intro", "lines": [
        "Unidad 3: sistemas en la nube.",
        "¡Despegamos!"]},
    {"type": "definition", "kicker": "01 · Qué es", "term": "La nube", "abbr": "Cloud", "icon": "cloud",
     "text": "El ordenador de otra persona, al que accedemos por internet.",
     "chips": ["Almacenamiento masivo", "Aplicaciones", "Mantenimiento externo", "Desde cualquier lugar"],
     "lines": [
        "La nube es, en pocas palabras, el ordenador de otra persona al que accedemos por internet.",
        "Ofrece {c0}almacenamiento, {c1}aplicaciones {c2}y mantenimiento fuera de la empresa, {c3}desde cualquier lugar y dispositivo."]},
    {"type": "timeline", "kicker": "02 · Breve historia", "title": "De idea a servicio global",
     "items": [
        {"year": "1960", "tag": "La idea", "label": "John McCarthy", "desc": "La informática como servicio público", "icon": "lightbulb"},
        {"year": "1999", "tag": "Primer SaaS", "label": "Salesforce", "desc": "Aplicaciones a través de internet", "icon": "globe"},
        {"year": "2002", "tag": "Infraestructura", "label": "Amazon Web Services", "desc": "Almacenamiento y cómputo online", "icon": "server"},
        {"year": "2009", "tag": "Expansión", "label": "Google, Microsoft…", "desc": "Se suman al cloud computing", "icon": "cloud"}],
     "lines": [
        "Su historia es reciente: {0}en 1960, John McCarthy imagina la informática como un servicio público.",
        "{1}En 1999, Salesforce ofrece aplicaciones por internet; {2}en 2002 nace Amazon Web Services; {3}y en 2009 se suman Google y Microsoft."]},
    {"type": "grid", "kicker": "03 · En tu día a día", "title": "La usamos sin darnos cuenta", "cols": 4,
     "items": [
        {"icon": "hard-drive", "label": "Almacenamiento", "desc": "Tus archivos, con copias automáticas"},
        {"icon": "monitor-play", "label": "Streaming", "desc": "Series y música sin descargar nada"},
        {"icon": "message-circle", "label": "Redes y mensajería", "desc": "Todo reaparece al iniciar sesión"},
        {"icon": "gamepad-2", "label": "Juego en la nube", "desc": "Un servidor lejano procesa los gráficos"}],
     "banner": {"icon": "server", "text": "Todo vive en centros de datos… ¡incluso bajo el mar!"},
     "lines": [
        "La usamos a diario: {0}guardamos archivos con copias automáticas, {1}vemos series en streaming, {2}chateamos en redes sociales {3}e incluso jugamos a videojuegos en la nube.",
        "{x}Todo funciona en enormes centros de datos; hay incluso centros submarinos, refrigerados por el mar."]},
    {"type": "stack", "kicker": "04 · Niveles de servicio", "title": "La nube, como un restaurante",
     "items": [
        {"abbr": "SaaS", "name": "Software como servicio", "analogy": "Solo disfrutas del plato", "examples": "Gmail · Netflix · Spotify", "icon": "utensils"},
        {"abbr": "PaaS", "name": "Plataforma como servicio", "analogy": "Alquilas la cocina equipada y cocinas tú", "examples": "Tú creas el software", "icon": "chef-hat"},
        {"abbr": "IaaS", "name": "Infraestructura como servicio", "analogy": "Alquilas el local vacío", "examples": "Instalas y mantienes el servidor", "icon": "store"}],
     "meter": ["Más comodidad", "Más control y mantenimiento"],
     "lines": [
        "Hay tres niveles de servicio, como en un restaurante.",
        "{0}SaaS, software como servicio: solo disfrutas del plato, como en Gmail, Netflix o Spotify.",
        "{1}PaaS, plataforma como servicio: alquilas la cocina equipada y tú creas tus recetas.",
        "{2}Y por último, IaaS, infraestructura como servicio: alquilas el local vacío, un servidor que tú instalas y mantienes."]},
    {"type": "tiers", "kicker": "05 · ¿Dónde se procesan los datos?", "title": "Cloud, fog y edge",
     "items": [
        {"icon": "cloud", "label": "Cloud", "sub": "La nube", "where": "Grandes centros de datos lejanos", "desc": "Máxima potencia, pero más latencia"},
        {"icon": "cloud-fog", "label": "Fog", "sub": "La niebla", "where": "Routers, gateways y servidores locales", "desc": "Filtra y resume antes de subir"},
        {"icon": "car", "label": "Edge", "sub": "El borde", "where": "En el propio dispositivo", "desc": "Decide en milisegundos"}],
     "lines": [
        "¿Y dónde se procesan los datos? {0}En el cloud, grandes centros de datos lejanos, con mucha potencia pero más latencia.",
        "{1}En el fog, nodos intermedios, como routers o servidores locales, que filtran y resumen.",
        "{2}Y en el edge, el propio dispositivo, que decide en milisegundos: como el coche que frena al detectar a un peatón."]},
    {"type": "proscons", "kicker": "06 · Balance", "title": "Ventajas e inconvenientes",
     "pros": ["Ahorro de costes", "Pago por uso", "Almacenamiento casi ilimitado", "Soporte 24/7", "Actualizaciones automáticas"],
     "cons": ["Menos control de la infraestructura", "Riesgos de seguridad si se gestiona mal", "Dependencia de la conexión a internet"],
     "lines": [
        "{P}Ventajas: ahorro de costes, pago por uso, almacenamiento casi sin límites, soporte 24 horas y actualizaciones automáticas.",
        "{C}Inconvenientes: menos control, riesgos de seguridad si se gestiona mal y dependencia total de internet."]},
    {"type": "outro", "title": "Ideas clave",
     "items": ["La nube: recursos informáticos a través de internet",
               "SaaS, PaaS e IaaS: tres niveles de servicio",
               "Cloud, fog y edge: más cerca, menos latencia",
               "Ahorro y flexibilidad… con control y seguridad"],
     "lines": [
        "La nube ya forma parte de tu día a día.",
        "{end}¡Nos vemos en la próxima unidad!"]},
  ]},

# ─────────────────────────────────────────────────────────────── UT4
{
  "id": "UT4", "num": "4",
  "title": "Aplicación de la inteligencia artificial",
  "accent": "#F472B6", "accent2": "#FB923C", "icon": "brain",
  "next": "UT5 · Big data",
  "scenes": [
    {"type": "intro", "lines": [
        "Unidad 4: aplicación de la inteligencia artificial.",
        "¡Arrancamos!"]},
    {"type": "definition", "kicker": "01 · Qué es", "term": "Inteligencia artificial", "abbr": "IA", "icon": "brain",
     "text": "La ciencia que intenta crear sistemas capaces de pensar y actuar por sí mismos.",
     "chips": ["Razonamiento", "Planificación", "Percepción"],
     "lines": [
        "La inteligencia artificial es la ciencia que intenta crear sistemas capaces de pensar y actuar por sí mismos, {c0}imitando el razonamiento, {c1}la planificación {c2}y la percepción humanas."]},
    {"type": "compare", "kicker": "02 · Tipos de IA", "title": "IA débil frente a IA fuerte", "mode": "versus",
     "left": {"icon": "target", "label": "IA débil o estrecha", "desc": "Creada para una tarea concreta",
              "items": ["Asistentes de voz", "Reconocimiento de imágenes", "La que usamos a diario"]},
     "right": {"icon": "sparkles", "label": "IA fuerte o general", "desc": "No simula una mente: sería una mente",
               "items": ["Piensa, razona y juzga", "Aprende nuevas habilidades", "Se comunica por sí sola"]},
     "center": "VS",
     "lines": [
        "Hay dos tipos: {L}la IA débil, creada para tareas concretas, que es la que usamos a diario.",
        "{R}Y la IA fuerte o general, que no simularía una mente: sería una mente capaz de razonar y aprender por sí sola."]},
    {"type": "flow", "kicker": "03 · Cómo aprende", "title": "De los datos a la predicción",
     "items": [
        {"icon": "database", "label": "Datos", "desc": "Enormes cantidades de ejemplos"},
        {"icon": "scan-search", "label": "Patrones", "desc": "Busca correlaciones"},
        {"icon": "trending-up", "label": "Predicción", "desc": "Anticipa lo que vendrá"}],
     "prompt": {"label": "Prompt multimodal", "chips": ["Texto", "Imagen", "Audio", "Vídeo", "Sensores"]},
     "lines": [
        "¿Cómo aprende? {0}Ingiriendo enormes cantidades de datos, {1}buscando patrones {2}y usándolos para predecir.",
        "{p}Le damos instrucciones con prompts: texto, imágenes, audio, vídeo o sensores; {m}si combina varias fuentes a la vez, es un prompt multimodal."]},
    {"type": "grid", "kicker": "04 · Aplicaciones", "title": "Ya está en todas partes", "cols": 3,
     "items": [
        {"icon": "scan-face", "label": "Voz y rostro", "desc": "Reconocimiento avanzado"},
        {"icon": "stethoscope", "label": "Imagen médica", "desc": "Detecta patrones en pruebas"},
        {"icon": "message-square", "label": "Chatbots", "desc": "Asistentes virtuales"},
        {"icon": "wand-sparkles", "label": "Creación de contenido", "desc": "Imagen y vídeo desde un prompt"},
        {"icon": "siren", "label": "Emergencias", "desc": "Predice riesgos y prioriza avisos"},
        {"icon": "drone", "label": "Búsqueda y rescate", "desc": "Drones con visión artificial"}],
     "lines": [
        "Ya está en todas partes: {0}reconocimiento de voz y rostro, {1}análisis de imágenes médicas, {2}chatbots {3}y creación de contenido.",
        "{4}En emergencias, predice riesgos y prioriza incidentes, {5}y ayuda a localizar personas con drones."]},
    {"type": "timeline", "kicker": "05 · Un poco de historia", "title": "De Turing a AlphaGo",
     "items": [
        {"year": "1950", "tag": "Las bases", "label": "Alan Turing", "desc": "¿Pueden pensar las máquinas?", "icon": "user"},
        {"year": "1956", "tag": "Nacimiento", "label": "Nace la «IA»", "desc": "Se acuña el término", "icon": "sparkles"},
        {"year": "1966", "tag": "Lenguaje", "label": "ELIZA", "desc": "El primer chatbot", "icon": "message-circle"},
        {"year": "1997", "tag": "Ajedrez", "label": "Deep Blue", "desc": "Vence a Kasparov", "icon": "crown"},
        {"year": "2016", "tag": "Deep learning", "label": "AlphaGo", "desc": "Gana al campeón de Go", "icon": "trophy"}],
     "lines": [
        "Su historia: {0}Alan Turing sienta las bases; {1}en 1956 nace el término; {2}en 1966 llega ELIZA, el primer chatbot.",
        "{3}En 1997, Deep Blue vence a Kasparov, {4}y en 2016 AlphaGo impulsa el boom del deep learning."]},
    {"type": "proscons", "kicker": "06 · Luces y sombras", "title": "Dónde brilla y dónde no",
     "pros": ["Muchos datos", "Rapidez", "Precisión", "Tareas repetitivas"],
     "cons": ["Creatividad pura e intuición", "Empatía real", "Poca información o datos confusos", "Cara, gasta mucha energía y hereda sesgos"],
     "lines": [
        "{P}Brilla con muchos datos, rapidez, precisión y tareas repetitivas; {C}pero flojea en creatividad, empatía y contextos con poca información.",
        "{c3}Además, es cara, consume mucha energía y refleja los sesgos de sus datos."]},
    {"type": "compare", "kicker": "07 · Datos y empleo", "title": "Una IA responsable", "mode": "chips",
     "left": {"icon": "shield-check", "label": "RGPD y LOPDGDD",
              "items": ["Consentimiento informado", "Minimización", "Anonimización", "Derecho al olvido", "Transparencia"]},
     "right": {"icon": "briefcase", "label": "Empleos nuevos",
               "items": ["Entrenadores de modelos", "Auditores de sesgos", "Ingenieros de prompts", "Ciberseguridad de IA"]},
     "lines": [
        "{L}Como aprende de datos, debe cumplir el RGPD: consentimiento, minimización, anonimización, derecho al olvido y transparencia.",
        "{R}Y aunque transformará el empleo, también crea perfiles nuevos: entrenadores de modelos, auditores de sesgos o ingenieros de prompts."]},
    {"type": "outro", "title": "Ideas clave",
     "items": ["IA débil (la de hoy) frente a IA fuerte",
               "Aprende de datos: patrones y predicciones",
               "Útil en salud, emergencias, atención al cliente…",
               "Con datos protegidos y sin sesgos"],
     "lines": [
        "No sustituye tu criterio: lo potencia.",
        "{end}¡Nos vemos en la próxima unidad!"]},
  ]},

# ─────────────────────────────────────────────────────────────── UT5
{
  "id": "UT5", "num": "5",
  "title": "Big data",
  "accent": "#FBBF24", "accent2": "#F97316", "icon": "database",
  "next": None,
  "scenes": [
    {"type": "intro", "lines": [
        "Unidad 5: big data.",
        "¡Empezamos!"]},
    {"type": "stats", "kicker": "01 · Cada minuto en internet", "title": "¿Cuántos datos generamos?",
     "items": [
        {"value": 625, "dec": 0, "suffix": " M", "label": "vídeos vistos en TikTok", "icon": "smartphone"},
        {"value": 3.47, "dec": 2, "suffix": " M", "label": "vídeos vistos en YouTube", "icon": "monitor-play"},
        {"value": 6.3, "dec": 1, "suffix": " M", "label": "búsquedas en Google", "icon": "search"},
        {"value": 231, "dec": 0, "suffix": " M", "label": "correos electrónicos", "icon": "mail"}],
     "source": "Fuente: LocaliQ, «Every minute of the day» (2023)",
     "lines": [
        "¿Sabes cuántos datos generamos cada minuto?",
        "{0}Seiscientos veinticinco millones de vídeos en TikTok, {1}casi tres millones y medio en YouTube, {2}más de seis millones de búsquedas en Google {3}y doscientos treinta y un millones de correos.",
        "Y todo eso, en solo sesenta segundos."]},
    {"type": "grid", "kicker": "02 · Qué es", "title": "Las 5 V del big data", "cols": 5,
     "lead": "Datos tan grandes, variados y rápidos que no caben en las herramientas tradicionales.",
     "items": [
        {"icon": "boxes", "label": "Volumen", "desc": "Cantidades enormes"},
        {"icon": "gauge", "label": "Velocidad", "desc": "Uso ágil, en tiempo real"},
        {"icon": "shapes", "label": "Variedad", "desc": "Texto, vídeo, IoT, GPS"},
        {"icon": "badge-check", "label": "Veracidad", "desc": "Datos fiables, no bulos"},
        {"icon": "gem", "label": "Valor", "desc": "Que sirva para algo"}],
     "lines": [
        "{d}Eso es big data: datos tan grandes, variados y rápidos que no caben ni se pueden procesar con herramientas tradicionales.",
        "Se define con cinco uves: {0}volumen, {1}velocidad, {2}variedad, {3}veracidad {4}y, sobre todo, valor: el resultado debe servir para algo."]},
    {"type": "flow", "kicker": "03 · Cómo funciona", "title": "Del dato al conocimiento",
     "items": [
        {"icon": "thumbs-up", "label": "Generación", "desc": "Likes, compras, GPS…"},
        {"icon": "database", "label": "Data lake", "desc": "Se guarda cada dato"},
        {"icon": "network", "label": "En paralelo", "desc": "Se trocea, se reparte y se une"},
        {"icon": "sparkles", "label": "Análisis", "desc": "Algoritmos, estadística e IA"}],
     "lines": [
        "{0}Cada vez que usamos el móvil, la tarjeta o el coche generamos datos: un like, una compra, un trayecto con GPS.",
        "{1}Todo se guarda en un data lake.",
        "{2}Después se trocea, se reparte entre muchos ordenadores que trabajan en paralelo y se unen los resultados.",
        "{3}Por último, algoritmos, estadística e inteligencia artificial buscan patrones y predicen comportamientos."]},
    {"type": "compare", "kicker": "04 · Tus datos en redes sociales", "title": "Explícitos frente a implícitos", "mode": "versus",
     "left": {"icon": "id-card", "label": "Datos explícitos", "desc": "Lo que escribes en tu perfil",
              "items": ["Nombre y edad", "Ubicación", "Estudios"]},
     "right": {"icon": "eye", "label": "Datos implícitos", "desc": "Los más valiosos",
               "items": ["A qué das like", "Cuánto miras un vídeo", "A quién sigues y cuándo te conectas"]},
     "center": "VS",
     "footer": "Like al fútbol → «fan del deporte»",
     "lines": [
        "En una red social hay {L}datos explícitos, lo que escribes en tu perfil, {R}y datos implícitos, los más valiosos: a qué das like, cuánto miras un vídeo o a quién sigues.",
        "{f}Con esos patrones te etiquetan: si siempre das like al fútbol, eres fan del deporte; si compras ropa online, consumidor de moda."]},
    {"type": "grid", "kicker": "05 · Resultados", "title": "Aplicaciones reales", "cols": 5,
     "lead": "Los datos se convierten en dashboards… y en acciones.",
     "items": [
        {"icon": "clapperboard", "label": "Entretenimiento", "desc": "Recomendaciones en Netflix o Spotify"},
        {"icon": "heart-pulse", "label": "Salud", "desc": "Detección temprana de enfermedades"},
        {"icon": "truck", "label": "Logística", "desc": "Rutas y envíos en tiempo real"},
        {"icon": "credit-card", "label": "Finanzas", "desc": "Detección de fraude"},
        {"icon": "building-2", "label": "Smart cities", "desc": "Tráfico y ahorro energético"}],
     "lines": [
        "{d}El resultado se convierte en gráficos, mapas y dashboards, y en acciones: {0}recomendaciones en Netflix, {1}diagnóstico temprano de enfermedades, {2}rutas en tiempo real en Google Maps, {3}detección de fraudes {4}o ciudades inteligentes que ahorran energía."]},
    {"type": "proscons", "kicker": "06 · Conclusión", "title": "Usar los datos con inteligencia",
     "quote": "Big data no es tener muchos datos, sino usarlos con inteligencia.",
     "pros": ["Mejores servicios", "Recomendaciones personalizadas", "Detección de fraudes", "Avances en salud"],
     "cons": ["Privacidad", "Manipulación de la información", "Sesgos en los algoritmos"],
     "lines": [
        "{q}Big data no es solo tener muchos datos, sino usarlos con inteligencia.",
        "{P}Aporta mejores servicios, recomendaciones personalizadas y avances en salud, {C}pero también riesgos: privacidad, manipulación de la información y sesgos en los algoritmos."]},
    {"type": "outro", "title": "Ideas clave",
     "items": ["Big data: volumen, velocidad, variedad, veracidad y valor",
               "Del dato al data lake y al procesamiento en paralelo",
               "Los datos implícitos son los más valiosos",
               "Privacidad y ética: úsalos con inteligencia"],
     "lines": [
        "Tus datos valen mucho: cuídalos y úsalos con cabeza.",
        "{end}¡Sigue aprendiendo!"]},
  ]},
]
