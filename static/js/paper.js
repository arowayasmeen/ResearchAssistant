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
    const saveBtn = document.getElementById('save-paper-full-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            showToast('Paper saved successfully!', 'success');
        });
    }
    
    // Document editor and hidden fields
    const documentEditor = document.getElementById('document-editor');
    const hiddenEditorContent = document.getElementById('hidden-editor-content');
    const hiddenPdfContent = document.getElementById('hidden-pdf-content');
    
    // Fix for the export button
    const exportForm = document.getElementById('export-form');
    
    // Export to Word functionality
    exportForm.addEventListener('submit', function(e) {
        // Update the hidden field with current document content
        hiddenEditorContent.value = documentEditor.innerHTML;
    });
    
    // Setup dropdown export options
    const exportOptions = document.querySelectorAll('.dropdown-item');
    exportOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            if (this.textContent.includes('PDF')) {
                // Choose between two PDF methods:
                // Method 1: Using pdfkit (backend processing)
                exportToPDF();

            }
            // Word export will be handled by the form submit
            if (this.textContent.includes('Word')) {
                // Make sure the hidden field is updated with current content
                document.getElementById('hidden-editor-content').value = 
                    document.getElementById('document-editor').innerHTML;
                // Submit the form
                document.getElementById('export-form').submit();
            }
        });
    });
    
    // PDF Export function using pdfkit on backend
    function exportToPDF() {
        // Create a form dynamically
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/export_pdf';
        form.style.display = 'none';
        
        // Create hidden input for content
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'document_content';
        input.value = documentEditor.innerHTML;
        
        // Add input to form
        form.appendChild(input);
        
        // Add form to document and submit
        document.body.appendChild(form);
        form.submit();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(form);
        }, 1000);
    }
    
    // Simpler PDF Export function using browser's print dialog
    function exportToPDFSimple() {
        // Create a form dynamically
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/export_pdf_simple';
        form.target = '_blank'; // Open in new tab
        form.style.display = 'none';
        
        // Create hidden input for content
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'document_content';
        input.value = documentEditor.innerHTML;
        
        // Add input to form
        form.appendChild(input);
        
        // Add form to document and submit
        document.body.appendChild(form);
        form.submit();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(form);
        }, 1000);
    }

    // Auto-resize functionality for textareas
    const autoResizeTextareas = () => {
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
            
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        });
    };
    
    autoResizeTextareas();
    
    // Add new section functionality
    const addSectionBtn = document.getElementById('add-section-btn');
    const sectionsContainer = document.getElementById('sections-container');
    
    addSectionBtn.addEventListener('click', () => {
        const newSection = document.createElement('div');
        newSection.className = 'section-item border rounded p-2 bg-white/60 dark:bg-gray-800/60';
        newSection.innerHTML = `
            <div class="flex justify-between items-center">
                <input type="text" class="section-title w-full p-1 bg-transparent border-b border-gray-200 dark:border-gray-700 text-sm" value="New Section">
                <button class="remove-section-btn text-red-500 hover:text-red-700 px-1">×</button>
            </div>
            <textarea class="section-notes w-full p-1 text-xs mt-1 bg-transparent" placeholder="Section notes..."></textarea>
        `;
        sectionsContainer.appendChild(newSection);
        
        // Set up event listener for the new remove button
        const removeBtn = newSection.querySelector('.remove-section-btn');
        removeBtn.addEventListener('click', () => {
            newSection.remove();
        });
        
        // Auto-resize for the new textarea
        const textarea = newSection.querySelector('textarea');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Set up event listeners for existing remove section buttons
    document.querySelectorAll('.remove-section-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.section-item').remove();
        });
    });

    // Add reference functionality
    const addReferenceBtn = document.getElementById('add-reference-btn');
    const referencesContainer = document.getElementById('references-container');

    addReferenceBtn.addEventListener('click', () => {
        const newReference = document.createElement('div');
        newReference.className = 'reference-item flex items-center';
        newReference.innerHTML = `
            <input type="text" class="reference-text w-full p-2 bg-white/60 dark:bg-gray-800/60 border rounded text-sm" placeholder="Add reference...">
            <button class="remove-reference-btn text-red-500 hover:text-red-700 px-2 ml-1">×</button>
        `;
        
        // Insert before the add button
        referencesContainer.insertBefore(newReference, addReferenceBtn);
        
        // Set up event listener for the new remove button
        const removeBtn = newReference.querySelector('.remove-reference-btn');
        removeBtn.addEventListener('click', () => {
            newReference.remove();
        });
    });

    // Set up event listeners for existing remove reference buttons
    document.querySelectorAll('.remove-reference-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.reference-item').remove();
        });
    });

    const applyOutlineBtn = document.getElementById('apply-outline-btn');
    if (applyOutlineBtn) {
        applyOutlineBtn.addEventListener('click', () => {
            // Get the title, author, abstract
            const title = document.getElementById('paper-title').value;
            const author = document.getElementById('paper-author').value;
            const abstract = document.getElementById('abstract-input').value;

            // Get all sections
            const sections = Array.from(document.querySelectorAll('.section-item')).map(item => {
                return {
                    title: item.querySelector('.section-title').value,
                    notes: item.querySelector('.section-notes').value
                };
            });

            // Get all references
            const references = Array.from(document.querySelectorAll('.reference-text')).map(item => item.value).filter(ref => ref.trim() !== '');

            // Generate document content
            let documentContent = `<h1>${title}</h1>`;
            documentContent += `<p class="author">${author}</p>`;

            if (abstract.trim() !== '') {
                documentContent += `<h2>Abstract</h2>`;
                documentContent += `<p>${abstract}</p>`;
            }

            // Add sections
            sections.forEach(section => {
                if (section.title.trim() !== '') {
                    documentContent += `<h2>${section.title}</h2>`;
                    if (section.notes.trim() !== '') {
                        documentContent += `<p class="section-note"><em>${section.notes}</em></p>`;
                    }
                    documentContent += `<p contenteditable="true" class="editable-section">Start writing your ${section.title.toLowerCase()} here...</p>`;
                }
            });

            // Add references if any exist
            if (references.length > 0) {
                documentContent += `<h2>References</h2>`;
                documentContent += `<ol class="references">`;
                references.forEach(ref => {
                    documentContent += `<li>${ref}</li>`;
                });
                documentContent += `</ol>`;
            }

            // Update the document editor content
            documentEditor.innerHTML = documentContent;

            // Set the content to hidden fields for export
            if (hiddenEditorContent) {
                hiddenEditorContent.value = documentContent;
            }
            
            if (hiddenPdfContent) {
                hiddenPdfContent.value = documentContent;
            }

            showToast('Outline applied to document!', 'success');
        });
    }
});

// Helper function to show toasts
function showToast(message, type) {
    // Implementation of toast notification
    console.log(`Toast: ${message} (${type})`);
    
    // Simple implementation if not already defined
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = message;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.padding = '10px 20px';
    toast.style.backgroundColor = type === 'success' ? '#4CAF50' : '#2196F3';
    toast.style.color = 'white';
    toast.style.borderRadius = '5px';
    toast.style.zIndex = '1000';
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        document.body.removeChild(toast);
    }, 3000);
}