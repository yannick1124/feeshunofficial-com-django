function applyAccessibilityMode() {
    const isEasyRead = localStorage.getItem('accessibilityMode') == 'true';
    if (isEasyRead) {
        document.body.classList.add('accessibility-mode');
    }
    else {
        document.body.classList.remove('accessibility-mode');
    }
}

function toggleAccessibility() {
    const isNowActive = document.body.classList.toggle('accessibility-mode');
    localStorage.setItem('accessibilityMode', isNowActive);
}

document.addEventListener('DOMContentLoaded', applyAccessibilityMode);