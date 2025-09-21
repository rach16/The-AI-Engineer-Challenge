import React, { useState, useRef } from 'react';
import { Database, Upload, MessageSquare, CheckCircle, AlertTriangle, FileText, Send, Bot, User, Loader } from 'lucide-react';
import './DataPromoAgent.css';

const DataPromoAgent = () => {
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // API base URL - adjust for your environment
  const API_BASE = process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000' 
    : window.location.origin;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setUploadStatus({ success: false, message: 'Please upload a PDF file only.' });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/api/upload-document`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (result.success) {
        setUploadedDocument({
          name: file.name,
          id: result.document_id,
          chunks: result.chunks_count,
          uploadTime: new Date().toLocaleTimeString()
        });
        setUploadStatus({ success: true, message: result.message });
        setChatMessages([{
          type: 'system',
          content: `🎉 Document "${file.name}" uploaded successfully! Split into ${result.chunks_count} searchable chunks. Ask me anything about it!`
        }]);
      } else {
        setUploadStatus({ success: false, message: result.message || 'Upload failed' });
      }
    } catch (error) {
      setUploadStatus({ success: false, message: `Upload failed: ${error.message}` });
    } finally {
      setIsUploading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !uploadedDocument) return;

    const userMessage = { type: 'user', content: currentMessage, timestamp: new Date() };
    setChatMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat-with-document`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: currentMessage,
          document_id: uploadedDocument.id,
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        const botMessage = {
          type: 'bot',
          content: result.answer,
          sources: result.sources || [],
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          type: 'error',
          content: result.message || 'Sorry, I encountered an error processing your question.',
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearDocument = () => {
    setUploadedDocument(null);
    setChatMessages([]);
    setUploadStatus(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };


  const getSampleQuestions = () => {
    if (!uploadedDocument) return [];
    
    return [
      "What are the main steps in this process?",
      "What warnings or important notes should I be aware of?",
      "How long does each step typically take?",
      "What are the prerequisites for getting started?",
      "What should I do if something goes wrong?"
    ];
  };

  return (
    <div className="data-promo-agent">
      <div className="tab-header">
        <div className="tab-header-icon">
          <Database size={24} />
        </div>
        <div className="tab-header-content">
          <h2>Data Promo Agent</h2>
          <p>Upload your process documents and get intelligent answers! Perfect for complex guides like data promotion processes, deployment procedures, and operational documentation.</p>
          <div className="status-badge live">
            <CheckCircle size={16} />
            Live & Ready - RAG Powered!
          </div>
        </div>
      </div>

      <div className="tab-content">
        <div className="data-promo-content">
          
          {/* Document Upload Section */}
          <div className="section">
            <h3 className="section-title">
              <Upload size={20} />
              Upload Process Document
            </h3>
            <p className="section-description">
              Upload a PDF document (like your data promotion guide) to start asking questions about it
            </p>
            
            {!uploadedDocument ? (
              <div className="upload-area">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf"
                  className="file-input"
                  id="pdf-upload"
                />
                <label htmlFor="pdf-upload" className="upload-label">
                  <div className="upload-content">
                    <FileText size={48} className="upload-icon" />
                    <div className="upload-text">
                      <h4>Choose PDF Document</h4>
                      <p>Click here to upload your process documentation</p>
                      <span className="upload-hint">Perfect for: Process guides, SOPs, deployment docs</span>
                    </div>
                  </div>
                </label>
                
                {isUploading && (
                  <div className="upload-progress">
                    <Loader className="spinner" size={20} />
                    <span>Processing document and creating searchable index...</span>
                  </div>
                )}
                
                {uploadStatus && (
                  <div className={`upload-status ${uploadStatus.success ? 'success' : 'error'}`}>
                    {uploadStatus.success ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                    <span>{uploadStatus.message}</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="uploaded-document">
                <div className="document-info">
                  <FileText size={24} />
                  <div className="document-details">
                    <h4>{uploadedDocument.name}</h4>
                    <p>{uploadedDocument.chunks} chunks • Uploaded at {uploadedDocument.uploadTime}</p>
                  </div>
                  <button onClick={clearDocument} className="clear-btn">
                    Clear Document
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Chat Interface */}
          {uploadedDocument && (
            <div className="section chat-section">
              <h3 className="section-title">
                <MessageSquare size={20} />
                Chat with Your Document
              </h3>
              <p className="section-description">
                Ask questions about your document and get intelligent answers with source citations
              </p>
              
              {/* Sample Questions */}
              {chatMessages.length <= 1 && (
                <div className="sample-questions">
                  <h4>Try asking:</h4>
                  <div className="question-chips">
                    {getSampleQuestions().map((question, index) => (
                      <button
                        key={index}
                        className="question-chip"
                        onClick={() => setCurrentMessage(question)}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Chat Messages */}
              <div className="chat-container">
                <div className="chat-messages">
                  {chatMessages.map((message, index) => (
                    <div key={index} className={`message ${message.type}`}>
                      <div className="message-header">
                        {message.type === 'user' && <User size={16} />}
                        {message.type === 'bot' && <Bot size={16} />}
                        {message.type === 'system' && <CheckCircle size={16} />}
                        {message.type === 'error' && <AlertTriangle size={16} />}
                        <span className="message-type">
                          {message.type === 'user' ? 'You' : 
                           message.type === 'bot' ? 'AI Assistant' : 
                           message.type === 'system' ? 'System' : 'Error'}
                        </span>
                        {message.timestamp && (
                          <span className="message-time">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        )}
                      </div>
                      <div className="message-content">
                        {message.content}
                        {message.sources && message.sources.length > 0 && (
                          <div className="message-sources">
                            <h5>📚 Sources from document:</h5>
                            {message.sources.map((source, idx) => (
                              <div key={idx} className="source-chunk">
                                {source.substring(0, 200)}...
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="message bot loading">
                      <div className="message-header">
                        <Bot size={16} />
                        <span className="message-type">AI Assistant</span>
                      </div>
                      <div className="message-content">
                        <Loader className="spinner" size={16} />
                        <span>Searching document and generating answer...</span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
                
                {/* Chat Input */}
                <div className="chat-input-container">
                  <div className="chat-input-wrapper">
                    <textarea
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask anything about your document... (Press Enter to send)"
                      className="chat-input"
                      rows="1"
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!currentMessage.trim() || isLoading}
                      className="send-btn"
                    >
                      <Send size={18} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Getting Started Guide */}
          {!uploadedDocument && (
            <div className="section getting-started">
              <h3 className="section-title">
                <CheckCircle size={20} />
                Perfect for Data Promotion Guides!
              </h3>
              <div className="getting-started-content">
                <div className="feature-highlight">
                  <div className="highlight-icon">
                    <FileText size={32} />
                  </div>
                  <div className="highlight-content">
                    <h4>Transform Static Docs into Smart Assistants</h4>
                    <p>
                      Upload complex process documents like your <strong>CH Data Promotion Process Guide</strong> 
                      and get instant answers to questions like:
                    </p>
                    <ul className="example-questions">
                      <li>"What's the first step in data promotion?"</li>
                      <li>"What warnings should I know about DNS changes?"</li>
                      <li>"How long does hydration take?"</li>
                      <li>"Show me the ArgoCD sync commands"</li>
                      <li>"What should I do if something goes wrong?"</li>
                    </ul>
                  </div>
                </div>
                
                <div className="feature-list">
                  <div className="feature-item">
                    <CheckCircle size={20} />
                    <span>Intelligent document chunking preserves context</span>
                  </div>
                  <div className="feature-item">
                    <CheckCircle size={20} />
                    <span>Source citations show exactly where answers come from</span>
                  </div>
                  <div className="feature-item">
                    <CheckCircle size={20} />
                    <span>Perfect for complex multi-step processes</span>
                  </div>
                  <div className="feature-item">
                    <CheckCircle size={20} />
                    <span>Powered by OpenAI embeddings + Gemini AI</span>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default DataPromoAgent;
