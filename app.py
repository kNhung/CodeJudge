import asyncio
import os
import re
import json
import html
import logging
from dotenv import load_dotenv
from starlette.responses import StreamingResponse, HTMLResponse
from starlette.background import BackgroundTasks
from fasthtml.common import *

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CodeJudgeWebDemo")

import tempfile
import shutil
import io

def extract_text_from_pdf(content_bytes: bytes) -> str:
    try:
        import pypdf
        pdf_file = io.BytesIO(content_bytes)
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text
    except ImportError:
        logger.warning("pypdf is not installed. Cannot parse PDF file content.")
        return "[Lỗi: Thư viện pypdf chưa được cài đặt trên hệ thống để đọc file PDF]"
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return f"[Lỗi đọc file PDF: {str(e)}]"

def extract_text_from_docx(content_bytes: bytes) -> str:
    try:
        import docx
        docx_file = io.BytesIO(content_bytes)
        doc = docx.Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except ImportError:
        logger.warning("python-docx is not installed. Cannot parse DOCX file content.")
        return "[Lỗi: Thư viện python-docx chưa được cài đặt trên hệ thống để đọc file DOCX]"
    except Exception as e:
        logger.error(f"Error parsing DOCX: {e}")
        return f"[Lỗi đọc file DOCX: {str(e)}]"

# Import CodeJudge Core Assessor and Factory
from codejudge.core.multi_agent_assessor import MultiAgentAssessor
from codejudge.core.llm_client import LLMFactory
from codejudge.core.compiler_helper import check_syntax

FILE_INPUT_CLS = (
    "upload-file-input file-input file-input-bordered file-input-sm w-full "
    "bg-slate-50 dark:bg-slate-850 border-slate-200 dark:border-white/10 rounded-xl text-xs"
)
UPLOAD_ZONE_CLS = (
    "upload-zone p-4 bg-slate-50/50 dark:bg-slate-900/20 "
    "border-2 border-dashed border-[#9E8AEC]/25 dark:border-[#9E8AEC]/20 rounded-2xl"
)

def file_upload_field(label_text, input_id, name, accept="", hint="", webkitdirectory=False, directory=False, multiple=False, zone_cls=""):
    upload_kwargs = {"type": "file", "id": input_id, "name": name, "cls": FILE_INPUT_CLS}
    if accept:
        upload_kwargs["accept"] = accept
    if webkitdirectory:
        upload_kwargs["webkitdirectory"] = True
    if directory:
        upload_kwargs["directory"] = True
    if multiple:
        upload_kwargs["multiple"] = True
    children = [
        Label(label_text, cls="label-text text-[11px] text-slate-500 dark:text-slate-400 mb-2 block font-semibold"),
        Input(**upload_kwargs),
    ]
    if hint:
        children.append(P(hint, cls="text-[10px] text-slate-400 dark:text-slate-500 mt-2"))
    return Div(*children, cls=f"{UPLOAD_ZONE_CLS} {zone_cls}".strip())

