import fitz
import re

def read_pdf_pymupdf(file_path):
    """
    Reads the contents of a PDF file and returns the extracted text.
    """
    text = ""
    with fitz.open(file_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text()
    return text

def extract_info(document, prompt, client, model, role, temperature, top_p, max_tokens):
    """
    Extracts information from the given document using the specified LLM model.
    """
    response = client.chat.completions.create(
        model       = model,
        messages    = [{"role": role,
                        "content": f"{prompt}: {document}"}],
        temperature = temperature,
        top_p       = top_p,
        max_tokens  = max_tokens,
    )

    # Collect streamed output into a single variable
    text = response.choices[0].message.content

    return (text)

def extract_info(contract_text):
    """
    Extracts clauses with subpoints combined into their main numbered clauses.
    Returns them as a numbered string with each main clause (including subpoints) on one line.
    """
    # Split the text into main sections using Arabic numbers or Chinese numbers/formats
    # e.g., "1.", "1、", "一、", "（一）", "第一条", "第1条"
    # The previous regex missed the simple '\d+\.' because of the non-capturing group structure.
    pattern = r'(?=\n(?:(?:\d+[\.、])|(?:[一二三四五六七八九十百千万]+[\.、])|(?:（[一二三四五六七八九十百千万]+）)|(?:\([0-9]+\))|(?:第[一二三四五六七八九十百千万0-9]+[章节条])))'
    main_sections = re.split(pattern, contract_text.strip())

    # Sometimes the very first section is just the title (e.g., "房屋租赁合同")
    # We want to keep it if it contains actual clause data, but usually we filter empty ones later.
    processed_clauses = []

    for section in main_sections:
        if not section.strip():
            continue

        # Remove leading/trailing whitespace
        section = section.strip()

        # Combine all lines in the section into one line
        combined = ' '.join(line.strip() for line in section.split('\n') if line.strip())

        # Clean up multiple spaces
        combined = ' '.join(combined.split())

        processed_clauses.append(combined)

    return '\n'.join(processed_clauses)