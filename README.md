# Personal Research Companion

A simple MVP application that allows users to save articles, papers, and bookmarks, then ask questions about their personal knowledge base using AI-powered search and Q&A.

## Features

- **User Authentication**: Sign up/login with email and password
- **Article Management**: Save web articles by pasting URLs
- **Smart Search**: Semantic search through saved content
- **AI Q&A**: Ask questions and get AI-powered answers based on your saved articles
- **Content Processing**: Automatic web scraping and text extraction
- **Vector Embeddings**: Uses sentence-transformers for semantic search

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **SQLite**: Database for user accounts and article metadata
- **SQLAlchemy**: ORM for database operations
- **JWT**: Authentication using JSON Web Tokens with python-jose
- **OpenAI API**: For question-answering functionality
- **ChromaDB**: Vector database for embeddings storage and similarity search
- **Scikit-learn**: For machine learning utilities
- **BeautifulSoup**: For web scraping and content extraction

### Frontend
- **Next.js 15**: React framework with App Router and Turbopack
- **NextAuth.js**: Authentication
- **Tailwind CSS 4**: Styling 
- **TypeScript**: Type safety
- **Axios**: HTTP client for API requests


### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   
   Edit `.env` and add your configuration:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `JWT_SECRET_KEY`: A secure random string for JWT signing
   
4. Start the backend server:
   ```
   python main.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   
   Edit `.env.local` and add your configuration:
   - `NEXTAUTH_SECRET`: A secure random string for NextAuth

4. Start the frontend development server:
   ```
   npm run dev
   ```

## Usage

1. **Sign Up**: Create a new account 
2. **Sign In**: Log in to your account 
3. **Add Articles**: In the dashboard, paste article URLs to save them
4. **Search**: Use the search tab to find relevant content semantically
5. **Ask Questions**: Use the Q&A tab to ask questions about your saved articles

## API Endpoints

### Authentication
- `POST /auth/register`: Create a new user account
- `POST /auth/login`: Login with email/password

### Articles
- `GET /articles`: Get user's saved articles
- `POST /articles`: Add a new article by URL
- `DELETE /articles/{id}`: Delete an article

### Search & Q&A
- `POST /search`: Search through articles semantically
- `POST /qa`: Ask questions about saved articles

## Development Notes

- The app automatically creates embeddings for saved articles and stores them in ChromaDB
- ChromaDB provides persistent vector storage with similarity search capabilities
- The SQLite database is created automatically on first run
- CORS is configured to allow requests from the Next.js frontend
- Frontend uses React 19 with Next.js 15 and Turbopack for enhanced performance

## Security Features

- Password hashing using bcrypt
- JWT-based authentication
- Protected API routes requiring authentication
- Input validation and sanitization
- CORS configuration

## Limitations (MVP)
- new updated llm re ranking could be used
-  local SQLite database (not suitable for production scale) but easily can plug somethig like supabase or postgres 
- ChromaDB runs locally (not suitable for production deployment)/ alternatives like pinecone can be easily migrated
- rate limiting has to be designed if app ever goes to production
- Simple web scraping (may not work on all sites), extended functionality on a case by case basis can be implemented