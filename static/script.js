// Tab switching avec data-attributes
document.querySelectorAll('.tab-link').forEach(tab => {
    tab.addEventListener('click', e => {
        e.preventDefault();
        const targetId = tab.getAttribute('href');

        // Masquer tous les contenus
        document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));

        // Désactiver tous les onglets
        document.querySelectorAll('.tab-link').forEach(t => {
            t.classList.remove('active');
        });

        // Afficher le contenu cible
        document.querySelector(targetId).classList.remove('hidden');

        // Activer l'onglet cliqué
        tab.classList.add('active');
    });
});

// Téléchargement côté navigateur (pas de POST serveur)
async function downloadMedia(url, filename) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename || 'image_studio_' + Date.now() + (url.includes('.mp4') ? '.mp4' : '.png');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(blobUrl);
    } catch (err) {
        alert('Erreur lors du téléchargement : ' + err.message);
    }
}
