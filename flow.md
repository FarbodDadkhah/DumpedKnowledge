Phase 1: Article URL Submission (POST /articles - main.py:124-163)

  1. Authentication Check (auth.py:56-76)
    - JWT token validated via get_current_user()
    - User credentials extracted from token payload
  2. Content Extraction (scraper.py:14-80)
    - extract_article_content() fetches URL with headers
    - BeautifulSoup parses HTML, removes scripts/styles/nav elements
    - Searches for main content using CSS selectors (article, main, .content, etc.)
    - Cleans text with regex, validates minimum 100 characters
    - Returns {title, content, url} dictionary
  3. Database Storage (database.py + main.py:138-149)
    - Creates Article object with scraped data
    - Links to authenticated user via user_id foreign key
    - Commits to SQLite database using SQLAlchemy ORM
    - Article schema: id, title, url, content, tags, embedding_path, created_at, user_id
  4. AI Embedding Generation (embeddings.py:14-23 + main.py:152-162)
    - embedding_service.create_embedding() uses SentenceTransformer model all-MiniLM-L6-v2
    - Converts full article content to 384-dimensional vector
    - save_embedding() pickles vector to embeddings/article_{id}.pkl
    - Updates article record with embedding file path

  Phase 2: User Q&A Query (POST /qa - main.py:243-319)

  1. Authentication & Article Retrieval (main.py:249-257)
    - Validates user JWT token
    - Queries database for user's articles with non-null embedding_path
  2. Semantic Search (embeddings.py:43-63)
    - find_similar_articles() creates embedding for user's question
    - Loads each stored article embedding from pickle files
    - Computes cosine similarity between question and article vectors
    - Returns top K articles sorted by similarity score
  3. Context Preparation (main.py:271-289)
    - Filters articles with similarity > 0.3 threshold
    - Extracts first 1000 characters from each relevant article
    - Builds context string: "From '{title}': {content_snippet}"
    - Collects source article metadata (title, URL, similarity score)
  4. AI Response Generation (main.py:291-319)
    - OpenAI GPT-3.5-turbo API call with system prompt
    - Context injection: provides article excerpts as knowledge base
    - User question combined with context in prompt
    - Returns structured response with answer, sources, and context count

  Key Technical Details:

  - Vector Storage: Local pickle files in embeddings/ directory
  - Similarity Matching: Cosine similarity with 0.3 minimum threshold
  - Context Window: 1000 characters per article, max 3 articles (configurable)
  - Database Relations: Users → Articles (1:many) with proper foreign keys
  - Security: JWT-based authentication for all operations
  - Error Handling: Graceful fallbacks at each processing stage




