# Image Studio ✨

Application web moderne de génération d'images et de vidéos propulsée par l'API xAI Grok. Interface élégante en thème sombre avec design responsive mobile-first.

🔗 **[Demo Live](https://image.fmenguy.fr)**

## 📋 Fonctionnalités

- **Génération d'images** : Créez jusqu'à 4 images simultanément à partir d'un prompt textuel
- **Choix du format** : Sélecteur visuel de ratio d'aspect (1:1, 4:3, 3:4, 16:9, 9:16, Auto)
- **Résolution** : Choix entre 1K et 2K
- **Génération de vidéos** : Transformez vos idées en vidéos avec ou sans image de référence
- **Modification d'images** : Raffinez vos créations avec de nouveaux prompts
- **Animation d'images** : Donnez vie à vos images statiques
- **Historique de session** : Retrouvez toutes vos générations (images et vidéos) de la session en cours
- **Téléchargement direct** : Sauvegardez vos créations en un clic
- **Authentification sécurisée** : Protection par mot de passe avec rate limiting anti-bruteforce
- **Interface responsive** : Design adapté à tous les écrans (desktop, tablette, mobile)

## 🛠️ Stack Technique

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderne et performant
- **[Python 3.11+](https://www.python.org/)** - Langage de programmation
- **[Uvicorn](https://www.uvicorn.org/)** - Serveur ASGI haute performance
- **[xAI SDK](https://x.ai/)** - API de génération d'images/vidéos Grok

### Frontend
- **[Jinja2](https://jinja.palletsprojects.com/)** - Moteur de templates
- **HTML5 / CSS3** - Structure et design
- **JavaScript (Vanilla)** - Interactions dynamiques
- **[Font Awesome](https://fontawesome.com/)** - Icônes
- **[Google Fonts (Sora, JetBrains Mono)](https://fonts.google.com/)** - Typographie

### Design
- **Thème sombre** : Design "Cinematic Dark UI"
- **Palette de couleurs** : Noir profond (#08090c) + accents or/ambre (#e8a838)
- **Animations CSS** : Transitions fluides et micro-interactions
- **Mobile-first** : Responsive à partir de 400px

### Sécurité
- Authentification par mot de passe
- Rate limiting (5 tentatives / 5 minutes)
- Protection CSRF via session middleware
- Variables d'environnement pour les secrets
- Upload sécurisé (validation MIME, taille limitée, UUID)

## 📦 Installation

### Prérequis

- Python 3.11 ou supérieur
- Clé API xAI ([obtenir une clé](https://console.x.ai/))
- Git

### Configuration locale

1. **Cloner le repository**
   ```bash
   git clone https://github.com/fmenguy/grok-image-web.git
   cd grok-image-web
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**

   Créer un fichier `.env` à la racine du projet :
   ```env
   XAI_API_KEY=your_xai_api_key_here
   APP_PASSWORD=your_secure_password
   SESSION_SECRET=your_random_secret_key
   SAVE_DIR=./downloads
   ```

5. **Lancer l'application**
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000
   ```

6. **Accéder à l'application**

   Ouvrir http://127.0.0.1:8000 dans votre navigateur

## 🚀 Déploiement sur Render

### Configuration automatique

Le projet inclut un fichier `render.yaml` pour un déploiement automatisé sur [Render](https://render.com).

1. **Créer un compte** sur [Render](https://render.com)

2. **Connecter le repository GitHub**
   - New → Web Service
   - Sélectionner le repository `grok-image-web`
   - Render détecte automatiquement `render.yaml`

3. **Configurer les variables d'environnement**

   Dans le dashboard Render → Environment :
   ```
   XAI_API_KEY=<votre_clé_xai>
   APP_PASSWORD=<votre_mot_de_passe_fort>
   SESSION_SECRET=<clé_secrète_aléatoire>
   ```

4. **Déployer**

   Render build et déploie automatiquement. L'application sera accessible sur :
   ```
   https://votre-app.onrender.com
   ```

### Custom Domain (optionnel)

1. Dans Render → Settings → Custom Domains
2. Ajouter votre domaine (ex: `image.votredomaine.fr`)
3. Configurer un CNAME chez votre registrar DNS :
   ```
   image IN CNAME votre-app.onrender.com
   ```
4. Certificat SSL provisionné automatiquement (Let's Encrypt)

## 🔒 Sécurité

- **Mot de passe fort** : Utilisez un générateur de mots de passe
- **Secrets** : Ne jamais commiter le fichier `.env`
- **Rate limiting** : Protection contre les attaques par force brute
- **HTTPS** : Obligatoire en production (géré par Render)
- **Validation uploads** : MIME types autorisés, taille limitée à 10 Mo

## 📝 Utilisation

### Génération d'images

1. Connectez-vous avec votre mot de passe
2. Onglet **Image**
3. Saisissez un prompt descriptif
4. Choisissez le **format** (ratio d'aspect) via les icônes visuelles (défaut : 9:16)
5. Choisissez la **résolution** (1K ou 2K)
6. Choisissez le **nombre d'images** (1-4, défaut : 4)
7. Cliquez sur **Générer les Images**

> Les générations sont automatiquement ajoutées à l'**historique de session**, visible dans le panneau de droite. L'historique persiste entre les rechargements de page et est effacé à la déconnexion.

### Génération de vidéos

1. Onglet **Vidéo**
2. Saisissez un prompt (ex: "Un océan au coucher du soleil")
3. Optionnel : Uploadez une image de référence
4. Cliquez sur **Générer la Vidéo**

### Modification d'images

1. Sur une image générée, cliquez sur **Modifier**
2. Saisissez un nouveau prompt (ex: "Ajouter des nuages")
3. L'image sera raffinée selon vos instructions

### Animation d'images

1. Sur une image générée, cliquez sur **Animer**
2. Décrivez le mouvement souhaité
3. Une vidéo sera générée à partir de l'image

## 🎨 Design System

### Couleurs
- **Fond principal** : `#08090c` (Noir profond)
- **Surface** : `#0f1115`
- **Carte** : `#1a1e27`
- **Accent** : `#e8a838` (Or/Ambre)
- **Texte** : `#f1f3f7` (Blanc cassé)

### Typographie
- **Display** : Sora (300, 400, 600, 700)
- **Monospace** : JetBrains Mono (logs)

### Animations
- Transitions : `0.2s - 0.25s ease`
- Stagger animations au chargement
- Hover effects avec couleur accent

## 📂 Structure du Projet

```
grok-image-web/
├── main.py                 # Application FastAPI principale
├── auth.py                 # Gestion de l'authentification
├── requirements.txt        # Dépendances Python
├── render.yaml             # Configuration Render
├── .env.example            # Template des variables d'environnement
├── templates/              # Templates Jinja2
│   ├── index.html          # Page principale
│   └── login.html          # Page de connexion
├── static/                 # Assets statiques
│   ├── styles.css          # Styles CSS
│   └── script.js           # JavaScript
└── downloads/              # Fichiers temporaires (ignoré par Git)
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**François MENGUY**

- Site web : [fmenguy.fr](https://fmenguy.fr)
- GitHub : [@fmenguy](https://github.com/fmenguy)

## 📦 Changelog

### v4
- Suppression du ratio "Auto" (non fonctionnel avec l'API)
- Historique masqué par défaut avec bouton "Historique (N)" dépliable
- Bouton "Vider" dans la toolbar de l'historique
- Refonte CSS : bouton toggle avec chevron animé

### v3
- Correction : application du preset "François" aux prompts vidéo (`expanded_prompt` utilisé dans `video.generate()`)

### v2-4
- Intégration du preset "François" dans les endpoints `generate_image` et `generate_video`
- Log "Preset appliqué." affiché quand la substitution est active

### v2-3
- Ajout du preset prompt "François" : le mot-clé est remplacé par une description visuelle du créateur
- Fonction `_expand_prompt()` avec support accent (François/Francois)

### v2-2
- Ajout du mode test (checkbox) : les générations ne sont pas enregistrées dans l'historique
- Endpoint `POST /clear_history` pour vider l'historique de session
- Bouton "Vider l'historique" dans le panneau de droite
- Toggle test sur les formulaires image et vidéo

### v2-1
- Format par défaut changé de 1:1 à 9:16
- Nombre d'images par défaut changé de 1 à 4
- Icônes SVG pour le sélecteur de ratio (rectangles proportionnels)
- Résolution et nombre d'images sur la même ligne (`.form-row`)
- Refonte CSS responsive du sélecteur de format

### v2
- Sélecteur de ratio d'aspect (1:1, 4:3, 3:4, 16:9, 9:16)
- Sélecteur de résolution (1K / 2K)
- Historique de session côté serveur (Starlette session)
- Paramètres `aspect_ratio` et `resolution` transmis à l'API xAI
- Section historique avec thumbnails et métadonnées

### v1
- Interface initiale : génération d'images et vidéos via API xAI Grok
- Modification et animation d'images
- Téléchargement via proxy CORS
- Authentification par mot de passe avec rate limiting
- Thème sombre "Cinematic Dark UI"

## 🙏 Remerciements

- [xAI](https://x.ai/) pour l'API Grok
- [FastAPI](https://fastapi.tiangolo.com/) pour le framework
- [Render](https://render.com/) pour l'hébergement

---

⭐ Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile sur GitHub !
