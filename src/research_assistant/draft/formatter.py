"""
LaTeX formatting utilities for research paper drafts.
"""

import re
from typing import Dict, List, Any, Optional

class LaTeXFormatter:
    """
    Converts generated research content to LaTeX format with proper academic styling.
    """
    
    def __init__(self, template_type: str = "article"):
        """
        Initialize the LaTeX formatter.
        
        Args:
            template_type: Type of LaTeX template (article, conference, etc.)
        """
        self.template_type = template_type
        self.citation_counter = 1
        self.citations = {}
    
    def escape_latex_special_chars(self, text: str) -> str:
        """
        Escape LaTeX special characters in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with LaTeX special characters escaped
        """
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
            '\\': r'\textbackslash{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
            
        return text
    
    def process_citations(self, text: str, literature: List[Dict[str, str]]) -> str:
        """
        Process citations in text and replace with LaTeX citation commands.
        
        Args:
            text: Input text
            literature: List of literature items
            
        Returns:
            Text with proper LaTeX citations
        """
        # Create citation keys for each literature item
        for item in literature:
            if 'authors' in item and 'year' in item:
                # Create citation key from first author's last name and year
                first_author = item['authors'].split(',')[0].strip().split()[-1]
                citation_key = f"{first_author}{item['year']}"
                self.citations[citation_key] = item
        
        # Simple pattern to find author-year style citations
        # This is a simplified approach; a real implementation would need more robust pattern matching
        # Sample pattern: (Smith, 2020) or (Smith et al., 2020)
        citation_pattern = r'\(([A-Za-z]+)( et al\.)?[,\s]+(\d{4})\)'
        
        def replace_citation(match):
            author = match.group(1)
            year = match.group(3)
            
            # Find matching citation key
            for key, item in self.citations.items():
                if author.lower() in key.lower() and year in key:
                    return f'\\cite{{{key}}}'
            
            # If no match found, keep the original
            return match.group(0)
        
        return re.sub(citation_pattern, replace_citation, text)
    
    def format_section(self, section_type: str, content: str, literature: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Format a section in LaTeX style.
        
        Args:
            section_type: Type of section (abstract, introduction, etc.)
            content: Section content
            literature: Optional list of literature for citations
            
        Returns:
            LaTeX formatted section
        """
        # Escape special LaTeX characters
        content = self.escape_latex_special_chars(content)
        
        # Process citations if literature is provided
        if literature:
            content = self.process_citations(content, literature)
            
        # Format section based on type
        section_formats = {
            "abstract": f"\\begin{{abstract}}\n{content}\n\\end{{abstract}}",
            "introduction": f"\\section{{Introduction}}\n{content}",
            "literature_review": f"\\section{{Literature Review}}\n{content}",
            "methodology": f"\\section{{Methodology}}\n{content}",
            "results": f"\\section{{Results}}\n{content}",
            "discussion": f"\\section{{Discussion}}\n{content}",
            "conclusion": f"\\section{{Conclusion}}\n{content}"
        }
        
        return section_formats.get(section_type, f"\\section{{{section_type.title()}}}\n{content}")
    
    def generate_bibliography(self) -> str:
        """
        Generate LaTeX bibliography from collected citations.
        
        Returns:
            LaTeX bibliography
        """
        bib_entries = []
        
        for key, item in self.citations.items():
            if 'title' in item and 'authors' in item and 'year' in item:
                entry = f"""
@article{{{key},
  author = {{{item['authors']}}},
  title = {{{item['title']}}},
  year = {{{item['year']}}},
  journal = {{{item.get('journal', 'Journal')}}},
  volume = {{{item.get('volume', '')}}},
  number = {{{item.get('number', '')}}},
  pages = {{{item.get('pages', '')}}},
}}"""
                bib_entries.append(entry)
                
        return "\n".join(bib_entries)
    
    def create_complete_document(self, paper_data: Dict[str, str], 
                               metadata: Dict[str, str],
                               literature: List[Dict[str, str]]) -> str:
        """
        Create a complete LaTeX document from all sections.
        
        Args:
            paper_data: Dictionary of paper sections
            metadata: Paper metadata (title, authors, etc.)
            literature: List of literature for citations
            
        Returns:
            Complete LaTeX document
        """
        # Document preamble
        document = f"""\\documentclass{{{self.template_type}}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{hyperref}}
\\usepackage{{graphicx}}
\\usepackage{{amsmath}}
\\usepackage{{natbib}}

\\title{{{metadata.get('title', 'Research Paper')}}}
\\author{{{metadata.get('authors', 'Author')}}}
\\date{{{metadata.get('date', 'today')}}}

\\begin{{document}}

\\maketitle

"""
        
        # Add abstract if present
        if 'abstract' in paper_data:
            document += self.format_section('abstract', paper_data['abstract'], literature) + "\n\n"
            
        # Standard sections
        standard_sections = ['introduction', 'literature_review', 'methodology', 
                          'results', 'discussion', 'conclusion']
        
        for section in standard_sections:
            if section in paper_data:
                document += self.format_section(section, paper_data[section], literature) + "\n\n"
        
        # Bibliography
        document += """
\\bibliographystyle{plainnat}
\\bibliography{references}

\\end{document}
"""
        
        return document
    
    def save_latex_files(self, document: str, references: str, output_dir: str) -> Dict[str, str]:
        """
        Save LaTeX document and bibliography files.
        
        Args:
            document: LaTeX document
            references: BibTeX references
            output_dir: Output directory
            
        Returns:
            Dictionary with paths to saved files
        """
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        document_path = os.path.join(output_dir, "paper.tex")
        references_path = os.path.join(output_dir, "references.bib")
        
        with open(document_path, 'w', encoding='utf-8') as f:
            f.write(document)
            
        with open(references_path, 'w', encoding='utf-8') as f:
            f.write(references)
            
        return {
            'document': document_path,
            'references': references_path
        }