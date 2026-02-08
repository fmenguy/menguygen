import os
import time
from collections import defaultdict

# Mot de passe défini en variable d'environnement
APP_PASSWORD = os.getenv("APP_PASSWORD", "")

# Rate limiting : max 5 tentatives par IP, blocage 5 minutes
MAX_ATTEMPTS = 5
BLOCK_DURATION = 300  # secondes

_failed_attempts: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(client_ip: str) -> bool:
    """Retourne True si l'IP est bloquée."""
    now = time.time()
    # Nettoyer les tentatives expirées
    _failed_attempts[client_ip] = [
        t for t in _failed_attempts[client_ip]
        if now - t < BLOCK_DURATION
    ]
    return len(_failed_attempts[client_ip]) >= MAX_ATTEMPTS


def record_failed_attempt(client_ip: str):
    """Enregistre une tentative échouée."""
    _failed_attempts[client_ip].append(time.time())


def clear_attempts(client_ip: str):
    """Réinitialise les tentatives après un login réussi."""
    _failed_attempts.pop(client_ip, None)
