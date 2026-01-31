
# Grok Image & Video Generator (Local)

Une application web locale pour générer des images et vidéos via l'API xAI (Grok). Utilise FastAPI, Jinja2, et Tailwind CSS pour une interface moderne en thème sombre VSCode-like.

## Installation

1. Clonez ou téléchargez les fichiers.
2. Installez les dépendances : `pip install fastapi uvicorn jinja2 requests xai_sdk python-multipart`.
3. Définissez la variable d'environnement : `export XAI_API_KEY=your_api_key` (ou via un .env).
4. Lancez : `uvicorn main:app --reload`.
5. Ouvrez http://localhost:8000.

## Fonctionnalités

- Génération d'images multiples (1 à 4 par prompt) avec boutons radio.
- Génération de vidéos (text-to-video ou depuis une image uploadée).
- Animation d'images en vidéos.
- Téléchargements automatiques des médias.
- Interface sombre inspirée de VSCode avec onglets.
- Créé par François MENGUY.

## Structure du projet

```
grok-image-web/
├── main.py                 # Serveur FastAPI principal
├── templates/
│   └── index.html          # Template HTML de l'interface
├── static/
│   ├── styles.css          # Styles CSS personnalisés (thème sombre)
│   ├── script.js           # JavaScript pour les onglets
│   └── manifest.json       # Manifest pour PWA (optionnel)
├── README.md               # Ce fichier
└── .gitignore              # Fichiers à ignorer pour Git
```

## Utilisation

- **Images** : Choisis le nombre (1-4), entre un prompt, génère.
- **Vidéos** : Entre un prompt ou upload une image, génère.
- **Animation** : Après une image, utilise le bouton pour animer.
- Télécharge les résultats via les boutons.

## Changelog

### [v1.4] - 2023-10-15

- Ajout génération multiple d'images (1-4) avec boutons radio.
- Support upload d'image pour génération de vidéos (image-to-video).

### [v1.3] - 2023-10-10

- Thème sombre VSCode-like.
- Nom du créateur ajouté.

### [v1.2] - 2023-10-05

- Système de génération de vidéos.
- Interface avec onglets.

### [v1.1] - 2023-10-01

- Génération d'images de base.
- Téléchargements.

### [v1.0] - 2023-09-25

- Version initiale avec FastAPI.

## Contribution

Ouvrez une issue ou PR sur GitHub.

## Licence

Propriétaire - Créé par François MENGUY.

```

### `.gitignore` (mis à jour, identique à avant mais confirmé)
```

# Byte-compiled / optimized / DLL files

__pycache__/
*.py[cod]
*$py.class

# C extensions

*.so

# Distribution / packaging

.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller

*.manifest
*.spec

# Installer logs

pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports

htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations

*.mo
*.pot

# Django stuff:

*.log
local_settings.py
db.sqlite3

# Flask stuff:

instance/
.webassets-cache

# Scrapy stuff:

.scrapy

# Sphinx documentation

docs/_build/

# PyBuilder

target/

# Jupyter Notebook

.ipynb_checkpoints

# IPython

profile_default/
ipython_config.py

# pyenv

.python-version

# celery beat schedule file

celerybeat-schedule

# SageMath parsed files

*.sage.py

# Environments

.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings

.spyderproject
.spyproject

# Rope project settings

.ropeproject

# mkdocs documentation

/site

# mypy

.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker

.pyre/

# IDEs

.vscode/
.idea/
*.swp
*.swo
*~

# OS

.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs

*.log
logs/

# Temp files

*.tmp
*.temp

# Project specific

*.exe
build/
dist/
