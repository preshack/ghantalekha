/**
 * WorkClock Dark Mode Toggle
 * Persists user preference in localStorage
 */
(function () {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;

    function applyDarkMode(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        localStorage.setItem('darkMode', isDark ? 'true' : 'false');
    }

    // Initialize from localStorage (already done inline in <head>, but wire up toggle)
    toggle.addEventListener('click', function () {
        const isDark = document.documentElement.classList.contains('dark');
        applyDarkMode(!isDark);
    });
})();
