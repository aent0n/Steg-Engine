// Constantes
const API_BASE_URL = 'http://localhost:5000/api';

// Gestionnaire pour la page de stéganographie d'image
class ImageSteganographyHandler {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        // Éléments d'encodage
        this.encodeInput = document.getElementById('imageInput');
        this.encodeUploadState = document.getElementById('encodeUploadState');
        this.encodeImagePreview = document.getElementById('encodeImagePreview');
        this.encodePreviewImg = document.getElementById('encodePreviewImg');
        this.encodeMessage = document.getElementById('secretMessage');
        this.encodeButton = document.getElementById('encodeButton');
        this.aesCheckbox = document.getElementById('aesEncryption');
        this.compressionCheckbox = document.getElementById('dataCompression');
        
        // Éléments de statistiques
        this.capacityIndicator = document.getElementById('capacityIndicator');
        this.encodingStats = document.getElementById('encodingStats');
        this.maxCapacity = document.getElementById('maxCapacity');
        this.messageSize = document.getElementById('messageSize');
        this.compressionRatio = document.getElementById('compressionRatio');
        this.spaceUsed = document.getElementById('spaceUsed');

        // Éléments de décodage
        this.decodeInput = document.getElementById('decodeImageInput');
        this.decodeUploadState = document.getElementById('decodeUploadState');
        this.decodeImagePreview = document.getElementById('decodeImagePreview');
        this.decodePreviewImg = document.getElementById('decodePreviewImg');
        this.decodeButton = document.getElementById('decodeButton');
        this.decodeResult = document.getElementById('decodedMessage');
        this.copyButton = document.getElementById('copyButton');

        // Bind des méthodes
        this.resetImageUpload = this.resetImageUpload.bind(this);
        this.updateCapacityIndicator = this.updateCapacityIndicator.bind(this);
        this.handleMessageInput = this.handleMessageInput.bind(this);
        this.copyDecodedMessage = this.copyDecodedMessage.bind(this);
        
