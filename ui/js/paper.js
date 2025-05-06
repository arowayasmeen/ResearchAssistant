document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const topicName = document.querySelector('.topic-name');
    const brainstormButton = document.getElementById('brainstorm-button');
    const enterTitleButton = document.getElementById('enter-title-button');
    const titleInputContainer = document.getElementById('title-input-container');
    const titleInput = document.getElementById('title-input');
    const saveTitleButton = document.getElementById('save-title-button');
    const titleSuggestions = document.getElementById('title-suggestions');
    const suggestionsContainer = document.getElementById('suggestions-container');
    const refreshTitlesButton = document.getElementById('refresh-titles-button');
    const titleDisplay = document.getElementById('title-display');
    const draftSection = document.getElementById('draft-section');
    const outlineArea = document.getElementById('outline-area');
    const generateOutlineButton = document.getElementById('generate-outline-button');
    const editOutlineButton = document.getElementById('edit-outline-button');
    const saveOutlineButton = document.getElementById('save-outline-button');
    const generatePaperButton = document.getElementById('generate-paper-button');
    const paperSection = document.getElementById('paper-section');
    const latexEditor = document.getElementById('latex-editor');
    const editLatexButton = document.getElementById('edit-latex-button');
    const saveLatexButton = document.getElementById('save-latex-button');
    const compileButton = document.getElementById('compile-button');
    const pdfPreview = document.getElementById('pdf-preview');
    const previewPlaceholder = document.getElementById('preview-placeholder');
    const downloadPdfButton = document.getElementById('download-pdf-button');
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const authorNameInput = document.getElementById('author-name');
    const authorInstitutionInput = document.getElementById('author-institution');
    const updateAuthorInfoButton = document.getElementById('update-author-info-button');
    const documentEditor = document.getElementById('document-editor');
    
    // Backend API endpoints
    const API_BASE_URL = 'http://localhost:5000/api/draft';
    const GENERATE_SECTION_ENDPOINT = `${API_BASE_URL}/generate-section`;
    const GENERATE_PAPER_ENDPOINT = `${API_BASE_URL}/generate-paper`;
    const FORMAT_LATEX_ENDPOINT = `${API_BASE_URL}/format-latex`;
    const REFINE_SECTION_ENDPOINT = `${API_BASE_URL}/refine-section`;
    
    // Set default author info
    let authorName = localStorage.getItem('authorName') || 'Author Name';
    let authorInstitution = localStorage.getItem('authorInstitution') || 'Institution';
    
    // Update author inputs with stored values
    authorNameInput.value = authorName !== 'Author Name' ? authorName : '';
    authorInstitutionInput.value = authorInstitution !== 'Institution' ? authorInstitution : '';
    
    // Add template selection dropdown to the draft section
    const templateSelector = document.createElement('div');
    templateSelector.className = 'form-group';
    templateSelector.innerHTML = `
        <label for="paper-template" class="form-label">Paper Template:</label>
        <select id="paper-template" class="input-field">
            <option value="standard">Standard Research Paper</option>
            <option value="review">Literature Review</option>
            <option value="case_study">Case Study</option>
            <option value="proposal">Research Proposal</option>
        </select>
    `;
    
    // Insert template selector before the outline area
    draftSection.insertBefore(templateSelector, draftSection.firstChild);
    
    // Get the template selector
    const paperTemplateSelect = document.getElementById('paper-template');
    
    // Load saved template selection if exists
    const savedTemplate = localStorage.getItem('paperTemplate');
    if (savedTemplate) {
        paperTemplateSelect.value = savedTemplate;
    }
    
    // Save template selection when changed
    paperTemplateSelect.addEventListener('change', function() {
        localStorage.setItem('paperTemplate', this.value);
    });
    
    // Update author info button click
    updateAuthorInfoButton.addEventListener('click', function() {
        authorName = authorNameInput.value.trim() || 'Author Name';
        authorInstitution = authorInstitutionInput.value.trim() || 'Institution';
        
        localStorage.setItem('authorName', authorName);
        localStorage.setItem('authorInstitution', authorInstitution);
        
        // Update LaTeX content with new author info
        updateAuthorInfoInLatex();
        
        // Show notification
        showNotification('Author information updated!');
        
        // Recompile to update PDF
        compileLatex();
    });
    
    // Function to update author info in LaTeX source
    function updateAuthorInfoInLatex() {
        const latexContent = latexEditor.value;
        
        // Update \author{...} in LaTeX
        const updatedLatex = latexContent.replace(/\\author{[^}]*}/, `\\author{${authorName}}`);
        
        // Store the updated LaTeX
        latexEditor.value = updatedLatex;
        localStorage.setItem('paperLatex', updatedLatex);
    }
    
    // Function to show notification
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.left = '50%';
        notification.style.transform = 'translateX(-50%)';
        notification.style.padding = '10px 20px';
        notification.style.backgroundColor = '#4CAF50';
        notification.style.color = 'white';
        notification.style.borderRadius = '5px';
        notification.style.zIndex = '1000';
        document.body.appendChild(notification);
        
        setTimeout(function() {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s';
            setTimeout(function() {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    }
    
    // Function to show loading indicator
    function showLoading(element, message = 'Loading...') {
        const loader = document.createElement('div');
        loader.className = 'loading-indicator';
        loader.innerHTML = `
            <div class="spinner"></div>
            <p>${message}</p>
        `;
        element.appendChild(loader);
        return loader;
    }
    
    // Function to hide loading indicator
    function hideLoading(loader) {
        if (loader && loader.parentNode) {
            loader.parentNode.removeChild(loader);
        }
    }
    
    // Load topic name from local storage
    const storedTopicName = localStorage.getItem('topicName');
    if (storedTopicName) {
        topicName.textContent = storedTopicName;
    }
    
    // Load saved title if exists
    const savedTitle = localStorage.getItem('paperTitle');
    if (savedTitle) {
        titleDisplay.textContent = savedTitle;
        draftSection.style.display = 'block';
    }
    
    // Load saved LaTeX if exists
    const savedLatex = localStorage.getItem('paperLatex');
    if (savedLatex) {
        latexEditor.value = savedLatex;
        paperSection.style.display = 'block';
        latexEditor.readOnly = true;
    }
    
  
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding content
            const tabId = tab.getAttribute('data-tab');
            const activeContent = document.getElementById(tabId + '-tab');
            if (activeContent) {
                activeContent.classList.add('active');
            }
        });
    });
    
    // Brainstorm button click
    brainstormButton.addEventListener('click', function() {
        titleInputContainer.style.display = 'none';
        titleSuggestions.style.display = 'block';
        
        // Generate title suggestions using the API
        generateTitleSuggestions(topicName.textContent);
    });
    
    // Enter title button click
    enterTitleButton.addEventListener('click', function() {
        titleSuggestions.style.display = 'none';
        titleInputContainer.style.display = 'block';
    });
    
    // Save title button click
    saveTitleButton.addEventListener('click', function() {
        const title = titleInput.value.trim();
        if (title) {
            titleDisplay.textContent = title;
            localStorage.setItem('paperTitle', title);
            titleInputContainer.style.display = 'none';
            draftSection.style.display = 'block';
        } else {
            alert('Please enter a title');
        }
    });
    
    // Refresh title suggestions
    refreshTitlesButton.addEventListener('click', function() {
        generateTitleSuggestions(topicName.textContent);
    });
    
    async function generateTitleSuggestions(topic) {
        suggestionsContainer.innerHTML = '';
        const loader = showLoading(suggestionsContainer, 'Generating title suggestions...');
        
        try {
            console.log('Sending request to generate titles for topic:', topic);
            
            // Use the dedicated title generation endpoint
            const response = await fetch(`${API_BASE_URL}/generate-titles`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    research_topic: topic,
                    count: 7  // Request 7 title suggestions
                })
            });
            
            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success) {
                // Display the suggestions
                data.titles.forEach(suggestion => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.className = 'suggestion-item';
                    suggestionItem.style.padding = '15px';
                    suggestionItem.style.margin = '10px 0';
                    suggestionItem.style.backgroundColor = '#e6f2ff';
                    suggestionItem.style.borderRadius = '10px';
                    suggestionItem.style.cursor = 'pointer';
                    suggestionItem.style.transition = 'background-color 0.3s';
                    
                    suggestionItem.textContent = suggestion;
                    
                    // Hover effect
                    suggestionItem.addEventListener('mouseover', function() {
                        this.style.backgroundColor = '#e6f2ff';
                    });
                    
                    suggestionItem.addEventListener('mouseout', function() {
                        this.style.backgroundColor = '#3a8bbd';
                    });
                    
                    suggestionItem.addEventListener('click', function() {
                        titleDisplay.textContent = suggestion;
                        localStorage.setItem('paperTitle', suggestion);
                        titleSuggestions.style.display = 'none';
                        draftSection.style.display = 'block';
                        
                        // Show notification
                        showNotification('Title selected!');
                    });
                    
                    suggestionsContainer.appendChild(suggestionItem);
                });
            } else {
                throw new Error(data.error || 'Failed to generate title suggestions');
            }
        } catch (error) {
            console.error('Error generating title suggestions:', error);
            suggestionsContainer.innerHTML = `
                <div style="color: #d9534f; padding: 15px; text-align: center;">
                    <p>Sorry, we couldn't generate title suggestions at this time.</p>
                    <p>Please try again later or enter a title manually.</p>
                    <p style="font-size: 0.9em; color: #777; margin-top: 10px;">Error: ${error.message}</p>
                </div>
            `;
        } finally {
            hideLoading(loader);
        }
    }
    
        // Generate outline button
