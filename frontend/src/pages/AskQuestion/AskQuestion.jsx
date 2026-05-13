import { useState, useRef, useEffect } from 'react'
import Sidebar from '../../components/Sidebar/Sidebar'
import { questionAPI } from '../../services/api'
import './AskQuestion.css'

function AskQuestion() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: "Hello! I'm your AI Skincare Concierge. Ask me anything about skincare routines, ingredients, or product recommendations. How can I help you today?",
      timestamp: new Date(),
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const suggestedQuestions = [
    "What's a good routine for oily skin?",
    "How to reduce dark circles?",
    "Best ingredients for acne?",
    "Morning vs night skincare routine?",
  ]

  const normalizeList = (value) => (Array.isArray(value) ? value : (value ? [value] : []))

  const normalizeQuestionResponse = (data) => {
    const payload = data?.question || data || {}
    return {
      answer: payload.answer_text || payload.answer || data?.answer_text || data?.answer || data?.message || '',
      recommendations: payload.recommendations || data?.recommendations || {},
      keyPoints: payload.key_points || data?.key_points || [],
      disclaimer: data?.disclaimer || '',
      safetyRedirect: data?.safety_redirect === true
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (message = inputValue) => {
    if (!message.trim()) return

    // Add user message
    const userMessage = {
      type: 'user',
      content: message.trim(),
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      const { ok, data } = await questionAPI.askQuestion(message.trim(), 'general')
      
      if (ok) {
        const {
          answer,
          recommendations: recData,
          keyPoints,
          disclaimer,
          safetyRedirect
        } = normalizeQuestionResponse(data)

        const recommendations = []
        const productList = normalizeList(recData.products || recData.product_recommendations)
        productList.forEach((product) => {
          if (typeof product === 'string') {
            recommendations.push({ type: 'product', name: product, brand: '' })
            return
          }
          recommendations.push({
            type: 'product',
            name: product?.name || product?.title || product?.product || 'Product recommendation',
            brand: product?.brand || product?.company || ''
          })
        })

        const naturalList = normalizeList(recData.natural || recData.natural_remedies)
        naturalList.forEach((remedy) => {
          if (typeof remedy === 'string') {
            recommendations.push({ type: 'natural', name: remedy, benefit: '' })
            return
          }
          recommendations.push({
            type: 'natural',
            name: remedy?.name || remedy?.title || 'Natural remedy',
            benefit: remedy?.benefit || remedy?.description || ''
          })
        })

        const responseText = answer || 'I apologize, I could not process that question.'
        const disclaimerLine = disclaimer ? `\n\n${disclaimer}` : ''
        const safetyLine = safetyRedirect ? '\n\nPlease consult a qualified professional for medical guidance.' : ''
        const tips = normalizeList(recData.tips)
        const relatedQuestions = normalizeList(recData.related_questions)

        setMessages(prev => [...prev, {
          type: 'bot',
          content: `${responseText}${safetyLine}${disclaimerLine}`.trim(),
          recommendations,
          keyPoints: normalizeList(keyPoints),
          tips,
          relatedQuestions,
          timestamp: new Date(),
        }])
      } else {
        setMessages(prev => [...prev, {
          type: 'bot',
          content: data?.message || 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        }])
      }
    } catch (error) {
      console.error('Question error:', error)
      setMessages(prev => [...prev, {
        type: 'bot',
        content: 'Unable to connect to the server. Please check your connection.',
        timestamp: new Date(),
      }])
    }
    
    setIsTyping(false)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="dashboard-main chat-main">
        {/* Top Bar */}
        <header className="dashboard-header chat-header">
          <button 
            className="mobile-menu-toggle"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="material-symbols-outlined">menu</span>
          </button>

          <div className="page-title">
            <span className="material-symbols-outlined">forum</span>
            <h1>AI Chat Concierge</h1>
          </div>

          <div className="header-actions">
            <button className="header-btn">
              <span className="material-symbols-outlined">history</span>
            </button>
            <button className="header-btn">
              <span className="material-symbols-outlined">more_vert</span>
            </button>
          </div>
        </header>

        {/* Chat Content */}
        <div className="chat-content">
          {/* Messages */}
          <div className="messages-container">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                {message.type === 'bot' && (
                  <div className="message-avatar">
                    <span className="material-symbols-outlined">smart_toy</span>
                  </div>
                )}
                <div className="message-content">
                  <div className="message-text">
                    {message.content.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                  {message.recommendations && message.recommendations.length > 0 && (
                    <div className="message-recommendations">
                      <span className="rec-label">Recommended:</span>
                      <div className="rec-list">
                        {message.recommendations.map((rec, i) => (
                          <div key={i} className={`rec-item ${rec.type}`}>
                            <span className="material-symbols-outlined">
                              {rec.type === 'product' ? 'science' : 'eco'}
                            </span>
                            <div className="rec-info">
                              <span className="rec-name">{rec.name}</span>
                              <span className="rec-detail">{rec.brand || rec.benefit}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {message.keyPoints && message.keyPoints.length > 0 && (
                    <div className="message-notes">
                      <span className="notes-label">Key Points</span>
                      <ul>
                        {message.keyPoints.map((point, i) => (
                          <li key={i}>{point}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {message.tips && message.tips.length > 0 && (
                    <div className="message-notes">
                      <span className="notes-label">Tips</span>
                      <ul>
                        {message.tips.map((tip, i) => (
                          <li key={i}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {message.relatedQuestions && message.relatedQuestions.length > 0 && (
                    <div className="message-notes">
                      <span className="notes-label">Related Questions</span>
                      <ul>
                        {message.relatedQuestions.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <span className="message-time">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="message bot">
                <div className="message-avatar">
                  <span className="material-symbols-outlined">smart_toy</span>
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Questions */}
          {messages.length === 1 && (
            <div className="suggested-questions">
              <span className="suggested-label">Try asking:</span>
              <div className="suggested-list">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    className="suggested-btn"
                    onClick={() => handleSend(question)}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="chat-input-area">
            <div className="chat-input-wrapper">
              <textarea
                className="chat-input"
                placeholder="Ask me about skincare..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                rows={1}
              />
              <button 
                className="send-btn"
                onClick={() => handleSend()}
                disabled={!inputValue.trim() || isTyping}
              >
                <span className="material-symbols-outlined">send</span>
              </button>
            </div>
            <p className="chat-disclaimer">
              AI responses are for informational purposes only. Not medical advice.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default AskQuestion
