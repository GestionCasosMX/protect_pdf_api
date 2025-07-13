from flask import Flask, request, send_file, abort, render_template_string
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

app = Flask(__name__)

# Clave requerida
CLAVE_ACCESO = "GCSCMx25"

# Página HTML protegida por clave
HTML_FORM = """
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Proteger PDF</title></head>
<body>
  <h2>Subir PDF y asignar contraseña</h2>
  <form action="/proteger-pdf" method="post" enctype="multipart/form-data">
    <label>Clave de acceso:</label><br>
    <input type="password" name="clave" required><br><br>
    <label>Archivo PDF:</label><br>
    <input type="file" name="file" required><br><br>
    <label>Contraseña del PDF:</label><br>
    <input type="text" name="password" required><br><br>
    <button type="submit">Proteger PDF</button>
  </form>
</body>
</html>
"""

@app.route('/')
def form():
    return render_template_string(HTML_FORM)

@app.route('/proteger-pdf', methods=['POST'])
def proteger_pdf():
    # Validar clave
    clave = request.form.get('clave', '')
    if clave != CLAVE_ACCESO:
        abort(403, "Clave de acceso incorrecta")

    # Validar archivo y contraseña
    if 'file' not in request.files or 'password' not in request.form:
        return {'error': 'Faltan el archivo o la contraseña'}, 400

    file = request.files['file']
    password = request.form['password']

    try:
        reader = PdfReader(file)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        # Eliminar referencia al archivo original y liberación de memoria
        file.close()
        del file

        return send_file(
            output,
            download_name="pdf_protegido.pdf",
            as_attachment=True,
            mimetype="application/pdf"
        )
    except Exception as e:
        return {'error': f'No se pudo procesar el PDF: {str(e)}'}, 500
