# ContractNerd International

ContractNerd International is an academic contract-analysis prototype that uses large language models to review contracts across jurisdictions. The system helps identify clauses that may be incomplete, ambiguous, prejudicial, potentially unenforceable, or in need of further legal review.

The application currently supports contract analysis across multiple jurisdictions, including China-based jurisdictions and India - Delhi.

## Overview

ContractNerd International allows a user to upload a PDF contract, select a jurisdiction and contract type, and receive clause-level analysis. The system extracts clauses from the uploaded document, compares them against jurisdiction-specific reference material, and returns structured results with risk levels, explanations, legal authority where available, and improvement guidance.

The goal is not only to label a clause as risky, but to explain why it may be risky, what information may be missing, and what legal or drafting issue should be reviewed.

## Supported Jurisdictions

The current interface includes the following jurisdiction options:

- National (全国)
- Beijing (北京)
- Shanghai (上海)
- Guangdong (广东)
- Hefei (合肥)
- India - Delhi

## Supported Contract Types

The current interface includes the following contract types:

- Rental
- Employment

Rental agreement analysis is currently implemented for India - Delhi. Employment analysis depends on whether jurisdiction-specific data files are available for the selected jurisdiction.

## Features

- PDF contract upload
- Jurisdiction selection
- Contract type selection
- Clause extraction from uploaded agreements
- Clause-level legal and drafting risk analysis
- Risk classification as High Risk, Medium Risk, or Low Risk
- Legal authority display where applicable
- Explanation of the clause issue
- Improvement guidance for flagged clauses
- Copyable analysis results
- Developer and team information page

## Analysis Philosophy

ContractNerd International is designed for source-backed issue spotting.

For each clause, the system should try to explain:

1. What the clause says.
2. Whether the clause is complete or missing important information.
3. Whether the clause is ambiguous or practically risky.
4. Whether a jurisdiction-specific legal reference applies.
5. What the relevant legal source says, when available.
6. How the clause may conflict with or fail to satisfy that source.
7. What revision or review step may improve the clause.

The system should avoid treating ordinary template blanks as legal violations. For example, placeholders such as `(Date)`, `(Amount)`, `(Address)`, `(Starting Date of Agreement)`, `(Expiry Date of Agreement)`, `(Amount of rent in Numbers)`, or `(city)` should generally be treated as missing required information unless a specific legal source supports a stronger conclusion.

## Output Format

The intended output for each clause is:

```text
Clause: "[Exact clause text]"
Legal Authority: [Exact Act and section, or None]
Classification: [Enforceable / Missing Required Information / Ambiguous / Potentially Prejudicial / Potentially Unenforceable / Requires Further Legal Review]
Risk Tier: [High Risk / Medium Risk / Low Risk]
Explanation: [Source-backed explanation of the legal, drafting, or practical issue]
Improvement Guidance: [Specific revision or review step]
```

The web interface displays:

- Total clauses
- Clauses flagged for review
- Selected jurisdiction
- Clause text
- Risk tier
- Legal authority, where available
- Explanation
- Improvement guidance

## Project Structure

```text
.
├── Code/
│   ├── app.py
│   ├── base/
│   │   ├── clause_comparison.py
│   │   ├── clause_generation.py
│   │   ├── main.py
│   │   ├── regulation_synthesizing.py
│   │   └── utils/
│   │       └── functions.py
│   ├── static/
│   └── ui/
│       └── templates/
│           ├── about.html
│           └── index.html
├── Data/
│   ├── Gold Standards/
│   ├── Regulations/
│   └── Risky Clauses/
├── uploads/
├── .env.example
├── .gitignore
├── LICENSE
├── Pipfile
└── README.md
```

## Data Organization

Jurisdiction-specific files are stored under the `Data/` directory.

For each contract type and jurisdiction, the expected structure is:

```text
Data/
├── Gold Standards/
│   └── [Contract Type]/
│       └── [Jurisdiction]/
│           └── gold_standard.txt
├── Regulations/
│   └── [Contract Type]/
│       └── [Jurisdiction]/
│           └── regulations.txt
└── Risky Clauses/
    └── [Contract Type]/
        └── [Jurisdiction]/
            └── risky_clauses.txt
```

For example, the India - Delhi rental workflow uses:

```text
Data/Gold Standards/Rental/India - Delhi/gold_standard.txt
Data/Regulations/Rental/India - Delhi/regulations.txt
Data/Risky Clauses/Rental/India - Delhi/risky_clauses.txt
```

For employment analysis, the same structure should be used under `Employment` when jurisdiction-specific employment data is available:

```text
Data/Gold Standards/Employment/[Jurisdiction]/gold_standard.txt
Data/Regulations/Employment/[Jurisdiction]/regulations.txt
Data/Risky Clauses/Employment/[Jurisdiction]/risky_clauses.txt
```

## Reference Files

### `gold_standard.txt`

The gold standard file describes what a strong contract should contain for a given jurisdiction and contract type. It can include completeness expectations, recommended drafting standards, and important clause categories.

### `regulations.txt`

The regulations file contains jurisdiction-specific legal references used for source-backed analysis. The model should cite only authorities included in this file and should not invent statutes, cases, sections, or legal rules.

### `risky_clauses.txt`

The risky clauses file gives guidance for classifying contract language by risk level. It helps distinguish high-risk legal issues from medium-risk drafting problems and low-risk standard clauses.

## Setup

Create a `.env` file using `.env.example` as a template.

```env
OPENAI_API_KEY="YOUR_API_KEY_HERE"
OPENAI_API_BASE="https://api.openai.com/v1"
LLM_MODEL="gpt-4o-mini"
```

Do not commit your real `.env` file.

Install dependencies:

```bash
pipenv install
```

Run the Flask app:

```bash
pipenv run python Code/app.py
```

Or, if you are using an activated virtual environment:

```bash
python Code/app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Usage

1. Start the Flask app.
2. Open the local web interface.
3. Upload a PDF contract.
4. Select the relevant jurisdiction.
5. Select the contract type.
6. Click **Analyze Contract**.
7. Review the clause-level output.

For the India - Delhi demo, use:

```text
Jurisdiction: India - Delhi
Contract Type: Rental
```

## Development Notes

The main Flask backend is located at:

```text
Code/app.py
```

The clause analysis pipeline is located at:

```text
Code/base/clause_comparison.py
```

The frontend templates are located at:

```text
Code/ui/templates/index.html
Code/ui/templates/about.html
```

Uploaded files are temporarily stored in:

```text
uploads/
```

## Legal Analysis Rules

The system should follow these principles:

- Use the exact clause text from the uploaded contract.
- Cite legal authority only when it appears in the jurisdiction-specific reference file.
- Do not invent legal sources.
- Do not treat placeholders or missing fields as legal violations by default.
- State uncertainty when the applicable law depends on facts not present in the contract.
- Explain the connection between the cited authority and the actual clause language.
- Provide practical improvement guidance.

For liquidated damages, penalty, holdover rent, or double-rent clauses, the analysis should explain the reasonable-compensation issue and should not automatically state that the amount must be limited to ordinary rent unless the legal reference specifically says so.

## Disclaimer

ContractNerd International is an academic research prototype. It is not legal advice and should not be used as a substitute for professional legal review. Users should consult qualified legal counsel before signing, enforcing, or relying on any legally binding agreement.

## Credits

- India/Delhi Developer: Dhruv Pandoh
- Original App Developer: Haowen (Hollan) Yuan
- Research Advisor: Professor Dennis Shasha
- Paper Co-authors: Musonda Sinkala and Yuge Duan