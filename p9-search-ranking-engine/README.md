Project: Enterprise Search / NLP Ranking Engine

Repo: 
    search-ranking-engine

Build:
    retrieval
    ranking
    embeddings
    vector DB
    reranking

-----------------------=========================----------------------

README Format

Problem Statement:
    What business problem are you Solving? 
        - Ecommerce search relevance.
        - Design Search feature for a e-commerce platform
        - Ex. Search Query 
            "red nike running shoes"

            Need relevant ranking

Architecture
    Diagrams & Documents

    ---------------------
    User Query
        → Query preprocessing
        → Candidate retrieval
        → Ranking model
        → Results API
    ---------------------

    --------------------------
    Development Phases 

        Phase 1
            Build inverted index

        Phase 2
            BM25 retrieval

        Phase 3
            Embedding retrieval

        Phase 4
            Learning to rank

        Phase 5
            API serving
    ---------------------------

Tech stack
    What tech stack to use?
        - AWS / Opensource
      
        Python
        Elasticsearch/OpenSearch
        Sentence Transformers
        FastAPI
        FAISS
        LightGBM/XGBoost

Dataset
    - Dataset 
        Amazon products dataset or Kaggle ecommerce datasets

    - Source 

How to run
    - Step by step instruction of how to run this app? 

Results
    - What are the results ? What is the impact ?

Future improvements
    - Critical improvements ?
    - Nice to have features ?
    - Known issues/bugs ?

    New features to add:
        personalization
        typo correction
        query rewriting
        hybrid retrieval

Learnings
    - Mistakes made and learnings 

