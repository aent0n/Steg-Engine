from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from steganography import (
    ImageSteganography,
    #AudioSteganography,
    #TextSteganography,
    #PDFSteganography
)

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Pour permettre les requêtes cross-origin depuis le frontend

# Route pour servir les fichiers frontend
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Route pour servir les fichiers encodés
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg'},
    'audio': {'wav'},
    'pdf': {'pdf'},
    'text': {'txt'}
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB et taille de 1024x1024

def allowed_file(filename, file_type):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

# Routes pour la stéganographie d'image
@app.route('/api/image/encode', methods=['POST'])
def encode_image():
    try:
        # Vérifier si un fichier a été uploadé
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier trouvé'}), 400
        
        file = request.files['file']
        message = request.form.get('message', '')
        use_encryption = request.form.get('use_encryption', 'false') == 'true'
        use_compression = request.form.get('use_compression', 'false') == 'true'
        
        if not file or not message:
            return jsonify({'success': False, 'error': 'Fichier ou message manquant'}), 400
        
        # Sauvegarder temporairement l'image
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(temp_path)
        
        # Encoder le message dans l'image
        steg = ImageSteganography()
        output_path = steg.encode(temp_path, message, use_encryption, use_compression)
        
        # Nettoyer le fichier temporaire
        os.remove(temp_path)
        
        # Retourner le chemin du fichier encodé
        return jsonify({
            'success': True,
            'file': output_path.replace(app.config['UPLOAD_FOLDER'], '/uploads')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/image/decode', methods=['POST'])
def decode_image():
    print("Début de la requête de décodage")
    if 'file' not in request.files:
        print("Pas de fichier dans la requête")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    print(f"Fichier reçu: {file.filename}")
    
    if file and allowed_file(file.filename, 'image'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Sauvegarde du fichier dans: {filepath}")
        file.save(filepath)
        
        try:
            steg = ImageSteganography()
            print("Début du décodage")
            message = steg.decode(filepath)
            print(f"Message décodé avec succès: {message[:100]}...")
            return jsonify({
                'success': True,
                'message': message,
                'details': {
                    'method': 'LSB',
                    'data_size': len(message),
                    'encryption': 'None'
                }
            })
        except Exception as e:
            print(f"Erreur lors du décodage: {str(e)}")
            return jsonify({'error': str(e)}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
                print("Fichier temporaire supprimé")
    
    print("Type de fichier non valide")
    return jsonify({'error': 'Invalid file type'}), 400

# Routes similaires pour audio, texte et PDF
# [...]

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True) 