# We use TailwindCSS, DaisyUI and Monaco Editor via CDN
app, rt = fast_app(
    hdrs=(
        Script(src="https://cdn.tailwindcss.com"),
        Script("tailwind.config = { darkMode: 'class' }"),
        Link(href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css", rel="stylesheet", type="text/css"),
        Script(src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs/loader.min.js"),
        Link(href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700;800&family=Nunito:wght@400;600;700;800&display=swap", rel="stylesheet"),
        Link(rel="icon", href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2280%22>🤖</text></svg>"),

        Style("""
            :root {
                font-family: 'Quicksand', 'Nunito', sans-serif;
                --bg-main: #FAF7F0;
                --bg-card: #FFFFFF;
                --border-color: rgba(0, 0, 0, 0.05);
                --input-bg: #F5F1E9;
                --text-main: #2D3748;
                --text-muted: #718096;
                --accent-purple: #9E8AEC;
                --accent-purple-hover: #8A75DE;
            }
            [data-theme="dark"] {
                --bg-main: #0B0E17;
                --bg-card: #131A26;
                --border-color: rgba(255, 255, 255, 0.05);
                --input-bg: #1A2333;
                --text-main: #E2E8F0;
                --text-muted: #8892B0;
                --accent-purple: #9E8AEC;
                --accent-purple-hover: #B4A5F4;
            }
            html, body, #main-container {
                background-color: var(--bg-main) !important;
                color: var(--text-main) !important;
                transition: background-color 0.3s, color 0.3s;
            }
            * {
                font-family: 'Quicksand', 'Nunito', sans-serif !important;
            }
            .monaco-editor, .monaco-editor *, #fallback_code, .code-editor, .code-editor * {
                font-family: 'Courier New', Courier, monospace !important;
            }
            .dashboard-card {
                background-color: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 24px;
                box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.02);
                padding: 2rem !important;
                transition: background-color 0.3s, border-color 0.3s;
            }
            [data-theme="dark"] .dashboard-card {
                box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.2);
            }
            select, input[type="text"], input[type="file"], textarea {
                border-radius: 16px !important;
                border: 1px solid var(--border-color) !important;
                background-color: var(--input-bg) !important;
                color: var(--text-main) !important;
                transition: background-color 0.3s, border-color 0.3s;
            }
            select:focus, input[type="text"]:focus, input[type="file"]:focus, textarea:focus {
                outline: 2px solid var(--accent-purple) !important;
                outline-offset: -1px;
            }
            select {
                appearance: none !important;
                background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23718096' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") !important;
                background-repeat: no-repeat !important;
                background-position: right 0.75rem center !important;
                background-size: 1em !important;
                padding-right: 2.25rem !important;
            }
            .monaco-editor-container {
                height: 360px;
                border: 1px solid var(--border-color);
                border-radius: 12px;
                overflow: hidden;
            }
            .placeholder-box {
                background-color: rgba(158, 138, 236, 0.03) !important;
                border: 2px dashed rgba(158, 138, 236, 0.2) !important;
                border-radius: 20px !important;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .animate-fade-in {
                animation: fadeIn 0.4s ease-out forwards;
            }
            /* Custom Scrollbars */
            ::-webkit-scrollbar {
                width: 6px;
                height: 6px;
            }
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
            [data-theme="dark"] ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.1);
            }
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(0, 0, 0, 0.2);
            }
            [data-theme="dark"] ::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            .upload-zone {
                transition: border-color 0.2s, background-color 0.2s;
            }
            .upload-zone:hover {
                border-color: rgba(158, 138, 236, 0.45) !important;
                background-color: rgba(158, 138, 236, 0.04) !important;
            }
            .upload-file-input {
                min-height: 2.5rem !important;
            }
            .upload-file-input::file-selector-button {
                background: #97D0DE !important;
                color: #1e3a44 !important;
                border: 2px solid #97D0DE !important;
                border-radius: 8px !important;
                padding: 0.4rem 0.85rem !important;
                margin-right: 0.75rem !important;
                font-weight: 700 !important;
                font-size: 0.7rem !important;
                cursor: pointer !important;
                transition: background-color 0.2s, border-color 0.2s !important;
            }
            .upload-file-input::file-selector-button:hover {
                background: #7fc0d0 !important;
                border-color: #7fc0d0 !important;
                color: #1e3a44 !important;
            }
            .upload-filename {
                font-size: 0.65rem;
                font-weight: 600;
                color: #9E8AEC;
                margin-top: 0.35rem;
            }
        """)
    )
)

def get_hcmus_config_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation", "hcmus", "configs")

def list_builtin_problem_ids() -> list:
    ids = set()
    config_dir = get_hcmus_config_dir()
    for filename in ["hcmus_tuned_weights.json", "hcmus_factors.json"]:
        path = os.path.join(config_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        ids.update(data.keys())
            except Exception as e:
                logger.error(f"Error listing problem ids from {filename}: {e}")
    return sorted(ids)

def load_builtin_hcmus_config(problem_id: str) -> dict:
    if not problem_id:
        return {}
    config_dir = get_hcmus_config_dir()
    for filename in ["hcmus_tuned_weights.json", "hcmus_factors.json"]:
        path = os.path.join(config_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and problem_id in data:
                        logger.info(f"Loaded configuration for {problem_id} from {filename}")
                        return data[problem_id]
            except Exception as e:
                logger.error(f"Error reading {filename}: {e}")
    return {}

def parse_uploaded_config(data: dict, problem_id: str = "") -> dict:
    if not isinstance(data, dict):
        raise ValueError("File config phải là JSON object.")

    if problem_id and problem_id in data and isinstance(data[problem_id], dict):
        return data[problem_id]

    if data and all(str(k).isdigit() for k in data.keys()):
        return data

    if len(data) == 1:
        only_val = next(iter(data.values()))
        if isinstance(only_val, dict) and any(str(k).isdigit() for k in only_val.keys()):
            return only_val

    for key, value in data.items():
        if isinstance(value, dict) and any(str(qk).isdigit() for qk in value.keys()):
            if not problem_id or key == problem_id:
                return value

    raise ValueError(
        "Không nhận diện được cấu trúc config. "
        "Hãy dùng dạng {\"1_final\": {\"1\": {...}}} hoặc {\"1\": {...}, \"2\": {...}}."
    )

def resolve_problem_config(config_mode: str, problem_id: str = "", config_file_bytes: bytes = None) -> tuple:
    mode = (config_mode or "none").strip().lower()
    if mode == "none":
        return {}, ""

    if mode == "upload":
        if not config_file_bytes:
            raise ValueError("Vui lòng chọn file config JSON để upload.")
        try:
            data = json.loads(config_file_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"File config không phải JSON hợp lệ: {e}") from e
        return parse_uploaded_config(data, problem_id), "uploaded"

    if mode == "builtin":
        cfg = load_builtin_hcmus_config(problem_id)
        if not cfg:
            if problem_id:
                raise ValueError(f"Không tìm thấy config có sẵn cho problem_id='{problem_id}'.")
            raise ValueError("Vui lòng nhập Problem ID hoặc upload file đề bài để tự nhận diện.")
        return cfg, "builtin"

    raise ValueError(f"Chế độ config không hợp lệ: {config_mode}")

@rt("/")
def get():
    builtin_problem_ids = list_builtin_problem_ids()
    builtin_ids_hint = ", ".join(builtin_problem_ids) if builtin_problem_ids else "Không có config có sẵn"
    return (
        Title("CodeEval Agent - Friendly SaaS Dashboard"),
        Div(
            # Header
            Div(
                # Left side: Logo + Tagline
                Div(
                    Div(
                        NotStr("""
                        <svg class="w-8 h-8 mr-2 text-[#9E8AEC]" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect x="6" y="10" width="28" height="22" rx="6" fill="#9E8AEC" fill-opacity="0.15" stroke="#9E8AEC" stroke-width="2.5"/>
                            <rect x="14" y="6" width="12" height="4" rx="2" fill="#9E8AEC"/>
                            <circle cx="15" cy="20" r="3" fill="#8BD3DD"/>
                            <circle cx="25" cy="20" r="3" fill="#FFAAA6"/>
                            <path d="M17 26C17 26 18.5 28 20 28C21.5 28 23 26 23 26" stroke="#9E8AEC" stroke-width="2" stroke-linecap="round"/>
                            <path d="M12 10L10 6" stroke="#9E8AEC" stroke-width="2" stroke-linecap="round"/>
                            <path d="M28 10L30 6" stroke="#9E8AEC" stroke-width="2" stroke-linecap="round"/>
                            <circle cx="9" cy="5" r="1.5" fill="#9E8AEC"/>
                            <circle cx="31" cy="5" r="1.5" fill="#9E8AEC"/>
                        </svg>
                        """),
                        H1("CodeEval Agent", cls="text-xl md:text-2xl font-extrabold bg-gradient-to-r from-[#9E8AEC] via-[#8BD3DD] to-[#FFAAA6] bg-clip-text text-transparent"),
                        cls="flex items-center"
                    ),
                    P("Hệ thống đa tác nhân chấm điểm và tạo phản hồi mã nguồn", cls="text-[10px] md:text-xs text-slate-400 mt-0.5 font-medium"),
                    cls="flex-1 flex flex-col items-start justify-center"
                ),
                # Right side: Theme switch + Avatar + Settings
                Div(
                    Label(
                        NotStr("""
                        <input type="checkbox" class="theme-controller hidden" id="theme-switch" onchange="toggleTheme()" />
                        <!-- sun icon -->
                        <svg class="swap-off fill-current w-5 h-5 text-yellow-500 cursor-pointer hover:scale-110 transition-transform" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                            <path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z"/>
                        </svg>
                        <!-- moon icon -->
                        <svg class="swap-on fill-current w-5 h-5 text-slate-400 cursor-pointer hover:scale-110 transition-transform" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                            <path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z"/>
                        </svg>
                        """),
                        cls="swap swap-rotate mr-4"
                    ),
                    NotStr("""
                    <div class="avatar placeholder mr-3">
                        <div class="bg-[#FFAAA6] text-neutral-content w-8 h-8 rounded-full flex items-center justify-center border border-white/20">
                            <span class="text-xs font-bold text-white">S</span>
                        </div>
                    </div>
                    """),
                    Button(
                        Span("⚙️", cls="mr-1 text-xs"), "Settings",
                        cls="btn btn-sm bg-[#E8E5F7] hover:bg-[#D7D2EE] text-[#5C4EB7] border-none font-bold rounded-lg px-3 text-xs"
                    ),
                    cls="flex-none flex items-center"
                ),
                cls="flex justify-between items-center py-4 mb-6 border-b border-black/[0.03] w-full"
            ),
            
            # Main Grid Layout
            Div(
                # Left Column: Inputs
                Div(
                    Div(
                        Div(
                            H2("Nhập thông tin bài toán", cls="text-lg md:text-xl font-bold text-slate-800 dark:text-slate-100"),
                            cls="flex items-center justify-between mb-4 border-b border-black/[0.02] pb-2"
                        ),
                        
                        Form(
                            # Language & LLM Selection Row
                            Div(
                                # Language Selection
                                Div(
                                    Label("Ngôn ngữ lập trình", cls="label-text text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block"),
                                    Details(
                                        Summary(
                                            Span("🐍 Python", id="selected-lang", cls="text-xs font-semibold text-slate-700 dark:text-slate-200"),
                                            cls="btn btn-sm w-full bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-white/10 hover:bg-slate-100 hover:dark:bg-slate-800 flex justify-between items-center px-3 font-normal !rounded-2xl h-9 min-h-[2.25rem] cursor-pointer"
                                        ),
                                        Ul(
                                            Li(A("🐍 Python", onclick="selectLang('python', '🐍 Python')", cls="text-xs")),
                                            Li(A("💻 C++", onclick="selectLang('cpp', '💻 C++')", cls="text-xs")),
                                            cls="dropdown-content z-20 menu p-1.5 bg-white dark:bg-[#1E293B] rounded-2xl w-full border border-slate-100 dark:border-white/5 mt-1 shadow-none"
                                        ),
                                        cls="dropdown w-full"
                                    ),
                                    Input(type="hidden", id="language", name="language", value="python"),
                                    cls="flex-1"
                                ),
                                # Model Selection
                                Div(
                                    Label("Mô hình LLM", cls="label-text text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block"),
                                    Details(
                                        Summary(
                                            Span("✨ Gemini-2.5-Flash", id="selected-model", cls="text-xs font-semibold text-slate-700 dark:text-slate-200"),
                                            cls="btn btn-sm w-full bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-white/10 hover:bg-slate-100 hover:dark:bg-slate-800 flex justify-between items-center px-3 font-normal !rounded-2xl h-9 min-h-[2.25rem] cursor-pointer"
                                        ),
                                        Ul(
                                            Li(A("✨ Gemini-2.5-Flash", onclick="selectModel('openrouter|google/gemini-2.5-flash', '✨ Gemini-2.5-Flash')", cls="text-xs")),
                                            Li(A("🧠 Qwen-2.5-7B-Instruct", onclick="selectModel('openrouter|qwen/qwen-2.5-7b-instruct', '🧠 Qwen-2.5-7B-Instruct')", cls="text-xs")),
                                            Li(A("🦙 Llama-3-8B-Instruct", onclick="selectModel('openrouter|meta-llama/llama-3-8b-instruct', '🦙 Llama-3-8B-Instruct')", cls="text-xs")),
                                            Li(A("🛠️ Mock Model (Local Test)", onclick="selectModel('mock|mock-model', '🛠️ Mock Model (Local Test)')", cls="text-xs")),
                                            cls="dropdown-content z-20 menu p-1.5 bg-white dark:bg-[#1E293B] rounded-2xl w-full border border-slate-100 dark:border-white/5 mt-1 shadow-none"
                                        ),
                                        cls="dropdown w-full"
                                    ),
                                    Input(type="hidden", id="model_select", name="model_select", value="openrouter|google/gemini-2.5-flash"),
                                    cls="flex-1"
                                ),
                                cls="flex gap-4 mb-4"
                            ),

                            # Grading Config
                            Div(
                                Label("Cấu hình tiêu chí đánh giá", cls="label-text text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block"),
                                Details(
                                    Summary(
                                        Span("Không dùng cấu hình có sẵn", id="selected-config-mode", cls="text-xs font-semibold text-slate-700 dark:text-slate-200"),
                                        cls="btn btn-sm w-full bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-white/10 hover:bg-slate-100 hover:dark:bg-slate-800 flex justify-between items-center px-3 font-normal !rounded-2xl h-9 min-h-[2.25rem] cursor-pointer"
                                    ),
                                    Ul(
                                        Li(A("Không dùng cấu hình có sẵn", onclick="selectConfigMode('none', 'Không dùng config')", cls="text-xs")),
                                        Li(A("Config HCMUS có sẵn", onclick="selectConfigMode('builtin', 'Config HCMUS có sẵn')", cls="text-xs")),
                                        Li(A("Upload file cấu hình", onclick="selectConfigMode('upload', 'Upload file config')", cls="text-xs")),
                                        cls="dropdown-content z-20 menu p-1.5 bg-white dark:bg-[#1E293B] rounded-2xl w-full border border-slate-100 dark:border-white/5 mt-1 shadow-none"
                                    ),
                                    cls="dropdown w-full mb-2"
                                ),
                                Input(type="hidden", id="config_mode", name="config_mode", value="none"),
                                Div(
                                    Label("Problem ID", cls="label-text text-[10px] text-slate-400 dark:text-slate-500 mb-1 block"),
                                    Input(
                                        type="text",
                                        id="problem_id",
                                        name="problem_id",
                                        placeholder="VD: 1_final, 48_midterm-123 (tự nhận từ tên file đề)",
                                        cls="input input-bordered input-sm w-full bg-slate-50 border-slate-200 dark:bg-slate-850 dark:border-white/10 rounded-lg text-xs"
                                    ),
                                    P(f"Có sẵn: {builtin_ids_hint}", cls="text-[10px] text-slate-400 dark:text-slate-500 mt-1"),
                                    id="config-builtin-panel",
                                    cls="hidden mt-2"
                                ),
                                Div(
                                    file_upload_field(
                                        "File config (.json)",
                                        "config_file", "config_file",
                                        accept=".json,application/json",
                                        hint='Hỗ trợ dạng {"1_final": {"1": {...}}} hoặc {"1": {...}, "2": {...}}.',
                                    ),
                                    id="config-upload-panel",
                                    cls="hidden mt-2"
                                ),
                                cls="form-control mb-4"
                            ),
                            
                            # Instruction
                            Div(
                                Label("Đề bài (Instruction)", cls="label-text text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block"),
                                Textarea(
                                    placeholder="Nhập yêu cầu hoặc mô tả bài toán ở đây...",
                                    id="question_text", name="question_text",
                                    cls="textarea textarea-bordered textarea-sm w-full h-20 bg-slate-50 border-slate-200 dark:bg-slate-850 dark:border-white/10 rounded-lg text-sm leading-relaxed"
                                ),
                                file_upload_field(
                                    "Nộp file đề bài (.txt, .md, .pdf, .docx)",
                                    "question_file", "question_file",
                                    accept=".txt,.md,.pdf,.docx",
                                    zone_cls="mt-2",
                                ),
                                cls="form-control mb-4"
                            ),

                            # Grading Mode
                            Div(
                                Label("Chế độ chấm", cls="label-text text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block"),
                                Div(
                                    Button("Chấm một bài", type="button", id="tab-grade-single", onclick="switchGradingMode('single')", cls="btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-[#9E8AEC] text-white border-none"),
                                    Button("Chấm nhiều bài", type="button", id="tab-grade-batch", onclick="switchGradingMode('batch')", cls="btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-none"),
                                    cls="flex gap-2 mb-2"
                                ),
                                Input(type="hidden", id="grading_mode", name="grading_mode", value="single"),
                                P("Batch: upload thư mục gốc, mỗi thư mục con = 1 bài sinh viên.", id="grading-mode-hint", cls="text-[10px] text-slate-400 dark:text-slate-500"),
                                cls="form-control mb-4"
                            ),
                            
                            # Code Editor - Single
                            Div(
                                Label("Mã nguồn sinh viên", cls="label-text text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1.5 block"),
                                Input(type="hidden", id="code_input_type", name="code_input_type", value="editor"),
                                
                                # Switcher tabs
                                Div(
                                    Button("Nhập trực tiếp", type="button", id="tab-editor", onclick="switchCodeInput('editor')", cls="btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-[#9E8AEC] text-white border-none"),
                                    Button("Tải tệp tin", type="button", id="tab-file", onclick="switchCodeInput('file')", cls="btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-none"),
                                    Button("Tải thư mục", type="button", id="tab-folder", onclick="switchCodeInput('folder')", cls="btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-none"),
                                    cls="flex gap-2 mb-3"
                                ),
                                
                                # Monaco Editor
                                Div(
                                    Textarea(id="student_code", name="student_code", cls="hidden"),
                                    Div(
                                        Textarea(
                                            id="fallback_code", 
                                            placeholder="Nhập mã nguồn của bạn ở đây...", 
                                            cls="textarea textarea-bordered w-full h-[360px] font-mono text-sm leading-relaxed"
                                        ),
                                        id="editor-container", 
                                        cls="monaco-editor-container"
                                    ),
                                    id="editor-wrapper",
                                    cls="block"
                                ),
                                
                                # File Wrapper (Hidden initially)
                                Div(
                                    file_upload_field(
                                        "Chọn tệp mã nguồn (.cpp, .py, .java)",
                                        "code_file", "code_file",
                                        accept=".cpp,.cc,.cxx,.c,.py,.java",
                                    ),
                                    id="file-wrapper",
                                    cls="hidden"
                                ),
                                
                                # Folder Wrapper (Hidden initially)
                                Div(
                                    file_upload_field(
                                        "Chọn thư mục mã nguồn sinh viên",
                                        "code_folder", "code_folder",
                                        webkitdirectory=True, directory=True, multiple=True,
                                    ),
                                    id="folder-wrapper",
                                    cls="hidden"
                                ),
                                id="single-code-section",
                                cls="form-control mb-4"
                            ),

                            # Batch upload
                            Div(
                                file_upload_field(
                                    "Thư mục nhiều bài làm (Batch)",
                                    "batch_folder", "batch_folder",
                                    webkitdirectory=True, directory=True, multiple=True,
                                    hint="Cấu trúc: thư_mục_gốc/1/Bai01.cpp, thư_mục_gốc/2/Bai01.cpp hoặc thư_mục_gốc/SV091214/Bai01.cpp",
                                ),
                                id="batch-code-section",
                                cls="hidden form-control mb-4"
                            ),
                            
                            # Action Buttons stacked vertically
                            Div(
                                Button(
                                    "👁️ Xem trước mã nguồn và đề bài",
                                    type="button",
                                    onclick="openPreview()",
                                    cls="btn btn-outline border-[#9E8AEC] text-[#9E8AEC] hover:bg-[#9E8AEC] hover:text-white font-bold rounded-xl px-6 py-2.5 text-xs w-full transition-all duration-200"
                                ),
                                Button(
                                    "🚀 Bắt đầu Đánh giá",
                                    type="submit",
                                    cls="btn bg-[#9E8AEC] hover:bg-[#8A75DE] text-white border-none font-bold rounded-xl px-6 py-2.5 text-xs transition-all duration-200 active:scale-[0.98] w-full"
                                ),
                                cls="flex flex-col gap-2 mt-4"
                            ),
                            
                            # HTMX integration
                            hx_post="/evaluate",
                            hx_target="#result-container",
                            hx_swap="innerHTML",
                            enctype="multipart/form-data",
                            onsubmit="""
                                const qText = document.getElementById('question_text').value.trim();
                                const qFile = document.getElementById('question_file').files.length;
                                if (!qText && qFile === 0) {
                                    alert('Vui lòng nhập đề bài hoặc nộp file đề bài!');
                                    return false;
                                }
                                const gradingMode = document.getElementById('grading_mode').value;
                                if (gradingMode === 'batch') {
                                    if (document.getElementById('batch_folder').files.length === 0) {
                                        alert('Vui lòng chọn thư mục chứa nhiều bài làm sinh viên!');
                                        return false;
                                    }
                                    const configMode = document.getElementById('config_mode').value;
                                    if (configMode === 'upload' && document.getElementById('config_file').files.length === 0) {
                                        alert('Vui lòng chọn file config JSON!');
                                        return false;
                                    }
                                    if (configMode === 'builtin') {
                                        const pid = document.getElementById('problem_id').value.trim();
                                        if (!pid && qFile === 0) {
                                            alert('Khi dùng config có sẵn, hãy nhập Problem ID hoặc upload file đề bài.');
                                            return false;
                                        }
                                    }
                                    return true;
                                }
                                const inputType = document.getElementById('code_input_type').value;
                                if (inputType === 'editor') {
                                    const val = window.editor ? window.editor.getValue() : document.getElementById('fallback_code').value;
                                    if(!val.trim()){
                                        alert('Vui lòng nhập mã nguồn sinh viên!');
                                        return false;
                                    }
                                    document.getElementById('student_code').value = val;
                                } else if (inputType === 'file') {
                                    if (document.getElementById('code_file').files.length === 0) {
                                        alert('Vui lòng chọn tệp tin mã nguồn sinh viên!');
                                        return false;
                                    }
                                } else if (inputType === 'folder') {
                                    if (document.getElementById('code_folder').files.length === 0) {
                                        alert('Vui lòng chọn thư mục mã nguồn sinh viên!');
                                        return false;
                                    }
                                }
                                const configMode = document.getElementById('config_mode').value;
                                if (configMode === 'upload') {
                                    if (document.getElementById('config_file').files.length === 0) {
                                        alert('Vui lòng chọn file config JSON!');
                                        return false;
                                    }
                                }
                                if (configMode === 'builtin') {
                                    const qFile = document.getElementById('question_file').files.length;
                                    const pid = document.getElementById('problem_id').value.trim();
                                    if (!pid && qFile === 0) {
                                        alert('Khi dùng config có sẵn, hãy nhập Problem ID hoặc upload file đề bài để tự nhận diện.');
                                        return false;
                                    }
                                }
                                return true;
                            """
                        ),
                        cls="dashboard-card p-6"
                    ),
                    cls="md:col-span-5 space-y-4"
                ),
                
                # Right Column: Results
                Div(
                    Div(
                        H2("Báo Cáo Đánh Giá", cls="text-lg md:text-xl font-bold text-slate-800 dark:text-slate-100 mb-4 border-b border-black/[0.02] pb-2"),
                        
                        # Result container which will receive the HTMX stream
                        Div(
                            Div(
                                Div(
                                    NotStr("""
                                    <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-[#9E8AEC]/10 flex items-center justify-center text-[#9E8AEC]">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                    """),
                                    Span("Chưa có dữ liệu đánh giá", cls="text-sm font-bold text-slate-600 dark:text-slate-300 block"),
                                    P("Nhập đề bài và mã nguồn sinh viên, sau đó bấm nút để nhận kết quả chi tiết.", cls="text-xs text-slate-400 dark:text-slate-500 mt-1.5 max-w-[280px] mx-auto"),
                                    cls="text-center p-8"
                                ),
                                cls="flex items-center justify-center min-h-[480px] placeholder-box"
                            ),
                            id="result-container", cls="space-y-4"
                        ),
                        cls="dashboard-card p-6 min-h-[550px]"
                    ),
                    cls="md:col-span-7"
                ),
                cls="grid grid-cols-1 md:grid-cols-12 gap-8"
            ),
            
            # Footer
            Div(
                P("© 2026 CodeEval Agent. Bản quyền đã được bảo hộ.", cls="text-[10px] text-slate-400 font-light"),
                cls="mt-16 text-center border-t border-black/[0.03] dark:border-white/5 pt-4 pb-8"
            ),
            
            # Script to initialize Monaco Editor and manage themes
            Script("""
                // Theme Toggle Function
                function toggleTheme() {
                    const container = document.getElementById('main-container');
                    const currentTheme = container.getAttribute('data-theme');
                    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                    
                    container.setAttribute('data-theme', newTheme);
                    localStorage.setItem('theme', newTheme);
                    
                    if (newTheme === 'dark') {
                        container.classList.add('dark');
                    } else {
                        container.classList.remove('dark');
                    }
                    
                    if (window.editor) {
                        monaco.editor.setTheme(newTheme === 'dark' ? 'vs-dark' : 'vs');
                    }
                }

                // Load saved theme on startup
                (function() {
                    const savedTheme = localStorage.getItem('theme') || 'light';
                    document.addEventListener('DOMContentLoaded', () => {
                        const container = document.getElementById('main-container');
                        if (container) {
                            container.setAttribute('data-theme', savedTheme);
                            if (savedTheme === 'dark') {
                                container.classList.add('dark');
                            } else {
                                container.classList.remove('dark');
                            }
                        }
                        const switchEl = document.getElementById('theme-switch');
                        if (switchEl) {
                            switchEl.checked = (savedTheme === 'dark');
                        }
                        
                        // Close preview modal when clicking backdrop
                        const modal = document.getElementById('preview_modal');
                        if (modal) {
                            modal.addEventListener('click', (e) => {
                                if (e.target === modal) {
                                    modal.close();
                                }
                            });
                        }
                        initFileUploadLabels();
                    });
                })();

                function initFileUploadLabels() {
                    document.querySelectorAll('.upload-file-input').forEach(input => {
                        if (input.dataset.bound === '1') return;
                        input.dataset.bound = '1';
                        input.addEventListener('change', function() {
                            const zone = this.closest('.upload-zone');
                            if (!zone) return;
                            let nameEl = zone.querySelector('.upload-filename');
                            if (!nameEl) {
                                nameEl = document.createElement('p');
                                nameEl.className = 'upload-filename';
                                zone.appendChild(nameEl);
                            }
                            if (!this.files || this.files.length === 0) {
                                nameEl.textContent = '';
                                return;
                            }
                            if (this.webkitdirectory || this.getAttribute('webkitdirectory') !== null) {
                                const folders = new Set();
                                Array.from(this.files).forEach(f => {
                                    const p = (f.webkitRelativePath || f.name || '').replace(/\\\\/g, '/');
                                    const top = p.split('/')[0];
                                    if (top) folders.add(top);
                                });
                                nameEl.textContent = folders.size
                                    ? `Đã chọn ${folders.size} thư mục · ${this.files.length} tệp`
                                    : `Đã chọn ${this.files.length} tệp`;
                            } else {
                                nameEl.textContent = this.files.length > 1
                                    ? `Đã chọn ${this.files.length} tệp`
                                    : `Đã chọn: ${this.files[0].name}`;
                            }
                        });
                    });
                }

                // Custom Select helpers
                function selectLang(val, label) {
                    document.getElementById('language').value = val;
                    document.getElementById('selected-lang').textContent = label;
                    if (window.editor) {
                        monaco.editor.setModelLanguage(window.editor.getModel(), val === 'cpp' ? 'cpp' : (val === 'java' ? 'java' : 'python'));
                    }
                    const details = document.getElementById('selected-lang').closest('details');
                    if (details) details.removeAttribute('open');
                }

                function selectModel(val, label) {
                    document.getElementById('model_select').value = val;
                    document.getElementById('selected-model').textContent = label;
                    const details = document.getElementById('selected-model').closest('details');
                    if (details) details.removeAttribute('open');
                }

                function selectConfigMode(mode, label) {
                    document.getElementById('config_mode').value = mode;
                    document.getElementById('selected-config-mode').textContent = label;
                    const builtinPanel = document.getElementById('config-builtin-panel');
                    const uploadPanel = document.getElementById('config-upload-panel');
                    if (builtinPanel) builtinPanel.classList.toggle('hidden', mode !== 'builtin');
                    if (uploadPanel) uploadPanel.classList.toggle('hidden', mode !== 'upload');
                    const details = document.getElementById('selected-config-mode').closest('details');
                    if (details) details.removeAttribute('open');
                }

                function switchGradingMode(mode) {
                    document.getElementById('grading_mode').value = mode;
                    const singleSection = document.getElementById('single-code-section');
                    const batchSection = document.getElementById('batch-code-section');
                    const tabSingle = document.getElementById('tab-grade-single');
                    const tabBatch = document.getElementById('tab-grade-batch');
                    const hint = document.getElementById('grading-mode-hint');
                    if (singleSection) singleSection.classList.toggle('hidden', mode !== 'single');
                    if (batchSection) batchSection.classList.toggle('hidden', mode !== 'batch');
                    if (tabSingle && tabBatch) {
                        if (mode === 'single') {
                            tabSingle.className = 'btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-[#9E8AEC] text-white border-none';
                            tabBatch.className = 'btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-none';
                        } else {
                            tabBatch.className = 'btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-[#9E8AEC] text-white border-none';
                            tabSingle.className = 'btn btn-xs rounded-full px-3 py-1 font-bold text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-none';
                        }
                    }
                    if (hint) {
                        hint.textContent = mode === 'batch'
                            ? 'Batch: mỗi thư mục con trong upload = 1 bài sinh viên.'
                            : 'Chấm từng bài: nhập code hoặc upload file/thư mục một sinh viên.';
                    }
                }

                // Global click listener to close details.dropdown when clicking outside
                document.addEventListener('click', function(e) {
                    const dropdowns = document.querySelectorAll('details.dropdown');
                    dropdowns.forEach(d => {
                        if (!d.contains(e.target)) {
                            d.removeAttribute('open');
                        }
                    });
                });

                // Switch between Code Input tabs (Editor, File, Folder)
                function switchCodeInput(type) {
                    document.getElementById('code_input_type').value = type;
                    const tabs = ['editor', 'file', 'folder'];
                    tabs.forEach(t => {
                        const btn = document.getElementById('tab-' + t);
                        const wrapper = document.getElementById(t + '-wrapper');
                        if (!btn || !wrapper) return;
                        
                        if (t === type) {
                            btn.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-500', 'dark:text-slate-400');
                            btn.classList.add('bg-[#9E8AEC]', 'text-white');
                            wrapper.classList.remove('hidden');
                        } else {
                            btn.classList.remove('bg-[#9E8AEC]', 'text-white');
                            btn.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-500', 'dark:text-slate-400');
                            wrapper.classList.add('hidden');
                        }
                    });
                }

                // Toggle Accordion dynamically
                function toggleAccordion(titleEl) {
                    const collapseEl = titleEl.closest('.collapse');
                    if (!collapseEl) return;
                    
                    const allCollapses = document.querySelectorAll('.collapse');
                    allCollapses.forEach(c => {
                        if (c !== collapseEl) {
                            c.classList.remove('collapse-open');
                        }
                    });
                    
                    collapseEl.classList.toggle('collapse-open');
                }

                // File reading helper
                function readFileAsText(file) {
                    return new Promise((resolve) => {
                        const reader = new FileReader();
                        reader.onload = (e) => resolve(e.target.result);
                        reader.onerror = () => resolve('Không thể đọc nội dung file.');
                        reader.readAsText(file);
                    });
                }

                // Open preview modal and populate data
                async function openPreview() {
                    const modal = document.getElementById('preview_modal');
                    const instrContent = document.getElementById('preview-instruction-content');
                    const codeContent = document.getElementById('preview-code-content');
                    
                    if(!modal || !instrContent || !codeContent) return;
                    
                    instrContent.innerHTML = 'Đang tải...';
                    codeContent.innerHTML = 'Đang tải...';
                    
                    // 1. Get Instruction Content
                    const instrText = document.getElementById('question_text').value.trim();
                    const instrFiles = document.getElementById('question_file').files;
                    
                    if (instrText) {
                        instrContent.textContent = instrText;
                    } else if (instrFiles.length > 0) {
                        const file = instrFiles[0];
                        if (file.name.endsWith('.pdf') || file.name.endsWith('.docx')) {
                            instrContent.textContent = `Tệp tin: ${file.name} (${(file.size/1024).toFixed(1)} KB) - Định dạng tài liệu nhị phân sẽ được trích xuất trên server.`;
                        } else {
                            const text = await readFileAsText(file);
                            instrContent.textContent = `Tệp tin: ${file.name}\\n-------------------\\n\n${text}`;
                        }
                    } else {
                        instrContent.textContent = '(Trống - Chưa nhập đề bài)';
                    }
                    
                    // 2. Get Student Code Content
                    const inputType = document.getElementById('code_input_type').value;
                    codeContent.innerHTML = '';
                    
                    if (inputType === 'editor') {
                        const val = window.editor ? window.editor.getValue() : document.getElementById('fallback_code').value;
                        const div = document.createElement('div');
                        div.className = 'p-4 bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-white/5 rounded-2xl text-xs font-mono break-words whitespace-pre-wrap max-h-60 overflow-y-auto';
                        div.textContent = val.trim() ? val : '(Trống - Chưa nhập mã nguồn)';
                        codeContent.appendChild(div);
                    } else if (inputType === 'file') {
                        const codeFiles = document.getElementById('code_file').files;
                        if (codeFiles.length > 0) {
                            const file = codeFiles[0];
                            const text = await readFileAsText(file);
                            const title = document.createElement('div');
                            title.className = 'text-[11px] font-bold text-slate-500 mb-1';
                            title.textContent = `File: ${file.name}`;
                            const div = document.createElement('div');
                            div.className = 'p-4 bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-white/5 rounded-2xl text-xs font-mono break-words whitespace-pre-wrap max-h-60 overflow-y-auto';
                            div.textContent = text;
                            codeContent.appendChild(title);
                            codeContent.appendChild(div);
                        } else {
                            codeContent.textContent = '(Chưa chọn file mã nguồn)';
                        }
                    } else if (inputType === 'folder') {
                        const codeFolderFiles = document.getElementById('code_folder').files;
                        if (codeFolderFiles.length > 0) {
                            const filesArr = Array.from(codeFolderFiles).filter(f => {
                                const ext = f.name.split('.').pop().toLowerCase();
                                return ['cpp', 'cc', 'cxx', 'c', 'py', 'java'].includes(ext);
                            });
                            
                            if (filesArr.length === 0) {
                                codeContent.textContent = '(Thư mục không chứa file mã nguồn hợp lệ .py, .cpp, .java)';
                            } else {
                                for (const file of filesArr) {
                                    const text = await readFileAsText(file);
                                    const fileDiv = document.createElement('div');
                                    fileDiv.className = 'mb-4 last:mb-0';
                                    
                                    const title = document.createElement('div');
                                    title.className = 'text-[11px] font-bold text-slate-500 mb-1 flex items-center justify-between';
                                    title.innerHTML = `<span>📂 ${file.webkitRelativePath || file.name}</span><span class="text-[9px] text-slate-400">${(file.size/1024).toFixed(1)} KB</span>`;
                                    
                                    const div = document.createElement('div');
                                    div.className = 'p-4 bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-white/5 rounded-2xl text-xs font-mono break-words whitespace-pre-wrap max-h-40 overflow-y-auto';
                                    div.textContent = text;
                                    
                                    fileDiv.appendChild(title);
                                    fileDiv.appendChild(div);
                                    codeContent.appendChild(fileDiv);
                                }
                            }
                        } else {
                            codeContent.textContent = '(Chưa chọn thư mục)';
                        }
                    }
                    
                    modal.showModal();
                }

                // Initialize Monaco Editor
                function initMonaco() {
                    if (typeof require !== 'undefined') {
                        require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' } });
                        require(['vs/editor/editor'], function () {
                            const container = document.getElementById('editor-container');
                            if (!container) return;
                            const fallbackVal = document.getElementById('fallback_code').value;
                            container.innerHTML = ''; // Clear fallback textarea
                            
                            const savedTheme = localStorage.getItem('theme') || 'light';
                            window.editor = monaco.editor.create(container, {
                                value: fallbackVal || `# Nhập mã nguồn của bạn ở đây...\\ndef longest_substring(s: str) -> int:\\n    pass`,
                                language: 'python',
                                theme: savedTheme === 'dark' ? 'vs-dark' : 'vs',
                                automaticLayout: true,
                                fontSize: 13,
                                minimap: { enabled: false },
                                scrollBeyondLastLine: false,
                                lineNumbers: 'on',
                                roundedSelection: true,
                                cursorStyle: 'line',
                                padding: { top: 10, bottom: 10 }
                            });
                            // Hook language select change
                            document.getElementById('language').addEventListener('change', function(e) {
                                const lang = e.target.value;
                                monaco.editor.setModelLanguage(window.editor.getModel(), lang === 'cpp' ? 'cpp' : (lang === 'java' ? 'java' : 'python'));
                            });
                        });
                    } else {
                        setTimeout(initMonaco, 100);
                    }
                }
                initMonaco();
            """),
            id="main-container",
            cls="w-full px-4 md:px-8 font-sans min-h-screen text-base-content",
            data_theme="light"
        ),
        # Dialog modal for previewing files on the client side
        NotStr("""
        <dialog id="preview_modal" class="modal">
          <div class="modal-box max-w-4xl bg-white dark:bg-[#131A26] rounded-3xl p-6 border border-slate-100 dark:border-white/5">
            <h3 class="font-extrabold text-lg text-slate-800 dark:text-slate-100 border-b border-black/[0.03] dark:border-white/5 pb-3">👁️ Xem trước thông tin</h3>
            
            <div class="py-4 space-y-6 max-h-[60vh] overflow-y-auto pr-2">
              <!-- Instruction Preview Section -->
              <div>
                <h4 class="text-xs font-extrabold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">1. Đề bài (Problem)</h4>
                <div id="preview-instruction-content" class="p-4 bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-white/5 rounded-2xl text-xs font-mono break-words whitespace-pre-wrap max-h-40 overflow-y-auto"></div>
              </div>
              
              <!-- Student Code Preview Section -->
              <div>
                <h4 class="text-xs font-extrabold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">2. Mã nguồn sinh viên (Student Code)</h4>
                <div id="preview-code-content" class="space-y-4"></div>
              </div>
            </div>
            
            <div class="modal-action border-t border-black/[0.03] dark:border-white/5 pt-3">
              <form method="dialog">
                <button class="btn btn-sm rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 border-none font-bold px-4">Đóng</button>
              </form>
            </div>
          </div>
        </dialog>
        """)
    )

@rt("/evaluate")
async def post(request):
    import uuid
    import tempfile
    import os
    import shutil
    from codejudge.core.compiler_helper import merge_folder_code

    form = await request.form()
    
    language = form.get("language", "python")
    model_select = form.get("model_select", "")
    code_input_type = form.get("code_input_type", "editor")
    
    # 1. Parse LLM provider and model_name
    if "|" in model_select:
        provider, model_name = model_select.split("|", 1)
    else:
        provider, model_name = "openrouter", model_select

    # 2. Extract problem statement (Instruction)
    question_text = form.get("question_text", "").strip()
    question_file = form.get("question_file") # UploadFile
    problem_id = ""
    
    if question_file and question_file.filename:
        problem_id = os.path.splitext(question_file.filename)[0]
        try:
            content_bytes = await question_file.read()
            filename_lower = question_file.filename.lower()
            if filename_lower.endswith((".txt", ".md")):
                extracted_text = content_bytes.decode("utf-8", errors="ignore")
            elif filename_lower.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(content_bytes)
            elif filename_lower.endswith(".docx"):
                extracted_text = extract_text_from_docx(content_bytes)
            else:
                extracted_text = content_bytes.decode("utf-8", errors="ignore")
            
            if extracted_text.strip():
                question_text = extracted_text.strip()
        except Exception as e:
            logger.error(f"Error reading question file: {e}")

    if not problem_id:
        if "pokemon.txt" in question_text.lower() and "pokemon" in question_text.lower():
            problem_id = "1_final"
        elif "automorphic" in question_text.lower():
            problem_id = "48_midterm-123"
        elif "đối xứng" in question_text.lower() and "đường chéo" in question_text.lower():
            problem_id = "96_final-123"

    manual_problem_id = form.get("problem_id", "").strip()
    if manual_problem_id:
        problem_id = manual_problem_id

    config_mode = form.get("config_mode", "none")
    config_file = form.get("config_file")
    config_file_bytes = None
    if config_file and getattr(config_file, "filename", None):
        try:
            config_file_bytes = await config_file.read()
        except Exception as e:
            logger.error(f"Error reading config file: {e}")
            return HTMLResponse(content=f"""
            <div class="p-4 bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/50 rounded-2xl text-sm text-rose-600 dark:text-rose-400">
                Không thể đọc file config: {e}
            </div>
            """)

    try:
        problem_config, config_source = resolve_problem_config(config_mode, problem_id, config_file_bytes)
    except ValueError as e:
        return HTMLResponse(content=f"""
        <div class="p-4 bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/50 rounded-2xl text-sm text-rose-600 dark:text-rose-400">
            Lỗi cấu hình chấm điểm: {e}
        </div>
        """)

    grading_mode = form.get("grading_mode", "single")

    # --- Batch grading mode ---
    if grading_mode == "batch":
        batch_files = form.getlist("batch_folder")
        if not batch_files:
            return HTMLResponse(content="""
            <div class="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-sm text-rose-600">
                Vui lòng chọn thư mục chứa nhiều bài làm sinh viên.
            </div>
            """)

        temp_dir = tempfile.mkdtemp()
        for uf in batch_files:
            if uf.filename:
                rel = uf.filename.replace("\\", "/")
                dest = os.path.join(temp_dir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                content_bytes = await uf.read()
                with open(dest, "wb") as f:
                    f.write(content_bytes)

        submissions = group_batch_submissions_root(temp_dir)
        if not submissions:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return HTMLResponse(content="""
            <div class="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-sm text-rose-600">
                Không tìm thấy thư mục bài làm con. Mỗi thư mục con trong upload phải là 1 sinh viên.
            </div>
            """)

        task_id = str(uuid.uuid4())
        EVAL_STATUS[task_id] = {
            "status": "running",
            "step": 1,
            "html": render_batch_progress_html(task_id, 0, len(submissions), [], "Khởi tạo batch...")
        }
        asyncio.create_task(
            run_batch_evaluation_task(
                task_id, question_text, submissions, language, provider, model_name,
                problem_id=problem_id, problem_config=problem_config, config_source=config_source,
                temp_dir_to_clean=temp_dir,
            )
        )
        return HTMLResponse(content=EVAL_STATUS[task_id]["html"])

    # --- Single submission mode ---
    # 3. Extract student code and set up temp files
    student_code = ""
    temp_dir = tempfile.mkdtemp()
    source_path = None
    
    if code_input_type == "editor":
        student_code = form.get("student_code", "")
        # Save Monaco Editor content to a temp file for syntax check
        ext = ".py" if language == "python" else (".java" if language == "java" else ".cpp")
        temp_file_path = os.path.join(temp_dir, f"student_code{ext}")
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(student_code)
        source_path = temp_file_path
        
    elif code_input_type == "file":
        code_file = form.get("code_file") # UploadFile
        if code_file and code_file.filename:
            content_bytes = await code_file.read()
            student_code = content_bytes.decode("utf-8", errors="ignore")
            
            temp_file_path = os.path.join(temp_dir, code_file.filename)
            with open(temp_file_path, "wb") as f:
                f.write(content_bytes)
            source_path = temp_file_path
            
    elif code_input_type == "folder":
        code_files = form.getlist("code_folder") # List[UploadFile]
        saved_files = []
        for uf in code_files:
            if uf.filename:
                # Reconstruct directory structure if available
                file_path = os.path.join(temp_dir, uf.filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                content_bytes = await uf.read()
                with open(file_path, "wb") as f:
                    f.write(content_bytes)
                saved_files.append(file_path)
                
        # Resolve source_path if there is a single top-level directory in temp_dir
        top_level_items = os.listdir(temp_dir)
        source_path = temp_dir
        if len(top_level_items) == 1:
            single_item = os.path.join(temp_dir, top_level_items[0])
            if os.path.isdir(single_item):
                source_path = single_item
                
        # Merge all folder files into student_code
        student_code = merge_folder_code(source_path, language)

    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    initial_steps_html = render_progress_steps(1)
    # Initialize global status for this task
    EVAL_STATUS[task_id] = {
        "status": "running",
        "step": 1,
        "html": f"""
        <div id="evaluation-progress-container" hx-get="/evaluate/status/{task_id}" hx-trigger="every 1s" hx-swap="outerHTML" class="p-6 bg-slate-50/50 dark:bg-slate-900/30 border border-slate-100 dark:border-white/5 rounded-2xl min-h-[380px] flex flex-col justify-between">
            <div>
                <div class="flex items-center space-x-3 mb-6 border-b border-black/[0.03] dark:border-white/5 pb-3">
                    <span class="loading loading-spinner text-[#9E8AEC] loading-sm"></span>
                    <h3 class="font-extrabold text-sm text-slate-800 dark:text-slate-100">Tiến trình đánh giá bài làm</h3>
                </div>
                {initial_steps_html}
            </div>
            <div class="text-[10px] text-slate-400 dark:text-slate-500 text-center border-t border-black/[0.02] dark:border-white/5 pt-3 mt-4">
                Hệ thống Multi-Agent đang chạy song song để chấm điểm và phân tích mã nguồn của bạn. Vui lòng chờ trong giây lát.
            </div>
        </div>
        """
    }
    
    # Start background execution
    asyncio.create_task(
        run_evaluation_task(
            task_id, question_text, student_code, language, provider, model_name,
            source_path=source_path, temp_dir_to_clean=temp_dir, problem_id=problem_id,
            problem_config=problem_config, config_source=config_source
        )
    )
    
    # Return the initial polling element
    return HTMLResponse(content=EVAL_STATUS[task_id]["html"])

@rt("/evaluate/status/{task_id}")
def get(task_id: str):
    if task_id not in EVAL_STATUS:
        return HTMLResponse(content=f"""
        <div id="evaluation-progress-container" hx-get="/evaluate/status/{task_id}" hx-trigger="every 1s" hx-swap="outerHTML" class="p-4 text-center text-xs text-base-content/50">
            <span class="loading loading-spinner loading-xs mr-2"></span> Đang kết nối server...
        </div>
        """)
    return HTMLResponse(content=EVAL_STATUS[task_id]["html"])

# Global state to store evaluation progress
EVAL_STATUS = {}

def render_accordion_html(question_evals, language):
    import re
    accordion_html = ""
    # Define pastel themes
    pastel_themes = [
        # Blue
        {
            "bg": "bg-[#F0F7FF] dark:bg-[#15233A] border-[#D0E5FF] dark:border-[#243F6A]",
            "badge": "bg-[#D0E5FF] text-[#1D549D] dark:bg-[#243F6A] dark:text-[#7EB5FF]",
            "text": "text-slate-700 dark:text-slate-200"
        },
        # Pink
        {
            "bg": "bg-[#FDF2F4] dark:bg-[#2A1822] border-[#FAD5DC] dark:border-[#4F203A]",
            "badge": "bg-[#FAD5DC] text-[#971D3E] dark:bg-[#4F203A] dark:text-[#FFA1B8]",
            "text": "text-slate-700 dark:text-slate-200"
        },
        # Mint
        {
            "bg": "bg-[#F0FCF7] dark:bg-[#11271D] border-[#C7F5E6] dark:border-[#1E4D3B]",
            "badge": "bg-[#C7F5E6] text-[#055C41] dark:bg-[#1E4D3B] dark:text-[#5BE8B9]",
            "text": "text-slate-700 dark:text-slate-200"
        }
    ]
    
    for idx, q_res in enumerate(question_evals):
        q_name = q_res["question_name"]
        q_max = q_res["question_max"]
        q_score = q_res["scoring"].get("scaled_score", 0.0)
        
        # Cycle through pastel themes
        theme = pastel_themes[idx % len(pastel_themes)]
        
        # First question expanded by default
        checked_attr = "checked" if idx == 0 else ""
        
        # Build factors list
        factors_html = ""
        for factor, details in q_res["factor_eval"].items():
            compliance = details.get("compliance", 0)
            reasoning = details.get("reasoning", "")
            comp_percent = int(compliance * 100)
            
            # Compliance pill colors
            if compliance >= 0.8:
                bg_pill = "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
            elif compliance >= 0.5:
                bg_pill = "bg-amber-500/10 text-amber-600 dark:text-amber-400"
            else:
                bg_pill = "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                
            factors_html += f"""
            <div class="py-2 border-b border-black/[0.03] dark:border-white/[0.03] last:border-b-0">
                <div class="flex items-center justify-between gap-4">
                    <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">{factor}</span>
                    <span class="text-[10px] font-bold px-1.5 py-0.5 rounded-full {bg_pill}">{comp_percent}%</span>
                </div>
                <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">{reasoning}</p>
            </div>
            """
            
        # Build suggestions list
        suggestions_html = ""
        q_suggs = q_res.get("suggestions", [])
        if q_suggs:
            suggs_items = "".join([f"<li class='text-[11px] list-disc list-inside text-slate-600 dark:text-slate-300 ml-1 py-0.5'>{s}</li>" for s in q_suggs])
            suggestions_html = f"""
            <div class="mt-3 pt-3 border-t border-black/[0.04] dark:border-white/[0.04]">
                <span class="text-[10px] text-[#9E8AEC] font-bold uppercase tracking-wider block mb-1">💡 Đề Xuất & Gợi Ý Cải Thiện</span>
                <ul class="space-y-0.5">
                    {suggs_items}
                </ul>
            </div>
            """
        else:
            suggestions_html = f"""
            <div class="mt-3 pt-3 border-t border-black/[0.04] dark:border-white/[0.04]">
                <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-1">💡 Đề Xuất & Gợi Ý Cải Thiện</span>
                <p class="text-[11px] italic text-slate-400">Không có đề xuất cải thiện.</p>
            </div>
            """
            
        # Compile errors
        syntax_err_html = ""
        syntax_errs = q_res.get("syntax_errors", [])
        if syntax_errs:
            err_clean = [re.sub(r'<[^>]+>', '', e) for e in syntax_errs]
            err_display = re.sub(r'/[^:\s]+', 'student_code.' + ('py' if language == 'python' else 'cpp'), err_clean[0])
            syntax_err_html = f"""
            <div class="mb-3 p-2 bg-rose-950/20 border border-rose-900/40 rounded-lg text-rose-400 text-[10px] font-mono break-words whitespace-pre-wrap max-w-full overflow-x-auto">
                <span class="font-bold">⚠️ Lỗi biên dịch:</span> {err_display}
            </div>
            """
            
        initial_open_class = "collapse-open" if idx == 0 else ""
        accordion_html += f"""
        <div class="collapse collapse-arrow {theme['bg']} border rounded-2xl mb-3 shadow-sm hover:shadow-md transition-all duration-200 {initial_open_class}">
            <div class="collapse-title flex justify-between items-center pr-12 py-3 cursor-pointer" onclick="toggleAccordion(this)">
                <span class="text-sm font-bold text-slate-800 dark:text-slate-100">{q_name}</span>
                <span class="text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap flex-shrink-0 {theme['badge']} ml-4">{q_score:.2f} <span class="opacity-60 font-normal">/ {q_max:.1f}đ</span></span>
            </div>
            <div class="collapse-content px-5 pb-5 pt-0">
                {syntax_err_html}
                <div class="space-y-1">
                    <span class="text-[9px] text-slate-400 font-bold uppercase tracking-wider block border-b border-black/[0.03] dark:border-white/[0.03] pb-1 mb-1">📊 Chi Tiết Tiêu Chí</span>
                    {factors_html}
                </div>
                {suggestions_html}
            </div>
        </div>
        """
    return accordion_html

def render_results_block_html(question_evals, total_max_score, final_score, factor_score, syntax_penalty, model_name, provider, language, question_text):
    # Calculate percentage for circle
    circle_percentage = min(100.0, max(0.0, (final_score / total_max_score) * 100.0)) if total_max_score > 0 else 0.0
    
    # Model display
    model_display = model_name.split('/')[-1] if '/' in model_name else model_name
    
    # Assignment name
    lines = [l.strip() for l in question_text.splitlines() if l.strip()]
    assignment_name = lines[0][:40] + "..." if lines and len(lines[0]) > 40 else (lines[0] if lines else "Student Code")
    
    # Render accordion list
    accordion_html = render_accordion_html(question_evals, language)
    
    html = f"""
    <div class="space-y-6">
        <!-- Part 1: Overview -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-6 p-6 bg-slate-50/50 dark:bg-slate-900/25 rounded-2xl border border-slate-100 dark:border-white/5 shadow-sm animate-fade-in">
            <!-- SVG Arc Gauge -->
            <div class="relative flex flex-col items-center justify-center w-full sm:w-auto">
                <div class="relative w-44 h-24">
                    <svg viewBox="0 0 120 70" class="w-full h-full">
                        <defs>
                            <linearGradient id="arc-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="#8BD3DD" />
                                <stop offset="50%" stop-color="#A8E6CF" />
                                <stop offset="100%" stop-color="#FFAAA6" />
                            </linearGradient>
                        </defs>
                        <!-- Background arc -->
                        <path d="M 15 60 A 45 45 0 0 1 105 60" stroke="var(--input-bg)" stroke-width="8" stroke-linecap="round" fill="none" />
                        <!-- Active arc -->
                        <path d="M 15 60 A 45 45 0 0 1 105 60" stroke="url(#arc-grad)" stroke-width="8" stroke-linecap="round" fill="none"
                              stroke-dasharray="142" stroke-dashoffset="{142 - (142 * circle_percentage) / 100}"
                              class="transition-all duration-1000 ease-out" />
                    </svg>
                    <div class="absolute bottom-1 left-0 right-0 flex flex-col items-center">
                        <span class="text-[8px] uppercase tracking-wider font-extrabold text-slate-400">Final Score</span>
                        <span class="text-xl font-black text-slate-800 dark:text-slate-100 mt-0.5">{final_score:.2f} <span class="text-[10px] font-semibold text-slate-400">/ {total_max_score:.1f}</span></span>
                    </div>
                </div>
            </div>
            
            <!-- Summary Stats -->
            <div class="flex-1 w-full space-y-3">
                <div class="border-b border-black/[0.03] dark:border-white/[0.03] pb-1.5">
                    <span class="text-[8px] text-slate-400 font-extrabold uppercase tracking-wider">Evaluation Summary</span>
                    <h4 class="text-xs font-bold text-slate-700 dark:text-slate-200 mt-0.5 truncate" title="{assignment_name}">Assignment: {assignment_name}</h4>
                </div>
                
                <div class="grid grid-cols-3 gap-2">
                    <div class="flex flex-col p-2 rounded-xl bg-white dark:bg-[#1A2333] border border-slate-100 dark:border-white/5 shadow-sm">
                        <span class="text-[8px] text-slate-400 font-bold uppercase tracking-wider">Logical Score</span>
                        <span class="text-xs font-black text-emerald-500 mt-0.5">{factor_score:.2f}</span>
                    </div>
                    <div class="flex flex-col p-2 rounded-xl bg-white dark:bg-[#1A2333] border border-slate-100 dark:border-white/5 shadow-sm">
                        <span class="text-[8px] text-slate-400 font-bold uppercase tracking-wider">Syntax Penalty</span>
                        <span class="text-xs font-black text-rose-500 mt-0.5">-{syntax_penalty:.2f}</span>
                    </div>
                    <div class="flex flex-col p-2 rounded-xl bg-white dark:bg-[#1A2333] border border-slate-100 dark:border-white/5 shadow-sm overflow-hidden">
                        <span class="text-[8px] text-slate-400 font-bold uppercase tracking-wider">LLM Model</span>
                        <span class="text-[10px] font-bold text-[#9E8AEC] mt-0.5 truncate" title="{model_name}">{model_display}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Part 2: Detailed Questions Accordion -->
        <div class="space-y-3">
            <span class="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider block border-b border-black/[0.03] dark:border-white/[0.03] pb-1 mb-2">Detailed Questions</span>
            {accordion_html}
        </div>
    </div>
    """
    return html

def render_progress_steps(step_num: int) -> str:
    steps = [
        ("Bước 1: Khởi tạo và kiểm tra biên dịch (Syntax Check)", 1),
        ("Bước 2: Agent 1 - Trích xuất các tiêu chí chấm điểm (Criteria Extraction)", 2),
        ("Bước 3: Agent 2 - Đánh giá và chấm điểm chi tiết (Multi-Agent Grading)", 3),
        ("Bước 4: Tổng hợp kết quả và xây dựng báo cáo", 4)
    ]
    
    steps_html = ""
    for label, num in steps:
        if num < step_num:
            # Completed
            icon = '<span class="text-emerald-500 font-bold">✓</span>'
            cls = "bg-emerald-500/5 text-slate-800 dark:text-slate-200 border-emerald-500/20"
            badge = "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
        elif num == step_num:
            # Active (loading)
            icon = '<span class="loading loading-spinner text-[#9E8AEC] loading-xs"></span>'
            cls = "bg-[#9E8AEC]/10 text-[#5C4EB7] dark:text-[#B4A5F4] border-[#9E8AEC]/20 shadow-sm font-semibold animate-pulse"
            badge = "bg-[#9E8AEC]/20 text-[#5C4EB7] dark:text-[#B4A5F4]"
        else:
            # Pending
            icon = '<span class="text-slate-300 dark:text-slate-600">•</span>'
            cls = "text-slate-400 dark:text-slate-500 opacity-60 border-transparent"
            badge = "bg-slate-100 dark:bg-slate-800 text-slate-400"
            
        steps_html += f"""
        <div class="flex items-center justify-between p-3.5 border rounded-xl transition-all duration-300 {cls}">
            <div class="flex items-center space-x-3">
                <div class="flex items-center justify-center w-6 h-6 rounded-full {badge} text-xs font-bold">
                    {icon}
                </div>
                <span class="text-xs">{label}</span>
            </div>
            <span class="text-[10px] font-bold uppercase tracking-wider opacity-60">
                {"Hoàn thành" if num < step_num else ("Đang xử lý" if num == step_num else "Chờ")}
            </span>
        </div>
        """
        
    return f"""
    <div class="space-y-3">
        {steps_html}
    </div>
    """

def update_html(task_id: str, step_num: int, step_1_html: str = "", step_2_html: str = "", step_3_html: str = "", step_4_html: str = ""):
    # If running, include the hx-trigger to poll again
    poll_attr = f'hx-get="/evaluate/status/{task_id}" hx-trigger="every 1s" hx-swap="outerHTML"' if EVAL_STATUS[task_id]["status"] == "running" else ""
    
    if EVAL_STATUS[task_id]["status"] == "running":
        progress_steps = render_progress_steps(step_num)
        EVAL_STATUS[task_id]["html"] = f"""
        <div id="evaluation-progress-container" {poll_attr} class="p-6 bg-slate-50/50 dark:bg-slate-900/30 border border-slate-100 dark:border-white/5 rounded-2xl min-h-[380px] flex flex-col justify-between">
            <div>
                <div class="flex items-center space-x-3 mb-6 border-b border-black/[0.03] dark:border-white/5 pb-3">
                    <span class="loading loading-spinner text-[#9E8AEC] loading-sm"></span>
                    <h3 class="font-extrabold text-sm text-slate-800 dark:text-slate-100">Tiến trình đánh giá bài làm</h3>
                </div>
                {progress_steps}
            </div>
            <div class="text-[10px] text-slate-400 dark:text-slate-500 text-center border-t border-black/[0.02] dark:border-white/5 pt-3 mt-4">
                Hệ thống Multi-Agent đang chạy song song để chấm điểm và phân tích mã nguồn của bạn. Vui lòng chờ trong giây lát.
            </div>
        </div>
        """
    elif EVAL_STATUS[task_id]["status"] == "completed":
        # Simply set the complete HTML block
        EVAL_STATUS[task_id]["html"] = f"""
        <div id="evaluation-progress-container" class="animate-fade-in">
            {step_4_html}
        </div>
        """
    else:
        # Failed state
        EVAL_STATUS[task_id]["html"] = f"""
        <div id="evaluation-progress-container" class="flex flex-col items-center justify-center p-8 bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/50 rounded-2xl min-h-[380px]">
            <span class="text-3xl mb-4">❌</span>
            <span class="text-sm font-bold text-rose-600 dark:text-rose-400">Đánh giá thất bại</span>
            <p class="text-xs text-rose-400 dark:text-rose-500 text-center mt-2">
                Đã xảy ra lỗi trong quá trình xử lý. Vui lòng kiểm tra lại mã nguồn hoặc thử lại sau.
            </p>
        </div>
        """

def split_questions(problem_text: str) -> list:
    """Split a problem file into question blocks, e.g. Cau/Bai 1,2,3."""
    parts = re.split(r"(?=^\s*(?:C\S*u|B\S*i)\s*\d+)", problem_text, flags=re.MULTILINE)
    blocks = [p.strip() for p in parts if p.strip()]
    return blocks if blocks else [problem_text.strip()]

def parse_question_max(question_text: str) -> Optional[float]:
    """Extract per-question max score from heading, e.g. '(3đ)' or '(2.5 điểm)'."""
    patterns = [
        r"\((\d+(?:[\.,]\d+)?)\s*đ\)",
        r"\((\d+(?:[\.,]\d+)?)\s*điểm\)",
        r"\b(\d+(?:[\.,]\d+)?)\s*đ\b",
        r"\b(\d+(?:[\.,]\d+)?)\s*điểm\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, question_text, flags=re.IGNORECASE)
        if match:
            raw = match.group(1).replace(",", ".")
            try:
                value = float(raw)
                if value > 0:
                    return value
            except ValueError:
                continue
    return None

def list_code_files(student_dir: str) -> list:
    """Sort Bai01/Bai02/... files or directories in stable numeric order."""
    def key_fn(name: str):
        m = re.search(r"(\d+)", name)
        return int(m.group(1)) if m else 10**9

    entries = []
    if os.path.isdir(student_dir):
        for name in os.listdir(student_dir):
            p = os.path.join(student_dir, name)
            if os.path.isfile(p) and os.path.splitext(name)[1].lower() in {".cpp", ".cc", ".cxx", ".c", ".py"}:
                entries.append(p)
            elif os.path.isdir(p) and not name.startswith("."):
                entries.append(p)
    return sorted(entries, key=lambda x: key_fn(os.path.basename(x)))

BATCH_MAX_CONCURRENCY = 2

def _batch_sort_key(name: str):
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else 10**9

def group_batch_submissions_root(temp_dir: str) -> list:
    """Group uploaded batch folder into one submission per immediate subfolder."""
    root = temp_dir
    entries = [e for e in os.listdir(root) if not e.startswith(".")]
    if len(entries) == 1:
        only_path = os.path.join(root, entries[0])
        if os.path.isdir(only_path):
            children = [c for c in os.listdir(only_path) if not c.startswith(".")]
            if children and any(os.path.isdir(os.path.join(only_path, c)) for c in children):
                root = only_path
                entries = [c for c in children if os.path.isdir(os.path.join(only_path, c))]

    submissions = []
    for name in sorted(entries, key=_batch_sort_key):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            submissions.append({"student_id": name, "source_path": path})
    return submissions

async def extract_factors_for_questions(questions: list, problem_config: dict, provider: str, model_name: str) -> dict:
    """Pre-extract factors for all questions (shared across batch submissions)."""
    import asyncio
    factors_by_question = {}

    async def extract_one(idx: int, q_text: str):
        question_config = problem_config.get(str(idx), {})
        pre_factors = question_config.get("pre_extracted_factors")
        if pre_factors is not None:
            return idx, pre_factors
        try:
            local_client = LLMFactory.create(provider=provider, model_name=model_name)
            local_assessor = MultiAgentAssessor(llm_client=local_client)
            factors = await asyncio.to_thread(local_assessor.extract_factors, q_text)
            return idx, factors
        except Exception as e:
            logger.error(f"Error extracting factors for Q{idx}: {e}")
            return idx, ["Thực hiện đúng logic của câu hỏi"]

    results = await asyncio.gather(*[
        extract_one(idx, q_text) for idx, q_text in enumerate(questions, start=1)
    ])
    for idx, factors in results:
        factors_by_question[idx] = factors
    return factors_by_question

async def evaluate_submission_core(
    questions: list,
    language: str,
    provider: str,
    model_name: str,
    source_path: str,
    problem_config: dict,
    factors_by_question: dict,
) -> dict:
    """Grade one student submission folder."""
    import asyncio
    from codejudge.core.compiler_helper import merge_folder_code

    assessor = MultiAgentAssessor(llm_client=LLMFactory.create(provider=provider, model_name=model_name))
    code_files = list_code_files(source_path) if source_path and os.path.isdir(source_path) else []
    question_evals = []

    async def grade_one_question(idx: int, q_text: str):
        factors = factors_by_question.get(idx, ["Thực hiện đúng logic của câu hỏi"])
        if code_files and (idx - 1) < len(code_files):
            file_path = code_files[idx - 1]
            if os.path.isdir(file_path):
                code_i = merge_folder_code(file_path, language)
                source_path_i = file_path
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code_i = f.read()
                source_path_i = file_path
        else:
            code_i = merge_folder_code(source_path, language) if source_path else ""
            source_path_i = source_path

        syntax_errors_i = check_syntax(source_path_i if source_path_i else code_i, language)
        question_config = problem_config.get(str(idx), {})
        f_weights = question_config.get("factor_weights")
        s_penalties = question_config.get("syntax_penalties")
        qmax = parse_question_max(q_text)
        if qmax is None:
            qmax = 10.0 / len(questions)

        try:
            local_client = LLMFactory.create(provider=provider, model_name=model_name)
            local_assessor = MultiAgentAssessor(llm_client=local_client)
            factor_eval = await asyncio.to_thread(
                local_assessor.assess_factors, code_i, factors, language, use_cache=False
            )
        except Exception as e:
            logger.error(f"Error assessing factors for Q{idx}: {e}")
            factor_eval = {
                f: {"compliance": -1.0, "reasoning": f"Lỗi chấm LLM: {e}"} for f in factors
            }

        scoring = assessor.calculate_score(
            factor_eval=factor_eval,
            syntax_errors=syntax_errors_i,
            question_max=qmax,
            factor_weights=f_weights,
            syntax_penalties=s_penalties,
        )
        suggestions = assessor.generate_suggestions(factor_eval, syntax_errors_i)
        return {
            "question_index": idx,
            "question_name": q_text.splitlines()[0].strip() if q_text else f"Câu {idx}",
            "question_max": qmax,
            "factor_eval": factor_eval,
            "scoring": scoring,
            "suggestions": suggestions,
            "syntax_errors": syntax_errors_i,
            "code_file": os.path.basename(code_files[idx - 1]) if (code_files and (idx - 1) < len(code_files)) else "student_code",
        }

    graded = await asyncio.gather(*[grade_one_question(idx, q_text) for idx, q_text in enumerate(questions, start=1)])
    question_evals = sorted(graded, key=lambda x: x["question_index"])

    total_max_score = sum(q["question_max"] for q in question_evals)
    final_score = sum(q["scoring"].get("scaled_score", 0.0) for q in question_evals)
    factor_score = sum((q["scoring"].get("factor_score_on_10", 0.0) / 10.0) * q["question_max"] for q in question_evals)
    syntax_penalty = sum((q["scoring"].get("syntax_penalty_on_10", 0.0) / 10.0) * q["question_max"] for q in question_evals)

    return {
        "question_evals": question_evals,
        "total_max_score": total_max_score,
        "final_score": final_score,
        "factor_score": factor_score,
        "syntax_penalty": syntax_penalty,
    }

def render_batch_progress_html(task_id: str, done: int, total: int, results: list, current_student: str = "") -> str:
    poll_attr = f'hx-get="/evaluate/status/{task_id}" hx-trigger="every 1s" hx-swap="outerHTML"'
    pct = int((done / total) * 100) if total else 0
    rows = ""
    for r in results:
        sid = html.escape(str(r.get("student_id", "")))
        if r.get("error"):
            score_cell = f'<span class="text-rose-500 text-xs">{html.escape(r["error"])}</span>'
        else:
            score_cell = f'<span class="font-bold text-[#9E8AEC]">{r.get("final_score", 0):.2f}</span> / {r.get("total_max_score", 10):.1f}'
        rows += f"""
        <tr class="border-b border-slate-100 dark:border-white/5">
            <td class="py-2 px-2 text-xs font-semibold">{sid}</td>
            <td class="py-2 px-2 text-xs text-right">{score_cell}</td>
        </tr>
        """
    current_line = f'<p class="text-xs text-slate-500 mb-2">Đang chấm: <span class="font-bold">{html.escape(current_student)}</span></p>' if current_student else ""
    return f"""
    <div id="evaluation-progress-container" {poll_attr} class="p-6 bg-slate-50/50 dark:bg-slate-900/30 border border-slate-100 dark:border-white/5 rounded-2xl min-h-[380px]">
        <div class="flex items-center space-x-3 mb-4 border-b border-black/[0.03] dark:border-white/5 pb-3">
            <span class="loading loading-spinner text-[#9E8AEC] loading-sm"></span>
            <h3 class="font-extrabold text-sm text-slate-800 dark:text-slate-100">Chấm batch: {done}/{total} bài ({pct}%)</h3>
        </div>
        <progress class="progress progress-primary w-full mb-3" value="{done}" max="{total}"></progress>
        {current_line}
        <div class="overflow-x-auto max-h-[280px] overflow-y-auto">
            <table class="table table-xs w-full">
                <thead><tr><th class="text-[10px]">Sinh viên</th><th class="text-[10px] text-right">Điểm</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    """

def render_batch_results_html(batch_results: list, model_name: str, provider: str, language: str, question_text: str, problem_id: str = "") -> str:
    model_display = html.escape(model_name.split("/")[-1] if "/" in model_name else model_name)
    lines = [l.strip() for l in question_text.splitlines() if l.strip()]
    assignment_name = html.escape(lines[0][:50] + ("..." if lines and len(lines[0]) > 50 else "") if lines else (problem_id or "Batch grading"))

    ok_results = [r for r in batch_results if not r.get("error")]
    avg_score = sum(r.get("final_score", 0) for r in ok_results) / len(ok_results) if ok_results else 0
    max_score = ok_results[0].get("total_max_score", 10) if ok_results else 10

    rows = ""
    detail_blocks = ""
    for r in batch_results:
        sid = html.escape(str(r.get("student_id", "")))
        if r.get("error"):
            rows += f'<tr class="border-b border-slate-100 dark:border-white/5"><td class="py-2 text-xs font-semibold">{sid}</td><td class="py-2 text-xs text-rose-500">{html.escape(r["error"])}</td></tr>'
            continue
        fs = r.get("final_score", 0)
        tmax = r.get("total_max_score", 10)
        rows += f'<tr class="border-b border-slate-100 dark:border-white/5"><td class="py-2 text-xs font-semibold">{sid}</td><td class="py-2 text-xs text-right font-bold text-[#9E8AEC]">{fs:.2f} / {tmax:.1f}</td></tr>'
        detail_html = render_results_block_html(
            r.get("question_evals", []), tmax, fs,
            r.get("factor_score", 0), r.get("syntax_penalty", 0),
            model_name, provider, language, question_text
        )
        detail_blocks += f"""
        <details class="collapse collapse-arrow bg-slate-50/50 dark:bg-slate-900/20 border border-slate-100 dark:border-white/5 rounded-xl mb-2">
            <summary class="collapse-title text-xs font-bold py-3 min-h-0">{sid} — {fs:.2f}/{tmax:.1f}</summary>
            <div class="collapse-content px-3 pb-3">{detail_html}</div>
        </details>
        """

    return f"""
    <div class="space-y-4 animate-fade-in">
        <div class="p-5 bg-slate-50/50 dark:bg-slate-900/25 rounded-2xl border border-slate-100 dark:border-white/5">
            <span class="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">Batch Summary</span>
            <h4 class="text-sm font-bold text-slate-800 dark:text-slate-100 mt-1">{assignment_name}</h4>
            <div class="grid grid-cols-3 gap-2 mt-3">
                <div class="p-2 rounded-xl bg-white dark:bg-[#1A2333] border border-slate-100 dark:border-white/5 text-center">
                    <span class="text-[8px] text-slate-400 font-bold uppercase block">Tổng bài</span>
                    <span class="text-sm font-black text-slate-700 dark:text-slate-200">{len(batch_results)}</span>
                </div>
                <div class="p-2 rounded-xl bg-white dark:bg-[#1A2333] border border-slate-100 dark:border-white/5 text-center">
                    <span class="text-[8px] text-slate-400 font-bold uppercase block">Thành công</span>
                    <span class="text-sm font-black text-emerald-500">{len(ok_results)}</span>
                </div>
                <div class="p-2 rounded-xl bg-white dark:bg-[#1A2333] border border-slate-100 dark:border-white/5 text-center">
                    <span class="text-[8px] text-slate-400 font-bold uppercase block">Điểm TB</span>
                    <span class="text-sm font-black text-[#9E8AEC]">{avg_score:.2f}/{max_score:.1f}</span>
                </div>
            </div>
            <p class="text-[10px] text-slate-400 mt-2">Model: {model_display} · {html.escape(language)}</p>
        </div>
        <div class="overflow-x-auto">
            <table class="table table-sm w-full">
                <thead><tr><th class="text-[10px]">Sinh viên</th><th class="text-[10px] text-right">Điểm</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        <div class="space-y-2">
            <span class="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">Chi tiết từng bài</span>
            {detail_blocks}
        </div>
    </div>
    """

def update_batch_html(task_id: str, done: int, total: int, results: list, current_student: str = "", completed: bool = False, final_html: str = ""):
    if completed:
        EVAL_STATUS[task_id]["status"] = "completed"
        EVAL_STATUS[task_id]["html"] = f'<div id="evaluation-progress-container" class="animate-fade-in">{final_html}</div>'
    else:
        EVAL_STATUS[task_id]["status"] = "running"
        EVAL_STATUS[task_id]["html"] = render_batch_progress_html(task_id, done, total, results, current_student)

async def run_batch_evaluation_task(
    task_id: str,
    question_text: str,
    submissions: list,
    language: str,
    provider: str,
    model_name: str,
    problem_id: str = None,
    problem_config: dict = None,
    config_source: str = "",
    temp_dir_to_clean: str = None,
):
    import asyncio
    import shutil

    try:
        EVAL_STATUS[task_id]["status"] = "running"
        total = len(submissions)
        problem_config = problem_config or {}
        questions = split_questions(question_text)
        batch_results = []

        if "mock" in provider or "mock" in model_name:
            await asyncio.sleep(0.5)
            for i, sub in enumerate(submissions, start=1):
                batch_results.append({
                    "student_id": sub["student_id"],
                    "final_score": round(10.0 - i * 0.5, 2),
                    "total_max_score": 10.0,
                    "factor_score": 8.0,
                    "syntax_penalty": 0.5,
                    "question_evals": [],
                })
                update_batch_html(task_id, i, total, batch_results)
                await asyncio.sleep(0.2)
            final_html = render_batch_results_html(batch_results, model_name, provider, language, question_text, problem_id or "")
            update_batch_html(task_id, total, total, batch_results, completed=True, final_html=final_html)
            return

        update_batch_html(task_id, 0, total, batch_results, "Đang trích xuất tiêu chí...")
        factors_by_question = await extract_factors_for_questions(questions, problem_config, provider, model_name)

        semaphore = asyncio.Semaphore(BATCH_MAX_CONCURRENCY)
        completed_count = 0
        lock = asyncio.Lock()

        async def grade_submission(sub: dict):
            nonlocal completed_count
            sid = sub["student_id"]
            async with semaphore:
                update_batch_html(task_id, completed_count, total, batch_results, sid)
                try:
                    result = await evaluate_submission_core(
                        questions=questions,
                        language=language,
                        provider=provider,
                        model_name=model_name,
                        source_path=sub["source_path"],
                        problem_config=problem_config,
                        factors_by_question=factors_by_question,
                    )
                    row = {"student_id": sid, **result}
                except Exception as e:
                    logger.error(f"Batch grading failed for {sid}: {e}")
                    row = {"student_id": sid, "error": str(e)}
                async with lock:
                    batch_results.append(row)
                    batch_results.sort(key=lambda x: _batch_sort_key(str(x.get("student_id", ""))))
                    completed_count += 1
                    update_batch_html(task_id, completed_count, total, batch_results)

        await asyncio.gather(*[grade_submission(sub) for sub in submissions])
        final_html = render_batch_results_html(batch_results, model_name, provider, language, question_text, problem_id or "")
        update_batch_html(task_id, total, total, batch_results, completed=True, final_html=final_html)
    except Exception as e:
        logger.error(f"Batch evaluation failed: {e}")
        EVAL_STATUS[task_id]["status"] = "failed"
        EVAL_STATUS[task_id]["html"] = f"""
        <div id="evaluation-progress-container" class="p-6 bg-rose-50 dark:bg-rose-950/20 border border-rose-200 rounded-2xl text-sm text-rose-600">
            Lỗi chấm batch: {html.escape(str(e))}
        </div>
        """
    finally:
        if temp_dir_to_clean and os.path.exists(temp_dir_to_clean):
            try:
                shutil.rmtree(temp_dir_to_clean)
            except Exception as e:
                logger.warning(f"Error cleaning batch temp dir: {e}")

async def run_evaluation_task(task_id: str, question_text: str, student_code: str, language: str, provider: str, model_name: str, source_path: str = None, temp_dir_to_clean: str = None, problem_id: str = None, problem_config: dict = None, config_source: str = ""):
    import asyncio
    import re
    import shutil
    import os
    import json
    
    try:
        EVAL_STATUS[task_id]["status"] = "running"
        
        if "mock" in provider or "mock" in model_name:
            await asyncio.sleep(1.0)
            
            # mock question_evals
            question_evals = [
                {
                    "question_index": 1,
                    "question_name": "Câu 1 (3đ):",
                    "question_max": 3.0,
                    "scoring": {
                        "scaled_score": 2.5,
                        "factor_score_on_10": 8.33,
                        "syntax_penalty_on_10": 0.0
                    },
                    "factor_eval": {
                        "Khởi tạo đúng cấu trúc đĩa": {"compliance": 1.0, "reasoning": "Khởi tạo đĩa thành công với giá trị truyền vào."},
                        "Thao tác rút đĩa chính xác": {"compliance": 0.8, "reasoning": "Hàm rút đĩa đúng logic nhưng thiếu kiểm tra biên khi đĩa rỗng."},
                        "In kết quả đĩa theo thứ tự": {"compliance": 0.7, "reasoning": "In đĩa đúng thứ tự yêu cầu nhưng chưa format đẹp mắt."}
                    },
                    "suggestions": [
                        "Cần bổ sung điều kiện kiểm tra đĩa rỗng trước khi thực hiện rút đĩa.",
                        "Format lại định dạng in kết quả đĩa cho đúng với đề bài yêu cầu."
                    ],
                    "syntax_errors": [],
                    "code_file": "student_code.py"
                },
                {
                    "question_index": 2,
                    "question_name": "Câu 2 (2đ):",
                    "question_max": 2.0,
                    "scoring": {
                        "scaled_score": 1.5,
                        "factor_score_on_10": 7.5,
                        "syntax_penalty_on_10": 0.0
                    },
                    "factor_eval": {
                        "Định nghĩa hàm tính tổng": {"compliance": 1.0, "reasoning": "Định nghĩa hàm đầy đủ tham số đầu vào và kiểu trả về."},
                        "Logic tính toán chính xác": {"compliance": 0.5, "reasoning": "Phép cộng bị lệch 1 đơn vị do sai số chỉ mục vòng lặp."}
                    },
                    "suggestions": [
                        "Sửa chỉ mục vòng lặp chạy từ 0 thay vì 1 để tránh bỏ sót phần tử đầu tiên."
                    ],
                    "syntax_errors": [],
                    "code_file": "student_code.py"
                },
                {
                    "question_index": 3,
                    "question_name": "Câu 3 (5đ):",
                    "question_max": 5.0,
                    "scoring": {
                        "scaled_score": 0.0,
                        "factor_score_on_10": 0.0,
                        "syntax_penalty_on_10": 5.0
                    },
                    "factor_eval": {
                        "Định nghĩa cấu trúc dữ liệu": {"compliance": 0.0, "reasoning": "Không thể đánh giá do lỗi biên dịch."}
                    },
                    "suggestions": [
                        "Sửa lỗi biên dịch dòng 12: thiếu dấu chấm phẩy ';' ở cuối khai báo cấu trúc."
                    ],
                    "syntax_errors": ["student_code.cpp:12:5: error: expected ';' after struct definition"],
                    "code_file": "student_code.cpp"
                }
            ]
            
            total_max_score = 10.0
            final_score = 4.0
            factor_score = 9.0
            syntax_penalty = 5.0
            
            results_block_html = render_results_block_html(
                question_evals, total_max_score, final_score, factor_score, syntax_penalty,
                model_name, provider, language, question_text
            )
            
            EVAL_STATUS[task_id]["status"] = "completed"
            update_html(task_id, 4, step_4_html=results_block_html)
            return
        
        # Split questions
        questions = split_questions(question_text)
        
        # 1. Step 1: Run compiler syntax check
        update_html(task_id, 1)
        await asyncio.sleep(0.5)
        
        # Get all files if folder
        code_files = []
        if source_path and os.path.isdir(source_path):
            code_files = list_code_files(source_path)
            
        all_syntax_errors = []
        if code_files:
            for cf in code_files:
                errs = check_syntax(cf, language)
                all_syntax_errors.extend(errs)
        else:
            check_target = source_path if source_path else student_code
            all_syntax_errors = check_syntax(check_target, language)
            
        if all_syntax_errors:
            err_clean = [re.sub(r'<[^>]+>', '', e) for e in all_syntax_errors]
            err_display = re.sub(r'/[^:\s]+', 'student_code.' + ('py' if language == 'python' else ('java' if language == 'java' else 'cpp')), err_clean[0])
            step_1_html = f"""
            <div id="step-1" class="flex flex-col p-3 bg-error/20 border border-error/40 text-error rounded-lg space-y-1">
                <div class="flex items-center space-x-3">
                    <div class="badge badge-error">✗</div>
                    <span class="font-bold text-sm">Bước 1: Phát hiện {len(all_syntax_errors)} lỗi cú pháp biên dịch.</span>
                </div>
                <div class="text-[11px] font-mono bg-base-300 p-2 rounded text-base-content break-words whitespace-pre-wrap max-w-full overflow-x-auto mt-2">
                    {err_display}
                </div>
            </div>
            """
        else:
            step_1_html = """
            <div id="step-1" class="flex items-center space-x-3 p-3 bg-success/20 border border-success/40 text-success rounded-lg">
                <div class="badge badge-success">✓</div>
                <span class="font-bold text-sm">Bước 1: Kiểm tra cú pháp thành công (Không có lỗi).</span>
            </div>
            """
            
        # Step 2: Agent 1 - Factor Extraction
        EVAL_STATUS[task_id]["step"] = 2
        
        llm_client = LLMFactory.create(provider=provider, model_name=model_name)
        assessor = MultiAgentAssessor(llm_client=llm_client)
        
        problem_config = problem_config or {}
        if config_source:
            logger.info(f"Using grading config source={config_source}, problem_id={problem_id}")
            
        # Helper list to keep results
        question_evals = []
        total_input_tokens = 0
        total_output_tokens = 0
        
        # If there are multiple questions, we process them in parallel
        if len(questions) > 1:
            # Multi-question progress
            step_2_html = f"""
            <div id="step-2" class="flex items-center space-x-3 p-3 bg-base-200 rounded-lg">
                <span class="loading loading-spinner text-primary"></span>
                <span class="font-medium text-sm text-primary">Bước 2: Đang trích xuất tiêu chí cho {len(questions)} câu hỏi...</span>
            </div>
            """
            update_html(task_id, 2, step_1_html=step_1_html, step_2_html=step_2_html)
            
            async def extract_for_q(idx, q_text):
                question_config = problem_config.get(str(idx), {})
                pre_factors = question_config.get("pre_extracted_factors")
                
                if pre_factors is not None:
                    return idx, pre_factors, 0, 0
                
                try:
                    local_client = LLMFactory.create(provider=provider, model_name=model_name)
                    local_assessor = MultiAgentAssessor(llm_client=local_client)
                    factors = await asyncio.to_thread(local_assessor.extract_factors, q_text)
                    in_t = local_client.last_usage.get("input_tokens", 0) if hasattr(local_client, "last_usage") and local_client.last_usage else 0
                    out_t = local_client.last_usage.get("output_tokens", 0) if hasattr(local_client, "last_usage") and local_client.last_usage else 0
                    return idx, factors, in_t, out_t
                except Exception as e:
                    logger.error(f"Error extracting factors for Q{idx}: {e}")
                    return idx, ["Thực hiện đúng logic của câu hỏi"], 0, 0

            # Step 2 extraction in parallel
            tasks = [extract_for_q(idx, q_text) for idx, q_text in enumerate(questions, start=1)]
            extraction_results = await asyncio.gather(*tasks)
            extraction_results.sort(key=lambda x: x[0])
            
            total_factors_extracted = 0
            for idx, factors, in_t, out_t in extraction_results:
                total_factors_extracted += len(factors)
                total_input_tokens += in_t
                total_output_tokens += out_t
                question_evals.append({
                    "question_index": idx,
                    "question_name": questions[idx - 1].splitlines()[0].strip(),
                    "question_text": questions[idx - 1],
                    "factors": factors
                })
                
            step_2_html = f"""
            <div id="step-2" class="flex flex-col p-3 bg-success/20 border border-success/40 text-success rounded-lg space-y-2">
                <div class="flex items-center space-x-3">
                    <div class="badge badge-success">✓</div>
                    <span class="font-bold text-sm">Bước 2: Trích xuất thành công tổng cộng {total_factors_extracted} tiêu chí cho {len(questions)} câu hỏi.</span>
                </div>
            </div>
            """
            
            # Step 3: Factor Grading
            EVAL_STATUS[task_id]["step"] = 3
            step_3_html = f"""
            <div id="step-3" class="flex items-center space-x-3 p-3 bg-base-200 rounded-lg">
                <span class="loading loading-spinner text-primary"></span>
                <span class="font-medium text-sm text-primary">Bước 3: Đang chấm điểm tiêu chí cho {len(questions)} câu hỏi...</span>
            </div>
            """
            update_html(task_id, 3, step_1_html=step_1_html, step_2_html=step_2_html, step_3_html=step_3_html)
            
            async def grade_for_q(q_res):
                idx = q_res["question_index"]
                factors = q_res["factors"]
                q_text = q_res["question_text"]
                
                # Determine student code file matching this question
                if code_files and (idx - 1) < len(code_files):
                    file_path = code_files[idx - 1]
                    if os.path.isdir(file_path):
                        code_i = merge_folder_code(file_path, language)
                        source_path_i = file_path
                    else:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            code_i = f.read()
                        source_path_i = file_path
                else:
                    code_i = student_code
                    source_path_i = source_path
                    
                # Compiler errors for this specific file
                syntax_errors_i = check_syntax(source_path_i if source_path_i else code_i, language)
                
                # Question Config
                question_config = problem_config.get(str(idx), {})
                f_weights = question_config.get("factor_weights")
                s_penalties = question_config.get("syntax_penalties")
                
                qmax = parse_question_max(q_text)
                if qmax is None:
                    qmax = 10.0 / len(questions)
                    
                # Assess factors
                in_t = 0
                out_t = 0
                try:
                    local_client = LLMFactory.create(provider=provider, model_name=model_name)
                    local_assessor = MultiAgentAssessor(llm_client=local_client)
                    factor_eval = await asyncio.to_thread(local_assessor.assess_factors, code_i, factors, language, use_cache=False)
                    if hasattr(local_client, "last_usage") and local_client.last_usage:
                        in_t = local_client.last_usage.get("input_tokens", 0)
                        out_t = local_client.last_usage.get("output_tokens", 0)
                except Exception as e:
                    logger.error(f"Error assessing factors for Q{idx}: {e}")
                    factor_eval = {
                        f: {
                            "compliance": -1.0,
                            "reasoning": f"Gặp lỗi khi gọi tác vụ chấm điểm LLM cho Câu {idx}: {str(e)}"
                        } for f in factors
                    }
                    
                # Calculate score
                scoring = assessor.calculate_score(
                    factor_eval=factor_eval,
                    syntax_errors=syntax_errors_i,
                    question_max=qmax,
                    factor_weights=f_weights,
                    syntax_penalties=s_penalties
                )
                suggestions = assessor.generate_suggestions(factor_eval, syntax_errors_i)
                
                return {
                    "question_index": idx,
                    "factor_eval": factor_eval,
                    "scoring": scoring,
                    "suggestions": suggestions,
                    "syntax_errors": syntax_errors_i,
                    "question_max": qmax,
                    "code_file": os.path.basename(code_files[idx - 1]) if (code_files and (idx - 1) < len(code_files)) else "student_code",
                    "in_tokens": in_t,
                    "out_tokens": out_t
                }

            # Step 3 grading in parallel
            grade_tasks = [grade_for_q(q_res) for q_res in question_evals]
            grade_results = await asyncio.gather(*grade_tasks)
            grade_results.sort(key=lambda x: x["question_index"])
            
            for i, res in enumerate(grade_results):
                question_evals[i].update(res)
                total_input_tokens += res["in_tokens"]
                total_output_tokens += res["out_tokens"]
                
            step_3_html = f"""
            <div id="step-3" class="flex flex-col p-3 bg-success/20 border border-success/40 text-success rounded-lg space-y-2">
                <div class="flex items-center space-x-3">
                    <div class="badge badge-success">✓</div>
                    <span class="font-bold text-sm">Bước 3: Hoàn thành chấm điểm cho toàn bộ {len(questions)} câu hỏi.</span>
                </div>
            </div>
            """
            
            # Step 4: Final calculation & suggestions
            EVAL_STATUS[task_id]["step"] = 4
            update_html(task_id, 4, step_1_html=step_1_html, step_2_html=step_2_html, step_3_html=step_3_html)
            
                        # Aggregate scores
            total_max_score = sum(q["question_max"] for q in question_evals)
            total_final_score = sum(q["scoring"].get("scaled_score", 0.0) for q in question_evals)
            total_factor_score = sum((q["scoring"].get("factor_score_on_10", 0.0) / 10.0) * q["question_max"] for q in question_evals)
            total_syntax_penalty = sum((q["scoring"].get("syntax_penalty_on_10", 0.0) / 10.0) * q["question_max"] for q in question_evals)
            
            final_score = total_final_score
            factor_score = total_factor_score
            syntax_penalty = total_syntax_penalty

            results_block_html = render_results_block_html(
                question_evals, total_max_score, final_score, factor_score, syntax_penalty,
                model_name, provider, language, question_text
            )
            
            EVAL_STATUS[task_id]["status"] = "completed"
            update_html(task_id, 4, step_4_html=results_block_html)
            return

        # If there is only 1 question, fallback to the original single question logic
        else:
            # Step 2: Agent 1 - Factor Extraction (for 1 question)
            try:
                if problem_id and problem_config.get("1", {}).get("pre_extracted_factors") is not None:
                    factors = problem_config.get("1", {}).get("pre_extracted_factors")
                else:
                    factors = await asyncio.to_thread(assessor.extract_factors, question_text)
                    
                factors_list_html = "".join([f"<li class='text-xs list-disc list-inside text-base-content/85'>{f}</li>" for f in factors])
                step_2_html = f"""
                <div id="step-2" class="flex flex-col p-3 bg-success/20 border border-success/40 text-success rounded-lg space-y-2">
                    <div class="flex items-center space-x-3">
                        <div class="badge badge-success">✓</div>
                        <span class="font-bold text-sm">Bước 2: Trích xuất thành công {len(factors)} tiêu chí đánh giá:</span>
                    </div>
                    <ul class="pl-6 space-y-1">
                        {factors_list_html}
                    </ul>
                </div>
                """
            except Exception as e:
                logger.error(f"Error in Step 2: {e}")
                EVAL_STATUS[task_id]["status"] = "failed"
                step_2_html = f"""
                <div id="step-2" class="flex items-center space-x-3 p-3 bg-error/20 text-error rounded-lg">
                    <div class="badge badge-error">✗</div>
                    <span class="font-bold text-sm">Bước 2: Lỗi trích xuất tiêu chí - {str(e)}</span>
                </div>
                """
                update_html(task_id, 2, step_1_html=step_1_html, step_2_html=step_2_html)
                return
    
            # Step 3: Agent 2 - Factor Grading
            EVAL_STATUS[task_id]["step"] = 3
            update_html(task_id, 3, step_1_html=step_1_html, step_2_html=step_2_html)
            
            try:
                factor_eval = await asyncio.to_thread(assessor.assess_factors, student_code, factors, language, use_cache=False)
                
                eval_preview = ""
                for f, d in factor_eval.items():
                    comp = int(d.get("compliance", 0) * 100)
                    color = "text-success" if comp >= 80 else ("text-warning" if comp >= 50 else "text-error")
                    eval_preview += f"<div class='text-xs font-semibold'><span class='text-base-content/70 font-normal'>{f}:</span> <span class='{color}'>{comp}%</span></div>"
                    
                step_3_html = f"""
                <div id="step-3" class="flex flex-col p-3 bg-success/20 border border-success/40 text-success rounded-lg space-y-2">
                    <div class="flex items-center space-x-3">
                        <div class="badge badge-success">✓</div>
                        <span class="font-bold text-sm">Bước 3: Hoàn thành chấm điểm các tiêu chí:</span>
                    </div>
                    <div class="pl-6 space-y-1">
                        {eval_preview}
                    </div>
                </div>
                """
            except Exception as e:
                logger.error(f"Error in Step 3: {e}")
                EVAL_STATUS[task_id]["status"] = "failed"
                step_3_html = f"""
                <div id="step-3" class="flex items-center space-x-3 p-3 bg-error/20 text-error rounded-lg">
                    <div class="badge badge-error">✗</div>
                    <span class="font-bold text-sm">Bước 3: Lỗi chấm điểm tiêu chí - {str(e)}</span>
                </div>
                """
                update_html(task_id, 3, step_1_html=step_1_html, step_2_html=step_2_html, step_3_html=step_3_html)
                return
    
                        # Step 4: Final calculation & suggestions
            EVAL_STATUS[task_id]["step"] = 4
            update_html(task_id, 4, step_1_html=step_1_html, step_2_html=step_2_html, step_3_html=step_3_html)
            
            try:
                # Extract weights and penalties if any
                f_weights = problem_config.get("1", {}).get("factor_weights")
                s_penalties = problem_config.get("1", {}).get("syntax_penalties")
                
                scoring = assessor.calculate_score(
                    factor_eval=factor_eval,
                    syntax_errors=all_syntax_errors,
                    factor_weights=f_weights,
                    syntax_penalties=s_penalties
                )
                suggestions = assessor.generate_suggestions(factor_eval, all_syntax_errors)
                
                final_score = scoring.get("final_score_on_10", 0)
                factor_score = scoring.get("factor_score_on_10", 0)
                syntax_penalty = scoring.get("syntax_penalty_on_10", 0)
                
                question_evals = [{
                    "question_name": "Câu 1",
                    "question_max": 10.0,
                    "scoring": scoring,
                    "factor_eval": factor_eval,
                    "suggestions": suggestions,
                    "syntax_errors": all_syntax_errors,
                    "code_file": "student_code"
                }]

                results_block_html = render_results_block_html(
                    question_evals, 10.0, final_score, factor_score, syntax_penalty,
                    model_name, provider, language, question_text
                )
                
                EVAL_STATUS[task_id]["status"] = "completed"
                update_html(task_id, 4, step_4_html=results_block_html)
            except Exception as e:
                logger.error(f"Error in Step 4: {e}")
                EVAL_STATUS[task_id]["status"] = "failed"
                update_html(task_id, 4)
    finally:
        if temp_dir_to_clean and os.path.exists(temp_dir_to_clean):
            try:
                shutil.rmtree(temp_dir_to_clean)
                logger.info(f"Cleaned up temp directory: {temp_dir_to_clean}")
            except Exception as e:
                logger.warning(f"Error cleaning up temp directory {temp_dir_to_clean}: {e}")

if __name__ == "__main__":
    serve(port=5000, reload=False)
