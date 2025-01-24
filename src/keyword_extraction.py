import openai

def extract_keywords(user_prompt: str, model_name: str = "gpt-4") -> str:
    """
    Uses ChatCompletion to interpret the user's natural language prompt 
    and return a short, clean string of keywords for PubMed.

    Example:
    user_prompt = "I want the latest news in microbiology and the connection between the microbiota and human health"

    GPT might return: "microbiology, microbiota, human health"
    """

    system_instructions = (
        "You are an assistant specialized in extracting concise PubMed search terms "
        "from a user's query."
        "Never include phrases like 'latest news' or 'I want to learn.' or extraneous filler"
        "Never include words like 'news' or 'learn' or 'about' or 'research' or 'study' or 'findings' or 'advancements'"
        "Only provide the best short scientific keywords, each separated by commas. "
        "Give 1 to 5 words maximum, strictly."
        "No extra commentary. No filler words."
    )

    messages = [
        {"role": "system", "content": system_instructions},
        {
            "role": "user",
            "content": f"User's query:\n'{user_prompt}'\n\nExtract the best short keywords for PubMed search."
        },
    ]

    response = openai.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=1.0,
        presence_penalty=0.0
    )

    keywords_str = response.choices[0].message.content.strip()
    return keywords_str