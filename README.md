# Chinese Contract Nerd (CN-Contract-Analyst)

An LLM-powered application for analyzing Chinese contracts and identifying risky, unenforceable, or ambiguous clauses with a premium Liquid Glass aesthetic.

## Project Overview

Chinese Contract Nerd is a state-of-the-art contract analysis tool designed to detect and highlight potential risks in Chinese legal agreements. The tool empowers second parties (such as renters and employees) by identifying missing elements, illegal terms, and unfair clauses.

This application is an extended development based on the academic article:  
**[LLM-Based Analysis of Unconscionable Contracts](https://doi.org/10.3390/electronics14214212)** (Electronics 2025).

- **Developer:** Haowen (Hollan) Yuan ([https://www.hyuan.io/](https://www.hyuan.io/))
- **Advisor:** Dennis Shasha ([https://cs.nyu.edu/~shasha/](https://cs.nyu.edu/~shasha/))
- **Co-authors:** Musonda Sinkala, Yuge Duan

## Features

- **Bilingual Analysis:** Provides risk assessments, legal explanations, and improvement guidance in both English and Chinese.
- **Clause Risk Profiling:** Detects lexical ambiguity, syntactic ambiguity, undue generality, and redundant clauses specific to Chinese legal contexts.
- **Premium User Interface:** A modern, frosted glassmorphism UI styled after Apple's liquid glass design.
- **API Integration:** Backend processing via LLM pipeline (Meta-Llama 3.3).

## Folder Structure

```
Chinese-Contract-Nerd
│── Code/                        # Source code for the project
│   ├── base/                    # Core contract analysis logic
│   │   ├── utils/               # Utility code
│   │   │   ├── functions.py     
│   │   ├── clause_comparison.py # Compares clauses against regulations 
│   │   ├── clause_generation.py # Generates risky clauses
│   │   ├── regulation_synthesizing.py 
│   ├── ui/                      # Front-end interface
│   │   ├── templates/           # HTML templates (index.html, about.html)
│   ├── app.py                   # Flask server application
│── Data/                        # Repository of regulations and risky clauses
│   ├── Regulations/             # Chinese regional and national legal codes
│   ├── Risky Clauses/           # Example clauses for few-shot learning
│   ├── Tests/                   # Sample contracts for validation
│── requirements.txt             # Python dependencies
│── README.md                    # Project documentation
```

## Running the Web App

1. Clone the repository:
   ```bash
   git clone https://github.com/hwyuanzi/CN-Contract-Analyst.git
   cd CN-Contract-Analyst
   ```
2. Setup the Environment with Pipenv:
   *Ensure you have Python 3.10+ installed on your system. Pipenv is used to manage dependencies cleanly.*
   ```bash
   pip install pipenv
   pipenv install
   ```
3. Start the Flask Server:
   ```bash
   pipenv run python Code/app.py
   ```
4. Access the UI: Open `http://127.0.0.1:5000` in your web browser.

---

## 摘要 (Chinese Summary)

**Chinese Contract Nerd (中国合同分析助手)** 是一款基于大语言模型 (LLM) 的工具，专为分析中文合同中的风险条款而设计。

本项目是我们2025年发表的论文 [《基于LLM的显失公平合同分析》](https://doi.org/10.3390/electronics14214212) 的延伸与落地开发。工具通过精准的自然语言处理技术，可有效识别中文合同中存在歧义、过度泛化、冗余以及违反相关法律法规（如《民法典》）的霸王条款，并提供风险地图与修改建议。全站采用时尚且富有高级感的“苹果玻璃态 (Liquid Glass)” UI设计，同时以中英双语输出鉴定结果。

- **开发人员:** 袁浩文 (Haowen Yuan) - [https://www.hyuan.io/](https://www.hyuan.io/)
- **指导教授:** Dennis Shasha - [https://cs.nyu.edu/~shasha/](https://cs.nyu.edu/~shasha/)
- **合作作者:** Musonda Sinkala, Yuge Duan
