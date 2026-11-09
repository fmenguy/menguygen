# MenguyGen

🇫🇷 Français · 🇬🇧 [English](#english)

<a id="francais"></a>

> [!WARNING]
> **Projet arrêté le 9 novembre 2026.** L'application n'est plus en ligne, son service d'hébergement est supprimé et le code n'est plus maintenu. Ce dépôt est archivé : le code reste consultable pour référence, en lecture seule.

MenguyGen était une application web personnelle de génération d'images et de vidéos par l'API xAI (modèles Grok Imagine). On y accédait avec un mot de passe, ou en mode invité avec sa propre clé API xAI.

## Ce que faisait l'application

- **Images** : modèle Standard ou Pro (`grok-imagine-image`, `grok-imagine-image-pro`), 1, 4, 6 ou 8 images par lot, ou génération continue par lots successifs jusqu'à l'arrêt. Une dizaine de formats (de 2:1 à 1:2, 9:16 par défaut), résolution 1K ou 2K, coût estimé affiché après chaque génération.
- **Vidéos** (`grok-imagine-video`) : à partir d'un texte, ou d'une image de référence envoyée (PNG, JPEG ou WebP, 10 Mo au plus), en 480p ou 720p, de 1 à 15 secondes.
- **Retouche et animation** : modifier une image générée avec une nouvelle consigne, ou l'animer en vidéo.
- **Historique** de session dépliable, **mode test** qui n'inscrit rien dans l'historique, **favoris** et réglages conservés dans le navigateur (`localStorage`).
- **Téléchargement** des fichiers par un proxy côté serveur, pour contourner les restrictions CORS.
- **Solde de crédits xAI** affiché dans l'en-tête, pour le compte administrateur uniquement (API de gestion xAI).
- **Connexion** par mot de passe unique, limitée à 5 essais par adresse IP sur 5 minutes.
- **Mode invité** : le visiteur saisit sa propre clé xAI. Elle reste dans son navigateur, part avec chaque requête et n'est jamais stockée sur le serveur.

## La faille du mode invité

Dans une première version du mode invité, un visiteur qui retirait le champ de clé du formulaire (avec les outils de développement du navigateur) faisait retomber l'application sur la clé API du serveur, donc sur le compte du propriétaire. Le commit `c4ffd54` corrige ce repli : `_get_client()` refuse toute requête invité sans clé et renvoie vers `/guest`.

Le récit complet, avec le code vulnérable, l'exploitation et la correction : [Quand le mode invité utilise ta clé API : une faille de fallback](https://fmenguy.fr/blog/mode-invite-cle-api/).

## Stack

- **Serveur** : Python 3.11+, FastAPI, Uvicorn, sessions signées de Starlette, SDK `xai_sdk`, `requests`.
- **Interface** : gabarits Jinja2, HTML et CSS, JavaScript sans framework, Font Awesome, polices Sora et JetBrains Mono (Google Fonts). Thème sombre noir et ambre, décrit dans [STACK.md](STACK.md).
- **Hébergement d'origine** : Render, via [`render.yaml`](render.yaml), conservé à titre d'exemple.

## Lancer en local

Pour qui veut étudier le code. Chaque génération est facturée sur le compte xAI de la clé utilisée, et les modèles et tarifs inscrits dans `main.py` datent de 2026 : ils ont pu changer depuis.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Les variables d'environnement sont lues au démarrage, depuis un fichier `.env` à la racine (chargé par python-dotenv, ignoré par git) :

| Variable | Rôle |
|---|---|
| `XAI_API_KEY` | Obligatoire : sans elle, l'application refuse de démarrer. |
| `APP_PASSWORD` | Mot de passe de connexion. |
| `SESSION_SECRET` | Clé de signature des cookies de session. Une valeur de développement sert par défaut : à remplacer. |
| `SAVE_DIR` | Facultative : dossier créé au démarrage (`./downloads` par défaut). |
| `XAI_MANAGEMENT_KEY`, `XAI_TEAM_ID` | Facultatives : affichage du solde de crédits xAI. |

## Avant de réutiliser ce code

Le code est figé dans son dernier état, sans revue pour une remise en ligne. Trois points au moins seraient à reprendre :

- le proxy `/download` va chercher n'importe quelle URL qu'on lui donne, y compris pour une session invité : il faudrait le limiter aux domaines de xAI ;
- les tentatives de connexion sont comptées en mémoire : le compteur se perd au redémarrage et n'est pas partagé entre les processus (`render.yaml` en lance deux) ;
- le mot de passe est comparé avec `==` plutôt qu'avec une comparaison à temps constant.

## Contenu du dépôt

```
main.py              application FastAPI et routes
auth.py              mot de passe et limitation des essais
templates/           pages principale, de connexion et du mode invité
static/              styles et JavaScript
render.yaml          déploiement Render d'origine
CHANGELOG.md         historique des versions
STACK.md             stack et charte graphique
```

## Auteur

François Menguy, [fmenguy.fr](https://fmenguy.fr), [@fmenguy](https://github.com/fmenguy)

---

<a id="english"></a>

🇬🇧 English · 🇫🇷 [Français](#francais)

> [!WARNING]
> **Project shut down on 9 November 2026.** The app is no longer online, its hosting service has been deleted and the code is no longer maintained. This repository is archived: the code stays available as read-only reference.

MenguyGen was a personal web app for generating images and videos through the xAI API (Grok Imagine models). Access was password protected, with a guest mode for visitors bringing their own xAI API key.

## What the app did

- **Images**: Standard or Pro model (`grok-imagine-image`, `grok-imagine-image-pro`), batches of 1, 4, 6 or 8 images, or continuous generation in successive batches until stopped. About ten aspect ratios (from 2:1 to 1:2, 9:16 by default), 1K or 2K resolution, estimated cost shown after each run.
- **Videos** (`grok-imagine-video`): from a text prompt or an uploaded reference image (PNG, JPEG or WebP, up to 10 MB), at 480p or 720p, 1 to 15 seconds long.
- **Refine and animate**: edit a generated image with a new prompt, or turn it into a video.
- **Session history** in a collapsible panel, a **test mode** that keeps runs out of the history, and **favorites** and settings saved in the browser (`localStorage`).
- **Downloads** through a server side proxy, to get around CORS restrictions.
- **xAI credit balance** in the header, for the admin account only (xAI Management API).
- **Login** with a single password, limited to 5 attempts per IP address over 5 minutes.
- **Guest mode**: visitors enter their own xAI key. It stays in their browser, is sent with each request and is never stored on the server.

## The guest mode flaw

In an early version of guest mode, a visitor who removed the key field from the form (with the browser's developer tools) made the app fall back to the server's API key, and therefore to the owner's account. Commit `c4ffd54` fixes that fallback: `_get_client()` now rejects any guest request without a key and redirects to `/guest`.

The full story, with the vulnerable code, the exploit and the fix, is on my blog (in French): [Quand le mode invité utilise ta clé API : une faille de fallback](https://fmenguy.fr/blog/mode-invite-cle-api/).

## Stack

- **Server**: Python 3.11+, FastAPI, Uvicorn, Starlette signed sessions, the `xai_sdk` SDK, `requests`.
- **Frontend**: Jinja2 templates, HTML and CSS, plain JavaScript, Font Awesome, Sora and JetBrains Mono fonts (Google Fonts). Dark black and amber theme, described in [STACK.md](STACK.md) (in French).
- **Original hosting**: Render, through [`render.yaml`](render.yaml), kept as an example.

## Running it locally

For anyone who wants to study the code. Every generation is billed to the xAI account that owns the key, and the models and prices hardcoded in `main.py` date from 2026: they may have changed since.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Environment variables are read at startup, from a `.env` file at the repository root (loaded by python-dotenv, ignored by git):

| Variable | Purpose |
|---|---|
| `XAI_API_KEY` | Required: the app refuses to start without it. |
| `APP_PASSWORD` | Login password. |
| `SESSION_SECRET` | Signing key for session cookies. Falls back to a development value: replace it. |
| `SAVE_DIR` | Optional: folder created at startup (`./downloads` by default). |
| `XAI_MANAGEMENT_KEY`, `XAI_TEAM_ID` | Optional: show the xAI credit balance. |

## Before reusing this code

The code is frozen in its last state and was not reviewed for going back online. At least three things would need work:

- the `/download` proxy fetches any URL it is given, guest sessions included: it should be restricted to xAI domains;
- login attempts are counted in memory, so the counter resets on restart and is not shared between processes (`render.yaml` starts two);
- the password is checked with `==` instead of a constant time comparison.

## Repository layout

```
main.py              FastAPI app and routes
auth.py              password check and attempt limiting
templates/           main, login and guest pages
static/              styles and JavaScript
render.yaml          original Render deployment
CHANGELOG.md         version history (in French)
STACK.md             stack and design system (in French)
```

## Author

François Menguy, [fmenguy.fr](https://fmenguy.fr), [@fmenguy](https://github.com/fmenguy)
