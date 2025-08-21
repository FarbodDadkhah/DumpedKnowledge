'use client'

import { useState, useEffect } from 'react'
import { useSession, signOut } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { articlesApi, Article, SearchResult, QAResponse } from '@/lib/api'

export default function Dashboard() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [newUrl, setNewUrl] = useState('')
  const [newTags, setNewTags] = useState('')
  const [addingArticle, setAddingArticle] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [searching, setSearching] = useState(false)
  const [question, setQuestion] = useState('')
  const [qaResponse, setQaResponse] = useState<QAResponse | null>(null)
  const [askingQuestion, setAskingQuestion] = useState(false)
  const [activeTab, setActiveTab] = useState<'articles' | 'search' | 'qa'>('articles')

  useEffect(() => {
    if (status === 'loading') return
    if (!session) {
      router.push('/auth/signin')
      return
    }
    loadArticles()
  }, [session, status, router])

  const loadArticles = async () => {
    try {
      const data = await articlesApi.getAll()
      setArticles(data)
    } catch (error) {
      console.error('Error loading articles:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddArticle = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newUrl.trim()) return

    setAddingArticle(true)
    try {
      const article = await articlesApi.create(newUrl.trim(), newTags.trim())
      setArticles([article, ...articles])
      setNewUrl('')
      setNewTags('')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error adding article')
    } finally {
      setAddingArticle(false)
    }
  }

  const handleDeleteArticle = async (id: number) => {
    if (!confirm('Are you sure you want to delete this article?')) return

    try {
      await articlesApi.delete(id)
      setArticles(articles.filter(a => a.id !== id))
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error deleting article')
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const data = await articlesApi.search(searchQuery.trim())
      setSearchResults(data.results)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error searching articles')
    } finally {
      setSearching(false)
    }
  }

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setAskingQuestion(true)
    try {
      const response = await articlesApi.askQuestion(question.trim())
      setQaResponse(response)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error asking question')
    } finally {
      setAskingQuestion(false)
    }
  }

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-black">Personal Research Companion</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">{session?.user?.email}</span>
              <button
                onClick={() => signOut({ callbackUrl: '/' })}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="mb-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { key: 'articles', label: 'My Articles', count: articles.length },
              { key: 'search', label: 'Search' },
              { key: 'qa', label: 'Ask Questions' },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`${
                  activeTab === tab.key
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
              >
                {tab.label}
                {tab.count !== undefined && (
                  <span className={`${
                    activeTab === tab.key ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-900'
                  } ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {activeTab === 'articles' && (
          <div>
            <div className="mb-6 bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium mb-4 text-black">Add New Article</h3>
              <form onSubmit={handleAddArticle} className="space-y-4">
                <div>
                  <label htmlFor="url" className="block text-sm font-medium text-black">
                    Article URL
                  </label>
                  <input
                    type="url"
                    id="url"
                    required
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border text-black"
                    placeholder="https://example.com/article"
                    value={newUrl}
                    onChange={(e) => setNewUrl(e.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor="tags" className="block text-sm font-medium text-black">
                    Tags (optional)
                  </label>
                  <input
                    type="text"
                    id="tags"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border text-black"
                    placeholder="AI, research, technology"
                    value={newTags}
                    onChange={(e) => setNewTags(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  disabled={addingArticle}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
                >
                  {addingArticle ? 'Adding...' : 'Add Article'}
                </button>
              </form>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {articles.map((article) => (
                  <li key={article.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {article.title}
                        </h4>
                        <p className="text-sm text-gray-500 truncate">
                          {article.url}
                        </p>
                        {article.tags && (
                          <p className="text-xs text-indigo-600 mt-1">
                            Tags: {article.tags}
                          </p>
                        )}
                        <p className="text-xs text-gray-400">
                          Added: {new Date(article.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-600 hover:text-indigo-900 text-sm"
                        >
                          View
                        </a>
                        <button
                          onClick={() => handleDeleteArticle(article.id)}
                          className="text-red-600 hover:text-red-900 text-sm"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
                {articles.length === 0 && (
                  <li className="px-6 py-4 text-center text-gray-500">
                    No articles saved yet. Add your first article above!
                  </li>
                )}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'search' && (
          <div>
            <div className="mb-6 bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium mb-4 text-black">Search Your Articles</h3>
              <form onSubmit={handleSearch}>
                <div className="flex gap-4">
                  <input
                    type="text"
                    className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border text-black"
                    placeholder="Search for concepts, topics, or keywords..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <button
                    type="submit"
                    disabled={searching}
                    className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {searching ? 'Searching...' : 'Search'}
                  </button>
                </div>
              </form>
            </div>

            {searchResults.length > 0 && (
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                  {searchResults.map((result) => (
                    <li key={result.article.id} className="px-6 py-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          {result.article.title}
                        </h4>
                        <p className="text-sm text-gray-500 mt-1">
                          {result.article.url}
                        </p>
                        <p className="text-sm text-gray-700 mt-2">
                          {result.article.content}
                        </p>
                        <p className="text-xs text-gray-400 mt-2">
                          Similarity: {Math.round(result.similarity_score * 100)}%
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'qa' && (
          <div>
            <div className="mb-6 bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium mb-4 text-black">Ask a Question</h3>
              <form onSubmit={handleAskQuestion}>
                <div className="space-y-4">
                  <textarea
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border text-black"
                    rows={3}
                    placeholder="What would you like to know about your saved articles?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                  />
                  <button
                    type="submit"
                    disabled={askingQuestion}
                    className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {askingQuestion ? 'Asking...' : 'Ask Question'}
                  </button>
                </div>
              </form>
            </div>

            {qaResponse && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h4 className="text-lg font-medium mb-4">Answer</h4>
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{qaResponse.answer}</p>
                </div>
                
                {qaResponse.sources && qaResponse.sources.length > 0 && (
                  <div className="mt-6">
                    <h5 className="text-sm font-medium text-gray-900 mb-2">Sources:</h5>
                    <ul className="space-y-2">
                      {qaResponse.sources.map((source, index) => (
                        <li key={index} className="text-sm">
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-indigo-600 hover:text-indigo-800"
                          >
                            {source.title}
                          </a>
                          <span className="text-gray-500 ml-2">
                            (Relevance: {Math.round(source.similarity_score * 100)}%)
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}