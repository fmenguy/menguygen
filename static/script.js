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

// Téléchargement via proxy serveur (contourne les CORS)
function downloadMedia(url) {
    const downloadUrl = `/download?url=${encodeURIComponent(url)}`;
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = '';  // Le serveur définit le nom via Content-Disposition
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
