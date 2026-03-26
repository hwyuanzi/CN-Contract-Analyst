import os
import pickle
import time
import openai
from base.utils.functions import read_pdf_pymupdf, extract_info  # If publishing the code using flask
# from utils.functions import read_pdf_pymupdf, extract_info  # If testing locally

def clause_generation(contract_path, output_file, model, role, api_base, api_key, temperature, top_p, max_tokens, retries = 5):
    # Define Llama client
    client = openai.OpenAI(
        api_key  = api_key,
        base_url = api_base,
    )

    # Function to transform clauses using Llama
    def llama_transformation(clause, retries):
        prompt = f"""
            You are a contract language specialist tasked with identifying and creating transformations of Chinese contract clauses to illustrate linguistic and legal ambiguities. Using the clause provided, apply each of the following transformations IN CHINESE:
                1. Lexical Ambiguity (词汇歧义): Adjust the clause so that it contains terms or phrases with multiple possible interpretations due to insufficient context.
                2. Syntactic Ambiguity (语法歧义): Restructure the clause so the grammatical relationship between words or phrases is unclear or open to multiple interpretations.
                3. Undue Generality (过度泛化): Remove specific details or context to make the clause overly broad or vague, so it becomes unclear what it applies to.
                4. Redundancy (冗余): Add unnecessary or repetitive terms that restate the same information, leading to redundancy in the clause.
                5. A combination of all of the above.

            CLAUSE:
            {clause}

            The output should strictly be of the following format, with no exceptions. Do not include explanations:
                  You are a contract language specialist. You are analyzing Chinese contract clauses and transforming them based on specific directions.
                  ALL YOUR OUTPUT MUST BE BILINGUAL (ENGLISH AND CHINESE).
                  
                  Directions:
                  1. If the goal is "Lexical Ambiguity", introduce terms that could be interpreted in multiple ways in both English and Chinese translations.
                  2. If the goal is "Syntactic Ambiguity", alter the sentence structure so the modification applies ambiguously. 
                  3. If the goal is "Undue Generality", use overly broad language that captures more situations than customary.
                  4. If the goal is "Redundancy", add necessary repetitions in both languages.
                  5. If the goal is "Combination", apply two or more of the above techniques.
                  
                  Below is the original clause, write the transformed clause based on the specified goal in both English and Chinese:
                  Original: {text}
                  Goal: {goal}
                  
                  Output format:
                  Transformed Clause: [English translation of transformed clause]
                  [Chinese transformed clause]
                  """

        delay = 5
        for i in range(retries):
            try:
                response = client.chat.completions.create(
                    model       = model,
                    messages    = [{"role": role, "content": prompt}],
                    temperature = temperature,
                    top_p       = top_p,
                    max_tokens  = max_tokens,
                )
                return response.choices[0].message.content
            except Exception as e:
                if "rate limit" in str(e).lower():
                    print(f"Rate limit hit. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"Error: {e}")
                    break
        print(f"Failed to get a response for post after {retries} retries.")
        return None

    # Read the contract file
    contract_text = read_pdf_pymupdf(contract_path)

    # Extract clauses from the contract
    clauses = extract_info(
        document = contract_text,
        prompt = "Identify the Chinese contract clauses in this contract, detailing all figures and necessary specifics. Do not use any \\n characters within individual clauses - only use it to separate clauses, all parts of an individual clause must be written without any \\n characters. Include the clause name and detail in the same line (e.g., 租金:...). Don't number the clauses. Output in Chinese:",
        client = client,
        model  = model,
        role   = role,
        temperature = temperature,
        top_p  = top_p,
        max_tokens = max_tokens,
    )

    # Split clauses and clean up the list
    clauses_list = [item for item in clauses.split("\n") if item]

    # Transform clauses
    transformed_clauses = []
    for clause in clauses_list:
        result = llama_transformation(clause, retries)
        if result:
            transformed_clauses.append(result)

    # Save to file
    with open(output_file, 'wb') as file:
        pickle.dump(transformed_clauses, file)
    print(f"Output saved to {output_file}")

    return transformed_clauses

if __name__ == "__main__":
    transformed_clauses = clause_generation(
        contract_path = "example_contract.pdf",
        output_file   = "example_risky_clauses.pkl",
        model         = "deepseek-chat",
        role          = "You are an experienced Chinese contract analyst.",
        api_key       = os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE"),
        api_base      = "https://api.deepseek.com",
        temperature   = 0.3,
        top_p         = 0.1,
        max_tokens    = 8192
    )