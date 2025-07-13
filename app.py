from flask import Flask, request, send_file, abort, render_template
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

app = Flask(__name__)

# Clave requerida
CLAVE_ACCESO = "GCSCMx25"

@app.route('/')
def form():
    return render_template('index.html')

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

        # Eliminar referencia al archivo original y liberar memoria
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