// Generate outline button
generateOutlineButton.addEventListener('click', async function() {
    const title = titleDisplay.textContent;
    const topic = topicName.textContent;
    const paperType = paperTemplateSelect.value;
    
    if (!topic) {
        alert('Please enter a research topic first');
        return;
    }
    
    // Clear existing outline
    outlineArea.value = '';
    
    // Show loading indicator
    const loader = showLoading(draftSection, 'Generating outline...');
    
    try {

        
        console.log('Sending request to generate outline for topic:', topic);
        console.log('Paper type:', paperType);
        
        // Call the correct endpoint with the correct parameters
        const response = await fetch(`${API_BASE_URL}/generate-outline`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                research_topic: topic,
                paper_type: paperType
            })
        });
        
        // Log the raw response for debugging
        const rawResponse = await response.text();
        console.log('Raw API response:', rawResponse);
        
        // Parse the JSON response
        const data = JSON.parse(rawResponse);
        
        if (data.success) {
            // The API returns an 'outline' field, not 'content'
            outlineArea.value = data.outline;
            updateDocumentEditor('Outline', data.outline);
            
            // Save outline to local storage
            localStorage.setItem('paperOutline', outlineArea.value);
            
            // Style and display controls
            outlineArea.style.display = 'block';
            outlineArea.readOnly = true;
            outlineArea.style.backgroundColor = '#e6f2ff';
            
            // Show draft section if it's hidden
            if (draftSection.style.display === 'none') {
                draftSection.style.display = 'block';
            }
        } else {
            // Handle API error
            console.error('API Error:', data.error);
            alert(`Failed to generate outline: ${data.error}`);
        }
    } catch (error) {
        console.error('Error generating outline:', error);
        alert('Error connecting to the outline generation service. Please check the console for details.');
    } finally {
        hideLoading(loader);
    }
});

    // Function to update the document editor with new content
    function updateDocumentEditor(sectionTitle, content) {
        // Parse markdown to HTML
        const html = parseMarkdownToHtml(content);
        documentEditor.innerHTML = `<h2>${sectionTitle}</h2>${html}`;
    }
    
    // Function to parse markdown to HTML
    function parseMarkdownToHtml(markdown) {
        // Basic markdown to HTML conversion
        let html = markdown
            // Headers
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            // List items
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            // Wrap list items in <ul> tags
            .replace(/(<li>.*<\/li>)\n(?!\<li>)/gm, '$1</ul>\n')
            .replace(/\n<li>/g, '\n<ul><li>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Line breaks
            .replace(/\n/g, '<br>');
        
        return html;
    }
    
    // Edit outline button
    editOutlineButton.addEventListener('click', function() {
        outlineArea.readOnly = false;
        outlineArea.style.backgroundColor = '#fff';
        editOutlineButton.style.display = 'none';
        saveOutlineButton.style.display = 'inline-block';
    });
    
    // Save outline button
    saveOutlineButton.addEventListener('click', function() {
        outlineArea.readOnly = true;
        outlineArea.style.backgroundColor ="rgb(203, 207, 207)";
        saveOutlineButton.style.display = 'none';
        editOutlineButton.style.display = 'inline-block';
        
        // Update the document editor with the edited outline
        updateDocumentEditor('Outline', outlineArea.value);
        
        localStorage.setItem('paperOutline', outlineArea.value);
    });
    
    // Generate full paper button
    generatePaperButton.addEventListener('click', async function() {
        const title = titleDisplay.textContent;
        const topic = topicName.textContent;
        const outline = outlineArea.value;
        const paperType = paperTemplateSelect.value;
        
        if (!outline) {
            alert('Please generate an outline first');
            return;
        }
        
        // Show loading indicator
        const loader = showLoading(paperSection, 'Generating paper draft... This may take a minute.');
        paperSection.style.display = 'block';
        
        try {
            // Call the API to generate the full paper
            const response = await fetch(GENERATE_PAPER_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    research_topic: topic,
                    paper_type: paperType,
                    paper_title: title,
                    outline: outline
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Format the paper sections for display
                let completeContent = '';
                
                // Create LaTeX source from the generated content
                const latexDoc = await formatPaperToLatex(title, data.sections, topic);
                
                // Update LaTeX editor
                latexEditor.value = latexDoc;
                latexEditor.readOnly = true;
                
                // Save to local storage
                localStorage.setItem('paperLatex', latexDoc);
                
                // Update the document editor with full paper content
                let paperHtml = `<h1>${title}</h1>`;
                paperHtml += `<p><strong>Author:</strong> ${authorName}<br><strong>Institution:</strong> ${authorInstitution}</p>`;
                
                // Add each section
                for (const [sectionName, content] of Object.entries(data.sections)) {
                    paperHtml += `<h2>${formatSectionName(sectionName)}</h2>`;
                    paperHtml += `<div>${parseMarkdownToHtml(content)}</div>`;
                    completeContent += `## ${formatSectionName(sectionName)}\n${content}\n\n`;
                }
                
                documentEditor.innerHTML = paperHtml;
                
                // Compile to PDF
                compileLatex();
            } else {
                throw new Error(data.error || 'Failed to generate paper');
            }
        } catch (error) {
            console.error('Error generating full paper:', error);

        } finally {
            hideLoading(loader);
            
            // Scroll to paper section
            paperSection.scrollIntoView({ behavior: 'smooth' });
        }
    });
    
    // Format section name from snake_case to Title Case
    function formatSectionName(name) {
        return name
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
// Format paper sections to LaTeX
async function formatPaperToLatex(title, sections, topic) {
    try {
        // Try to use the API for LaTeX formatting
        const metadata = {
            title: title,
            author: authorName,
            institution: authorInstitution,
            template_type: 'article'
        };
        
        const response = await fetch(FORMAT_LATEX_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                paper_data: sections,
                metadata: metadata
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.latex;
        } else {
            throw new Error(data.error || 'Failed to format LaTeX');
        }
    } catch (error) {
        console.error('Error formatting LaTeX:', error);
        return generateLaTeXPaper(title, JSON.stringify(sections), topic);
    }
}


// Edit LaTeX button
editLatexButton.addEventListener('click', function() {
    latexEditor.readOnly = false;
    latexEditor.style.backgroundColor = '#fff';
    editLatexButton.style.display = 'none';
    saveLatexButton.style.display = 'inline-block';
});

// Save LaTeX button
saveLatexButton.addEventListener('click', function() {
    latexEditor.readOnly = true;
    latexEditor.style.backgroundColor = '#f9f9f9';
    saveLatexButton.style.display = 'none';
    editLatexButton.style.display = 'inline-block';
    
    // Save the updated LaTeX
    localStorage.setItem('paperLatex', latexEditor.value);
    
    // Automatically compile after saving
    compileLatex();
    
    // Show notification
    showNotification('Changes saved and compiled!');
});

// Compile to PDF button
compileButton.addEventListener('click', function() {
    compileLatex();
});

// Function to compile LaTeX to PDF
function compileLatex() {
    // Show a loading indicator
    previewPlaceholder.innerHTML = '<p>Compiling LaTeX to PDF...</p>';
    previewPlaceholder.style.display = 'block';
    
    // Simulate compilation delay
    setTimeout(function() {
        // Hide placeholder
        previewPlaceholder.style.display = 'none';
        
        // Create a simulated PDF viewer (in a real app, this would be an iframe to a real PDF)
        const pdfViewer = document.createElement('div');
        pdfViewer.style.width = '100%';
        pdfViewer.style.height = '100%';
        pdfViewer.style.backgroundColor = 'white';
        pdfViewer.style.overflow = 'auto';
        pdfViewer.style.padding = '40px';
        pdfViewer.style.boxSizing = 'border-box';
        
        // Get the current LaTeX content
        const latexContent = latexEditor.value;
        
        // Parse the title and topic from the LaTeX
        let title = titleDisplay.textContent;
        let topic = topicName.textContent;
        
        // Try to extract title from LaTeX
        const titleMatch = latexContent.match(/\\title{([^}]+)}/);
        if (titleMatch && titleMatch[1]) {
            title = titleMatch[1];
        }
        
        // Generate HTML representation of the LaTeX
        // This is a simplified parser that attempts to convert basic LaTeX to HTML
        let htmlContent = `
            <div style="font-family: serif; max-width: 800px; margin: 0 auto; line-height: 1.5;">
                <h1 style="text-align: center; margin-bottom: 30px;">${title}</h1>
                <p style="text-align: center; margin-bottom: 40px;">${authorName}<br>${authorInstitution}<br>${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
        `;
        
        // Extract abstract
        const abstractMatch = latexContent.match(/\\begin{abstract}([\s\S]*?)\\end{abstract}/);
        if (abstractMatch && abstractMatch[1]) {
            const abstractContent = abstractMatch[1].trim();
            htmlContent += `
                <h2 style="margin-top: 20px;">Abstract</h2>
                <p style="text-align: justify;">${abstractContent}</p>
            `;
        }
        
        // Process sections
        const sectionMatches = latexContent.matchAll(/\\section{([^}]+)}([\s\S]*?)(?=\\section{|\\subsection{|\\begin{thebibliography}|\\end{document})/g);
        let sectionNumber = 1;
        
        for (const match of sectionMatches) {
            const sectionTitle = match[1];
            let sectionContent = match[2].trim();
            
            htmlContent += `
                <h2 style="margin-top: 30px;">${sectionNumber}. ${sectionTitle}</h2>
            `;
            
            // Process subsections for this section
            const subsectionMatches = sectionContent.matchAll(/\\subsection{([^}]+)}([\s\S]*?)(?=\\subsection{|$)/g);
            let subsectionNumber = 1;
            let hasSubsections = false;
            
            // Extract content before first subsection
            const beforeSubsection = sectionContent.split(/\\subsection{/)[0].trim();
            if (beforeSubsection) {
                htmlContent += `<p style="text-align: justify;">${parseLatexContent(beforeSubsection)}</p>`;
            }
            
            for (const subMatch of subsectionMatches) {
                hasSubsections = true;
                const subsectionTitle = subMatch[1];
                const subsectionContent = subMatch[2].trim();
                
                htmlContent += `
                    <h3 style="margin-top: 20px;">${sectionNumber}.${subsectionNumber} ${subsectionTitle}</h3>
                    <p style="text-align: justify;">${parseLatexContent(subsectionContent)}</p>
                `;
                
                subsectionNumber++;
            }
            
            // If no subsections were found, add the section content directly
            if (!hasSubsections && !beforeSubsection) {
                htmlContent += `<p style="text-align: justify;">${parseLatexContent(sectionContent)}</p>`;
            }
            
            sectionNumber++;
        }
        
        // Extract bibliography
        const bibMatch = latexContent.match(/\\begin{thebibliography}{[^}]*}([\s\S]*?)\\end{thebibliography}/);
        if (bibMatch && bibMatch[1]) {
            const bibContent = bibMatch[1].trim();
            const bibItems = bibContent.matchAll(/\\bibitem{[^}]*}([\s\S]*?)(?=\\bibitem{|$)/g);
            
            htmlContent += `<h2 style="margin-top: 30px;">References</h2>`;
            
            for (const item of bibItems) {
                const citation = item[1].trim();
                htmlContent += `<p style="text-align: left; margin-left: 40px; text-indent: -40px; margin-bottom: 10px;">${parseLatexContent(citation)}</p>`;
            }
        }
        
        htmlContent += `</div>`;
        
        // Set the HTML content
        pdfViewer.innerHTML = htmlContent;
        
        // Clear previous content
        pdfPreview.innerHTML = '';
        pdfPreview.appendChild(pdfViewer);
        
        // Store a flag indicating compilation is complete
        localStorage.setItem('pdfCompiled', 'true');
    }, 1000);
}

// Helper function to parse LaTeX content
function parseLatexContent(content) {
    // Convert basic LaTeX formatting to HTML
    let parsed = content
        // Replace itemize environments
        .replace(/\\begin{itemize}([\s\S]*?)\\end{itemize}/g, function(match, items) {
            const listItems = items.split('\\item').filter(item => item.trim());
            let html = '<ul>';
            listItems.forEach(item => {
                html += `<li>${item.trim()}</li>`;
            });
            html += '</ul>';
            return html;
        })
        // Replace text formatting
        .replace(/\\textit{([^}]+)}/g, '<i>$1</i>')
        .replace(/\\textbf{([^}]+)}/g, '<b>$1</b>')
        .replace(/\\emph{([^}]+)}/g, '<em>$1</em>')
        // Replace math mode
        .replace(/\$([^$]+)\$/g, '$1');
    
    return parsed;
}

