/**
 * Misión 4.0 · Recepción de notas (Google Apps Script)
 *
 * Recibe el resultado que envía el juego al terminar, guarda el PDF
 * en la carpeta de Drive y añade una fila a la hoja «Notas UT1 · Misión 4.0»
 * (se crea sola dentro de la misma carpeta la primera vez).
 *
 * Instrucciones de instalación: envio-notas/LEEME.md
 */
const FOLDER_ID = '1DfAF6UebHTmwujkiHn78rM4x7Uvy_jXX';
const HOJA = 'Notas UT1 · Misión 4.0';
const CICLOS = [
  'DJK 1º Acondicionamiento Físico',
  'DJK 1º Animación Sociodeportiva',
  'DJK 1º Integración Social',
  'DJK 1º Educación Infantil',
  'DJK 1º Higiene Bucodental'
];

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    if (!d || !d.pdf || !d.nombre || !d.apellidos) throw new Error('Faltan datos del alumno');
    if (CICLOS.indexOf(d.ciclo) < 0) throw new Error('Ciclo no válido');
    const nota = Number(d.nota);
    if (!(nota >= 0 && nota <= 10)) throw new Error('Nota no válida');

    const nombreArchivo = String(d.filename || 'resultado.pdf').replace(/[^\w.,\-]/g, '_').slice(0, 150);
    const blob = Utilities.newBlob(Utilities.base64Decode(d.pdf), 'application/pdf', nombreArchivo);
    const carpeta = DriveApp.getFolderById(FOLDER_ID);
    const archivo = carpeta.createFile(blob);

    registrar_(carpeta, d, nota, archivo);
    return salida_({ ok: true, archivo: archivo.getName() });
  } catch (err) {
    return salida_({ ok: false, error: String((err && err.message) || err) });
  }
}

// Permite comprobar en el navegador que la aplicación web está publicada.
function doGet() {
  return salida_({ ok: true, servicio: 'Misión 4.0 · recepción de notas' });
}

function registrar_(carpeta, d, nota, archivo) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const it = carpeta.getFilesByName(HOJA);
    let ss;
    if (it.hasNext()) {
      ss = SpreadsheetApp.open(it.next());
    } else {
      ss = SpreadsheetApp.create(HOJA);
      DriveApp.getFileById(ss.getId()).moveTo(carpeta);
      ss.getSheets()[0].appendRow(['Recibido', 'Apellidos', 'Nombre', 'Ciclo', 'Nota', 'Aciertos', 'Retos', 'Puntos', 'Intento', 'Tiempo', 'PDF']);
      ss.getSheets()[0].setFrozenRows(1);
    }
    ss.getSheets()[0].appendRow([new Date(), d.apellidos, d.nombre, d.ciclo, nota, d.aciertos, d.retos, d.puntos, d.intento, d.tiempo, archivo.getUrl()]);
  } finally {
    lock.releaseLock();
  }
}

function salida_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
