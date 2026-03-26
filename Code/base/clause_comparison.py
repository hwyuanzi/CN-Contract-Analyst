import os
import pickle
import openai
import json
from Code.base.utils.functions import read_pdf_pymupdf, extract_info  # If publishing the code using flask
# from utils.functions import read_pdf_pymupdf, extract_info  # If testing locally

def clause_comparison(contract_path, law_path, risky_clauses, model, role, api_base, api_key, temperature, top_p, max_tokens, retries = 5):
    # Define Llama client
    client = openai.OpenAI(
        api_key  = api_key,
        base_url = api_base,
    )

    def completeness_assesment(contract, laws):
        prompt = f"""
                     You are a contract language specialist tasked with reviewing the
                     following Chinese contract relative to the gold standard contract provided.
                     Highlight each clause in the gold standard contract that is not present
                     in the provided contract and detail the possible implications of this
                     clause not being present. ALL OUTPUT MUST BE IN CHINESE.
                     The output should be of the following format:
                     Clause:
                     Implication if missing:   
                  """

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": role, "content": prompt}],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    # Function to compare contract against relevant laws
    def law_comparison(contract, laws):

        prompt = f"""
                  You are a contract language specialist reviewing Chinese contract clauses against regulations. 
                  ALL YOUR RESPONSES AND REASONING MUST BE BILINGUAL (BOTH ENGLISH AND CHINESE).
                  Output Requirements:
                  - Analyze each clause individually
                  - Use EXACTLY this format for every clause without deviation:
                      
                  Clause: "[EXACT FULL CLAUSE TEXT FROM CONTRACT IN CHINESE]"
                  Regulation(s) Implicated: [REGULATION CITATION IN ENGLISH / REGULATION CITATION IN CHINESE OR "None/无" IF COMPLIANT]
                  Reasoning: [CONCISE EXPLANATION OF COMPLIANCE/NON-COMPLIANCE IN ENGLISH]
                  [CONCISE EXPLANATION OF COMPLIANCE/NON-COMPLIANCE IN CHINESE]
                    
                  Rules:
                  1. Always include the exact clause text in quotes after "Clause:"
                  2. Never create titles or summarize clauses - use them exactly as written
                  3. If uncertain about compliance, state this in both languages in the reasoning
                  4. Never combine clauses - analyze each separately
                  5. Include all clauses, even compliant ones
                  6. Preserve all numbers and names exactly as written
                    
                  Contract Clauses:
                  {contract}
                   
                  Regulations:
                  {laws}
                  """

        response = client.chat.completions.create(
            model       = model,
            messages    = [{"role": role, "content": prompt}],
            temperature = temperature,
            top_p       = top_p,
            max_tokens  = max_tokens,
        )

        return response.choices[0].message.content

    # Function to conduct few shot learning to classify "risky" clauses
    def few_shot_learning(comparison, risky_clauses_text):
        prompt = f"""
                  You are a contract language specialist.
                  Having compared a Chinese contract against a set of regulations, you've identified the following:
                  {comparison}

                  YOUR TASK:
                  Provide all explanations and guidance BILINGUALLY in both English and Chinese.

                  1. Risk Tier Assignment:
                     - High Risk (高风险): Clearly violates law in common scenarios
                     - Medium Risk (中风险): Potentially problematic in some contexts
                     - Low Risk (低风险): Generally compliant but needs monitoring
                
                  2. Contextual Classification:
                     - For each clause, specify bilingually:
                       * "Enforceable in [specific contexts] (在[特定背景]下可执行)"
                       * OR "Unenforceable under [specific conditions] (在[特定条件]下不可执行)"
                     - Note any exception cases in both languages.
                     
                  3. Improvement Framework:
                    - For medium/high risk clauses, suggest:
                      Alternative phrasing options in both English and Chinese.
                    - For low risk clauses:
                      No changes needed (无需修改).

                  Output Format:
                  - Clause: The full text of the clause.
                  - Regulation(s) Implicated: The exact regulation(s) or criteria implicated (if unenforceable). Provide in English & Chinese.
                  - Classification: Either `Enforceable (可执行)` or `Unenforceable (不可执行)`. Include bilingual contextual conditions.
                  - Risk Tier: [High Risk (高风险)/Medium Risk (中风险)/Low Risk (低风险)]
                  - Explanation of Classification: A clear bilingual explanation of why the clause was classified as enforceable or unenforceable. If one-sided, mention this in both languages.
                  - Improvement Guidance: [Actionable steps in English] [Actionable steps in Chinese]
                  
                  Rules:
                  1. Always include the exact clause text in quotes after "Clause:"
                  2. Never create titles or summarize clauses - use them exactly as written
                  3. If uncertain about compliance, state this in the reasoning
                  4. Never combine clauses - analyze each separately
                  5. Include all clauses, even compliant ones
                  6. Preserve all numbers and names exactly as written
                  """

        response = client.chat.completions.create(
            model       = model,
            messages    = [{"role": role, "content": prompt}],
            temperature = temperature,
            top_p       = top_p,
            max_tokens  = max_tokens,
        )

        return response.choices[0].message.content

    def language_detection(comparison):
        prompt = f"""You are provided with a list of Chinese contract clauses:
                     {comparison}
                     For each clause, the following fields are included:
                     - Clause:
                     - Regulation(s) Implicated:
                     - Classification:
                     - Risk Tier:
                     - Explanation of Classification:
                     - Improvement Guidance:
                     
                     YOUR TASK:
                     ALL YOUR OUTPUT AND EXPLANATIONS MUST BE IN CHINESE.
                     
                     - For all clauses, reproduce all the provided fields in the output. Translate the field values into Chinese if they are not already.
                     - If a clause is classified as unenforceable, analyze it to determine whether it exhibits any of the following linguistic flaws:
                  1. Lexical Ambiguity (词汇模糊)
                  2. Syntactic Ambiguity (语法模糊)
                  3. Undue Generality (过分宽泛)
                  4. Redundancy (冗余)
                  5. None of these traits (None/无)
                  
                  Analyze EACH CLAUSE individually.
                  Do not combine clauses. If a clause has multiple traits, list all applicable traits.
                  Provide an explanation for your choice for EACH CLAUSE that exhibits a trait.
                  The explanation MUST be in both English and Chinese.
                  If the clause does not exhibit any trait, write "Not applicable (不适用)".

                  Format your response EXACTLY as follows for each clause:
                  Clause: "[Full text of the clause exactly as provided]"
                  Trait: [Trait 1], [Trait 2], ...
                  Explanation: [Bilingual reasoning for trait selection, or "Not applicable (不适用)"]
                  """

        response = client.chat.completions.create(
            model       = model,
            messages    = [{"role": role, "content": prompt}],
            temperature = temperature,
            top_p       = top_p,
            max_tokens  = max_tokens,
        )

        return response.choices[0].message.content

    # Read the contract file
    contract_text = read_pdf_pymupdf(contract_path)

    ##############################################################
    ######### Include Code to split clauses into batches #########
    ##############################################################

    # Unpack the list into a string
    risky_clauses_text = ""
    # for item in loaded_data:
    #     risky_clauses_text += item + ('\n\n' if 'Combination:' in item else '\n')

    # Read the regulation file
    regulations_text = read_pdf_pymupdf(law_path)

    clauses = extract_info(contract_text = contract_text)

    comparison1 = law_comparison(clauses, regulations_text)
    comparison2 = few_shot_learning(comparison1, risky_clauses_text)
    comparison3 = language_detection(comparison2)

    return comparison3

if __name__ == "__main__":
    final_evaluation  = clause_comparison(
        contract_path = "example_contract.pdf",
        law_path      = "example_regulations.txt",
        risky_clauses = "example_risky_clauses.txt",
        model         = "deepseek-chat",
        role          = "You are an experienced Chinese contract analyst.",
        api_key       = os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE"),
        api_base      = "https://api.deepseek.com",
        temperature   = 0.3,
        top_p         = 0.1,
        max_tokens    = 8192
    )
    print(final_evaluation)