        // Exposer la méthode resetImageUpload globalement
        window.resetImageUpload = this.resetImageUpload;
    }

    attachEventListeners() {
        // Gestionnaires d'événements pour l'encodage
        this.encodeInput.addEventListener('change', (e) => this.handleImageSelect(e, true));
        this.encodeButton.addEventListener('click', () => this.handleEncode());
        this.encodeMessage.addEventListener('input', this.handleMessageInput);
        this.compressionCheckbox.addEventListener('change', this.handleMessageInput);

        // Gestionnaires d'événements pour le décodage
        this.decodeInput.addEventListener('change', (e) => this.handleImageSelect(e, false));
        this.decodeButton.addEventListener('click', () => this.handleDecode());
        this.copyButton.addEventListener('click', this.copyDecodedMessage);

        // Gestion du drag & drop
        this.setupDragAndDrop();
    }

    setupDragAndDrop() {
        const dropZones = document.querySelectorAll('.border-dashed');
        
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('border-indigo-500');
            });

            zone.addEventListener('dragleave', () => {
                zone.classList.remove('border-indigo-500');
            });

            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('border-indigo-500');
                const isEncode = zone.closest('#encodeSection') !== null;
                const file = e.dataTransfer.files[0];
                this.handleDroppedFile(file, isEncode);
            });
        });
    }

    handleDroppedFile(file, isEncode) {
        if (file.type.startsWith('image/')) {
            if (isEncode) {
                this.encodeInput.files = new DataTransfer().files;
                this.handleImageSelect({ target: { files: [file] } }, true);
            } else {
                this.decodeInput.files = new DataTransfer().files;
                this.handleImageSelect({ target: { files: [file] } }, false);
            }
        } else {
            this.showError('Veuillez déposer une image valide');
        }
    }

    handleImageSelect(event, isEncode) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            if (isEncode) {
                this.encodeUploadState.classList.add('hidden');
                this.encodeImagePreview.classList.remove('hidden');
                this.encodePreviewImg.src = URL.createObjectURL(file);
                this.calculateImageCapacity(file);
            } else {
                this.decodeUploadState.classList.add('hidden');
                this.decodeImagePreview.classList.remove('hidden');
                this.decodePreviewImg.src = URL.createObjectURL(file);
            }
        } else {
            this.showError('Veuillez sélectionner une image valide');
        }
    }

    async calculateImageCapacity(file) {
        const img = new Image();
        img.src = URL.createObjectURL(file);
        await new Promise(resolve => img.onload = resolve);
        
        // Calculer la capacité en bits (1 bit par canal RGB par pixel)
        const totalBits = img.width * img.height * 3;
        // Convertir en caractères (8 bits par caractère)
        const maxChars = Math.floor(totalBits / 8);
        
        this.maxCapacity.textContent = maxChars;
        this.encodingStats.classList.remove('hidden');
        this.updateCapacityIndicator();
    }

    handleMessageInput() {
        this.updateCapacityIndicator();
        this.updateCompressionStats();
    }

    async updateCompressionStats() {
        const message = this.encodeMessage.value;
        if (!message) {
            this.compressionRatio.textContent = 'N/A';
            return;
        }

        if (this.compressionCheckbox.checked) {
            // Simuler la compression
            const blob = new Blob([message]);
            const compressed = await new Response(blob.stream().pipeThrough(new CompressionStream('gzip'))).blob();
            const ratio = ((1 - compressed.size / blob.size) * 100).toFixed(1);
            this.compressionRatio.textContent = `${ratio}% de réduction`;
        } else {
            this.compressionRatio.textContent = 'Désactivée';
        }
    }

    updateCapacityIndicator() {
        const currentLength = this.encodeMessage.value.length;
        const maxLength = parseInt(this.maxCapacity.textContent) || 0;
        
        this.capacityIndicator.textContent = `${currentLength}/${maxLength} caractères`;
        this.messageSize.textContent = currentLength;
        
        const usedPercentage = maxLength > 0 ? ((currentLength / maxLength) * 100).toFixed(1) : 0;
        this.spaceUsed.textContent = `${usedPercentage}%`;
        
        // Mettre à jour les couleurs selon l'utilisation
        if (currentLength > maxLength) {
            this.capacityIndicator.className = 'absolute bottom-2 right-2 text-sm text-red-500';
        } else if (currentLength > maxLength * 0.9) {
            this.capacityIndicator.className = 'absolute bottom-2 right-2 text-sm text-orange-500';
        } else {
            this.capacityIndicator.className = 'absolute bottom-2 right-2 text-sm text-gray-500';
        }
    }

    async copyDecodedMessage() {
        try {
            await navigator.clipboard.writeText(this.decodeResult.textContent);
            this.showSuccess('Message copié dans le presse-papiers !');
        } catch (err) {
            this.showError('Impossible de copier le message');
        }
    }

    resetImageUpload(isEncode) {
        if (isEncode) {
            this.encodeInput.value = '';
            this.encodeUploadState.classList.remove('hidden');
            this.encodeImagePreview.classList.add('hidden');
            this.encodePreviewImg.src = '';
        } else {
            this.decodeInput.value = '';
            this.decodeUploadState.classList.remove('hidden');
            this.decodeImagePreview.classList.add('hidden');
            this.decodePreviewImg.src = '';
            this.decodeResult.textContent = 'Le message décodé apparaîtra ici...';
            this.decodeResult.classList.add('text-gray-400', 'italic');
        }
    }

    async handleEncode() {
        const file = this.encodeInput.files[0];
        const message = this.encodeMessage.value;
        const useEncryption = this.aesCheckbox.checked;
        const useCompression = this.compressionCheckbox.checked;

        if (!file || !message) {
            this.showError('Veuillez sélectionner une image et entrer un message');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('message', message);
        formData.append('use_encryption', useEncryption);
        formData.append('use_compression', useCompression);

        try {
            this.showLoading(true);
            const response = await fetch(`${API_BASE_URL}/image/encode`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.success) {
                // Créer un lien temporaire pour télécharger le fichier
                const downloadUrl = `http://localhost:5000${data.file}`;
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = data.file.split('/').pop(); // Extraire le nom du fichier
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                this.showSuccess('Message encodé avec succès !');
            } else {
                this.showError(data.error || 'Une erreur est survenue');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showError('Erreur de connexion au serveur');
        } finally {
            this.showLoading(false);
        }
    }

    async handleDecode() {
        console.log('Début de handleDecode');
        const file = this.decodeInput.files[0];
        if (!file) {
            this.showError('Veuillez sélectionner une image à décoder');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showLoading(true);
            console.log('Envoi de la requête de décodage');
            const response = await fetch(`${API_BASE_URL}/image/decode`, {
                method: 'POST',
                body: formData
            });

            console.log('Réponse reçue:', response);
            const data = await response.json();
            console.log('Données reçues:', data);

            if (data.success) {
                this.decodeResult.textContent = data.message;
                this.decodeResult.classList.remove('text-gray-400', 'italic');
                this.copyButton.classList.remove('hidden');
                this.showSuccess('Message décodé avec succès !');
            } else {
                this.showError(data.error || 'Aucun message trouvé dans l\'image');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showError('Erreur de connexion au serveur');
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(isLoading) {
        // Ajouter un indicateur de chargement
        const buttons = [this.encodeButton, this.decodeButton];
        buttons.forEach(button => {
            if (isLoading) {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Traitement...';
            } else {
                button.disabled = false;
                button.innerHTML = button.dataset.originalText;
            }
        });
    }

    showError(message) {
        // Créer une notification d'erreur
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    showSuccess(message) {
        // Créer une notification de succès
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}

// Initialiser le gestionnaire si nous sommes sur la page de stéganographie d'image
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#imageInput')) {
        new ImageSteganographyHandler();
    }
});
