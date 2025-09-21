import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import FileUpload from './FileUpload';
import TestCaseTable from './TestCaseTable';
import UsageInfo from './UsageInfo';
import PromptingTool from './PromptingTool';
import { FileText, MessageSquare, Zap, Bot, User, Send, Loader, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import './PRDGenerator.css';

const PRDGenerator = () => {
  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasResults, setHasResults] = useState(false);
  const [usageInfo, setUsageInfo] = useState(null);
  const [serviceAvailable, setServiceAvailable] = useState(false);
  
  // RAG-related state
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null); // Store file reference
  const [showOptions, setShowOptions] = useState(false);
  const [showRAGChat, setShowRAGChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isRAGLoading, setIsRAGLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // API base URL
  const API_BASE = process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000' 
    : window.location.origin;

  // Check usage info on component mount
  useEffect(() => {
    fetchUsageInfo();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const fetchUsageInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/usage-info`);
      setUsageInfo(response.data);
      setServiceAvailable(response.data.service_available);
    } catch (error) {
      console.error('Error fetching usage info:', error);
      // Don't show error to user - backend might not be running yet
    }
  };

  // RAG helper functions
  // const scrollToBottom = () => {
  //   messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  // };

  const uploadToRAG = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/api/upload-document`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setUploadedDocument({
          name: file.name,
          id: response.data.document_id,
          chunks: response.data.chunks_count,
          uploadTime: new Date().toLocaleTimeString()
        });
        setChatMessages([{
          type: 'system',
          content: `🎉 PRD "${file.name}" uploaded successfully! Split into ${response.data.chunks_count} searchable chunks. You can now chat with your PRD to understand requirements better, or generate test cases directly.`
        }]);
        setShowOptions(true);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error uploading to RAG:', error);
      toast.error('Failed to upload document for RAG analysis');
      return false;
    }
  };

  const sendRAGMessage = async () => {
    if (!currentMessage.trim() || !uploadedDocument) return;

    const userMessage = { type: 'user', content: currentMessage, timestamp: new Date() };
    setChatMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsRAGLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/chat-with-document`, {
        question: currentMessage,
        document_id: uploadedDocument.id,
      });

      if (response.data.success) {
        const botMessage = {
          type: 'bot',
          content: response.data.answer,
          sources: response.data.sources || [],
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          type: 'error',
          content: response.data.message || 'Sorry, I encountered an error processing your question.',
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
      setIsRAGLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendRAGMessage();
    }
  };

  const getSampleQuestions = () => [
    "What are the main features described in this document?",
    "What user requirements are mentioned in this PRD?",
    "Are there any edge cases or error scenarios described?",
    "What integrations or dependencies are mentioned?",
    "What performance requirements does this document specify?",
    "Who is the target audience mentioned in this PRD?",
    "What business objectives are outlined in this document?"
  ];

  const handleFileUpload = async (file) => {
    setLoading(true);
    
    try {
      // Store the file reference for later use
      setUploadedFile(file);
      
      // First upload to RAG system for analysis capabilities
      const ragSuccess = await uploadToRAG(file);
      
      if (ragSuccess) {
        toast.success('✅ PRD uploaded successfully! Choose how to proceed.');
        await fetchUsageInfo();
      } else {
        toast.error('Failed to upload PRD. Please try again.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      
      // Handle different error scenarios with helpful messages
      if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        toast.error('❌ Unable to connect to server. Please try again.');
      } else if (error.response?.status === 503) {
        toast.error('⚠️ Service temporarily unavailable. Please try again later.');
      } else if (error.response?.status === 429) {
        toast.error('📊 Daily limit reached! Please try again tomorrow.');
      } else if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error('Failed to process the file. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const generateTestCasesFromPRD = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/api/upload-prd`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setTestCases(response.data.test_cases);
        setHasResults(true);
        setUsageInfo(response.data.usage_info);
        
        // Show success message with usage info
        const message = response.data.usage_info?.message || response.data.message;
        toast.success(message);
        
        // Refresh usage info to update the display
        await fetchUsageInfo();
      } else {
        toast.error('Failed to generate test cases');
      }
    } catch (error) {
      console.error('Error generating test cases:', error);
      
      if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        toast.error('❌ Unable to connect to server. Please try again.');
      } else if (error.response?.status === 503) {
        toast.error('⚠️ Service temporarily unavailable. Please try again later.');
      } else if (error.response?.status === 429) {
        toast.error('📊 Daily limit reached! Please try again tomorrow.');
      } else if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error('Failed to process the file. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/download-csv`, testCases, {
        responseType: 'blob',
      });

      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'test_cases.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('CSV file downloaded successfully!');
    } catch (error) {
      console.error('Error downloading CSV:', error);
      toast.error('Failed to download CSV file');
    }
  };

  const handleReset = () => {
    setTestCases([]);
    setHasResults(false);
    setUploadedDocument(null);
    setUploadedFile(null); // Clear file reference
    setShowOptions(false);
    setShowRAGChat(false);
    setChatMessages([]);
    setCurrentMessage('');
    fetchUsageInfo(); // Refresh usage info
    toast.success('Ready for new upload');
  };

  return (
    <div className="prd-generator">
      <div className="tab-header">
        <div className="tab-header-icon">
          <FileText size={24} />
        </div>
        <div className="tab-header-content">
          <h2>PRD to Test Case Generator</h2>
          <p>Transform your Product Requirements Documents into comprehensive test cases using AI-powered analysis. Upload PDFs or images and get structured test cases instantly.</p>
          <div className="supported-formats">
            <span className="format-tag">PDF</span>
            <span className="format-tag">JPEG</span>
            <span className="format-tag">JPG</span>
            <span className="format-tag">PNG</span>
          </div>
        </div>
      </div>

      <div className="tab-content">
        {!uploadedDocument && !hasResults ? (
          <div className="upload-section">
            <UsageInfo 
              usageInfo={usageInfo} 
              serviceAvailable={serviceAvailable}
            />
            <FileUpload 
              onFileUpload={handleFileUpload} 
              loading={loading}
              usageInfo={usageInfo}
              serviceAvailable={serviceAvailable}
            />
          </div>
        ) : showOptions && !showRAGChat && !hasResults ? (
          <div className="options-section">
            <div className="document-uploaded">
              <div className="document-info">
                <FileText size={24} />
                <div className="document-details">
                  <h3>{uploadedDocument.name}</h3>
                  <p>{uploadedDocument.chunks} chunks • Uploaded at {uploadedDocument.uploadTime}</p>
                </div>
              </div>
            </div>
            
            <div className="workflow-options">
              <h3>How would you like to proceed?</h3>
              <p>You can chat with your PRD first to understand requirements better, or generate test cases directly.</p>
              
              <div className="option-cards">
                <button 
                  className="option-card chat-option"
                  onClick={() => {
                    setShowRAGChat(true);
                    toast('💬 Now chatting with your document - ask questions about requirements!', { duration: 3000 });
                  }}
                >
                  <div className="option-icon">
                    <MessageSquare size={32} />
                  </div>
                  <div className="option-content">
                    <h4>💬 Chat with PRD (Recommended)</h4>
                    <p>Ask questions about requirements, features, and edge cases - does NOT generate test cases</p>
                    <div className="option-benefits">
                      <span>❓ Ask questions only</span>
                      <span>💡 Understand requirements</span>
                      <span>🔍 Analyze document content</span>
                    </div>
                  </div>
                  <ArrowRight size={20} className="option-arrow" />
                </button>

                <button 
                  className="option-card generate-option"
                  onClick={() => {
                    if (uploadedFile) {
                      toast('⚡ Generating test cases - this will create a table below!', { duration: 3000 });
                      generateTestCasesFromPRD(uploadedFile);
                    }
                  }}
                  disabled={loading}
                >
                  <div className="option-icon">
                    <Zap size={32} />
                  </div>
                  <div className="option-content">
                    <h4>⚡ Generate Test Cases</h4>
                    <p>Creates a table of test cases below - separate from chat feature</p>
                    <div className="option-benefits">
                      <span>📋 Creates test table</span>
                      <span>🎯 Comprehensive coverage</span>
                      <span>💾 Export to CSV</span>
                    </div>
                  </div>
                  <ArrowRight size={20} className="option-arrow" />
                </button>
              </div>
              
              <button 
                onClick={handleReset}
                className="reset-button"
              >
                Upload Different PRD
              </button>
            </div>
          </div>
        ) : showRAGChat && !hasResults ? (
          <div className="rag-chat-section">
            <div className="document-header">
              <div className="document-info">
                <FileText size={20} />
                <div className="document-details">
                  <h3>{uploadedDocument.name}</h3>
                  <p>{uploadedDocument.chunks} chunks indexed</p>
                </div>
                <button 
                  onClick={() => {
                    if (uploadedFile) {
                      toast('⚡ Creating test cases table below - separate from this chat!', { duration: 4000 });
                      generateTestCasesFromPRD(uploadedFile);
                    }
                  }}
                  className="generate-tests-btn"
                  disabled={loading}
                  title="This will create a test cases table below, separate from the chat"
                >
                  {loading ? <Loader className="spinner" size={16} /> : <Zap size={16} />}
                  Generate Test Cases Table
                </button>
              </div>
            </div>

            <div className="chat-interface">
              <h3>
                <MessageSquare size={20} />
                Chat with Your PRD
              </h3>
              <p>Ask questions to understand requirements better before generating test cases</p>
              
              {/* Sample Questions */}
              {chatMessages.length <= 1 && (
                <div className="sample-questions">
                  <h4>Suggested questions:</h4>
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
                           message.type === 'bot' ? 'PRD Assistant' : 
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
                            <h5>📚 Sources from PRD:</h5>
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
                  {isRAGLoading && (
                    <div className="message bot loading">
                      <div className="message-header">
                        <Bot size={16} />
                        <span className="message-type">PRD Assistant</span>
                      </div>
                      <div className="message-content">
                        <Loader className="spinner" size={16} />
                        <span>Analyzing PRD and generating response...</span>
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
                      placeholder="Ask about requirements, features, edge cases... (Press Enter to send)"
                      className="chat-input"
                      rows="1"
                    />
                    <button
                      onClick={sendRAGMessage}
                      disabled={!currentMessage.trim() || isRAGLoading}
                      className="send-btn"
                    >
                      <Send size={18} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="chat-actions">
              <button onClick={() => setShowRAGChat(false)} className="back-button">
                ← Back to Options
              </button>
              <button onClick={handleReset} className="reset-button">
                Start Over
              </button>
            </div>
          </div>
        ) : (
          <div className="results-section">
            <div className="section-header">
              <h2>🧪 Generated Test Cases</h2>
              <p>📋 These test cases were generated separately from the chat feature above.</p>
            </div>
            <TestCaseTable 
              testCases={testCases} 
              onDownloadCSV={handleDownloadCSV}
              onReset={handleReset}
              usageInfo={usageInfo}
            />
          </div>
        )}
      </div>
      <PromptingTool testCases={testCases} apiKey={usageInfo?.api_key} />
    </div>
  );
};

export default PRDGenerator;
