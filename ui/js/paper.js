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
    const API_BASE_URL = '/api/draft';
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
    
    // Tab functionality
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all tab content
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Show corresponding tab content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId + '-tab').classList.add('active');
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
    
    // Generate title suggestions
    async function generateTitleSuggestions(topic) {
        suggestionsContainer.innerHTML = '';
        const loader = showLoading(suggestionsContainer, 'Generating title suggestions...');
        
        try {
            // Use the API to generate title suggestions
            const response = await fetch(GENERATE_SECTION_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    research_topic: topic,
                    section_type: 'title_suggestions'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Parse the generated titles (assuming they come as a list in the content)
                let suggestions = data.content.split('\n')
                    .filter(line => line.trim().length > 0)
                    .map(line => line.replace(/^\d+\.\s*/, '').trim())
                    .slice(0, 5);
                
                // Fallback to mock suggestions if API doesn't return proper format
                if (suggestions.length < 3) {
                    suggestions = [
                        `Advances in ${topic}: A Comprehensive Review`,
                        `The Impact of ${topic} on Modern Research`,
                        `Exploring New Frontiers in ${topic}`,
                        `${topic}: Challenges and Opportunities`,
                        `A Novel Approach to ${topic} Research`
                    ];
                }
                
                // Display the suggestions
                suggestions.forEach(suggestion => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.className = 'suggestion-item';
                    suggestionItem.style.padding = '15px';
                    suggestionItem.style.margin = '10px 0';
                    suggestionItem.style.backgroundColor = '#f9f6f0';
                    suggestionItem.style.borderRadius = '10px';
                    suggestionItem.style.cursor = 'pointer';
                    
                    suggestionItem.textContent = suggestion;
                    
                    suggestionItem.addEventListener('click', function() {
                        titleDisplay.textContent = suggestion;
                        localStorage.setItem('paperTitle', suggestion);
                        titleSuggestions.style.display = 'none';
                        draftSection.style.display = 'block';
                    });
                    
                    suggestionsContainer.appendChild(suggestionItem);
                });
            } else {
                throw new Error(data.error || 'Failed to generate title suggestions');
            }
        } catch (error) {
            console.error('Error generating title suggestions:', error);
            
            // Fallback to mock suggestions on error
            const suggestions = [
                `Advances in ${topic}: A Comprehensive Review`,
                `The Impact of ${topic} on Modern Research`,
                `Exploring New Frontiers in ${topic}`,
                `${topic}: Challenges and Opportunities`,
                `A Novel Approach to ${topic} Research`
            ];
            
            suggestions.forEach(suggestion => {
                const suggestionItem = document.createElement('div');
                suggestionItem.className = 'suggestion-item';
                suggestionItem.style.padding = '15px';
                suggestionItem.style.margin = '10px 0';
                suggestionItem.style.backgroundColor = '#f9f6f0';
                suggestionItem.style.borderRadius = '10px';
                suggestionItem.style.cursor = 'pointer';
                
                suggestionItem.textContent = suggestion;
                
                suggestionItem.addEventListener('click', function() {
                    titleDisplay.textContent = suggestion;
                    localStorage.setItem('paperTitle', suggestion);
                    titleSuggestions.style.display = 'none';
                    draftSection.style.display = 'block';
                });
                
                suggestionsContainer.appendChild(suggestionItem);
            });
        } finally {
            hideLoading(loader);
        }
    }
    
    // Generate outline button
    generateOutlineButton.addEventListener('click', async function() {
        const title = titleDisplay.textContent;
        const topic = topicName.textContent;
        const paperType = paperTemplateSelect.value;
        
        if (!title) {
            alert('Please enter a paper title first');
            return;
        }
        
        // Clear existing outline
        outlineArea.value = '';
        
        // Show loading indicator
        const loader = showLoading(draftSection, 'Generating outline...');
        
        try {
            // Get paper structure based on selected template
            const response = await fetch(`${API_BASE_URL}/generate-section`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    research_topic: topic,
                    section_type: 'outline',
                    paper_type: paperType,
                    paper_title: title
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                outlineArea.value = data.content;
                updateDocumentEditor('Outline', data.content);
            } else {
                // Fallback to mock outline if API fails
                const outline = generateMockOutline(title, topic, paperType);
                outlineArea.value = outline;
                updateDocumentEditor('Outline', outline);
            }
        } catch (error) {
            console.error('Error generating outline:', error);
            
            // Fallback to mock outline
            const outline = generateMockOutline(title, topic, paperType);
            outlineArea.value = outline;
            updateDocumentEditor('Outline', outline);
        } finally {
            hideLoading(loader);
            
            // Save outline to local storage
            localStorage.setItem('paperOutline', outlineArea.value);
            
            // Style and display controls
            outlineArea.style.display = 'block';
            outlineArea.readOnly = true;
            outlineArea.style.backgroundColor = '#f9f6f0';
        }
    });
    
    // Generate a mock outline as fallback
    function generateMockOutline(title, topic, paperType = 'standard') {
        // Get structure based on paper type
        let structure;
        switch (paperType) {
            case 'review':
                structure = [
                    'Abstract',
                    'Introduction',
                    'Methods',
                    'Findings',
                    'Discussion',
                    'Conclusion'
                ];
                break;
            case 'case_study':
                structure = [
                    'Abstract',
                    'Introduction',
                    'Background',
                    'Case Presentation',
                    'Discussion',
                    'Conclusion'
                ];
                break;
            case 'proposal':
                structure = [
                    'Abstract',
                    'Introduction',
                    'Literature Review',
                    'Proposed Methodology',
                    'Expected Results',
                    'Timeline',
                    'Conclusion'
                ];
                break;
            default: // standard
                structure = [
                    'Abstract',
                    'Introduction',
                    'Literature Review',
                    'Methodology',
                    'Results',
                    'Discussion',
                    'Conclusion'
                ];
        }
        
        let outline = `# ${title}\n\n`;
        
        structure.forEach(section => {
            outline += `## ${section}\n`;
            
            if (section === 'Abstract') {
                outline += `- Brief overview of research on ${topic}\n`;
                outline += `- Key objectives and significance\n`;
                outline += `- Methodology highlights\n`;
                outline += `- Summary of findings or expected outcomes\n\n`;
            } else if (section === 'Introduction') {
                outline += `- Background on ${topic}\n`;
                outline += `- Problem statement and research gap\n`;
                outline += `- Research questions/objectives\n`;
                outline += `- Significance of the study\n\n`;
            } else if (section === 'Literature Review') {
                outline += `- Historical context of ${topic}\n`;
                outline += `- Current theoretical frameworks\n`;
                outline += `- Analysis of recent research\n`;
                outline += `- Identification of research gaps\n\n`;
            } else if (section === 'Methodology') {
                outline += `- Research design\n`;
                outline += `- Data collection methods\n`;
                outline += `- Analysis techniques\n`;
                outline += `- Limitations and ethical considerations\n\n`;
            } else if (section === 'Results') {
                outline += `- Key findings organized by research questions\n`;
                outline += `- Data presentation (tables, figures)\n`;
                outline += `- Statistical analysis\n\n`;
            } else if (section === 'Discussion') {
                outline += `- Interpretation of results\n`;
                outline += `- Comparison with existing literature\n`;
                outline += `- Theoretical and practical implications\n`;
                outline += `- Limitations of the study\n\n`;
            } else if (section === 'Conclusion') {
                outline += `- Summary of key findings\n`;
                outline += `- Contribution to the field\n`;
                outline += `- Recommendations for future research\n\n`;
            } else {
                // Generic section outline
                outline += `- Main points related to ${section.toLowerCase()}\n`;
                outline += `- Key components and analysis\n`;
                outline += `- Relevant connections to the research topic\n\n`;
            }
        });
        
        outline += `## References\n`;
        outline += `- Relevant literature on ${topic}\n`;
        
        return outline;
    }
    
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
        outlineArea.style.backgroundColor = '#f9f6f0';
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
            
            // Generate a mock paper as fallback
            const mockPaper = generateMockPaper(title, topic, paperType);
            const latexDoc = generateLaTeXPaper(title, outline, topic);
            
            latexEditor.value = latexDoc;
            localStorage.setItem('paperLatex', latexDoc);
            
            // Update document editor with mock paper
            documentEditor.innerHTML = mockPaper;
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
    
    // Generate a mock paper as fallback
    function generateMockPaper(title, topic, paperType) {
        let html = `<h1>${title}</h1>`;
        html += `<p><strong>Author:</strong> ${authorName}<br><strong>Institution:</strong> ${authorInstitution}</p>`;
        
        // Get structure based on paper type
        let structure;
        switch (paperType) {
            case 'review':
                structure = ['Abstract', 'Introduction', 'Methods', 'Findings', 'Discussion', 'Conclusion'];
                break;
            case 'case_study':
                structure = ['Abstract', 'Introduction', 'Background', 'Case Presentation', 'Discussion', 'Conclusion'];
                break;
            case 'proposal':
                structure = ['Abstract', 'Introduction', 'Literature Review', 'Proposed Methodology', 'Expected Results', 'Timeline', 'Conclusion'];
                break;
            default: // standard
                structure = ['Abstract', 'Introduction', 'Literature Review', 'Methodology', 'Results', 'Discussion', 'Conclusion'];
        }
        
        structure.forEach(section => {
            html += `<h2>${section}</h2>`;
            
            if (section === 'Abstract') {
                html += `<p>This paper explores ${topic} with a focus on recent developments and their implications. The research addresses significant gaps in understanding through a comprehensive analysis of existing literature and new methodological approaches. Key findings indicate important relationships between several factors, contributing to the advancement of knowledge in this field.</p>`;
            } else if (section === 'Introduction') {
                html += `<p>${topic} has been a subject of increasing interest in recent years. This paper seeks to address the following research questions...</p>`;
                html += `<p>The significance of this research lies in its potential to...</p>`;
            } else {
                // Generic content for other sections
                html += `<p>This section discusses the ${section.toLowerCase()} aspects of ${topic}, including analysis of relevant components and their significance to the overall research.</p>`;
                html += `<p>Further exploration reveals important connections between key factors that contribute to our understanding of this field.</p>`;
            }
        });
        
        return html;
    }
    
});

