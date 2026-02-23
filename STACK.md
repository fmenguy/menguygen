# Stack Technique

## Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderne et performant
- **[Python 3.11+](https://www.python.org/)**
- **[Uvicorn](https://www.uvicorn.org/)** - Serveur ASGI haute performance
- **[xAI SDK](https://x.ai/)** - API de génération d'images/vidéos Grok

## Frontend
- **[Jinja2](https://jinja.palletsprojects.com/)** - Moteur de templates
- **HTML5 / CSS3** - Structure et design
- **JavaScript (Vanilla)** - Interactions dynamiques
- **[Font Awesome](https://fontawesome.com/)** - Icônes
- **[Google Fonts (Sora, JetBrains Mono)](https://fonts.google.com/)** - Typographie

## Design
- **Thème sombre** : Design "Cinematic Dark UI"
- **Palette de couleurs** : Noir profond (#08090c) + accents or/ambre (#e8a838)
- **Animations CSS** : Transitions fluides et micro-interactions
- **Mobile-first** : Responsive à partir de 400px

| Token          | Valeur    |
|----------------|-----------|
| Fond principal | `#08090c` |
| Surface        | `#0f1115` |
| Carte          | `#1a1e27` |
| Accent         | `#e8a838` |
| Texte          | `#f1f3f7` |

**Typographie** : Sora (display) / JetBrains Mono (logs)
**Transitions** : 0.2s - 0.25s ease, stagger animations, hover avec couleur accent

## Sécurité
- Authentification par mot de passe
- Rate limiting (5 tentatives / 5 minutes)
- Protection CSRF via session middleware
- Variables d'environnement pour les secrets
- Upload sécurisé (validation MIME, taille limitée, UUID)

## Hébergement
- **[Render](https://render.com/)** avec `render.yaml` pour le déploiement automatisé
- Certificat SSL automatique (Let's Encrypt)
