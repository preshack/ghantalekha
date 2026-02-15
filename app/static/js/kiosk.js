/**
 * WorkClock Kiosk — Numeric Keypad Logic
 * Handles PIN input, auto-submit, live clock, and GPS capture
 */
(function () {
    let pin = '';
    const MAX_PIN_LENGTH = 4;
    let submitting = false;

    // ---- Live Clock ----
    function updateClock() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
        const dateStr = now.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const clockEl = document.getElementById('liveClock');
        const dateEl = document.getElementById('liveDate');
        if (clockEl) clockEl.textContent = timeStr;
        if (dateEl) dateEl.textContent = dateStr;
    }

    updateClock();
    setInterval(updateClock, 1000);

    // ---- PIN Dots ----
    function updateDots() {
        for (let i = 0; i < MAX_PIN_LENGTH; i++) {
            const dot = document.getElementById('dot' + i);
            if (!dot) continue;
            if (i < pin.length) {
                dot.classList.add('pin-dot-filled');
            } else {
                dot.classList.remove('pin-dot-filled');
            }
        }
    }

    // ---- GPS (optional) ----
    function captureGPS() {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                function (pos) {
                    const latInput = document.getElementById('gpsLat');
                    const lngInput = document.getElementById('gpsLng');
                    if (latInput) latInput.value = pos.coords.latitude;
                    if (lngInput) lngInput.value = pos.coords.longitude;
                },
                function () {
                    // GPS denied or unavailable — silently ignore
                },
                { timeout: 5000, maximumAge: 60000 }
            );
        }
    }

    // Try to get GPS on page load
    captureGPS();

    // ---- Keypad Actions ----
    window.addDigit = function (digit) {
        if (submitting || pin.length >= MAX_PIN_LENGTH) return;

        pin += digit;
        updateDots();

        // Auto-submit when 4 digits entered
        if (pin.length === MAX_PIN_LENGTH) {
            submitPin();
        }
    };

    window.backspace = function () {
        if (submitting) return;
        pin = pin.slice(0, -1);
        updateDots();
    };

    window.clearPin = function () {
        if (submitting) return;
        pin = '';
        updateDots();
    };

    function submitPin() {
        submitting = true;

        const pinInput = document.getElementById('pinInput');
        const form = document.getElementById('pinForm');
        const loading = document.getElementById('loadingIndicator');

        if (pinInput) pinInput.value = pin;
        if (loading) loading.classList.remove('hidden');

        // Small delay for visual feedback
        setTimeout(function () {
            if (form) form.submit();
        }, 300);
    }

    // ---- Keyboard Support ----
    document.addEventListener('keydown', function (e) {
        if (submitting) return;

        if (e.key >= '0' && e.key <= '9') {
            e.preventDefault();
            window.addDigit(e.key);
        } else if (e.key === 'Backspace') {
            e.preventDefault();
            window.backspace();
        } else if (e.key === 'Escape' || e.key === 'Delete') {
            e.preventDefault();
            window.clearPin();
        }
    });
})();
