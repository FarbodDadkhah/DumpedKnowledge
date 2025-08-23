from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv
import openai

from database import create_tables, get_db, User, Article
from auth import (
    authenticate_user, create_access_token, get_current_user, 
    create_user, get_user_by_email, ACCESS_TOKEN_EXPIRE_MINUTES
)
from scraper import extract_article_content
from embeddings import embedding_service

load_dotenv()


client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    create_tables()
    yield
    pass

app = FastAPI(title="Personal Research Companion API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic 
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ArticleCreate(BaseModel):
    url: str
    tags: Optional[str] = ""

class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    content: str
    tags: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 5

class QAQuery(BaseModel):
    question: str
    limit: Optional[int] = 3


# Auth endpoints
@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    

    created_user = create_user(db, email=user.email, password=user.password)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": created_user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/articles", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
  
    scraped_data = extract_article_content(article_data.url)
    if not scraped_data:
        raise HTTPException(
            status_code=400,
            detail="Could not extract content from URL"
        )
    
    
    db_article = Article(
        title=scraped_data['title'],
        url=scraped_data['url'],
        content=scraped_data['content'],
        tags=article_data.tags,
        user_id=current_user.id
    )
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    # Add article to ChromaDB
    try:
        embedding_service.add_article(
            article_id=db_article.id,
            content=scraped_data['content'],
            metadata={
                "title": scraped_data['title'],
                "url": scraped_data['url'],
                "user_id": current_user.id,
                "tags": article_data.tags
            }
        )
    except Exception as e:
        print(f"Error adding article to ChromaDB: {e}")
    
    return db_article

@app.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    articles = db.query(Article).filter(Article.user_id == current_user.id).all()
    return articles

@app.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(
        Article.id == article_id,
        Article.user_id == current_user.id
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Delete article from ChromaDB
    try:
        embedding_service.delete_article(article.id)
    except Exception as e:
        print(f"Error deleting article from ChromaDB: {e}")
    
    db.delete(article)
    db.commit()
    
    return {"message": "Article deleted successfully"}

@app.post("/search")
async def search_articles(
    search_query: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
   
    similar_results = embedding_service.search_similar_articles(
        query=search_query.query,
        user_id=current_user.id,
        limit=search_query.limit
    )
    
    if not similar_results:
        return {"results": [], "message": "No articles found"}
    
    # Get article details from database
    results = []
    for article_id, similarity_score, content_snippet in similar_results:
        article = db.query(Article).filter(
            Article.id == article_id,
            Article.user_id == current_user.id
        ).first()
        
        if article:
            results.append({
                "article": {
                    "id": article.id,
                    "title": article.title,
                    "url": article.url,
                    "content": content_snippet[:500] + "..." if len(content_snippet) > 500 else content_snippet,
                    "tags": article.tags,
                    "created_at": article.created_at
                },
                "similarity_score": similarity_score
            })
    
    return {"results": results}

@app.post("/qa")
async def answer_question(
    qa_query: QAQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
   
    similar_results = embedding_service.search_similar_articles(
        query=qa_query.question,
        user_id=current_user.id,
        limit=qa_query.limit
    )
    
    if not similar_results:
        return {"answer": "No articles found in your collection to answer this question."}
    
   
    context_parts = []
    source_articles = []
    

    max_similarity = max([score for _, score, _ in similar_results], default=0)
    adaptive_threshold = max(0.12, min(0.25, max_similarity * 0.6))  # Dynamic threshold
    
    for article_id, similarity_score, content_snippet in similar_results:
        if similarity_score > adaptive_threshold:
            article = db.query(Article).filter(
                Article.id == article_id,
                Article.user_id == current_user.id
            ).first()
            
            if article:
                #increasing relevance
                full_context = embedding_service.get_article_context(
                    article_id, 
                    query=qa_query.question, 
                    max_chunks=3
                )
                context_parts.append(f"From '{article.title}': {full_context}")
                source_articles.append({
                    "title": article.title,
                    "url": article.url,
                    "similarity_score": similarity_score
                })
    
    if not context_parts:
        return {"answer": "No relevant articles found to answer your question."}
    
    context = "\n\n".join(context_parts)
    
   
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledgeable research assistant that answers questions based on the user's saved articles. Always cite which articles you're drawing from. If the context doesn't fully answer the question, mention what information is missing and provide the best answer possible from available content."
                },
                {
                    "role": "user", 
                    "content": f"Based on these excerpts from my saved articles:\n\n{context}\n\nQuestion: {qa_query.question}\n\nPlease provide a detailed, well-structured answer. Reference specific articles when possible and indicate if you need more information to give a complete answer. "
                }
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "sources": source_articles,
            "context_used": len(context_parts)
        }
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"answer": "Sorry, I couldn't generate an answer at this time. Please try again later."}

@app.get("/")
async def root():
    return {"message": "Personal Research Companion API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
