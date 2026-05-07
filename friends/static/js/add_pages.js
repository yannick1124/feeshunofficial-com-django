const selector = document.getElementById('theme-selector');
const exampleImg = document.getElementById('theme-example');

////////////
// THEMES //
////////////

function updateImage() {
    if (!selector || !exampleImg) return;
    
    const selectedOption = selector.options[selector.selectedIndex];
    
    const imagePath = selectedOption.getAttribute('data-example');
    
    if (imagePath) {
        exampleImg.src = imagePath;
    }
}

if (selector) {
    selector.addEventListener('change', updateImage);

    updateImage();
}

/////////////
// CONTENT //
/////////////

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form.content-extension');
    const streams = document.querySelectorAll('.streamfield-container');

    streams.forEach(stream => {
        stream.addEventListener('input', (e) => {
            if (!e.target.matches('.stream-input')) return;

            const entriesDiv = stream.querySelector('.stream-entries');
            const lastItem = entriesDiv.querySelector('.stream-item-wrapper:last-child');
            const lastInput = lastItem.querySelector('input');

            if (e.target === lastInput && lastInput.value.trim() !== '') {
                const newItem = lastItem.cloneNode(true);
                const newInput = newItem.querySelector('input');
                const newBtn = newItem.querySelector('.remove-stream-item');

                newInput.value = '';
                newBtn.style.visibility = 'hidden';

                entriesDiv.appendChild(newItem);
            }

            const currentWrapper = e.target.closest('.stream-item-wrapper');
            const currentBtn = currentWrapper.querySelector('.remove-stream-item');

            if (e.target.value.trim() !== '') {
                currentBtn.style.visibility = 'visible';
            }
            else if (currentWrapper !== lastItem) {
                currentBtn.style.visibility = 'hidden';
            }
        });

        stream.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.remove-stream-item');

            if (removeBtn) {
                const wrapper = e.target.closest('.stream-item-wrapper');
                const entriesDiv = stream.querySelector('.stream-entries');
                
                if (entriesDiv.querySelectorAll('.stream-item-wrapper').length > 1) {
                    wrapper.remove();
                }
            }
        });
    });

    form.addEventListener('submit', (e) => {
        streams.forEach(stream => {
            const fieldName = stream.id.replace('container-', '');
            const inputs = stream.querySelectorAll('.stream-input');

            const data = Array.from(inputs)
                .map(i => i.value.trim())
                .filter(v => v !== '')
                .map(v => ({ type: 'item', value: v }));
            
            const hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = fieldName;
            hidden.value = JSON.stringify(data);
            form.appendChild(hidden);

            inputs.forEach(i => i.disabled = true);
        });
    });
});