// Download PDF button
downloadPdfButton.addEventListener('click', function() {
    const isPdfCompiled = localStorage.getItem('pdfCompiled') === 'true';
    
    if (!isPdfCompiled) {
        alert('Please compile the LaTeX document first');
        return;
    }
    
    // In a real app, this would download the actual PDF
    alert('In a real application, this would download the compiled PDF file.');
});

// Load saved outline if exists
const savedOutline = localStorage.getItem('paperOutline');
if (savedOutline) {
    outlineArea.value = savedOutline;
    outlineArea.style.display = 'block';
    outlineArea.readOnly = true;
    outlineArea.style.backgroundColor = '#f9f6f0';
}
// Navigation between pages
const homeIcon = document.querySelector('.sidebar-icon:nth-child(1)');
homeIcon.addEventListener('click', function() {
    window.location.href = 'index.html';
});

const literatureReviewIcon = document.querySelector('.sidebar-icon:nth-child(2)');
literatureReviewIcon.addEventListener('click', function() {
    window.location.href = 'literature-review.html';
});

const ideaGenerationIcon = document.querySelector('.sidebar-icon:nth-child(3)');
ideaGenerationIcon.addEventListener('click', function() {
    window.location.href = 'idea-generation.html';
});

document.addEventListener('DOMContentLoaded', function() {
    // Collapsible sections
    const toggleLatexSection = document.getElementById('toggle-latex-section');
    const latexSectionContent = document.getElementById('latex-section-content');
    const latexSection = document.getElementById('paper-section');
    
    if (toggleLatexSection && latexSectionContent) {
        toggleLatexSection.addEventListener('click', function() {
            latexSectionContent.classList.toggle('collapsed');
            toggleLatexSection.classList.toggle('collapsed');
            
            // Adjust section flex when collapsing/expanding
            if (latexSectionContent.classList.contains('collapsed')) {
                latexSection.style.flex = '0';
                latexSection.style.padding = '0 20px';
            } else {
                latexSection.style.flex = '1';
                latexSection.style.padding = '20px';
            }
        });
    }

    // Tab functionality
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
});

});

