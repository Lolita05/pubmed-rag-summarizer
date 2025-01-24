# app/streamlit_app.py

import streamlit as st
import os
import sys

# Adjusting sys.path so that src/ is recognized
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..")) 
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.pubmed_api import get_summaries, filter_medline_summaries
from src.rag_pipeline import build_index, find_top_k
from src.summarizer import generate_answer
from src.utils import parse_date
from src.keyword_extraction import extract_keywords
from src.enhanced_search import build_refined_query_with_mesh, do_two_phase_search, get_synonyms_dict_gpt

def main():
    st.title("PubMed Article Summarizer")

    # Sidebar
    st.sidebar.header("🔍 Search Settings")

    # Date Inputs
    start_date = st.sidebar.date_input(
        "Start Date",
        help="Select the start date for the publication date range of articles."
    )
    end_date = st.sidebar.date_input(
        "End Date",
        help="Select the end date for the publication date range of articles."
    )
    start_str = start_date.strftime("%Y-%m-%d") if start_date else ""
    end_str = end_date.strftime("%Y-%m-%d") if end_date else ""

    # Slider for Max Articles
    retmax = st.sidebar.slider(
        "📈 Max Articles",
        min_value=0,
        max_value=30,
        value=5,
        help="Choose the maximum number of articles to retrieve. Higher numbers may increase search time."
    )

    # Checkbox for Most Relevant (Best Match)
    most_relevant = st.sidebar.checkbox(
        "Most Relevant? (Best Match)",
        value=False,
        help=(
            "When selected, PubMed sorts the search results by relevance to your query rather than by publication date. "
            "This helps surface articles that best match your search terms."
        )
    )

    # Checkbox for Filter by MEDLINE
    filter_med = st.sidebar.checkbox(
        "Filter by MEDLINE?",
        value=False,
        help=(
            "Restrict your search to articles indexed in MEDLINE, PubMed's curated subset of biomedical literature. "
            "This ensures high-quality, peer-reviewed articles with standardized indexing."
        )
    )

    # Checkbox for GPT-based Keyword Extraction
    use_keyword_extraction = st.sidebar.checkbox(
        "Use GPT-based Keyword Extraction?",
        value=True,
        help=(
            "Automatically extract and refine keywords from your query using GPT to improve search relevance."
        )
    )

    # Checkbox for Synonyms Expansions
    use_synonyms = st.sidebar.checkbox(
        "Use Synonyms Expansions?",
        value=True,
        help=(
            "Expand your search terms with synonyms to include related articles that may use different terminology."
        )
    )

    # Main content: User Query
    st.header("PubMed Query")
    user_query = st.text_area(
        "Enter your research question or topic:",
        "Papers exploring the molecular mechanisms of PEMF stimulation assisting anticancer therapies based on doxorubicin",
        help="Type your research question or topic."
    )

    if st.button("🔍 Search & Summarize"):
        if not user_query.strip():
            st.warning("⚠️ Please enter a query before searching.")
            return

        # Step 1: GPT-based Keyword Extraction
        if use_keyword_extraction:
            extracted = extract_keywords(user_query, model_name="gpt-4")
            st.write("**Extracted Keywords:**", extracted)
        else:
            extracted = user_query  # Fallback to user query if extraction is disabled

        # Step 2: Synonyms Expansions via GPT
        synonyms_dict = {}
        if use_synonyms:
            synonyms_dict = get_synonyms_dict_gpt(extracted, model_name="gpt-4")

        # Step 3: Build a Refined PubMed Query
        main_terms = [t.strip() for t in extracted.split(",") if t.strip()]
        query_str = build_refined_query_with_mesh(main_terms, synonyms_dict)
        with st.expander("View Final PubMed Query"):
            st.write(query_str)

        # Step 4: Perform Two-Phase Search (Exact + Related Articles)
        pmids = do_two_phase_search(
            query_str, 
            parse_date(start_str) or "",
            parse_date(end_str) or "",
            retmax,
            most_relevant
        )
        if not pmids:
            st.warning("⚠️ No articles found after applying expansions and related searches.")
            return

        # Step 5: Retrieve Summaries
        summaries = get_summaries(pmids)
        if filter_med:
            summaries = filter_medline_summaries(summaries)

        if not summaries:
            st.warning("⚠️ No articles found after applying MEDLINE filtering.")
            return

        # Step 6: Prepare Articles for RAG Pipeline
        articles_for_rag = []
        for s in summaries:
            pmid = s["pmid"]
            # Here, using title and pubdate as a placeholder.
            fake_abstract = f"{s['title']} - {s['pubdate']}"
            articles_for_rag.append({"pmid": pmid, "abstract": fake_abstract})

        # Step 7: Build RAG Index
        rag_index = build_index(articles_for_rag, chunk_size=300)

        # Step 8: Find Top Chunks Relevant to User Query
        top_chunks = find_top_k(user_query, rag_index, k=3)
        context_list = [x["chunk_text"] for x in top_chunks]

        # Step 9: Generate Final Answer with Summarization
        final_answer = generate_answer(context_list, user_query, model_name="gpt-4")
        st.subheader("Summaries")
        st.write(final_answer)

        # Step 10: Display References
        st.subheader("References")
        for item in top_chunks:
            pmid_link = f"https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/"
            st.markdown(f"- PMID [{item['pmid']}]({pmid_link})")

if __name__ == "__main__":
    main()