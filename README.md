# Steg'Engine 🛡️

![Steg'Engine Logo](frontend/ressources/stegengineSVG.svg)

Steg'Engine est une application web moderne de stéganographie, permettant de dissimuler des informations dans différents types de fichiers. L'application combine une interface utilisateur intuitive avec un backend robuste pour un traitement sécurisé des données.

## 🌟 Fonctionnalités Actuelles

- **Stéganographie d'Image**
  - Technique LSB (Least Significant Bit)
  - Support des formats PNG
  - Interface drag & drop
  - Prévisualisation en temps réel
  - Statistiques de capacité
  - Compression des données
  - Chiffrement AES
 
  Démonstration:
[![Watch the video](https://raw.githubusercontent.com/aent0n/Steg-Engine/main/ressources/thumbnail_demoLSB.png)](https://raw.githubusercontent.com/aent0n/Steg-Engine/blob/main/frontend/ressources/demoVideo.mp4)
## 🚀 Installation

### Prérequis
- Python 3.8+
- Node.js (optionnel, pour le développement frontend)
- Un navigateur web moderne

### Installation

1. Clonez le repository :
```bash
git clone https://github.com/aent0n/Steg-Engine.git
cd Steg-Engine
```

2. Configurez l'environnement Python :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Unix
# ou
.venv\Scripts\activate     # Sur Windows
pip install -r backend/requirements.txt
```

3. Démarrez le serveur backend :
```bash
cd backend
python app.py
```

4. Ouvrez `frontend/index.html` dans votre navigateur ou utilisez un serveur local.

## 💻 Architecture

Le projet est organisé en deux parties principales :

### Frontend (`/frontend`)
- Interface utilisateur moderne avec TailwindCSS
- Traitement asynchrone des fichiers
- Prévisualisation en temps réel
- Gestion intuitive des erreurs
- Notifications utilisateur

### Backend (`/backend`)
- API Flask pour le traitement des fichiers
- Implémentation sécurisée des algorithmes de stéganographie
- Support du chiffrement AES
- Compression des données
- Gestion des erreurs robuste

## 🔒 Sécurité

- Validation côté serveur des fichiers uploadés
- Chiffrement AES disponible pour les messages
- Compression des données pour optimiser l'espace
- Traitement sécurisé des fichiers temporaires

## 🛠️ Structure du Projet
```
Steg-Engine/
├── frontend/
│   ├── index.html
│   ├── image-steg.html
│   ├── script.js
│   └── ressources/
│       └── stegengineSVG.svg
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── steganography/
│       ├── __init__.py
│       └── image.py
├── README.md
└── LICENSE.md
```

## 🔜 Fonctionnalités à Venir

- Stéganographie Audio (WAV)
- Stéganographie de Texte
- Stéganographie PDF
- Support de formats d'image supplémentaires
- Interface d'administration
- API publique documentée

## 👥 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 License

Ce projet est sous licence MIT - voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.

## 👤 Auteur

- **Anton** - [aent0n](https://github.com/aent0n)

## 📧 Contact

Pour toute question ou suggestion, n'hésitez pas à :
- Ouvrir une issue
- Me contacter sur GitHub [@aent0n](https://github.com/aent0n)

---
⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !
