import os
import tempfile
import subprocess
import logging
from typing import List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

WORKSPACE_DIR = "/home/knhung/KLTN/CodeJudge"

def check_syntax(code_or_path: str, language: str) -> List[str]:
    """
    Check the syntax of code.
    code_or_path can be a raw code string OR a path to a file or directory.
    Supports C++ ('cpp', 'c++', 'c') and Python ('python', 'py').
    
    Returns a list of error strings. Empty list means syntax is clean.
    """
    lang = language.lower().strip()
    
    # Resolve if it is a path
    is_dir = False
    is_file = False
    path_str = ""
    
    if isinstance(code_or_path, str) and len(code_or_path) < 1024:
        try:
            if os.path.exists(code_or_path):
                is_dir = os.path.isdir(code_or_path)
                is_file = os.path.isfile(code_or_path)
                path_str = code_or_path
        except Exception:
            pass
            
    if lang in {"python", "py"}:
        if is_dir:
            return _check_python_directory_syntax(path_str)
        elif is_file:
            try:
                with open(path_str, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                return _check_python_syntax(content)
            except Exception as e:
                return [f"General Compile Error: {str(e)}"]
        else:
            return _check_python_syntax(code_or_path)
    elif lang in {"cpp", "c++", "c"}:
        if is_dir:
            return _check_cpp_directory_syntax(path_str)
        elif is_file:
            return _check_cpp_file_syntax(path_str)
        else:
            return _check_cpp_code_syntax(code_or_path)
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

def _check_python_directory_syntax(dir_path: str) -> List[str]:
    """Check Python syntax for all .py files in a directory."""
    errors = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if f.endswith(".py"):
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                    compile(content, f, "exec")
                except SyntaxError as e:
                    error_msg = f"File {f}, Line {e.lineno}"
                    if e.offset is not None:
                        error_msg += f", Col {e.offset}"
                    error_msg += f": {e.msg}"
                    errors.append(error_msg)
                except Exception as e:
                    errors.append(f"File {f}, General Compile Error: {str(e)}")
    return errors

def _check_cpp_directory_syntax(dir_path: str) -> List[str]:
    """Check syntax of a C++ directory by running g++ -fsyntax-only *.cpp in that directory."""
    cpp_files = []
    try:
        for f in os.listdir(dir_path):
            if f.lower().endswith((".cpp", ".cc", ".cxx", ".c")):
                cpp_files.append(f)
    except Exception as e:
        return [f"Error listing C++ files in directory: {str(e)}"]
            
    if not cpp_files:
        return []
        
    try:
        # Run g++ on all source files together in the directory cwd
        cmd = ["g++", "-fsyntax-only"] + cpp_files
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=dir_path, timeout=10)
        
        if res.returncode == 0:
            return []
            
        errors = []
        raw_stderr = res.stderr or ""
        for line in raw_stderr.splitlines():
            line = line.strip()
            if not line:
                continue
            if "error:" in line.lower() or "warning:" in line.lower() or "fatal error:" in line.lower():
                errors.append(line)
                
        if not errors and raw_stderr:
            errors.append(raw_stderr.strip())
            
        return errors
    except FileNotFoundError:
        logger.error("g++ compiler not found. Cannot check C++ directory syntax.")
        return ["g++ compiler not found. Cannot check C++ syntax."]
    except subprocess.TimeoutExpired:
        logger.error("C++ directory syntax checking timed out.")
        return ["Compilation timed out (g++ directory syntax check)."]
    except Exception as e:
        logger.error(f"Error checking C++ directory syntax: {e}")
        return [f"Compiler Error: {str(e)}"]

def _check_cpp_file_syntax(file_path: str) -> List[str]:
    """Check syntax of a C++ file by running g++ -fsyntax-only directly on it."""
    try:
        cmd = ["g++", "-fsyntax-only", file_path]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if res.returncode == 0:
            return []
            
        errors = []
        raw_stderr = res.stderr or ""
        basename = os.path.basename(file_path)
        for line in raw_stderr.splitlines():
            line = line.strip()
            if not line:
                continue
            if file_path in line:
                line = line.replace(file_path, basename)
            if "error:" in line.lower() or "warning:" in line.lower() or "fatal error:" in line.lower():
                errors.append(line)
                
        if not errors and raw_stderr:
            errors.append(raw_stderr.replace(file_path, basename).strip())
            
        return errors
    except FileNotFoundError:
        return ["g++ compiler not found. Cannot check C++ syntax."]
    except subprocess.TimeoutExpired:
        return ["Compilation timed out (g++ syntax check)."]
    except Exception as e:
        return [f"Compiler Error: {str(e)}"]

def _check_cpp_code_syntax(code: str) -> List[str]:
    """Check C++ syntax using g++ -fsyntax-only on a temp file in the workspace."""
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    temp_file = None
    temp_file_path = ""
    try:
        temp_file = tempfile.NamedTemporaryFile(
            dir=WORKSPACE_DIR,
            suffix=".cpp",
            mode="w",
            encoding="utf-8",
            delete=False
        )
        temp_file.write(code)
        temp_file.flush()
        temp_file.close()
        temp_file_path = temp_file.name
        
        errors = _check_cpp_file_syntax(temp_file_path)
        
        # Replace temp file name with generic student_code.cpp in output
        basename = os.path.basename(temp_file_path)
        sanitized_errors = []
        for err in errors:
            if temp_file_path in err:
                err = err.replace(temp_file_path, "student_code.cpp")
            elif basename in err:
                err = err.replace(basename, "student_code.cpp")
            sanitized_errors.append(err)
            
        return sanitized_errors
        
    except Exception as e:
        logger.error(f"Error checking C++ syntax: {e}")
        return [f"Compiler Error: {str(e)}"]
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Could not remove temp file {temp_file_path}: {e}")

def merge_folder_code(folder_path: Union[str, Path], language: str) -> str:
    """
    Merge all source code files in a folder into a single decorated string.
    Removes system includes <...> and comments local includes "..." to optimize context and avoid LLM confusion.
    """
    import re
    lang = language.lower().strip()
    folder = Path(folder_path)
    if not folder.is_dir():
        return ""
        
    merged_lines = []
    
    if lang in {"cpp", "c++", "c"}:
        merged_lines.append("// [HỆ THỐNG: Đã gộp các file nguồn và lược bỏ các thư viện hệ thống <...>]")
        merged_lines.append("// [HỆ THỐNG: Vui lòng chỉ tập trung đánh giá tư duy thuật toán và logic của sinh viên]")
        merged_lines.append("")
        
        header_files = []
        source_files = []
        try:
            for p in folder.iterdir():
                if p.is_file():
                    ext = p.suffix.lower()
                    if ext in {".h", ".hpp", ".hxx"}:
                        header_files.append(p)
                    elif ext in {".cpp", ".cc", ".cxx", ".c"}:
                        source_files.append(p)
        except Exception as e:
            return f"// Lỗi quét thư mục bài nộp: {e}"
                    
        header_files.sort()
        source_files.sort()
        all_files = header_files + source_files
        
        for p in all_files:
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                
                merged_lines.append("// " + "=" * 50)
                merged_lines.append(f"// FILE: {p.name}")
                merged_lines.append("// " + "=" * 50)
                
                for line in content.splitlines():
                    # Strip system headers like #include <vector> or #include <iostream>
                    if re.match(r'^\s*#\s*include\s*<[^>]+>', line):
                        continue
                    # Comment out local headers like #include "helper.h"
                    if re.match(r'^\s*#\s*include\s*"[^"]+"', line):
                        merged_lines.append(f"// {line} (Đã gộp nội dung file này vào bên dưới)")
                        continue
                    merged_lines.append(line)
                
                merged_lines.append("")
            except Exception as e:
                merged_lines.append(f"// Lỗi đọc file {p.name}: {e}")
                
    elif lang in {"python", "py"}:
        merged_lines.append("# [HỆ THỐNG: Đã gộp các file nguồn Python trong thư mục bài nộp]")
        merged_lines.append("# [HỆ THỐNG: Vui lòng chỉ tập trung đánh giá tư duy thuật toán và logic của sinh viên]")
        merged_lines.append("")
        
        try:
            py_files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".py"])
        except Exception as e:
            return f"# Lỗi quét thư mục bài nộp: {e}"
            
        for p in py_files:
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                merged_lines.append("# " + "=" * 50)
                merged_lines.append(f"# FILE: {p.name}")
                merged_lines.append("# " + "=" * 50)
                merged_lines.append(content)
                merged_lines.append("")
            except Exception as e:
                merged_lines.append(f"# Lỗi đọc file {p.name}: {e}")
                
    elif lang in {"java"}:
        merged_lines.append("// [HỆ THỐNG: Đã gộp các file nguồn Java trong thư mục bài nộp]")
        merged_lines.append("// [HỆ THỐNG: Vui lòng chỉ tập trung đánh giá tư duy thuật toán và logic của sinh viên]")
        merged_lines.append("")
        
        try:
            java_files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".java"])
        except Exception as e:
            return f"// Lỗi quét thư mục bài nộp: {e}"
            
        for p in java_files:
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                merged_lines.append("// " + "=" * 50)
                merged_lines.append(f"// FILE: {p.name}")
                merged_lines.append("// " + "=" * 50)
                merged_lines.append(content)
                merged_lines.append("")
            except Exception as e:
                merged_lines.append(f"// Lỗi đọc file {p.name}: {e}")
                
    return "\n".join(merged_lines)
