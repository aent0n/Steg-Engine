from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
import base64
import zlib
import json

class ImageSteganography:
    def __init__(self):
        self.bits_per_pixel = 1
        self.delimiter = "###END###"
        self.header_delimiter = "###HEADER###"
    
    def encode(self, image_path, message, use_encryption=False, use_compression=False):
        print(f"Encodage: message='{message}', encryption={use_encryption}, compression={use_compression}")
        # Charger l'image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        pixels = np.array(img)
        
        # Préparer les métadonnées
        metadata = {
            "encrypted": use_encryption,
            "compressed": use_compression,
            "key": None
        }
        
        # Préparer le message
        message_bytes = (message + self.delimiter).encode('utf-8')
        print(f"Message initial (longueur): {len(message_bytes)} bytes")
        
        # Appliquer la compression si demandée
        if use_compression:
            message_bytes = zlib.compress(message_bytes)
            print(f"Message compressé (longueur): {len(message_bytes)} bytes")
        
        # Appliquer le chiffrement si demandé
        if use_encryption:
            key = Fernet.generate_key()
            f = Fernet(key)
            message_bytes = f.encrypt(message_bytes)
            metadata["key"] = key.decode()
            print(f"Message chiffré (longueur): {len(message_bytes)} bytes")
        
        # Convertir le message en base64 pour assurer l'intégrité
        message_base64 = base64.b64encode(message_bytes)
        print(f"Message en base64 (longueur): {len(message_base64)} bytes")
        
        # Convertir en binaire
        binary_message = ''.join(format(b, '08b') for b in message_base64)
        print(f"Message binaire (longueur): {len(binary_message)} bits")
        
        # Préparer les métadonnées
        metadata_json = json.dumps(metadata)
        metadata_binary = ''.join(format(ord(char), '08b') for char in metadata_json)
        header_binary = ''.join(format(ord(char), '08b') for char in self.header_delimiter)
        
        # Assembler le message final
        final_binary = metadata_binary + header_binary + binary_message
        print(f"Longueur binaire totale: {len(final_binary)} bits")
        
        # Vérifier la capacité
        max_capacity = pixels.shape[0] * pixels.shape[1] * 3
        if len(final_binary) > max_capacity:
            raise ValueError(f"Message trop grand ({len(final_binary)} bits) pour l'image ({max_capacity} bits)")
        
        # Encoder le message
        message_index = 0
        modified_pixels = pixels.copy()
        
        for i in range(pixels.shape[0]):
            for j in range(pixels.shape[1]):
                for k in range(3):
                    if message_index < len(final_binary):
                        modified_pixels[i, j, k] = (pixels[i, j, k] & ~1) | int(final_binary[message_index])
                        message_index += 1
        
        # Sauvegarder l'image
        output_path = image_path.rsplit('.', 1)[0] + '_encoded.png'
        Image.fromarray(modified_pixels).save(output_path)
        print(f"Image sauvegardée: {output_path}")
        
        return output_path
    
    def decode(self, image_path):
        print(f"Décodage de l'image: {image_path}")
        # Charger l'image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        pixels = np.array(img)
        print(f"Dimensions de l'image: {pixels.shape}")
        
        # Extraire les bits LSB
        binary_message = ''
        for i in range(pixels.shape[0]):
            for j in range(pixels.shape[1]):
                for k in range(3):
                    binary_message += str(pixels[i, j, k] & 1)
        
        print(f"Longueur du message binaire: {len(binary_message)} bits")
        
        try:
            # Extraire et décoder les métadonnées
            metadata_text = ""
            header_found = False
            header_index = 0
            
            # Lire caractère par caractère jusqu'à trouver le délimiteur d'en-tête
            for i in range(0, len(binary_message), 8):
                if i + 8 > len(binary_message):
                    break
                byte = binary_message[i:i+8]
                try:
                    char = chr(int(byte, 2))
                    metadata_text += char
                    if metadata_text.endswith(self.header_delimiter):
                        header_found = True
                        header_index = i + 8
                        break
                except:
                    continue
            
            if not header_found:
                raise ValueError("Invalid message format: no header found")
            
            # Extraire les métadonnées
            metadata = json.loads(metadata_text[:-len(self.header_delimiter)])
            print(f"Métadonnées trouvées: {metadata}")
            
            # Extraire le message
            message_binary = binary_message[header_index:]
            message_bytes = bytearray()
            
            # Convertir les bits en bytes
            for i in range(0, len(message_binary) - 7, 8):
                byte = message_binary[i:i+8]
                try:
                    message_bytes.append(int(byte, 2))
                except:
                    continue
            
            # Décoder le base64
            try:
                message = base64.b64decode(bytes(message_bytes))
                print(f"Message décodé du base64 (longueur): {len(message)} bytes")
            except Exception as e:
                print(f"Erreur lors du décodage base64: {str(e)}")
                raise ValueError("Invalid base64 data")
            
            # Décrypter si nécessaire
            if metadata.get("encrypted"):
                if not metadata.get("key"):
                    raise ValueError("Encryption key not found")
                print("Déchiffrement du message...")
                try:
                    key = metadata["key"].encode()
                    f = Fernet(key)
                    message = f.decrypt(message)
                    print(f"Message déchiffré (longueur): {len(message)} bytes")
                except Exception as e:
                    print(f"Erreur lors du déchiffrement: {str(e)}")
                    print(f"Message problématique: {message[:100]}")
                    raise ValueError("Failed to decrypt message")
            
            # Décompresser si nécessaire
            if metadata.get("compressed"):
                print("Décompression du message...")
                try:
                    message = zlib.decompress(message)
                    print(f"Message décompressé (longueur): {len(message)} bytes")
                except Exception as e:
                    print(f"Erreur lors de la décompression: {str(e)}")
                    raise ValueError("Failed to decompress message")
            
            # Convertir en texte et retirer le délimiteur
            try:
                text = message.decode('utf-8')
                if self.delimiter not in text:
                    raise ValueError("Message delimiter not found")
                
                result = text[:text.index(self.delimiter)]
                print(f"Message final trouvé: {result}")
                return result
            except Exception as e:
                print(f"Erreur lors du décodage final: {str(e)}")
                raise ValueError("Failed to decode final message")
            
        except Exception as e:
            print(f"Erreur lors du décodage: {str(e)}")
            raise ValueError("No valid message found in image") 