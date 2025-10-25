"""
Module de traitement des documents pour l'Agent Knowledge Interne
Supporte PDF, Word, Markdown et fichiers texte
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import PyPDF2
import docx
import markdown
from bs4 import BeautifulSoup
from config import Config

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processeur de documents pour extraire le texte et créer des chunks"""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.md', '.txt'}
        self.max_chunk_size = Config.MAX_CHUNK_SIZE
        self.max_chunks_per_document = Config.MAX_CHUNKS_PER_DOCUMENT
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extraire le texte d'un fichier PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extraire le texte d'un fichier Word"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_markdown(self, file_path: Path) -> str:
        """Extraire le texte d'un fichier Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Convertir Markdown en HTML puis extraire le texte
            html = markdown.markdown(content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text().strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction Markdown {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extraire le texte d'un fichier texte"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction TXT {file_path}: {e}")
            return ""
    
    def extract_text(self, file_path: Path) -> str:
        """Extraire le texte selon l'extension du fichier"""
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif extension == '.md':
            return self.extract_text_from_markdown(file_path)
        elif extension == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            logger.warning(f"Extension non supportée: {extension}")
            return ""
    
    def create_chunks(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Diviser le texte en chunks pour l'indexation"""
        if not text:
            return []
        
        # Diviser le texte en phrases
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Si ajouter cette phrase dépasse la taille max, créer un nouveau chunk
            if len(current_chunk) + len(sentence) > self.max_chunk_size:
                if current_chunk:
                    chunks.append({
                        'content': current_chunk.strip(),
                        'metadata': metadata.copy()
                    })
                current_chunk = sentence
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
            
            # Limiter le nombre de chunks par document
            if len(chunks) >= self.max_chunks_per_document:
                break
        
        # Ajouter le dernier chunk
        if current_chunk:
            chunks.append({
                'content': current_chunk.strip(),
                'metadata': metadata.copy()
            })
        
        return chunks
    
    def process_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Traiter un document complet et retourner ses chunks"""
        logger.info(f"Traitement du document: {file_path}")
        
        # Vérifier la taille du fichier
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > Config.MAX_DOCUMENT_SIZE_MB:
            logger.warning(f"Fichier trop volumineux: {file_path} ({file_size_mb:.2f}MB)")
            return []
        
        # Extraire le texte
        text = self.extract_text(file_path)
        if not text:
            logger.warning(f"Aucun texte extrait de: {file_path}")
            return []
        
        # Créer les métadonnées
        metadata = {
            'source': str(file_path),
            'filename': file_path.name,
            'file_type': file_path.suffix.lower(),
            'file_size': file_size_mb,
            'last_modified': file_path.stat().st_mtime
        }
        
        # Créer les chunks
        chunks = self.create_chunks(text, metadata)
        logger.info(f"Créé {len(chunks)} chunks pour {file_path}")
        
        return chunks
    
    def process_directory(self, directory_path: Path) -> List[Dict[str, Any]]:
        """Traiter tous les documents d'un répertoire"""
        all_chunks = []
        
        if not directory_path.exists():
            logger.error(f"Répertoire inexistant: {directory_path}")
            return all_chunks
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                chunks = self.process_document(file_path)
                all_chunks.extend(chunks)
        
        logger.info(f"Traitement terminé: {len(all_chunks)} chunks créés")
        return all_chunks
    
    def get_supported_files(self, directory_path: Path) -> List[Path]:
        """Obtenir la liste des fichiers supportés dans un répertoire"""
        supported_files = []
        
        if not directory_path.exists():
            return supported_files
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                supported_files.append(file_path)
        
        return supported_files
