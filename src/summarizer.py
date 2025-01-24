import os
import openai
from typing import List

def generate_answer(context_chunks: List[str], user_query: str, model_name: str = "gpt-3.5-turbo") -> str:
    """
    Forms the final answer using context (chunks) + user question.

    :param context_chunks: List of text fragments that make up the context.
    :param user_query: User's question (string).
    :param model_name: Name of the OpenAI ChatCompletion model (e.g., "gpt-3.5-turbo").
    :return: Final answer from the model (string).
    """
    # Combine context into one string
    context_text = "\n".join(context_chunks)

    # Prepare messages for ChatCompletion
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that answers questions about scientific articles. "
                "Use the provided context to form a concise and accurate answer. "
                "Follow these rules strictly:"
                "1. First Paragraph (General Overview): Provide a broad statement about scientists finding numerous insights. Conclude with a lead-in that there are key takeaways or trends from these studies."
                "2. Short Summaries (Paragraph or Bulleted List):"
                "   - For each article, write a concise summary as a bulleted list. Sort summaries by year of publication (from oldest to newest)."
                "   - For each summary:"
                "   - Mention the **year** of the study (e.g., 2017, 2001, 2024). "
                "   - Briefly describe the **key focus** (e.g., PEMF stimulation + doxorubicin, melatonin + PEMF, synergy in cancer cells). "
                "   - **Discuss the methods** used in a concise way (e.g., \"tested on mouse osteosarcoma cells,\" \"investigated proliferation of human breast cancer cells\"). "
                "   - State the **results** or **conclusions** (e.g., synergy, potential anti-proliferative effect). "
                "   - Keep each summary to **2-3 sentences** maximum, focusing on results and methods. "
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\nUser question: {user_query}\nAnswer in a concise manner."
        }
    ]

    # Call ChatCompletion (similar to how you did in your karpov code)
    completion = openai.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7
    )

    # Access the answer via choices[0].message.content
    answer = completion.choices[0].message.content
    return answer