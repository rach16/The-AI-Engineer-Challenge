import React from 'react';
import { 
  FileText, 
  Database, 
  GitBranch, 
  Zap, 
  CheckCircle, 
  ArrowRight, 
  Upload,
  MessageSquare,
  Download,
  Bot,
  Sparkles,
  Target,
  Clock,
  Shield,
  Users
} from 'lucide-react';
import './LandingPage.css';

const LandingPage = ({ onNavigateToTab }) => {
  const features = [
    {
      id: 'prd-generator',
      title: 'PRD to Test Cases',
      icon: <FileText size={32} />,
      description: 'Transform Product Requirements Documents into comprehensive test cases using AI-powered analysis.',
      capabilities: [
        'Upload PDFs, images (JPEG, PNG)',
        'AI-powered content extraction',
        'Comprehensive test case generation',
        'Export to CSV format',
        'Multiple test categories & priorities'
      ],
      color: 'blue'
    },
    {
      id: 'data-promo-agent',
      title: 'Data Promo Agent',
      icon: <Database size={32} />,
      description: 'Upload process documents and get intelligent answers. Perfect for complex operational guides.',
      capabilities: [
        'Smart document indexing',
        'Interactive Q&A system',
        'Source citations',
        'Context-aware responses',
        'Perfect for SOPs & guides'
      ],
      color: 'green'
    },
    {
      id: 'release-agent',
      title: 'Release Agent',
      icon: <GitBranch size={32} />,
      description: 'Automate release planning, deployment workflows, and streamline your release process.',
      capabilities: [
        'Release planning automation',
        'Deployment workflow management',
        'Integration with CI/CD',
        'Risk assessment',
        'Timeline optimization'
      ],
      color: 'purple'
    }
  ];

  const workflows = [
    {
      step: 1,
      title: 'Upload Documents',
      description: 'Drag & drop your PRDs, process docs, or images',
      icon: <Upload size={24} />
    },
    {
      step: 2,
      title: 'AI Analysis',
      description: 'Our AI analyzes and structures your content',
      icon: <Bot size={24} />
    },
    {
      step: 3,
      title: 'Interactive Results',
      description: 'Get test cases, chat with docs, or plan releases',
      icon: <Sparkles size={24} />
    },
    {
      step: 4,
      title: 'Export & Integrate',
      description: 'Download results or integrate with your workflow',
      icon: <Download size={24} />
    }
  ];

  const benefits = [
    {
      icon: <Clock size={24} />,
      title: 'Save Time',
      description: 'Reduce manual testing preparation from hours to minutes'
    },
    {
      icon: <Target size={24} />,
      title: 'Improve Coverage',
      description: 'AI ensures comprehensive test scenario coverage'
    },
    {
      icon: <Shield size={24} />,
      title: 'Reduce Risk',
      description: 'Standardized processes reduce human error'
    },
    {
      icon: <Users size={24} />,
      title: 'Team Collaboration',
      description: 'Centralized knowledge base for entire team'
    }
  ];

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <Zap size={16} />
            <span>AI-Powered QA Automation</span>
          </div>
          
          <h1 className="hero-title">
            Welcome to <span className="brand-highlight">QA Hub</span>
          </h1>
          
          <p className="hero-description">
            Your one-stop solution for creating test cases, analyzing PRDs, automating workflows, 
            and transforming static documentation into intelligent, interactive assistants.
          </p>

          <div className="hero-stats">
            <div className="stat">
              <div className="stat-number">3</div>
              <div className="stat-label">Powerful Tools</div>
            </div>
            <div className="stat">
              <div className="stat-number">5+</div>
              <div className="stat-label">File Formats</div>
            </div>
            <div className="stat">
              <div className="stat-number">∞</div>
              <div className="stat-label">Possibilities</div>
            </div>
          </div>

          <div className="hero-cta">
            <button 
              className="cta-primary"
              onClick={() => onNavigateToTab('prd-generator')}
            >
              <FileText size={20} />
              Start with PRD Analysis
              <ArrowRight size={16} />
            </button>
            <button 
              className="cta-secondary"
              onClick={() => onNavigateToTab('data-promo-agent')}
            >
              <MessageSquare size={20} />
              Try Document Chat
            </button>
          </div>
        </div>

        <div className="hero-visual">
          <div className="floating-card card-1">
            <FileText size={24} />
            <div>
              <div className="card-title">PRD Analysis</div>
              <div className="card-desc">AI-powered insights</div>
            </div>
          </div>
          <div className="floating-card card-2">
            <Database size={24} />
            <div>
              <div className="card-title">Smart Docs</div>
              <div className="card-desc">Interactive guides</div>
            </div>
          </div>
          <div className="floating-card card-3">
            <GitBranch size={24} />
            <div>
              <div className="card-title">Release Automation</div>
              <div className="card-desc">Streamlined workflows</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <div className="section-header">
          <h2>Powerful Tools for Every QA Need</h2>
          <p>Choose the right tool for your workflow - or use them together for maximum efficiency</p>
        </div>

        <div className="features-grid">
          {features.map((feature) => (
            <div key={feature.id} className={`feature-card ${feature.color}`}>
              <div className="feature-icon">
                {feature.icon}
              </div>
              
              <div className="feature-content">
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                
                <ul className="feature-capabilities">
                  {feature.capabilities.map((capability, index) => (
                    <li key={index}>
                      <CheckCircle size={16} />
                      <span>{capability}</span>
                    </li>
                  ))}
                </ul>
                
                <button 
                  className="feature-cta"
                  onClick={() => onNavigateToTab(feature.id)}
                >
                  Try {feature.title}
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="workflow-section">
        <div className="section-header">
          <h2>How QA Hub Works</h2>
          <p>Simple, powerful workflow that transforms your documents into actionable insights</p>
        </div>

        <div className="workflow-steps">
          {workflows.map((workflow, index) => (
            <div key={workflow.step} className="workflow-step">
              <div className="step-number">{workflow.step}</div>
              <div className="step-icon">{workflow.icon}</div>
              <div className="step-content">
                <h3>{workflow.title}</h3>
                <p>{workflow.description}</p>
              </div>
              {index < workflows.length - 1 && (
                <div className="step-connector">
                  <ArrowRight size={20} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Benefits Section */}
      <div className="benefits-section">
        <div className="section-header">
          <h2>Why Choose QA Hub?</h2>
          <p>Built by QA professionals, for QA professionals</p>
        </div>

        <div className="benefits-grid">
          {benefits.map((benefit, index) => (
            <div key={index} className="benefit-card">
              <div className="benefit-icon">
                {benefit.icon}
              </div>
              <h3>{benefit.title}</h3>
              <p>{benefit.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="cta-section">
        <div className="cta-content">
          <h2>Ready to Transform Your QA Workflow?</h2>
          <p>Join QA professionals who are already saving hours with AI-powered automation</p>
          
          <div className="cta-buttons">
            <button 
              className="cta-primary large"
              onClick={() => onNavigateToTab('prd-generator')}
            >
              <FileText size={20} />
              Get Started Now
              <ArrowRight size={16} />
            </button>
          </div>

          <div className="cta-features">
            <div className="cta-feature">
              <CheckCircle size={16} />
              <span>Free to use</span>
            </div>
            <div className="cta-feature">
              <CheckCircle size={16} />
              <span>No setup required</span>
            </div>
            <div className="cta-feature">
              <CheckCircle size={16} />
              <span>Instant results</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
