import os
import tempfile
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

WORKSPACE_DIR = "/home/knhung/KLTN/CodeJudge"

def check_syntax(code: str, language: str) -> List[str]:
    """
    Check the syntax of code.
    Supports C++ ('cpp', 'c++', 'c') and Python ('python', 'py').
    
    Returns a list of error strings. Empty list means syntax is clean.
    """
    lang = language.lower().strip()
    
    if lang in {"python", "py"}:
        return _check_python_syntax(code)
    elif lang in {"cpp", "c++", "c"}:
        return _check_cpp_syntax(code)
    else:
        logger.warning(f"Unsupported language for compiler check: {language}. Skipping compiler check.")
        return []

def _check_python_syntax(code: str) -> List[str]:
    """Check Python syntax using built-in compile()."""
    try:
        compile(code, "<student_code>", "exec")
        return []
    except SyntaxError as e:
        # Format: Line X, Offset Y: error_message (code snippet)
        error_msg = f"Line {e.lineno}"
        if e.offset is not None:
            error_msg += f", Col {e.offset}"
        error_msg += f": {e.msg}"
        if e.text:
            error_msg += f" (in: '{e.text.strip()}')"
        return [error_msg]
    except Exception as e:
        return [f"General Compile Error: {str(e)}"]

def _check_cpp_syntax(code: str) -> List[str]:
    """Check C++ syntax using g++ -fsyntax-only on a temp file in the workspace."""
    # Ensure temporary files are created inside the workspace
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    temp_file = None
    temp_file_path = ""
    try:
        # Create temp file in workspace
        temp_file = tempfile.NamedTemporaryFile(
            dir=WORKSPACE_DIR,
            suffix=".cpp",
            mode="w",
            encoding="utf-8",
            delete=False
        )
        temp_file.write(code)
        temp_file.flush()
        temp_file.close() # Close it so subprocess can read it easily
        temp_file_path = temp_file.name
        
        # Run g++ -fsyntax-only to check syntax without compiling to a binary
        cmd = ["g++", "-fsyntax-only", temp_file_path]
        
        # Add timeout to prevent hang on weird compiler states
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if res.returncode == 0:
            return []
            
        # Extract stderr and sanitize path names to protect absolute paths
        errors = []
        raw_stderr = res.stderr or ""
        basename = os.path.basename(temp_file_path)
        
        for line in raw_stderr.splitlines():
            line = line.strip()
            if not line:
                continue
            # Replace absolute path of temporary file with a generic name
            if temp_file_path in line:
                line = line.replace(temp_file_path, "student_code.cpp")
            elif basename in line:
                line = line.replace(basename, "student_code.cpp")
                
            # Filter and collect only meaningful warning/error messages
            if "error:" in line.lower() or "warning:" in line.lower() or "fatal error:" in line.lower():
                errors.append(line)
                
        # If no explicit error/warning lines parsed but returncode was non-zero, return full stderr
        if not errors and raw_stderr:
            sanitized = raw_stderr.replace(temp_file_path, "student_code.cpp").strip()
            errors.append(sanitized)
            
        return errors
        
    except FileNotFoundError:
        # g++ is not installed
        logger.error("g++ compiler not found in system path. Cannot check C++ syntax.")
        return ["g++ compiler not found. Cannot check C++ syntax."]
    except subprocess.TimeoutExpired:
        logger.error("Syntax checking timed out.")
        return ["Compilation timed out (g++ syntax check)."]
    except Exception as e:
        logger.error(f"Error checking C++ syntax: {e}")
        return [f"Compiler Error: {str(e)}"]
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Could not remove temp file {temp_file_path}: {e}")
