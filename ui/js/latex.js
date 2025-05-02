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

// Generate LaTeX paper (fallback function)
function generateLaTeXPaper(title, outline, topic) {
    return `\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage[margin=1in]{geometry}
\\usepackage{natbib}
\\usepackage{graphicx}
\\usepackage{hyperref}
\\usepackage{amsmath}

\\title{${title}}
\\author{${authorName}}
\\date{\\today}

\\begin{document}

\\maketitle

\\begin{abstract}
This paper explores ${topic} with a focus on recent developments and their implications. The research addresses significant gaps in understanding through a comprehensive analysis of existing literature and new methodological approaches. Key findings indicate important relationships between several factors, contributing to the advancement of knowledge in this field.
\\end{abstract}

\\section{Introduction}
${topic} has been a subject of increasing interest in recent years. This paper seeks to address the following research questions...

The significance of this research lies in its potential to...

\\section{Literature Review}
The existing literature on ${topic} reveals several key themes and research gaps...

\\section{Methodology}
This study employs a mixed-methods approach to investigate ${topic}...

\\section{Results}
The analysis of data reveals several important findings related to ${topic}...

\\section{Discussion}
The results of this study contribute to our understanding of ${topic} in several ways...

\\section{Conclusion}
In conclusion, this research has demonstrated the importance of ${topic} and its implications for theory and practice...

\\begin{thebibliography}{99}
\\bibitem{ref1} Author, A. (Year). Title of the paper. \\textit{Journal Name}, Volume(Issue), pages.
\\bibitem{ref2} Author, B. (Year). Title of the book. Publisher Location: Publisher.
\\bibitem{ref3} Author, C. (Year). Title of the chapter. In Editor (Ed.), \\textit{Book Title} (pp. pages). Publisher Location: Publisher.
\\end{thebibliography}

\\end{document}`;
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