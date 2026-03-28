import os
from dotenv import load_dotenv
load_dotenv()
import re
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import time
from datetime import datetime
import traceback

# Set the working directory to the project root (Code directory)
# os.chdir(os.path.dirname(os.path.abspath(__file__)))
import sys

# Get the project root directory and add it to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Code.base.clause_comparison import clause_comparison

app = Flask(__name__, template_folder = 'ui/templates')

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Folder where uploaded files are stored
UPLOAD_FOLDER      = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Enhanced clause analysis endpoint with improved parsing and features"""
    try:
        # Input validation
        jurisdiction = request.form.get('jurisdiction')
        contract_type = request.form.get('contractType')
        contract_file = request.files.get('contract')

        if not jurisdiction or not contract_type:
            return jsonify({"error": "Please select both jurisdiction and contract type"}), 400

        # File handling
        contract_path = None
        if contract_file and allowed_file(contract_file.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            contract_filename = secure_filename(contract_file.filename)
            contract_path = os.path.join(app.config['UPLOAD_FOLDER'], contract_filename)
            contract_file.save(contract_path)
            print(f"Processing contract: {contract_path}")

        # Prepare legal references
        legal_resources = {
            'regulations': os.path.join(project_root, 'Data', 'Gold Standards', 
                                        contract_type, jurisdiction, 'gold_standard.txt'),
            'risky_clauses': os.path.join(project_root, 'Data', 'Gold Standards',
                                          contract_type, jurisdiction, 'gold_standard.txt')
        }

        # Enhanced analysis pipeline
        analysis_start = time.time()
        final_evaluation = clause_comparison(
            contract_path = contract_path,
            law_path      = legal_resources['regulations'],
            risky_clauses = legal_resources['risky_clauses'],
            model         = os.environ.get("LLM_MODEL", "deepseek-chat"),
            role          = "user",
            api_base      = os.environ.get("OPENAI_API_BASE", "https://api.deepseek.com"),
            api_key       = os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE"),
            temperature   = 0.3,
            top_p         = 0.1,
            max_tokens    = 8192
        )
        print(f"Analysis completed in {time.time() - analysis_start:.2f}s")

        # Parse enhanced output format (Bilingual loose matching)
        import re
        clauses = []
        current_clause = None

        for line in final_evaluation.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Lenient clause start matching
            if 'Clause:' in line or '条款:' in line or line.startswith('### Clause'):
                if current_clause and current_clause['text']:
                    clauses.append(current_clause)

                # Initialize a new clause dictionary
                current_clause = {
                    'number': len(clauses) + 1,
                    'text': '',
                    'classification': '',
                    'risk_tier': '',
                    'details': {
                        'regulations': '',
                        'linguistic_traits': '',
                        'explanation': '',
                        'improvement_guidance': ''
                    },
                    'current_field': 'text'
                }

                if ':' in line or '：' in line:
                    normalized_line = line.replace('：', ':')
                    text_part = normalized_line.split(':', 1)[1].strip().strip('"').strip("'")
                    if text_part:
                        current_clause['text'] = text_part

            elif current_clause:
                line_lower = line.lower()
                is_new_field = False
                
                # Check for standard field markers
                if ':' in line or '：' in line:
                    normalized_line = line.replace('：', ':')
                    field_part = normalized_line.split(':', 1)[0].strip()
                    content_part = normalized_line.split(':', 1)[1].strip()
                    
                    if len(field_part) < 60:
                        field_lower = field_part.lower()
                        matched_field = None
                        
                        if 'regulation' in field_lower or '法规' in field_lower or '法律' in field_lower:
                            matched_field = 'regulations'
                        elif 'classification' in field_lower or '分类' in field_lower or '定性' in field_lower:
                            matched_field = 'classification'
                            current_clause['is_unenforceable'] = ('unenforceable' in content_part.lower() or '不可执行' in content_part)
                        elif 'risk' in field_lower or '风险' in field_lower or 'tier' in field_lower:
                            matched_field = 'risk_tier'
                        elif 'explanation' in field_lower or '解释' in field_lower or 'reasoning' in field_lower or '分析' in field_lower or '说明' in field_lower:
                            matched_field = 'explanation'
                        elif 'improvement' in field_lower or 'guidance' in field_lower or '建议' in field_lower or '修改' in field_lower:
                            matched_field = 'improvement_guidance'
                        elif 'linguistic' in field_lower or '语言' in field_lower or 'trait' in field_lower or '缺陷' in field_lower:
                            matched_field = 'linguistic_traits'
                            
                        if matched_field:
                            is_new_field = True
                            current_clause['current_field'] = matched_field
                            
                            if matched_field in ['classification', 'risk_tier']:
                                current_clause[matched_field] = content_part
                            else:
                                current_clause['details'][matched_field] = content_part

                if not is_new_field:
                    # Append it robustly to the current field
                    curr_field = current_clause.get('current_field')
                    if curr_field == 'text' and not current_clause['text']:
                        current_clause['text'] = line.strip('"').strip("'")
                    elif curr_field in ['classification', 'risk_tier']:
                        current_clause[curr_field] = (current_clause[curr_field] + ' ' + line).strip()
                    elif curr_field in current_clause['details']:
                        existing = current_clause['details'][curr_field]
                        separator = '<br>' if existing else ''
                        current_clause['details'][curr_field] = existing + separator + line

        if current_clause and current_clause.get('text'):
            clauses.append(current_clause)
            
        # Clean up output formatting logic centrally
        for c in clauses:
            # Clean up regulations bullet numbering and remove "None (无)" text when empty
            if c['details'].get('regulations'):
                c['details']['regulations'] = re.sub(r'^(?:\d+[\.、\s]+|(?:[一二三四五六七八九十百千万]+)[\.、\s]+|(?:\([0-9]+\))|(?:\（[0-9一二三四五六七八九十]+\）))', '', c['details']['regulations']).strip()
                if c['details']['regulations'].lower() in ['none', 'none (无)', '无', 'none/无']:
                    c['details']['regulations'] = ''

        # Generate analysis metadata
        analysis_metadata = {
            'jurisdiction': jurisdiction,
            'contract_type': contract_type,
            'timestamp': datetime.now().isoformat(),
            'clause_count': len(clauses),
            'unenforceable_count': sum(
                1 for c in clauses 
                if c.get('is_unenforceable') 
                or (c.get('risk_tier') and any(r in c['risk_tier'].lower() for r in ['high', 'medium', '高风险', '中风险']))
            )
        }

        print("DEBUG: Extracted clauses ->", analysis_metadata)

        return jsonify({
            "metadata": analysis_metadata,
            "clauses": clauses,
            "raw": final_evaluation,
            "legal_resources": legal_resources
        })

    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}", exc_info=True)
        err_str = str(e)
        user_msg = "Analysis failed"
        if "429" in err_str or "Rate limit" in err_str:
            user_msg = "API Rate Limit Exceeded (大模型 API 请求频率过高或Token额度已用尽)。请稍等几分钟后重试，或检查您的账户额度。"
        elif "401" in err_str or "Authentication" in err_str:
            user_msg = "API Key Invalid (API 密钥无效)。请检查配置。"
        
        return jsonify({
            "error": user_msg,
            "message": err_str,
            "trace": traceback.format_exc() if app.debug else None
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
