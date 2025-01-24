# src/enhanced_search.py
from src.pubmed_api import search_pubmed
from typing import List, Dict
import openai


def get_synonyms_dict_gpt(extracted_keywords: str, model_name="gpt-4") -> Dict[str, list]:
    """
    Dynamically calls GPT to find synonyms/related terms for each extracted keyword.
    Example usage: 
      extracted_keywords = "PEMF, anticancer therapies, doxorubicin, molecular mechanisms"
      synonyms_dict = get_synonyms_dict_gpt(extracted_keywords)
    This might yield something like:
      {
        "PEMF": ["pulsed electromagnetic field", "pemf therapy"],
        "anticancer therapies": ["anticancer", "cancer", "chemotherapy"],
        "doxorubicin": ["adriamycin"],
        ...
      }

    Then you can build a final PubMed query.
    """
    synonyms_dict = {}
    # Split the extracted keywords by comma
    keywords_list = [k.strip() for k in extracted_keywords.split(",") if k.strip()]
    
    # A short system prompt that clarifies the format
    system_prompt = (
        "You are a helpful assistant that provides synonyms or related scientific terms. "
        "Given a single keyword (which may be multiple words), output synonyms or expansions "
        "that might help in broadening a PubMed search query. "
        "Return them in a short comma-separated list, with no extra commentary."
    )
    
    for kw in keywords_list:
        # Construct a user message for each keyword
        user_content = (
            f"Keyword: '{kw}'\n\n"
            "Please return synonyms or expansions that can broaden the PubMed search. "
            "For example, if 'anticancer therapies' is the keyword, you might include 'anticancer, cancer, chemotherapy'. "
            "No filler words, just synonyms or expansions, comma-separated."
        )

        # Call ChatCompletion
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2,
            max_tokens=100
        )

        raw_output = response.choices[0].message.content.strip()
        # Parse synonyms from the comma-separated string
        synonyms_list = [s.strip() for s in raw_output.split(",") if s.strip()]
        synonyms_dict[kw] = synonyms_list

    return synonyms_dict

def do_two_phase_search(base_query: str, start_date: str, end_date: str, retmax: int, most_relevant: bool) -> List[str]:
    """
    1) search with base_query via ESearch
    2) if results < threshold, find related articles from the top 1 or 2 PMIDs
    3) combine them
    """
    pmids = search_pubmed(base_query, start_date, end_date, retmax, most_relevant)
    if len(pmids) > 5:
        return pmids

    # If too few results, let's do a "related articles" approach for the top PMIDs
    related_pmids = []
    for pmid in pmids[:2]:
        # e.g. function to do ELink neighbor
        r_p = get_related_pmids(pmid)  # returns a list of PMIDs
        related_pmids.extend(r_p)

    pmids = list(set(pmids + related_pmids))
    return pmids

def get_related_pmids(pmid: str) -> List[str]:
    """
    Example: ELink neighbor approach
    E.g. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id=PMID&cmd=neighbor
    parse the result for LinkSetDb, LinkName=pubmed_pubmed
    """
    import requests
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
    params = {
        "dbfrom": "pubmed",
        "id": pmid,
        "cmd": "neighbor",
        "retmode": "json"
    }
    r = requests.get(base_url, params=params)
    data = r.json()
    # parse the data to get related pmids
    related_ids = []
    linksets = data.get("linksets", [])
    for ls in linksets:
        linksetdbs = ls.get("linksetdbs", [])
        for ldb in linksetdbs:
            if ldb.get("linkname") == "pubmed_pubmed":
                for link in ldb.get("links", []):
                    related_ids.append(str(link))
    return related_ids

def build_refined_query_with_mesh(main_terms: List[str], synonyms_dict: Dict[str, list]) -> str:
    """
    Builds a structured PubMed query with proper grouping and inclusion of MeSH terms.
    
    :param main_terms: List of primary keywords.
    :param synonyms_dict: Dictionary mapping keywords to their synonyms and MeSH terms.
    :return: A well-formatted PubMed search query string.
    """
    or_clauses = []
    for term in main_terms:
        synonyms = synonyms_dict.get(term, [])
        # Include the original term and its synonyms
        combined_terms = [term] + synonyms
        # Escape quotes and ensure proper formatting
        formatted_terms = [f'"{t}"' for t in combined_terms if t]
        if formatted_terms:
            or_clause = " OR ".join(formatted_terms)
            or_clauses.append(f"({or_clause})")
    
    # Combine all OR clauses with AND
    if or_clauses:
        base_query = " AND ".join(or_clauses)
        base_query = f"({base_query})"
    else:
        base_query = ""
    
    return base_query