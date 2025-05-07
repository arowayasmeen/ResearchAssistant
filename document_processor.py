import os
import uuid
from typing import Dict, List, Any, Tuple
import re

# Try to import PyMuPDF (if available)
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not available. PDF processing will be limited.")

from models import ProcessedPDF, MethodContribution


class PDFProcessor:
    """Processes PDF documents to extract structured information."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        if not PYMUPDF_AVAILABLE:
            print("Warning: PyMuPDF not installed. Install with: pip install pymupdf")
    
    def process_pdfs(self, pdf_files: List[str]) -> List[ProcessedPDF]:
        """
        Process a list of PDF files to extract structured data.
        
        Args:
            pdf_files: List of PDF file paths
            
        Returns:
            List of ProcessedPDF objects with extracted data
        """
        processed_data_list = []
        
        for pdf_file in pdf_files:
            try:
                # Check if file exists
                if not os.path.exists(pdf_file):
                    print(f"Error: File not found - {pdf_file}")
                    continue
                
                print(f"Processing PDF: {pdf_file}")
                
                # Extract text and metadata
                text, layout_info = self._extract_text_and_layout(pdf_file)
                metadata = self._extract_metadata(pdf_file)
                
                # Segment into sections
                sections = self._segment_sections(text)
                
                # Extract methodological contributions (simplified implementation)
                methodological_contributions = self._extract_contributions(sections, text, metadata)
                
                # Create ProcessedPDF object
                processed_pdf = ProcessedPDF(
                    file_path=pdf_file,
                    metadata=metadata,
                    full_text=text,
                    sections=sections,
                    methodological_contributions=methodological_contributions
                )
                
                processed_data_list.append(processed_pdf)
                print(f"Successfully processed: {pdf_file}")
                
            except Exception as e:
                print(f"Error processing PDF {pdf_file}: {str(e)}")
                # Continue with other PDFs
        
        return processed_data_list
    
    def _extract_text_and_layout(self, pdf_file: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text content and layout information from a PDF file."""
        text = ""
        layout_info = {"page_count": 0, "pages": []}
        
        if PYMUPDF_AVAILABLE:
            try:
                # Open PDF with PyMuPDF
                doc = fitz.open(pdf_file)
                
                # Initialize layout info
                layout_info["page_count"] = len(doc)
                layout_info["pages"] = []
                
                # Process each page
                full_text = []
                for page_num, page in enumerate(doc):
                    # Extract text
                    page_text = page.get_text()
                    full_text.append(page_text)
                    
                    # Store basic layout info
                    layout_info["pages"].append({
                        "page_num": page_num,
                        "width": page.rect.width,
                        "height": page.rect.height
                    })
                
                text = "\n\n".join(full_text)
                doc.close()
            except Exception as e:
                print(f"Error extracting text from PDF: {str(e)}")
                # Fall back to file info only
                text = f"Error extracting text: {str(e)}"
        else:
            # Fallback when PyMuPDF is not available
            text = f"PDF processing unavailable - PyMuPDF not installed"
            # Try to get basic file info
            try:
                file_size = os.path.getsize(pdf_file)
                layout_info = {"file_size": file_size}
            except:
                pass
        
        return text, layout_info
    
    def _extract_metadata(self, pdf_file: str) -> Dict[str, Any]:
        """Extract metadata from a PDF file."""
        metadata = {
            "title": "",
            "authors": [],
            "date": "",
            "keywords": []
        }
        
        if PYMUPDF_AVAILABLE:
            try:
                # Open the PDF
                doc = fitz.open(pdf_file)
                
                # Extract built-in metadata
                pdf_metadata = doc.metadata
                
                # Get title
                metadata["title"] = pdf_metadata.get("title", "")
                
                # Get author(s)
                author_str = pdf_metadata.get("author", "")
                if author_str:
                    # Split authors (may be comma or semicolon separated)
                    authors = re.split(r'[,;]\s*', author_str)
                    metadata["authors"] = [a.strip() for a in authors if a.strip()]
                
                # Get date
                metadata["date"] = pdf_metadata.get("creationDate", "")
                
                # If title is missing, use filename
                if not metadata["title"]:
                    base_name = os.path.basename(pdf_file)
                    name_without_ext = os.path.splitext(base_name)[0]
                    metadata["title"] = name_without_ext.replace('_', ' ').replace('-', ' ').title()
                
                doc.close()
            except Exception as e:
                print(f"Error extracting metadata: {str(e)}")
                # Still try to get a title from filename
                base_name = os.path.basename(pdf_file)
                name_without_ext = os.path.splitext(base_name)[0]
                metadata["title"] = name_without_ext.replace('_', ' ').replace('-', ' ').title()
        else:
            # Fallback when PyMuPDF is not available
            base_name = os.path.basename(pdf_file)
            name_without_ext = os.path.splitext(base_name)[0]
            metadata["title"] = name_without_ext.replace('_', ' ').replace('-', ' ').title()
        
        return metadata
    
    def _segment_sections(self, text: str) -> Dict[str, str]:
        """Segment text into logical sections."""
        # Simplified section detection
        sections = {
            "abstract": "",
            "introduction": "",
            "methodology": "",
            "results": "",
            "conclusion": "",
            "references": ""
        }
        
        # Fixed pattern matching for section headings (with correctly placed flags)
        patterns = {
            'abstract': r'abstract',
            'introduction': r'introduction|background',
            'methodology': r'method|methodology|approach',
            'results': r'results|findings',
            'conclusion': r'conclusion|discussion',
            'references': r'references|bibliography'
        }
        
        # Split by common section separators (simplistic approach)
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            # Check if this line is a section heading
            found_section = False
            for section, pattern in patterns.items():
                # Fixed regex with case insensitivity flag at the start
                if re.search(f"(?i){pattern}", line) and len(line) < 100:
                    current_section = section
                    found_section = True
                    break
            
            # If it's a section heading, skip adding it to the content
            if found_section:
                continue
                
            # Add line to current section if we're in one
            if current_section and current_section in sections:
                sections[current_section] += line + "\n"
        
        return sections
    
    def _extract_contributions(self, sections: Dict[str, str], text: str, metadata: Dict[str, Any]) -> List[MethodContribution]:
        """Extract methodological contributions (simplified implementation)."""
        contributions = []
        
        # Look for algorithm/method mentions in the methodology section
        methodology = sections.get("methodology", "")
        if not methodology:
            return contributions
        
        # Fixed method patterns with correctly placed flags
        method_patterns = [
            r'(?i)we propose (?:a|an|the) (algorithm|method|approach|technique) (?:called|named)? ([A-Za-z0-9-]+)',
            r'(?i)(?:our|the) (algorithm|method|approach|technique) (?:called|named)? ([A-Za-z0-9-]+)',
            r'(?i)([A-Za-z0-9-]+) (algorithm|method)'
        ]
        
        # Find potential method mentions
        for pattern in method_patterns:
            for match in re.finditer(pattern, methodology):
                try:
                    # Extract method type and name
                    if len(match.groups()) >= 2:
                        method_type = match.group(1).capitalize()
                        method_name = match.group(2)
                    else:
                        method_type = "Method"
                        method_name = "Unnamed Method"
                    
                    # Get context (surrounding text)
                    start = max(0, match.start() - 100)
                    end = min(len(methodology), match.end() + 200)
                    context = methodology[start:end].strip()
                    
                    # Create a contribution object
                    contribution = MethodContribution(
                        id=str(uuid.uuid4()),
                        type=method_type,
                        name=method_name,
                        description=context,
                        problem_solved=self._extract_problem(sections),
                        source_paper_id=metadata.get("title", ""),
                        location_in_paper="Methodology section"
                    )
                    
                    contributions.append(contribution)
                except Exception as e:
                    print(f"Error extracting contribution: {str(e)}")
        
        return contributions
    
    def _extract_problem(self, sections: Dict[str, str]) -> str:
        """Extract problem statement from abstract or introduction."""
        # First try abstract
        abstract = sections.get("abstract", "")
        if abstract:
            # Take first 2 sentences as problem statement (simplified approach)
            sentences = abstract.split('.')
            if len(sentences) >= 2:
                return '. '.join(sentences[:2]).strip() + '.'
            return abstract
        
        # If no abstract, try introduction
        intro = sections.get("introduction", "")
        if intro:
            sentences = intro.split('.')
            if len(sentences) >= 2:
                return '. '.join(sentences[:2]).strip() + '.'
            return intro
        
        return ""