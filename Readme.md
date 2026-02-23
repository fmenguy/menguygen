# MenguyGen

Mon app perso de génération d'images et vidéos via l'API xAI Grok. Interface dark UI avec thème cinématique or/ambre.

**[image.fmenguy.fr](https://image.fmenguy.fr)**

## Ce que ça fait

- Génération d'images (jusqu'à 4 en parallèle) avec choix du ratio (1:1, 4:3, 3:4, 16:9, 9:16) et résolution (1K/2K)
- Génération de vidéos avec ou sans image de référence
- Modification et animation d'images existantes
- Preset "François" : le mot-clé injecte automatiquement ma description visuelle dans le prompt
- Historique de session (dépliable, avec mode test pour ne pas polluer)
- Téléchargement direct via proxy CORS
- Auth par mot de passe + rate limiting anti-bruteforce

## Lancer en local

```bash
python -m venv .venv && source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

Créer un `.env` :
```env
XAI_API_KEY=...
APP_PASSWORD=...
SESSION_SECRET=...
SAVE_DIR=./downloads
```

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

## Déployer sur Render

Le `render.yaml` est inclus. Connecter le repo GitHub sur [Render](https://render.com), ajouter les variables d'environnement (`XAI_API_KEY`, `APP_PASSWORD`, `SESSION_SECRET`), et c'est parti.

Pour un domaine custom : ajouter un CNAME vers `votre-app.onrender.com`, SSL auto via Let's Encrypt.

## Structure

```
main.py              # App FastAPI + endpoints
auth.py              # Authentification + rate limiting
templates/
  index.html         # Page principale
  login.html         # Page de connexion
static/
  styles.css         # Styles (dark theme)
  script.js          # JS (tabs, download)
```

## Docs complémentaires

- [CHANGELOG.md](CHANGELOG.md) - Historique des versions
- [STACK.md](STACK.md) - Stack technique et design system

## Auteurs

**François MENGUY** - [fmenguy.fr](https://fmenguy.fr) | [@fmenguy](https://github.com/fmenguy)

**Claude** (Opus 4.6, Anthropic) - Co-développeur IA, architecture features v2+, refonte UI, et ce README.
