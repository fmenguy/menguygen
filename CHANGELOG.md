# Changelog

## Arrêt du projet (9 novembre 2026)
- Application retirée : le site n'est plus en ligne et le service d'hébergement est supprimé
- Plus de maintenance : le dépôt est archivé, le code reste consultable pour référence
- `Readme.md` renommé en `README.md` et réécrit en français et en anglais

## v6
- Renommage "Image Studio" → **MenguyGen**
- Mode invité : les visiteurs peuvent utiliser l'app avec leur propre clé API xAI
  - Nouvelle page `/guest` pour saisir la clé
  - Clé stockée dans `localStorage` (jamais côté serveur)
  - Badge "Invité" dans le header, déconnexion supprime la clé
  - Client xAI créé à la volée par requête pour les invités
- Lien vers [AI Prompt](https://aiprompt.fmenguy.fr/) dans le footer
- Refactoring : `_tpl_ctx()` helper pour les contextes template

## v5
- Logo cliquable : retour à l'accueil en cliquant sur "MenguyGen"

## v4
- Suppression du ratio "Auto" (non fonctionnel avec l'API)
- Historique masqué par défaut avec bouton "Historique (N)" dépliable
- Bouton "Vider" dans la toolbar de l'historique
- Refonte CSS : bouton toggle avec chevron animé

## v3
- Correction : application du preset "François" aux prompts vidéo (`expanded_prompt` utilisé dans `video.generate()`)

## v2-4
- Intégration du preset "François" dans les endpoints `generate_image` et `generate_video`
- Log "Preset appliqué." affiché quand la substitution est active

## v2-3
- Ajout du preset prompt "François" : le mot-clé est remplacé par une description visuelle du créateur
- Fonction `_expand_prompt()` avec support accent (François/Francois)

## v2-2
- Ajout du mode test (checkbox) : les générations ne sont pas enregistrées dans l'historique
- Endpoint `POST /clear_history` pour vider l'historique de session
- Bouton "Vider l'historique" dans le panneau de droite
- Toggle test sur les formulaires image et vidéo

## v2-1
- Format par défaut changé de 1:1 à 9:16
- Nombre d'images par défaut changé de 1 à 4
- Icônes SVG pour le sélecteur de ratio (rectangles proportionnels)
- Résolution et nombre d'images sur la même ligne (`.form-row`)
- Refonte CSS responsive du sélecteur de format

## v2
- Sélecteur de ratio d'aspect (1:1, 4:3, 3:4, 16:9, 9:16)
- Sélecteur de résolution (1K / 2K)
- Historique de session côté serveur (Starlette session)
- Paramètres `aspect_ratio` et `resolution` transmis à l'API xAI
- Section historique avec thumbnails et métadonnées

## v1
- Interface initiale : génération d'images et vidéos via API xAI Grok
- Modification et animation d'images
- Téléchargement via proxy CORS
- Authentification par mot de passe avec rate limiting
- Thème sombre "Cinematic Dark UI"
