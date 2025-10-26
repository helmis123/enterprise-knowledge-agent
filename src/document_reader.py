"""
Extracteur de texte pour différents formats de documents
Supporte : PDF, Word, TXT, Markdown
"""
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentReader:
    """Extraire le texte de différents types de documents"""
    
    def __init__(self):
        # Extensions supportées avec leurs fonctions de lecture
        self.supported_extensions = {
            '.pdf': self.read_pdf,
            '.docx': self.read_word,
            '.doc': self.read_word,
            '.txt': self.read_text,
            '.md': self.read_text,
            '.markdown': self.read_text
        }
    
    def read_pdf(self, file_path: Path) -> str:
        """Extraire le texte d'un fichier PDF"""
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Erreur lecture page {page_num} du PDF: {e}")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du PDF {file_path}: {e}")
            return ""
    
    def read_word(self, file_path: Path) -> str:
        """Extraire le texte d'un fichier Word"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])
            
            return text
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du Word {file_path}: {e}")
            return ""
    
    def read_text(self, file_path: Path) -> str:
        """Lire un fichier texte simple"""
        try:
            # Essayer différents encodages
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    return file_path.read_text(encoding=encoding)
                except UnicodeDecodeError:
                    continue
            
            logger.error(f"Impossible de décoder le fichier {file_path}")
            return ""
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
            return ""
    
    def extract_text(self, file_path: Path) -> str:
        """Extraire le texte d'un fichier selon son extension"""
        ext = file_path.suffix.lower()
        
        if ext not in self.supported_extensions:
            raise ValueError(f"Format non supporté: {ext}. Extensions supportées: {list(self.supported_extensions.keys())}")
        
        logger.info(f"Extraction du texte de: {file_path.name}")
        text = self.supported_extensions[ext](file_path)
        
        if not text:
            logger.warning(f"Aucun texte extrait de {file_path.name}")
        
        return text
    
    def create_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """
        Découper le texte en morceaux (chunks)
        
        Args:
            text: Le texte à découper
            chunk_size: Nombre de mots par chunk
        
        Returns:
            Liste de chunks de texte
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            chunks.append(chunk)
        
        logger.info(f"Texte découpé en {len(chunks)} chunks")
        return chunks
    
    def process_document(self, file_path: Path, chunk_size: int = 1000) -> Dict[str, Any]:
        """
        Traiter un document complet : extraction + découpage
        
        Args:
            file_path: Chemin du document
            chunk_size: Taille des chunks en mots
        
        Returns:
            Dictionnaire avec texte, chunks et métadonnées
        """
        logger.info(f"Traitement du document: {file_path.name}")
        
        # Extraire le texte
        text = self.extract_text(file_path)
        
        if not text:
            logger.warning(f"Aucun texte extrait de {file_path.name}")
            return {
                "success": False,
                "text": "",
                "chunks": [],
                "metadata": {}
            }
        
        # Créer les chunks
        chunks = self.create_chunks(text, chunk_size)
        
        # Métadonnées du document
        metadata = {
            "filename": file_path.name,
            "source": str(file_path),
            "file_type": file_path.suffix.lower(),
            "num_chunks": len(chunks),
            "total_words": len(text.split()),
            "total_characters": len(text)
        }
        
        logger.info(f"✅ Document traité: {metadata['num_chunks']} chunks créés")
        
        return {
            "success": True,
            "text": text,
            "chunks": chunks,
            "metadata": metadata
        }
    
    def get_supported_extensions(self) -> List[str]:
        """Obtenir la liste des extensions supportées"""
        return list(self.supported_extensions.keys())
    
    def is_supported(self, file_path: Path) -> bool:
        """Vérifier si un fichier est supporté"""
        return file_path.suffix.lower() in self.supported_extensions

