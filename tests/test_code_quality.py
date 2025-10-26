"""
Tests de qualité du code - détection des problèmes d'indentation
"""
import ast
import os
from pathlib import Path


def test_app_py_no_indentation_errors():
    """Test que app.py n'a pas d'erreurs d'indentation"""
    app_path = Path("app.py")
    
    if not app_path.exists():
        return  # Si app.py n'existe pas, on skip
    
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Essayer de compiler le code
        ast.parse(code)
        
        # Vérifier qu'il n'y a pas de lignes avec une mauvaise indentation
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Ignorer les lignes vides et les commentaires
            if line.strip() == '' or line.strip().startswith('#'):
                continue
            
            # Vérifier qu'il n'y a pas d'espaces mélangés avec des tabs
            if '\t' in line:
                assert False, f"Ligne {i} contient des tabs: {line[:50]}"
    
    except SyntaxError as e:
        assert False, f"Erreur de syntaxe dans app.py ligne {e.lineno}: {e.msg}"
    except Exception as e:
        assert False, f"Erreur lors de la lecture de app.py: {e}"


def test_src_files_no_indentation_errors():
    """Test que les fichiers src/ n'ont pas d'erreurs d'indentation"""
    src_dir = Path("src")
    
    if not src_dir.exists():
        return  # Si src/ n'existe pas, on skip
    
    errors = []
    
    for py_file in src_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Essayer de compiler le code
            ast.parse(code)
            
        except SyntaxError as e:
            errors.append(f"{py_file.name} ligne {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"{py_file.name}: {e}")
    
    if errors:
        assert False, f"Erreurs d'indentation dans les fichiers src/:\n" + "\n".join(errors)


def test_test_files_no_indentation_errors():
    """Test que les fichiers tests/ n'ont pas d'erreurs d'indentation"""
    tests_dir = Path("tests")
    
    if not tests_dir.exists():
        return  # Si tests/ n'existe pas, on skip
    
    errors = []
    
    for py_file in tests_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Essayer de compiler le code
            ast.parse(code)
            
        except SyntaxError as e:
            errors.append(f"{py_file.name} ligne {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"{py_file.name}: {e}")
    
    if errors:
        assert False, f"Erreurs d'indentation dans les fichiers tests/:\n" + "\n".join(errors)

