// Improved tab switching with neutral style for inactive tabs
document.querySelectorAll('.tabs a').forEach(tab => {
    tab.addEventListener('click', e => {
        e.preventDefault();
        document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
        document.querySelectorAll('.tabs a').forEach(t => {
            t.classList.remove('bg-gradient-to-r', 'from-blue-500', 'to-blue-600', 'from-green-500', 'to-green-600', 'text-white');
            t.classList.add('bg-gray-200', 'text-gray-700'); // Neutral style for inactive
        });
        document.querySelector(e.target.getAttribute('href')).classList.remove('hidden');
        e.target.classList.remove('bg-gray-200', 'text-gray-700');
        e.target.classList.add('bg-gradient-to-r', 'text-white', e.target.textContent.includes('Image') ? 'from-blue-500 to-blue-600' : 'from-green-500 to-green-600');
    });
});