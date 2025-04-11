// Functions specific to the paper page
document.addEventListener('DOMContentLoaded', () => {
    // Auto-resize textareas as you type
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
    
    // Save button functionality
    const saveBtn = document.querySelector('button.bg-blue-600');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            showToast('Paper saved successfully!', 'success');
        });
    }
    
    // Top bar button click handlers
    const menuButtons = document.querySelectorAll('.glass-card .bg-gray-200');
    menuButtons.forEach(button => {
        button.addEventListener('click', function() {
            const menuType = this.textContent.trim();
            showToast(`${menuType} menu clicked`, 'info');
        });
    });
});