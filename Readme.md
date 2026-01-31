# Grok Image & Video Generator (Local)

Une application web locale pour générer des images et vidéos via l'API xAI (Grok). Utilise FastAPI, Jinja2, et Tailwind CSS pour une interface moderne.

## Installation

1. Clonez ou téléchargez les fichiers.
2. Installez les dépendances : `pip install fastapi uvicorn jinja2 requests xai_sdk`.
3. Définissez la variable d'environnement : `export XAI_API_KEY=your_api_key` (ou via un .env).
4. Lancez : `uvicorn main:app --reload`.
5. Ouvrez http://localhost:8000.

## Fonctionnalités

- Génération d'images (1 à 4 par prompt).
- Génération de vidéos (text-to-video ou image-to-video).
- Téléchargement des médias.
- Animation d'images en vidéos.
- Interface sombre inspirée de VSCode.

## Changelog

### [v1.4] - 2023-10-15

- **Ajout de la génération multiple d'images** : Possibilité de sélectionner 1 à 4 images à générer par prompt (limite pour éviter la surcharge API).
- **Support pour génération de vidéos depuis une image uploadée** : Ajout d'un champ file dans l'onglet Vidéo pour uploader une image et générer une vidéo (image-to-video). Si aucune image, reste en mode text-to-video.
- **Amélioration de l'affichage** : Les images multiples s'affichent en grille, chaque avec ses options de téléchargement et d'animation.

### [v1.3] - 2023-10-10

- **Thème sombre VSCode** : Changement complet du style pour un thème sombre (fond noir/gris, texte clair, accents bleus/verts). Inspiré de l'IDE VSCode pour une ambiance développeur.
- **Ajout du nom du créateur** : "François MENGUY" affiché en footer pour créditer l'auteur.
- **Réorganisation des fichiers** : Déplacement du CSS et JS dans des fichiers séparés (`static/styles.css`, `static/script.js`) pour une meilleure maintenabilité.

### [v1.2] - 2023-10-05

- **Système de génération de vidéos** : Ajout de l'onglet "Vidéo" pour générer des vidéos via text-to-video (prompt textuel). Support pour animation image-to-video via le bouton "Animer" sur les images générées.
- **Amélioration de l'interface** : Système d'onglets pour séparer Image et Vidéo. Ajout d'icônes FontAwesome et transitions CSS.
- **Gestion d'erreurs améliorée** : Logs détaillés dans la section "Logs / Statut" pour déboguer les appels API.

### [v1.1] - 2023-10-01

- **Ajout du système de génération d'images** : Intégration de l'API xAI pour générer des images via prompts textuels. Affichage de l'image générée avec options de téléchargement et d'ouverture.
- **Interface utilisateur de base** : Formulaire simple avec textarea pour le prompt, bouton de génération, et affichage des résultats.
- **Support pour téléchargement** : Bouton pour sauvegarder les images/vidéos localement dans un dossier configuré.

### [v1.0] - 2023-09-25

- **Version initiale** : Mise en place de l'app FastAPI avec template Jinja2. Structure de base pour les routes `/generate_image`, `/download`, etc.
- **Configuration de base** : Support pour la clé API xAI, dossier de sauvegarde, et gestion des erreurs simples.

## Contribution

Pour contribuer : Ouvrez une issue ou une PR sur GitHub (si applicable).

## Licence

Propriétaire - Créé par François MENGUY.
