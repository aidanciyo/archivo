# Envío automático de notas · Misión 4.0

El juego (`index.html`) genera al terminar un PDF con **nombre, apellidos, ciclo y nota**
y lo envía a una pequeña aplicación de Google Apps Script. Esa aplicación lo guarda en la carpeta
de Drive `1DfAF6UebHTmwujkiHn78rM4x7Uvy_jXX` y apunta la nota en la hoja
«Notas UT1 · Misión 4.0» (se crea sola en esa carpeta).

Una página HTML no puede escribir directamente en una carpeta de Drive, por eso hace falta
este paso. Se hace **una sola vez** y tarda unos 5 minutos.

## 1. Crear la aplicación

1. Entra en <https://script.google.com> con la cuenta dueña de la carpeta y pulsa **Nuevo proyecto**.
2. Ponle de nombre «Misión 4.0 · notas».
3. Borra lo que aparece en `Código.gs` y pega el contenido de `Codigo.gs`.
4. Guarda (icono del disquete).

## 2. Publicarla

1. Pulsa **Implementar → Nueva implementación**.
2. En el engranaje de «Seleccionar tipo», elige **Aplicación web**.
3. Configura:
   - **Ejecutar como:** Yo (tu cuenta)
   - **Quién tiene acceso:** Cualquier usuario
4. Pulsa **Implementar** y **autoriza** los permisos (Drive y Hojas de cálculo). Si aparece
   «Google no ha verificado esta aplicación», pulsa *Configuración avanzada → Ir a … (no seguro)*:
   es tu propio script.
5. Copia la **URL de la aplicación web** (termina en `/exec`).

Puedes comprobarla abriéndola en el navegador: debe mostrar `{"ok":true,...}`.

## 3. Conectar el juego

Abre `index.html` con un editor de texto, busca esta línea cerca del principio del bloque de contenido:

```js
const ENVIO_URL = '';
```

y pega la URL entre las comillas:

```js
const ENVIO_URL = 'https://script.google.com/macros/s/XXXXXXXX/exec';
```

Guarda el archivo y repártelo al alumnado (Campus Virtual, Classroom, carpeta compartida…).
Los alumnos lo abren en el navegador y juegan; necesitan Internet al terminar.

## Cómo se calcula la nota

`nota = aciertos ÷ retos respondidos × 10` en la partida que llega al final (un decimal).
Si un alumno se queda sin vidas no se envía nada y debe empezar de nuevo; el PDF indica el
número de intento en ese dispositivo y la lista de retos fallados.

## Limitaciones

- Cada partida terminada envía un PDF nuevo: si un alumno juega dos veces, verás dos archivos
  (con fecha y hora en el nombre y una fila por envío en la hoja).
- El juego se ejecuta en el navegador del alumno: alguien con conocimientos técnicos podría
  manipular el archivo. Úsalo como evidencia de actividad, no como examen con garantías.
- Si se pierde la conexión al final, el resultado queda guardado en ese navegador y la portada
  muestra un botón «Enviar ahora».
