document.addEventListener('DOMContentLoaded', () => {
    const mappingElement = document.getElementById('email-mapping-data');
    if (!mappingElement) return;

    const emailMapping = JSON.parse(mappingElement.textContent);
    const urlParams = new URLSearchParams(window.location.search);
    const categoryParam = urlParams.get('category');

    let targetMatch = emailMapping.find(item => item.parameter === categoryParam);

    if (!targetMatch) {
        targetMatch = emailMapping.find(item => item.default === true);
    }
})