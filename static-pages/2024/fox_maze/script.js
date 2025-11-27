// Detect mobile and show controls
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

if (isMobileDevice()) {
    document.getElementById('mobile-controls').style.display = 'flex';
    document.getElementById('desktop-controls-info').remove();
} else {
    document.getElementById('mobile-controls-info').remove();
}

// Setup touch controls for canvas panning
const canvas = document.getElementById('canvas');
let touchIdentifier = null;
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;
let viewportStartX = 0;
let viewportStartY = 0;

// This will be set by script.js when engine is ready
window.getEngine = null;

canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (e.changedTouches.length > 0 && touchIdentifier === null && window.getEngine) {
        const touch = e.changedTouches[0];
        touchIdentifier = touch.identifier;
        isDragging = true;
        dragStartX = touch.clientX;
        dragStartY = touch.clientY;
        const engine = window.getEngine();
        viewportStartX = engine.winX;
        viewportStartY = engine.winY;
    }
}, { passive: false });

canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    if (isDragging && touchIdentifier !== null && window.getEngine) {
        for (let i = 0; i < e.touches.length; i++) {
            const touch = e.touches[i];
            if (touch.identifier === touchIdentifier) {
                const deltaX = dragStartX - touch.clientX;
                const deltaY = dragStartY - touch.clientY;
                const engine = window.getEngine();
                engine.setWindowPosition(viewportStartX + deltaX, viewportStartY + deltaY);
                break;
            }
        }
    }
}, { passive: false });

const endTouch = (e) => {
    e.preventDefault();
    for (let i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier === touchIdentifier) {
            isDragging = false;
            touchIdentifier = null;
            break;
        }
    }
};

canvas.addEventListener('touchend', endTouch, { passive: false });
canvas.addEventListener('touchcancel', endTouch, { passive: false });

// Setup mobile D-pad buttons
// These hook into the same keyPressed object used by Fox.js
const setupButton = (id, direction) => {
    const btn = document.getElementById(id);
    if (!btn) return;

    const keyChar = direction.toLowerCase(); // 'w','a','s','d'
    const keyCodeName = `Key${keyChar.toUpperCase()}`; // 'KeyW' etc.

    const start = (e) => {
        e.preventDefault();
        const ev = new KeyboardEvent('keydown', {
            key: keyChar,
            code: keyCodeName,
            bubbles: true,
            cancelable: true
        });
        window.dispatchEvent(ev);
    };

    const end = (e) => {
        e.preventDefault();
        const ev = new KeyboardEvent('keyup', {
            key: keyChar,
            code: keyCodeName,
            bubbles: true,
            cancelable: true
        });
        window.dispatchEvent(ev);
    };

    btn.addEventListener('touchstart', start, { passive: false });
    btn.addEventListener('mousedown', start);
    btn.addEventListener('touchend', end, { passive: false });
    btn.addEventListener('touchcancel', end, { passive: false });
    btn.addEventListener('mouseup', end);
    btn.addEventListener('mouseleave', end);
};

setupButton('btn-up', 'w');
setupButton('btn-down', 's');
setupButton('btn-left', 'a');
setupButton('btn-right', 'd');