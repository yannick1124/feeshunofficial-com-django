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
    const streams = document.querySelectorAll('.streamfield-container');

    streams.forEach(stream => {
        stream.addEventListener('input', (e) => {
            if (!e.target.matches('.form-item')) return;

            const entriesDiv = stream.querySelector('.stream-entries');
            const lastItem = entriesDiv.querySelector('.stream-item-wrapper:last-child');
            const lastInput = lastItem.querySelector('input');

            if (e.target === lastInput && lastInput.value.trim() !== '') {
                const newItem = lastItem.cloneNode(true);
                const newInput = newItem.querySelector('input');
                const newBtn = newItem.querySelector('.remove-stream-item');

                newInput.value = '';
                newBtn.style.display = 'none';

                entriesDiv.appendChild(newItem);
            }

            const currentWrapper = e.target.closest('.stream-item-wrapper');
            const currentBtn = currentWrapper.querySelector('.remove-stream-item');

            if (e.target.value.trim() !== '') {
                currentBtn.style.display = 'inline-block';
            }
            else if (currentWrapper !== lastItem) {
                currentBtn.style.display = 'none';
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
});