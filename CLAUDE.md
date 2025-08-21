# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains documentation for a "Personal Research Companion" application - a tool that enables users to save articles, papers, and bookmarks, then query their personal knowledge base for summaries and insights.

## Architecture

The planned system uses a multi-component architecture:

- **Frontend (Next.js)**: Chrome extension or web app for saving content and a dashboard for browsing/querying saved items
- **Backend (FastAPI)**: Handles content fetching, text processing, chunking, embedding, and Q&A retrieval
- **Vector Store (ChromaDB)**: Stores semantic embeddings for contextual search and retrieval
- **Database (Supabase)**: Manages structured metadata (titles, authors, URLs, timestamps, tags) and user accounts

## Current State

This repository contains a fully functional MVP implementation with:
- FastAPI backend with JWT authentication
- Next.js frontend with NextAuth.js
- SQLite database with SQLAlchemy ORM
- Vector embeddings using sentence-transformers
- Web scraping and content processing
- OpenAI integration for Q&A functionality

## Development Commands

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Runs backend on http://localhost:8000

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Runs frontend on http://localhost:3000

### Environment Setup
- Copy `.env.example` to `.env` in backend/ and configure:
  - OPENAI_API_KEY
  - JWT_SECRET_KEY
- Copy `.env.local.example` to `.env.local` in frontend/ and configure:
  - NEXTAUTH_SECRET

## Key Implementation Details

- User authentication uses JWT tokens with bcrypt password hashing
- Article content is extracted via BeautifulSoup web scraping
- Text embeddings created using 'all-MiniLM-L6-v2' sentence transformer model
- Embeddings stored as pickle files in local `embeddings/` directory
- Database schema includes users and articles tables with foreign key relationships
- Frontend uses NextAuth credentials provider for authentication
- Search functionality uses cosine similarity for semantic matching
- Q&A uses OpenAI GPT-3.5-turbo with article context injection