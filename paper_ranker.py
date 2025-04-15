from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def get_paper_embeddings(papers, query, model_name='all-MiniLM-L6-v2'):
    """
    Generate embeddings for papers and query using a BERT model.
    
    Args:
        papers (list): List of paper dictionaries
        query (str): Original search query
        model_name (str): Name of the BERT model to use
        
    Returns:
        tuple: (query_embedding, paper_embeddings, model)
    """
    
    # Load model
    model = SentenceTransformer(model_name)
    
    # Prepare text content from papers
    paper_texts = []
    for paper in papers:
        # Combine title and abstract for better semantic representation
        text = f"{paper.get('title', '')}. {paper.get('abstract', '')}"
        paper_texts.append(text)
    
    # Generate embeddings
    query_embedding = model.encode([query])[0]
    paper_embeddings = model.encode(paper_texts)
    
    return query_embedding, paper_embeddings

def get_paper_vectors(papers, query,):
    # Load model
    tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    # Prepare text content from papers
    paper_texts = [f"{p.get('title', '')}. {p.get('abstract', '')}" for p in papers]
    
    # Generate vectors
    query_vec = tfidf_vectorizer.transform([query])
    tfidf_matrix = tfidf_vectorizer.fit_transform(paper_texts)

    return query_vec, tfidf_matrix


def rank_papers_by_relevance(papers, query):
    """
    Rank papers by relevance to the query using BERT embeddings.
    
    Args:
        papers (list): List of paper dictionaries
        query (str): Original search query
        
    Returns:
        list: Ranked list of paper dictionaries with added relevance scores
    """
    if not papers:
        print("No papers to rank")
        return []
    
    # Get embeddings
    query_embedding, paper_embeddings = get_paper_embeddings(papers, query)

    # Get TF-IDF vectors
    query_vec, tfidf_matrix = get_paper_vectors(papers, query)
    
    # Calculate similarity scores
    semantic_similarities = cosine_similarity([query_embedding], paper_embeddings)[0]

    # Calculate TF-IDF similarity scores
    lexical_similarities = (tfidf_matrix @ query_vec.T).toarray().flatten()

    semantic_weight = 0.75
    lexical_weight = 1 - semantic_weight
    
    # Add scores to paper dictionaries
    ranked_papers = []
    for i, paper in enumerate(papers):
        paper_copy = paper.copy()
        paper_copy['similarity_score'] = float((semantic_weight * semantic_similarities[i]) + (lexical_weight * lexical_similarities[i]))
        paper_copy['citation_score'] = float(np.log1p(paper.get('citations', 0)/10)) # Citation score is based on the logarithmic scale, falls back to 0 if no citations
        # Recency score based on the year of publication (favours recent publications)
        if paper.get('year') == '':
            paper_copy['recency_score'] = 0
        else:
            paper_copy['recency_score'] = float(1 / (1 + 0.1 * (2025 - int(paper.get('year')))))
        paper_copy['relevance_score'] = 0.6 * paper_copy['similarity_score'] + 0.25 * paper_copy['citation_score'] + 0.15 * paper_copy['recency_score']
        ranked_papers.append(paper_copy)
    
    # Sort by relevance score (descending)
    ranked_papers.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return ranked_papers