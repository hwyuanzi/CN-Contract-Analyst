# Chinese Contract Nerd (CN-Contract-Analyst)

An LLM-powered application for analyzing Chinese contracts and identifying risky, unenforceable, or ambiguous clauses with a premium Liquid Glass aesthetic.

## Project Overview

Chinese Contract Nerd is a state-of-the-art contract analysis tool designed to detect and highlight potential risks in Chinese legal agreements. The tool empowers second parties (such as renters and employees) by identifying missing elements, illegal terms, and unfair clauses.

This application is an extended development based on the academic foundation and original web app launched alongside our research article:  
**[ContractNerd: An AI Tool to Find Unenforceable, Ambiguous, and Prejudicial Clauses in Contracts](https://doi.org/10.3390/electronics14214212)** (Electronics 2025).

- **App Developer:** Haowen (Hollan) Yuan ([https://www.hyuan.io/](https://www.hyuan.io/))
- **Research Advisor:** Dennis Shasha ([https://cs.nyu.edu/~shasha/](https://cs.nyu.edu/~shasha/))
- **Paper Co-authors:** Musonda Sinkala, Yuge Duan

## Features

- **Bilingual Analysis:** Provides risk assessments, legal explanations, and improvement guidance in both English and Chinese.
- **Clause Risk Profiling:** Detects lexical ambiguity, syntactic ambiguity, undue generality, and redundant clauses specific to Chinese legal contexts.
- **Premium User Interface:** A modern, frosted glassmorphism UI styled after Apple's liquid glass design.
- **API Integration:** Backend processing via LLM pipeline (Meta-Llama 3.3).

## Folder Structure

```text
Chinese-Contract-Nerd
│── Code/                        # Source code for the project
│   ├── base/                    # Core contract analysis logic
│   │   ├── utils/               # Utility scripts
│   │   ├── clause_comparison.py # Compares clauses against regulations 
│   │   ├── clause_generation.py # Generates risky clauses
│   │   ├── regulation_synthesizing.py 
│   ├── ui/                      # Front-end interface
│   │   ├── templates/           # HTML templates (index.html, about.html)
│   ├── static/                  # Static web assets (logos, images)
│   ├── app.py                   # Flask server application
│── Data/                        # Legal databases and repositories
│   ├── Gold Standards/          # Ground truth regulations & rules for the LLM pipeline
│   ├── Regulations/             # Chinese regional and national legal documents
│   ├── Risky Clauses/           # Example clauses for few-shot learning
│── .env.example                 # Template for API credentials
│── Pipfile / Pipfile.lock       # Python dependencies (managed by Pipenv)
│── README.md                    # Project documentation
```

## Running the Web App Locally (Deployment Guide)

Follow these detailed steps to host and launch the application on your local machine:

### 1. Clone the Repository
Open your terminal and clone the project source code:
```bash
git clone https://github.com/hwyuanzi/CN-Contract-Analyst.git
cd CN-Contract-Analyst
```

### 2. Set Up the Environment
This project uses **Pipenv** for clean dependency management. Ensure you have Python 3.10+ installed on your system.
```bash
# Install pipenv globally if you don't have it yet
pip install pipenv

# Install all required project dependencies
pipenv install
```

### 3. Configure the LLM API (.env file)
The application relies on large language models (such as Meta-Llama 3.3 or DeepSeek) to analyze contracts. You must provide your API credentials before launching the app.

Create a file named `.env` in the root directory (you can copy the provided `.env.example` file):
```bash
cp .env.example .env
```
Open the `.env` file and configure your API details. 
*Note: If you use the default DeepSeek model, you only need to provide the `OPENAI_API_KEY`.*

**Example for using DeepSeek (Default):**
```env
OPENAI_API_KEY="sk-your-deepseek-api-key"
```

**Example for using Meta-Llama 3.3 (via SambaNova or other OpenAI-compatible proxies):**
*(This allows handling UUID format keys and custom endpoints)*
```env
OPENAI_API_KEY="your-uuid-or-proxy-api-key"
OPENAI_API_BASE="https://api.sambanova.ai/v1"
LLM_MODEL="Meta-Llama-3.3-70B-Instruct"
```

### 4. Start the Flask Server
Once your environment variables are configured, launch the backend server:
```bash
pipenv run python Code/app.py
```
You should see terminal output confirming the server has started (e.g., `* Running on http://127.0.0.1:5000`).

### 5. Access the Web Interface
Open your favorite web browser and navigate to the local host address:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

You can now use the elegant UI to upload PDF contract files and run bilingual risk analyses!

---

## 摘要 (Chinese Summary)

**Chinese Contract Nerd (中国合同分析助手)** 是一款基于大语言模型 (LLM) 的工具，专为分析中文合同中的风险条款而设计。

本项目是基于我们团队2025年发表的基础研究论文及初期Web应用的进一步延伸与开发落地：[《ContractNerd: An AI Tool to Find Unenforceable, Ambiguous, and Prejudicial Clauses in Contracts》](https://doi.org/10.3390/electronics14214212)。该Web应用通过强大的自然语言处理技术，可有效识别中文合同中存在歧义、过度泛化、冗余以及违反相关法律法规（如《民法典》）的霸王条款。全站采用极具高级感的“苹果玻璃态 (Liquid Glass)” UI设计，提供严谨的双语鉴定报告。

- **应用开发者:** 袁浩文 (Haowen Yuan) - [https://www.hyuan.io/](https://www.hyuan.io/)
- **研究指导教授:** Dennis Shasha - [https://cs.nyu.edu/~shasha/](https://cs.nyu.edu/~shasha/)
- **论文合作作者:** Musonda Sinkala, Yuge Duan
