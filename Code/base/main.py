import os
from dotenv import load_dotenv
load_dotenv()
# from clause_generation import clause_generation
from clause_comparison import clause_comparison

def main():
    # Define parameters - Use dynamic pathing from the project root
    project_root  = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Contextual paths for the Chinese Contract tests
    contract_path = os.path.join(project_root, "Data", "Tests", "real_hefei_employment_contract.txt")
    output_file   = os.path.join(project_root, "Data", "Risky Clauses", "Employment", "National (全国)", "risky_clauses.txt")
    legal_doc_path= os.path.join(project_root, "Data", "Gold Standards", "Employment", "Hefei (合肥)", "gold_standard.txt")
    
    api_base      = "https://api.deepseek.com"
    api_key       = os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
    model         = "deepseek-chat"
    role          = "You are an experienced Chinese contract analyst and legal expert. Please analyze whether the following contract clauses have potential legal risks, ambiguity or unconscionable terminology."
    temperature   = 0.3
    top_p         = 0.1
    max_tokens    = 8192

    # Compare clauses
    final_evaluation = clause_comparison(
        contract_path = contract_path,
        law_path      = legal_doc_path,
        risky_clauses = output_file,
        model         = model,
        role          = role,
        api_key       = api_key,
        api_base      = api_base,
        temperature   = temperature,
        top_p         = top_p,
        max_tokens    = max_tokens
    )


    print(final_evaluation)

if __name__ == "__main__":
    main()
