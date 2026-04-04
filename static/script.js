// ═══ Tab switching ═══
document.querySelectorAll('.tab-link').forEach(tab => {
    tab.addEventListener('click', e => {
        e.preventDefault();
        const targetId = tab.getAttribute('href');
        document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
        document.querySelectorAll('.tab-link').forEach(t => t.classList.remove('active'));
        document.querySelector(targetId).classList.remove('hidden');
        tab.classList.add('active');
    });
});

// ═══ Download helper ═══
function downloadMedia(url) {
    const a = document.createElement('a');
    a.href = `/download?url=${encodeURIComponent(url)}`;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// ═══ Cost estimator ═══
function updateCostEstimate() {
    const model = document.querySelector('input[name="model_quality"]:checked');
    const num = document.querySelector('input[name="num_images"]:checked');
    if (!model || !num) return;
    const price = model.value === 'pro' ? 0.07 : 0.02;
    const el = document.getElementById('cost-text');
    if (num.value === 'infinite') {
        el.textContent = `Coût par batch : ~${(price * 4).toFixed(2)}$ (4 images/batch)`;
    } else {
        const count = parseInt(num.value) || 4;
        const total = (price * count).toFixed(2);
        el.textContent = `Coût estimé : ~${total}$`;
    }
}

document.querySelectorAll('input[name="model_quality"], input[name="num_images"]').forEach(input => {
    input.addEventListener('change', updateCostEstimate);
});
updateCostEstimate();

// ═══ Results tabs (Résultats / Favoris) ═══
function switchResultsTab(tab) {
    document.querySelectorAll('.results-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.results-tab[data-results-tab="${tab}"]`).classList.add('active');
    document.getElementById('tab-generated').classList.toggle('hidden', tab !== 'generated');
    document.getElementById('tab-favorites').classList.toggle('hidden', tab !== 'favorites');
    if (tab === 'favorites') renderFavorites();
}

// ═══ Favorites system (localStorage) ═══
const FAV_KEY = 'menguygen_favorites';

function getFavorites() {
    try {
        return JSON.parse(localStorage.getItem(FAV_KEY) || '[]');
    } catch { return []; }
}

function saveFavorites(favs) {
    localStorage.setItem(FAV_KEY, JSON.stringify(favs));
    updateFavCount();
}

function isFavorite(url) {
    return getFavorites().some(f => f.url === url);
}

function toggleFavorite(btn, url) {
    let favs = getFavorites();
    const idx = favs.findIndex(f => f.url === url);
    if (idx >= 0) {
        favs.splice(idx, 1);
        btn.classList.remove('is-fav');
        btn.querySelector('i').className = 'far fa-heart';
    } else {
        favs.unshift({ url, timestamp: new Date().toISOString() });
        btn.classList.add('is-fav');
        btn.querySelector('i').className = 'fas fa-heart';
    }
    saveFavorites(favs);
}

function removeFavorite(url) {
    let favs = getFavorites().filter(f => f.url !== url);
    saveFavorites(favs);
    renderFavorites();
    document.querySelectorAll('.btn-fav').forEach(btn => {
        const card = btn.closest('.image-card');
        if (card && card.dataset.url === url) {
            btn.classList.remove('is-fav');
            btn.querySelector('i').className = 'far fa-heart';
        }
    });
}

function updateFavCount() {
    const count = getFavorites().length;
    const el = document.getElementById('fav-count');
    if (el) {
        el.textContent = count > 0 ? count : '';
        el.classList.toggle('hidden', count === 0);
    }
}

function renderFavorites() {
    const grid = document.getElementById('favorites-grid');
    const empty = document.getElementById('favorites-empty');
    const favs = getFavorites();

    if (favs.length === 0) {
        grid.innerHTML = '';
        empty.classList.remove('hidden');
        return;
    }

    empty.classList.add('hidden');
    grid.innerHTML = favs.map(fav => `
        <div class="image-card fav-card" data-url="${fav.url}">
            <div class="image-card-wrapper">
                <img src="${fav.url}" alt="Favori" loading="lazy">
                <button type="button" class="btn-fav is-fav" onclick="removeFavorite('${fav.url}')" title="Retirer des favoris">
                    <i class="fas fa-heart"></i>
                </button>
            </div>
            <div class="image-actions">
                <div class="image-actions-row">
                    <a href="${fav.url}" target="_blank" class="image-link">
                        <i class="fas fa-external-link-alt"></i>
                    </a>
                    <button type="button" class="btn-icon" onclick="downloadMedia('${fav.url}')" title="Télécharger">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// ═══ Mark already-favorite images on page load ═══
function markExistingFavorites() {
    document.querySelectorAll('.image-card[data-url]').forEach(card => {
        if (isFavorite(card.dataset.url)) {
            const btn = card.querySelector('.btn-fav');
            if (btn) {
                btn.classList.add('is-fav');
                btn.querySelector('i').className = 'fas fa-heart';
            }
        }
    });
}

// ═══ Auto-generation system ═══
let lastPrompt = '';
let isGenerating = false;
let autoGenActive = false;
let autoGenStopped = false; // user clicked stop

function isInfiniteMode() {
    const num = document.querySelector('input[name="num_images"]:checked');
    return num && num.value === 'infinite';
}

function getBatchSize() {
    const num = document.querySelector('input[name="num_images"]:checked');
    if (!num || num.value === 'infinite') return 4; // default batch size for infinite
    return parseInt(num.value) || 4;
}

function getFormParams() {
    const form = document.querySelector('#image-tab form');
    const prompt = form.querySelector('textarea[name="prompt"]').value.trim();
    const ar = form.querySelector('input[name="aspect_ratio"]:checked')?.value || '9:16';
    const res = form.querySelector('input[name="resolution"]:checked')?.value || '1k';
    const model = form.querySelector('input[name="model_quality"]:checked')?.value || 'standard';
    const test = form.querySelector('input[name="test_mode"]')?.checked || false;
    return { prompt, aspect_ratio: ar, resolution: res, model_quality: model, num_images: getBatchSize(), test_mode: test };
}

function showAutoGenControls() {
    const el = document.getElementById('auto-gen-controls');
    if (el && lastPrompt) el.classList.remove('hidden');
}

function updateAutoGenButton() {
    const btn = document.getElementById('btn-auto-gen');
    const btnOnce = document.getElementById('btn-load-once');
    if (!btn) return;
    if (autoGenActive) {
        btn.innerHTML = '<i class="fas fa-stop"></i> <span>Stopper</span>';
        btn.classList.add('is-active');
        if (btnOnce) btnOnce.classList.add('hidden');
    } else {
        btn.innerHTML = '<i class="fas fa-play"></i> <span>Lancer la génération auto</span>';
        btn.classList.remove('is-active');
        if (btnOnce) btnOnce.classList.remove('hidden');
    }
}

function toggleAutoGen() {
    if (autoGenActive) {
        // Stop
        autoGenActive = false;
        autoGenStopped = true;
        updateAutoGenButton();
        appendLog('Génération auto stoppée.');
    } else {
        // Start
        autoGenActive = true;
        autoGenStopped = false;
        updateAutoGenButton();
        appendLog('Génération auto lancée...');
        if (!isGenerating) {
            loadMoreImages();
        }
    }
}

function createImageCard(url) {
    const card = document.createElement('div');
    card.className = 'image-card fade-in';
    card.dataset.url = url;
    const favClass = isFavorite(url) ? 'is-fav' : '';
    const heartIcon = isFavorite(url) ? 'fas fa-heart' : 'far fa-heart';
    card.innerHTML = `
        <div class="image-card-wrapper">
            <img src="${url}" alt="Image générée" loading="lazy">
            <button type="button" class="btn-fav ${favClass}" onclick="toggleFavorite(this, '${url}')" title="Ajouter aux favoris">
                <i class="${heartIcon}"></i>
            </button>
        </div>
        <div class="image-actions">
            <div class="image-actions-row">
                <a href="${url}" target="_blank" class="image-link"><i class="fas fa-external-link-alt"></i></a>
                <button type="button" class="btn-icon" onclick="downloadMedia('${url}')" title="Télécharger"><i class="fas fa-download"></i></button>
            </div>
        </div>
    `;
    return card;
}

function appendLog(msg) {
    const logEl = document.getElementById('log');
    if (logEl) logEl.textContent += msg + '\n';
}

async function loadMoreImages() {
    if (isGenerating || !lastPrompt) return;
    isGenerating = true;

    const loader = document.getElementById('scroll-loader');
    loader.classList.remove('hidden');

    const params = getFormParams();
    params.prompt = lastPrompt;

    // Guest API key
    const guestKey = localStorage.getItem('xai_guest_key');
    if (guestKey) params.api_key = guestKey;

    try {
        const resp = await fetch('/api/generate_images', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        const data = await resp.json();
        if (data.urls && data.urls.length > 0) {
            const grid = document.getElementById('image-results-grid');
            const emptyState = document.getElementById('empty-state');
            if (emptyState) emptyState.remove();

            data.urls.forEach(url => {
                grid.appendChild(createImageCard(url));
            });

            appendLog(`+${data.urls.length} image(s) générées.`);
            if (data.errors && data.errors.length > 0) {
                appendLog(data.errors.join('\n'));
            }
        } else if (data.errors && data.errors.length > 0) {
            appendLog('Erreurs : ' + data.errors.join(', '));
        }
    } catch (err) {
        appendLog(`Erreur : ${err.message}`);
        autoGenActive = false;
        updateAutoGenButton();
    }

    loader.classList.add('hidden');
    isGenerating = false;

    // Continue auto-gen if active and not stopped
    if (autoGenActive && !autoGenStopped) {
        // Small delay to avoid hammering the API
        setTimeout(() => {
            if (autoGenActive && !autoGenStopped) {
                loadMoreImages();
            }
        }, 500);
    }
}

// ═══ Intercept form submit to enable auto-gen controls ═══
function setupFormIntercept() {
    const form = document.querySelector('#image-tab form');
    if (!form) return;

    form.addEventListener('submit', () => {
        const params = getFormParams();
        lastPrompt = params.prompt;
        // Reset auto-gen state
        autoGenActive = false;
        autoGenStopped = false;
        updateAutoGenButton();
    });
}

// ═══ Init ═══
document.addEventListener('DOMContentLoaded', () => {
    updateFavCount();
    markExistingFavorites();
    setupFormIntercept();

    // If images were rendered server-side, show auto-gen controls
    const grid = document.getElementById('image-results-grid');
    if (grid && grid.children.length > 0) {
        const textarea = document.querySelector('#image-tab textarea[name="prompt"]');
        if (textarea && textarea.value.trim()) {
            lastPrompt = textarea.value.trim();
            showAutoGenControls();
        }
    }
});
