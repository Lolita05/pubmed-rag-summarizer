import requests
import logging
from typing import List, Dict
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

def fetch_mesh_terms(keyword: str, retmax: int = 5) -> List[str]:
    """
    Fetches MeSH terms for a given keyword using PubMed's E-Utilities API.
    
    :param keyword: The search keyword.
    :param retmax: The maximum number of PMIDs to retrieve for fetching MeSH terms.
    :return: A list of unique MeSH terms.
    """
    # Step 1: ESearch to get PMIDs
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esearch_params = {
        "db": "pubmed",
        "term": keyword,
        "retmax": retmax,
        "retmode": "xml"
    }
    
    esearch_resp = requests.get(esearch_url, params=esearch_params)
    if esearch_resp.status_code != 200:
        print(f"ESearch API request failed with status code {esearch_resp.status_code}")
        return []
    
    esearch_root = ET.fromstring(esearch_resp.content)
    pmids = [id_elem.text for id_elem in esearch_root.findall(".//Id")]
    
    if not pmids:
        return []
    
    # Step 2: EFetch to get MeSH terms
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    efetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }
    
    efetch_resp = requests.get(efetch_url, params=efetch_params)
    if efetch_resp.status_code != 200:
        print(f"EFetch API request failed with status code {efetch_resp.status_code}")
        return []
    
    efetch_root = ET.fromstring(efetch_resp.content)
    mesh_terms = set()
    
    for article in efetch_root.findall(".//PubmedArticle"):
        for mesh_heading in article.findall(".//MeshHeading/DescriptorName"):
            mesh_term = mesh_heading.text
            if mesh_term:
                mesh_terms.add(mesh_term)
    
    return list(mesh_terms)

def search_pubmed(
    query: str,
    start_date: str,
    end_date: str,
    retmax: int = 10,
    most_relevant: bool = False,
    filter_medline: bool = False
) -> List[str]:
    """
    This function performs a search for articles in PubMed using ESearch.
    
    :param query: Keywords for the search (e.g., "microbiology AND microbiota AND human health")
    :param start_date: Minimum date (format YYYY/MM/DD)
    :param end_date: Maximum date (format YYYY/MM/DD)
    :param retmax: Maximum number of articles (e.g., 0–15)
    :param most_relevant: If True, sort by "best match"
    :param filter_medline: If True, filtering by MEDLINE can be done in a subsequent step
    :return: List of PMIDs (list of strings)
    """
    # Build the base ESearch URL
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    # Construct a date filter; dp = Date of Publication in PubMed
    # Example: (query) AND (2023/01/01 : 2023/12/31[dp])
    if start_date and end_date:
        date_filter = f"({start_date}:{end_date}[dp])"
        full_query = f"({query}) AND {date_filter}"
    else:
        full_query = query

    # Prepare ESearch parameters
    params = {
        "db": "pubmed",
        "term": full_query,
        "retmax": retmax,
        "retmode": "json",
    }

    # If user wants "most relevant" articles, set "sort=relevance"
    if most_relevant:
        params["sort"] = "relevance"

    logger.info(f"PubMed ESearch params: {params}")

    # Send GET request to PubMed
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    # Extract list of PMIDs from the returned JSON
    pmid_list = data["esearchresult"].get("idlist", [])

    # If filter_medline=True, actual filtering may be done in a subsequent step
    return pmid_list


def get_summaries(pmids: List[str]) -> List[Dict]:
    """
    Получает краткие метаданные статей (title, journal, pubdate и т.д.) через ESummary.

    :param pmids: Список строковых идентификаторов PMID
    :return: Список словарей с информацией (pmid, title, journal, pubdate, pubstatus)
    """
    if not pmids:
        return []

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json"
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    result_dict = data["result"]
    summaries = []

    for pmid in pmids:
        summary_data = result_dict.get(pmid, {})
        if not summary_data:
            continue

        # Title, journal name, publication date, and pubstatus
        title = summary_data.get("title", "")
        journal = summary_data.get("fulljournalname", "")
        pubdate = summary_data.get("pubdate", "")
        pubstatus = summary_data.get("pubstatus", "")

        summaries.append({
            "pmid": pmid,
            "title": title,
            "journal": journal,
            "pubdate": pubdate,
            "pubstatus": pubstatus,
        })

    return summaries


def filter_medline_summaries(summaries: List[Dict]) -> List[Dict]:
    """
    Фильтрует статьи, если необходимо отобрать только те, у которых pubstatus в ['pubmed', 'medline'].

    :param summaries: Список словарей с метаданными статей
    :return: Отфильтрованный список
    """
    filtered = []
    for item in summaries:
        # Lowercase for robust comparison
        status = item["pubstatus"].lower()
        if status in ["pubmed", "medline"]:
            filtered.append(item)
    return filtered


def fetch_abstracts(pmids: List[str]) -> str:
    """
    Использует EFetch для получения XML, содержащего полный абстракт статьи.

    :param pmids: Список PMID
    :return: XML в формате строки
    """
    if not pmids:
        return ""

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.text


# Example usage (for testing)
if __name__ == "__main__":
    # Let's say Python 3.12 is used; the code is compatible with any modern Python 3.x
    query_example = "microbiology AND microbiota AND human health"
    start_d = "2023/01/01"
    end_d = "2023/12/31"

    # Searching up to 5 articles, sorted by best match, possibly check MEDLINE later
    pmids = search_pubmed(query_example, start_d, end_d, retmax=5, most_relevant=True, filter_medline=False)
    print("Found PMIDs:", pmids)

    # Retrieve ESummary data
    summary_list = get_summaries(pmids)
    # Optionally filter for MEDLINE
    summary_filtered = filter_medline_summaries(summary_list)

    print("Filtered Summaries (MEDLINE):")
    for item in summary_filtered:
        print(f"PMID: {item['pmid']}, Title: {item['title']}, PubDate: {item['pubdate']}, Status: {item['pubstatus']}")

    # If needed, fetch raw XML to parse abstracts
    # abstracts_xml = fetch_abstracts(pmids)
    # print("Raw XML snippet:", abstracts_xml[:500], "...")