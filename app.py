import asyncio
import os
import re
import json
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

# Import CodeJudge Core Assessor and Factory
from codejudge.core.multi_agent_assessor import MultiAgentAssessor
from codejudge.core.llm_client import LLMFactory
from codejudge.core.compiler_helper import check_syntax

# Initialize FastHTML App
# We use TailwindCSS, DaisyUI and Monaco Editor via CDN
app, rt = fast_app(
    hdrs=(
        Script(src="https://cdn.tailwindcss.com"),
        Link(href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css", rel="stylesheet", type="text/css"),
        Script(src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs/loader.min.js"),

        Style("""
            .monaco-editor-container {
                height: 330px;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                overflow: hidden;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .animate-fade-in {
                animation: fadeIn 0.4s ease-out forwards;
            }
        """)
    )
)

@rt("/")
def get():
    return (
        Title("CodeJudge Multi-Agent Demo"),
        Div(
            # Header
            Div(
                Div(
                    H1("🤖 CodeJudge Multi-Agent", cls="text-2xl md:text-3xl font-extrabold text-primary flex items-center gap-2"),
                    P("Hệ thống đánh giá ngữ nghĩa mã nguồn đa tác nhân không cần Test Case", cls="text-xs md:text-sm text-neutral-content/60 mt-1"),
                    cls="flex-1"
                ),
                Div(
                    Span("v1.2.0-beta", cls="badge badge-primary font-mono text-xs"),
                    cls="flex-none"
                ),
                cls="navbar bg-base-200 rounded-xl mb-6 p-4 border border-neutral/10 shadow-md"
            ),
            
            # Main Grid Layout
            Div(
                # Left Column: Inputs
                Div(
                    Div(
                        H2("⚙️ Tham Số Đánh Giá", cls="text-base md:text-lg font-bold mb-4 flex items-center gap-2 border-b border-neutral/20 pb-2"),
                        
                        Form(
                            # Language & LLM Selection Row
                            Div(
                                # Language Selection
                                Div(
                                    Label("Ngôn ngữ lập trình", cls="label-text text-xs font-bold text-neutral-content/80 mb-1 block"),
                                    Select(
                                        Option("Python", value="python", selected=True),
                                        Option("C++", value="cpp"),
                                        Option("Java", value="java"),
                                        id="language", name="language", cls="select select-bordered select-sm w-full"
                                    ),
                                    cls="flex-1"
                                ),
                                # Model Selection
                                Div(
                                    Label("LLM Model", cls="label-text text-xs font-bold text-neutral-content/80 mb-1 block"),
                                    Select(
                                        Option("Gemini-2.5-Flash", value="openrouter|google/gemini-2.5-flash", selected=True),
                                        Option("Llama-3-8B-Instruct", value="openrouter|meta-llama/llama-3-8b-instruct"),
                                        Option("Qwen2.5-7B-Instruct", value="openrouter|qwen/qwen2.5-7b-instruct"),
                                        id="model_select", name="model_select", cls="select select-bordered select-sm w-full"
                                    ),
                                    cls="flex-1"
                                ),
                                cls="flex gap-4 mb-4"
                            ),
                            
                            # Instruction
                            Div(
                                Label("Đề bài (Instruction)", cls="label-text text-xs font-bold text-neutral-content/80 mb-1 block"),
                                Textarea(
                                    placeholder="Nhập yêu cầu hoặc mô tả bài toán ở đây...",
                                    id="question_text", name="question_text",
                                    cls="textarea textarea-bordered textarea-sm w-full h-24 font-sans text-sm",
                                    required=True
                                ),
                                cls="form-control mb-4"
                            ),
                            
                            # Code Editor
                            Div(
                                Label("Mã nguồn sinh viên (Student Code)", cls="label-text text-xs font-bold text-neutral-content/80 mb-1 block"),
                                # Hidden textarea to hold code for form submission
                                Textarea(id="student_code", name="student_code", cls="hidden"),
                                # Container for Monaco Editor with fallback textarea
                                Div(
                                    Textarea(
                                        id="fallback_code", 
                                        placeholder="Nhập mã nguồn của bạn ở đây...", 
                                        cls="textarea textarea-bordered w-full h-[330px] font-mono text-sm leading-relaxed bg-base-300 text-neutral-content"
                                    ),
                                    id="editor-container", 
                                    cls="monaco-editor-container"
                                ),
                                cls="form-control mb-4"
                            ),
                            
                            # Action Button
                            Button(
                                "🚀 Bắt đầu Đánh giá",
                                type="submit",
                                cls="btn btn-primary w-full shadow-lg font-bold"
                            ),
                            
                            # HTMX integration
                            hx_post="/evaluate",
                            hx_target="#result-container",
                            hx_swap="innerHTML",
                            onsubmit="const val = window.editor ? window.editor.getValue() : document.getElementById('fallback_code').value; if(!val.trim()){ alert('Vui lòng nhập mã nguồn sinh viên!'); return false; } document.getElementById('student_code').value = val;"
                        ),
                        cls="bg-base-200 p-6 rounded-xl border border-neutral/10 shadow-sm"
                    ),
                    
                    # Preset Examples Card
                    Div(
                        H3("📚 Ví Dụ Mẫu (Preset Examples)", cls="text-sm font-bold mb-3 flex items-center gap-2 text-neutral-content/80"),
                        Div(
                            Button("Python: Longest Substring (Đúng)", onclick="loadExample(1, true)", cls="btn btn-outline btn-xs text-[10px] btn-success"),
                            Button("Python: Longest Substring (Lỗi)", onclick="loadExample(1, false)", cls="btn btn-outline btn-xs text-[10px] btn-error"),
                            Button("C++: Symmetric Tree (Đúng)", onclick="loadExample(2, true)", cls="btn btn-outline btn-xs text-[10px] btn-success"),
                            Button("C++: Symmetric Tree (Lỗi)", onclick="loadExample(2, false)", cls="btn btn-outline btn-xs text-[10px] btn-error"),
                            cls="flex flex-wrap gap-2"
                        ),
                        cls="bg-base-200 p-4 rounded-xl border border-neutral/10 mt-4 shadow-sm"
                    ),
                    cls="md:col-span-5 space-y-4"
                ),
                
                # Right Column: Results & Logs
                Div(
                    Div(
                        H2("🔍 Tiến Trình Đánh Giá", cls="text-base md:text-lg font-bold mb-4 flex items-center gap-2 border-b border-neutral/20 pb-2"),
                        
                        # Result container which will receive the HTMX stream
                        Div(
                            Div(
                                Div("💡 Nhấn 'Bắt đầu Đánh giá' để phân tích mã nguồn sử dụng hệ thống Multi-Agent của CodeJudge.", cls="text-sm text-neutral-content/50 italic text-center p-8"),
                                cls="flex items-center justify-center h-48 bg-base-300 rounded-lg border border-dashed border-neutral/30"
                            ),
                            id="result-container", cls="min-h-[350px] space-y-4"
                        ),
                        cls="bg-base-200 p-6 rounded-xl border border-neutral/10 min-h-[525px] shadow-sm"
                    ),
                    cls="md:col-span-7"
                ),
                cls="grid grid-cols-1 md:grid-cols-12 gap-6"
            ),
            
            # Footer
            Div(
                P("© 2026 CodeJudge Framework - Evaluating Code Generation with LLMs without Test Cases. Built with FastHTML.", cls="text-[10px] md:text-xs text-neutral-content/40"),
                cls="mt-12 text-center border-t border-neutral/10 pt-4 pb-8"
            ),
            
            # Script to initialize Monaco Editor and load examples
            Script("""
                // Define examples
                const examples = {
                    1: {
                        prompt: "Viết hàm Python `longest_substring(s: str) -> int` trả về độ dài của chuỗi con dài nhất không chứa ký tự lặp lại.",
                        lang: "python",
                        correct: `def longest_substring(s: str) -> int:
    char_map = {}
    left = 0
    max_len = 0
    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    return max_len`,
                        buggy: `def longest_substring(s: str) -> int:
    char_map = {}
    left = 0
    max_len = 0
    for right in range(len(s)):
        if s[right] in char_map:
            # Bug: quên không check điều kiện char_map[s[right]] >= left
            left = char_map[s[right]] + 1
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    return max_len`
                    },
                    2: {
                        prompt: "Định nghĩa cấu trúc TreeNode và viết hàm `isSymmetric(TreeNode* root)` trong C++ để kiểm tra xem một cây nhị phân có đối xứng qua trục giữa hay không.",
                        lang: "cpp",
                        correct: `#include <iostream>

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode(int x) : val(x), left(NULL), right(NULL) {}
};

class Solution {
public:
    bool isMirror(TreeNode* t1, TreeNode* t2) {
        if (t1 == NULL && t2 == NULL) return true;
        if (t1 == NULL || t2 == NULL) return false;
        return (t1->val == t2->val)
            && isMirror(t1->right, t2->left)
            && isMirror(t1->left, t2->right);
    }
    
    bool isSymmetric(TreeNode* root) {
        return isMirror(root, root);
    }
};`,
                        buggy: `#include <iostream>

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode(int x) : val(x), left(NULL), right(NULL) {}
};

class Solution {
public:
    bool isMirror(TreeNode* t1, TreeNode* t2) {
        if (t1 == NULL && t2 == NULL) return true;
        if (t1 == NULL || t2 == NULL) return false;
        // Bug: gọi sai đệ quy (t1->left với t2->left thay vì cross)
        return (t1->val == t2->val)
            && isMirror(t1->left, t2->left)
            && isMirror(t1->right, t2->right);
    }
    
    bool isSymmetric(TreeNode* root) {
        return isMirror(root, root);
    }
};`
                    }
                };

                function loadExample(id, isCorrect) {
                    const ex = examples[id];
                    document.getElementById('question_text').value = ex.prompt;
                    document.getElementById('language').value = ex.lang;
                    
                    const code = isCorrect ? ex.correct : ex.buggy;
                    if (window.editor) {
                        window.editor.setValue(code);
                        monaco.editor.setModelLanguage(window.editor.getModel(), ex.lang === 'cpp' ? 'cpp' : 'python');
                    } else {
                        document.getElementById('fallback_code').value = code;
                    }
                }

                // Initialize Monaco Editor
                if (typeof require !== 'undefined') {
                    require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' } });
                    require(['vs/editor/editor'], function () {
                        const container = document.getElementById('editor-container');
                        const fallbackVal = document.getElementById('fallback_code').value;
                        container.innerHTML = ''; // Clear fallback textarea
                        
                        window.editor = monaco.editor.create(container, {
                            value: fallbackVal || examples[1].correct,
                            language: 'python',
                            theme: 'vs-dark',
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
                }
            """),
            cls="container mx-auto p-4 max-w-7xl font-sans min-h-screen bg-base-100 text-neutral-content",
            data_theme="dark"
        )
    )

@rt("/evaluate")
async def post(question_text: str, student_code: str, language: str, model_select: str):
    import uuid
    # Parse provider and model_name from select value
    if "|" in model_select:
        provider, model_name = model_select.split("|", 1)
    else:
        provider, model_name = "openrouter", model_select
        
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Initialize global status for this task
    EVAL_STATUS[task_id] = {
        "status": "running",
        "step": 1,
        "html": f"""
        <div id="evaluation-progress-container" hx-get="/evaluate/status/{task_id}" hx-trigger="every 1s" hx-swap="outerHTML" class="space-y-4">
            <div class="space-y-4">
                <div id="step-1" class="flex items-center space-x-3 p-3 bg-base-200 rounded-lg">
                    <span class="loading loading-spinner text-primary"></span>
                    <span class="font-medium text-sm text-primary">Đang khởi động tiến trình đánh giá đa tác nhân...</span>
                </div>
                <div id="step-2" class="flex items-center space-x-3 p-3 text-neutral-content opacity-40">
                    <div class="badge badge-outline text-xs">⏳</div>
                    <span class="text-sm">Bước 2: Agent 1 - Trích xuất tiêu chí (Factor Extraction)...</span>
                </div>
                <div id="step-3" class="flex items-center space-x-3 p-3 text-neutral-content opacity-40">
                    <div class="badge badge-outline text-xs">⏳</div>
                    <span class="text-sm">Bước 3: Agent 2 - Chấm điểm tiêu chí (Factor Grading)...</span>
                </div>
                <div id="step-4" class="flex items-center space-x-3 p-3 text-neutral-content opacity-40">
                    <div class="badge badge-outline text-xs">⏳</div>
                    <span class="text-sm">Bước 4: Tổng hợp kết quả và gợi ý...</span>
                </div>
            </div>
        </div>
        """
    }
    
    # Start background execution
    asyncio.create_task(
        run_evaluation_task(
            task_id, question_text, student_code, language, provider, model_name
        )
    )
    
    # Return the initial polling element
    return HTMLResponse(content=EVAL_STATUS[task_id]["html"])

@rt("/evaluate/status/{task_id}")
def get(task_id: str):
    if task_id not in EVAL_STATUS:
        return HTMLResponse(content=f"""
        <div id="evaluation-progress-container" hx-get="/evaluate/status/{task_id}" hx-trigger="every 1s" hx-swap="outerHTML" class="p-4 text-center text-xs text-neutral-content/50">
            <span class="loading loading-spinner loading-xs mr-2"></span> Đang kết nối server...
        </div>
        """)
    return HTMLResponse(content=EVAL_STATUS[task_id]["html"])

# Global state to store evaluation progress
EVAL_STATUS = {}

def update_html(task_id: str, step_num: int, step_1_html: str = "", step_2_html: str = "", step_3_html: str = "", step_4_html: str = ""):
    # Helper to generate the HTML for the current state
    steps = [
        ("step-1", "Bước 1: Kiểm tra cú pháp (Compiler Check)", step_1_html),
        ("step-2", "Bước 2: Agent 1 - Trích xuất tiêu chí (Factor Extraction)", step_2_html),
        ("step-3", "Bước 3: Agent 2 - Chấm điểm tiêu chí (Factor Grading)", step_3_html),
        ("step-4", "Bước 4: Tổng hợp kết quả và gợi ý", step_4_html)
    ]
    
    steps_html = ""
    for i, (step_id, label, custom_html) in enumerate(steps):
        num = i + 1
        if custom_html:
            steps_html += custom_html
        elif num == step_num:
            # Running
            steps_html += f"""
            <div id="{step_id}" class="flex items-center space-x-3 p-3 bg-base-200 rounded-lg">
                <span class="loading loading-spinner text-primary"></span>
                <span class="font-medium text-sm text-primary">{label}...</span>
            </div>
            """
        elif num < step_num:
            # Completed (default success if no custom HTML)
            steps_html += f"""
            <div id="{step_id}" class="flex items-center space-x-3 p-3 bg-success/10 border border-success/30 text-success rounded-lg">
                <div class="badge badge-success">✓</div>
                <span class="font-medium text-sm">{label} thành công.</span>
            </div>
            """
        else:
            # Pending
            steps_html += f"""
            <div id="{step_id}" class="flex items-center space-x-3 p-3 text-neutral-content opacity-40">
                <div class="badge badge-outline text-xs">⏳</div>
                <span class="text-sm">{label}</span>
            </div>
            """
            
    # If running, include the hx-trigger to poll again
    poll_attr = f'hx-get="/evaluate/status/{task_id}" hx-trigger="every 1s" hx-swap="outerHTML"' if EVAL_STATUS[task_id]["status"] == "running" else ""
    
    EVAL_STATUS[task_id]["html"] = f"""
    <div id="evaluation-progress-container" {poll_attr} class="space-y-4 animate-fade-in">
        <div class="space-y-4">
            {steps_html}
        </div>
    </div>
    """

async def run_evaluation_task(task_id: str, question_text: str, student_code: str, language: str, provider: str, model_name: str):
    import asyncio
    import re
    
    EVAL_STATUS[task_id]["status"] = "running"
    
    # Step 1: Run compiler check
    update_html(task_id, 1)
    await asyncio.sleep(0.5)
    
    syntax_errors = []
    try:
        syntax_errors = check_syntax(student_code, language)
        if syntax_errors:
            err_clean = [re.sub(r'<[^>]+>', '', e) for e in syntax_errors]
            err_display = re.sub(r'/[^:\s]+', 'student_code.' + ('py' if language == 'python' else 'cpp'), err_clean[0])
            step_1_html = f"""
            <div id="step-1" class="flex flex-col p-3 bg-error/20 border border-error/40 text-error rounded-lg space-y-1">
                <div class="flex items-center space-x-3">
                    <div class="badge badge-error">✗</div>
                    <span class="font-bold text-sm">Bước 1: Phát hiện {len(syntax_errors)} lỗi cú pháp biên dịch.</span>
                </div>
                <div class="text-[11px] font-mono bg-base-300 p-2 rounded text-neutral-content break-words whitespace-pre-wrap max-w-full overflow-x-auto mt-2">
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
    except Exception as e:
        logger.error(f"Error in Step 1: {e}")
        EVAL_STATUS[task_id]["status"] = "failed"
        step_1_html = f"""
        <div id="step-1" class="flex items-center space-x-3 p-3 bg-error/20 text-error rounded-lg">
            <div class="badge badge-error">✗</div>
            <span class="font-bold text-sm">Bước 1: Lỗi kiểm tra cú pháp - {str(e)}</span>
        </div>
        """
        update_html(task_id, 1, step_1_html=step_1_html)
        return

    # Step 2: Agent 1 - Factor Extraction
    EVAL_STATUS[task_id]["step"] = 2
    update_html(task_id, 2, step_1_html=step_1_html)
    
    try:
        llm_client = LLMFactory.create(provider=provider, model_name=model_name)
        assessor = MultiAgentAssessor(llm_client=llm_client)
        
        factors = await asyncio.to_thread(assessor.extract_factors, question_text)
        
        factors_list_html = "".join([f"<li class='text-xs list-disc list-inside text-neutral-content/85'>{f}</li>" for f in factors])
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
        factor_eval = await asyncio.to_thread(assessor.assess_factors, student_code, factors, language)
        
        eval_preview = ""
        for f, d in factor_eval.items():
            comp = int(d.get("compliance", 0) * 100)
            color = "text-success" if comp >= 80 else ("text-warning" if comp >= 50 else "text-error")
            eval_preview += f"<div class='text-xs font-semibold'><span class='text-neutral-content/70 font-normal'>{f}:</span> <span class='{color}'>{comp}%</span></div>"
            
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
        scoring = assessor.calculate_score(factor_eval, syntax_errors)
        suggestions = assessor.generate_suggestions(factor_eval, syntax_errors)
        
        final_score = scoring.get("final_score_on_10", 0)
        factor_score = scoring.get("factor_score_on_10", 0)
        syntax_penalty = scoring.get("syntax_penalty_on_10", 0)
        
        usage = getattr(llm_client, "last_usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
        cost = (input_tokens * 0.000000075) + (output_tokens * 0.00000030)
        
        score_color = "text-success" if final_score >= 8.0 else ("text-warning" if final_score >= 5.0 else "text-error")
        
        rows_html = ""
        for factor, details in factor_eval.items():
            compliance = details.get("compliance", 0)
            reasoning = details.get("reasoning", "")
            comp_percent = int(compliance * 100)
            badge_class = "badge-success" if compliance >= 0.8 else ("badge-warning" if compliance >= 0.5 else "badge-error")
            rows_html += f"""
            <tr class="hover">
                <td class="font-medium text-xs break-words max-w-[150px] md:max-w-[200px]">{factor}</td>
                <td><span class="badge {badge_class} text-xs">{comp_percent}%</span></td>
                <td class="text-xs break-words max-w-[200px] md:max-w-[300px] text-neutral-content/85">{reasoning}</td>
            </tr>
            """
            
        suggestions_html = "".join([f"<li class='text-xs list-disc list-inside text-neutral-content/85'>{s}</li>" for s in suggestions])
        
        results_block_html = f"""
        <div class="mt-6 p-4 md:p-6 bg-base-300 rounded-xl border border-neutral/20 space-y-6 shadow-lg animate-fade-in">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-neutral/30 pb-4">
                <div>
                    <h2 class="text-lg md:text-xl font-bold flex items-center gap-2">
                        <span>📊 Kết Quả Đánh Giá Tổng Quan</span>
                    </h2>
                    <p class="text-[10px] md:text-xs text-neutral-content/60 mt-1">Được chấm điểm tự động bởi CodeJudge Multi-Agent</p>
                </div>
                <div class="flex items-center gap-4">
                    <div class="text-right">
                        <div class="text-[10px] md:text-xs text-neutral-content/60 font-bold">ĐIỂM CỦA BẠN</div>
                        <div class="text-2xl md:text-3xl font-extrabold {score_color}">{final_score} <span class="text-sm md:text-lg text-neutral-content/40 font-normal">/ 10</span></div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="stats bg-base-200 shadow-sm border border-neutral/10">
                    <div class="stat p-3 md:p-4">
                        <div class="stat-title text-xs">Điểm Logic (Factor Score)</div>
                        <div class="stat-value text-lg md:text-xl text-success">{factor_score} <span class="text-xs text-neutral-content/50">/ 10</span></div>
                        <div class="stat-desc text-[10px] text-neutral-content/60">Độ đáp ứng trung bình các tiêu chí</div>
                    </div>
                </div>
                <div class="stats bg-base-200 shadow-sm border border-neutral/10">
                    <div class="stat p-3 md:p-4">
                        <div class="stat-title text-xs">Trừ điểm Cú pháp (Syntax Penalty)</div>
                        <div class="stat-value text-lg md:text-xl text-error">-{syntax_penalty}</div>
                        <div class="stat-desc text-[10px] text-neutral-content/60">Dựa trên phân loại lỗi compiler</div>
                    </div>
                </div>
                <div class="stats bg-base-200 shadow-sm border border-neutral/10">
                    <div class="stat p-3 md:p-4">
                        <div class="stat-title text-xs">Mô hình sử dụng</div>
                        <div class="stat-value text-xs md:text-sm truncate max-w-[150px]" title="{model_name}">{model_name.split('/')[-1]}</div>
                        <div class="stat-desc text-[10px] text-neutral-content/60">Provider: {provider.upper()}</div>
                    </div>
                </div>
            </div>

            <div>
                <h3 class="font-bold text-xs md:text-sm mb-2 flex items-center gap-2">
                    <span>📝 Chi Tiết Đánh Giá Theo Tiêu Chi</span>
                </h3>
                <div class="overflow-x-auto border border-neutral/10 rounded-lg">
                    <table class="table table-xs md:table-sm w-full bg-base-200">
                        <thead>
                            <tr class="bg-base-100 text-xs">
                                <th>Tiêu chí (Factor)</th>
                                <th>Đáp ứng (%)</th>
                                <th>Phân tích lý giải</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <div>
                <h3 class="font-bold text-xs md:text-sm mb-2 flex items-center gap-2">
                    <span>💡 Đề Xuất & Gợi Ý Cải Thiện</span>
                </h3>
                <div class="bg-base-200 p-4 rounded-lg border border-neutral/10">
                    <ul class="space-y-1.5 list-none">
                        {suggestions_html}
                    </ul>
                </div>
            </div>

            <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-2 border-t border-neutral/20 pt-4 text-[10px] text-neutral-content/50">
                <div>Tokens: {total_tokens} (Input: {input_tokens} | Output: {output_tokens})</div>
                <div>Chi phí ước tính: <span class="text-success font-mono font-semibold">${cost:.6f}</span></div>
            </div>
        </div>
        """
        
        step_4_html = f"""
        <div id="step-4" class="flex flex-col p-3 bg-success/20 border border-success/40 text-success rounded-lg space-y-2">
            <div class="flex items-center space-x-3">
                <div class="badge badge-success">✓</div>
                <span class="font-bold text-sm">Bước 4: Tổng hợp kết quả thành công.</span>
            </div>
        </div>
        {results_block_html}
        """
        
        EVAL_STATUS[task_id]["status"] = "completed"
        update_html(task_id, 4, step_1_html=step_1_html, step_2_html=step_2_html, step_3_html=step_3_html, step_4_html=step_4_html)
        
    except Exception as e:
        logger.error(f"Error in Step 4: {e}")
        EVAL_STATUS[task_id]["status"] = "failed"
        step_4_html = f"""
        <div id="step-4" class="flex items-center space-x-3 p-3 bg-error/20 text-error rounded-lg">
            <div class="badge badge-error">✗</div>
            <span class="font-bold text-sm">Bước 4: Lỗi hoàn tất đánh giá - {str(e)}</span>
        </div>
        """
        update_html(task_id, 4, step_1_html=step_1_html, step_2_html=step_2_html, step_3_html=step_3_html, step_4_html=step_4_html)

if __name__ == "__main__":
    serve(port=5000, reload=False)
