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
            model         = "deepseek-chat",
            role          = "You are an experienced Chinese contract analyst and legal expert. Please analyze whether the following contract clauses have potential legal risks, ambiguity or unconscionable terminology.",
            api_base      = "https://api.deepseek.com",
            api_key       = os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE"),
            temperature   = 0.3,
            top_p         = 0.1,
            max_tokens    = 8192
        )
        print(f"Analysis completed in {time.time() - analysis_start:.2f}s")

        # Parse enhanced output format (Bilingual loose matching)
        clauses = []
        current_clause = None

        for line in final_evaluation.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Lenient clause start matching (e.g. "Clause:", "Clause 1:", "条款:", "### Clause")
            if 'Clause:' in line or '条款:' in line or line.startswith('### Clause'):
                if current_clause and current_clause['text']:
                    clauses.append(current_clause)

                # Initialize a new clause dictionary
                current_clause = {
                    'number': len(clauses) + 1,  # Simple incremental fallback
                    'text': '',
                    'classification': None,
                    'risk_tier': None,
                    'details': {
                        'regulations': None,
                        'linguistic_traits': None,
                        'explanation': None,
                        'improvement_guidance': None
                    }
                }

                # Try to extract the literal text from the same line if it exists
                if ':' in line:
                    text_part = line.split(':', 1)[1].strip().strip('"').strip("'")
                    if text_part:
                        current_clause['text'] = text_part

            elif current_clause:
                # Lenient field detection for bilingual outputs
                line_lower = line.lower()
                if ('regulation' in line_lower or '法规' in line_lower) and ':' in line:
                    current_clause['details']['regulations'] = line.split(':', 1)[1].strip()
                elif ('classification' in line_lower or '分类' in line_lower) and ':' in line:
                    classification = line.split(':', 1)[1].strip()
                    current_clause['classification'] = classification
                    current_clause['is_unenforceable'] = ('unenforceable' in classification.lower() or '不可执行' in classification)
                elif ('risk tier' in line_lower or '风险' in line_lower) and ':' in line:
                    current_clause['risk_tier'] = line.split(':', 1)[1].strip()
                elif ('explanation' in line_lower or '解释' in line_lower or 'reasoning' in line_lower) and ':' in line:
                    current_clause['details']['explanation'] = line.split(':', 1)[1].strip()
                elif ('improvement' in line_lower or 'guidance' in line_lower or '建议' in line_lower) and ':' in line:
                    current_clause['details']['improvement_guidance'] = line.split(':', 1)[1].strip()
                elif ('linguistic' in line_lower or '语言' in line_lower) and ':' in line:
                    current_clause['details']['linguistic_traits'] = line.split(':', 1)[1].strip()
                elif not current_clause['text'] and not ':' in line:
                    # If we just saw "Clause:" on the previous line and this line is plain text
                    current_clause['text'] = line.strip('"').strip("'")

        if current_clause and current_clause.get('text'):
            clauses.append(current_clause)

        # Generate analysis metadata
        analysis_metadata = {
            'jurisdiction': jurisdiction,
            'contract_type': contract_type,
            'timestamp': datetime.now().isoformat(),
            'clause_count': len(clauses),
            'unenforceable_count': sum(1 for c in clauses if c.get('is_unenforceable'))
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
        return jsonify({
            "error": "Analysis failed",
            "message": str(e),
            "trace": traceback.format_exc() if app.debug else None
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
