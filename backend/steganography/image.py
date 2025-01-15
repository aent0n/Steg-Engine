from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
import base64
import zlib
import json

class ImageSteganography:
    def __init__(self):
        self.bits_per_pixel = 1  # Nombre de bits LSB à utiliser
        self.delimiter = "###END###"  # Délimiteur de fin de message
        self.header_delimiter = "###HEADER###"  # Délimiteur pour l'en-tête
    
    def encode(self, image_path, message, use_encryption=False, use_compression=False):
        # Charger l'image
        img = Image.open(image_path)
        pixels = np.array(img)
        
        # Préparer les métadonnées
        metadata = {
            "encrypted": use_encryption,
            "compressed": use_compression,
            "key": None
        }
        
        # Ajouter le délimiteur au message
        message = message + self.delimiter
        
        # Traiter le message
        if use_compression:
            message_bytes = message.encode('utf-8')
            message = zlib.compress(message_bytes)
            
        if use_encryption:
            key = Fernet.generate_key()
            f = Fernet(key)
            message = f.encrypt(message if use_compression else message.encode())
            metadata["key"] = key.decode()  # Convertir la clé en string pour JSON
        
        # Convertir le message en binaire
        if use_encryption or use_compression:
            binary_message = ''.join(format(byte, '08b') for byte in message)
        else:
            binary_message = ''.join(format(ord(char), '08b') for char in message)
        
        # Ajouter les métadonnées au début
        metadata_json = json.dumps(metadata)
        metadata_binary = ''.join(format(ord(char), '08b') for char in metadata_json)
        
        # Assembler le message final avec les délimiteurs
        final_binary = (
            metadata_binary + 
            ''.join(format(ord(char), '08b') for char in self.header_delimiter) +
            binary_message
        )
        
        if len(final_binary) > pixels.size * self.bits_per_pixel:
            raise ValueError("Message too large for this image")
        
        # Encoder le message
        message_index = 0
        modified_pixels = pixels.copy()
        
        for i in range(pixels.shape[0]):
            for j in range(pixels.shape[1]):
                for k in range(3):  # RGB channels
                    if message_index < len(final_binary):
                        modified_pixels[i, j, k] = (pixels[i, j, k] & ~1) | int(final_binary[message_index])
                        message_index += 1
        
        # Sauvegarder l'image modifiée
        output_path = image_path.rsplit('.', 1)[0] + '_encoded.png'
        Image.fromarray(modified_pixels).save(output_path)
        
        return output_path
    
    def decode(self, image_path):
        print(f"Décodage de l'image: {image_path}")
        # Charger l'image
        img = Image.open(image_path)
        pixels = np.array(img)
        print(f"Dimensions de l'image: {pixels.shape}")
        
        # Extraire les bits LSB
        binary_message = ''
        for i in range(pixels.shape[0]):
            for j in range(pixels.shape[1]):
                for k in range(3):  # RGB channels
                    binary_message += str(pixels[i, j, k] & 1)
        
        print(f"Longueur du message binaire: {len(binary_message)}")
        
        try:
            # Extraire et décoder les métadonnées
            metadata_text = ""
            header_found = False
            header_index = 0
            
            # Lire caractère par caractère jusqu'à trouver le délimiteur d'en-tête
            for i in range(0, len(binary_message), 8):
                byte = binary_message[i:i+8]
                if len(byte) == 8:
                    char = chr(int(byte, 2))
                    metadata_text += char
                    if metadata_text.endswith(self.header_delimiter):
                        header_found = True
                        header_index = i + 8
                        break
            
            if not header_found:
                raise ValueError("Invalid message format: no header found")
            
            # Extraire les métadonnées
            metadata = json.loads(metadata_text[:-len(self.header_delimiter)])
            print(f"Métadonnées trouvées: {metadata}")
            
            # Extraire le message
            message_binary = binary_message[header_index:]
            message_bytes = []
            
            for i in range(0, len(message_binary), 8):
                byte = message_binary[i:i+8]
                if len(byte) == 8:
                    message_bytes.append(int(byte, 2))
            
            # Convertir en bytes
            message = bytes(message_bytes)
            
            # Décrypter si nécessaire
            if metadata.get("encrypted"):
                if not metadata.get("key"):
                    raise ValueError("Encryption key not found")
                print("Déchiffrement du message...")
                f = Fernet(metadata["key"].encode())
                message = f.decrypt(message)
            
            # Décompresser si nécessaire
            if metadata.get("compressed"):
                print("Décompression du message...")
                message = zlib.decompress(message)
            
            # Convertir en texte
            message = message.decode('utf-8')
            
            # Retirer le délimiteur de fin
            if self.delimiter not in message:
                raise ValueError("Message delimiter not found")
            
            message = message[:message.index(self.delimiter)]
            print("Message décodé avec succès")
            return message
            
        except Exception as e:
            print(f"Erreur lors du décodage: {str(e)}")
            raise ValueError("No valid message found in image") 