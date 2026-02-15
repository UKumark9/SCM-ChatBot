# SCM Chatbot Documentation Index

## Overview
Complete documentation for all Python modules in the SCM Chatbot application. Each document explains the purpose, functionality, key methods, usage examples, and integration points for its respective module.

---

## Core Application Files

### [main.md](main.md)
**File**: `main.py`
**Purpose**: Main application entry point with Gradio UI
**Key Features**:
- Application initialization and startup
- Mode selection (Agentic vs Enhanced)
- Gradio web interface
- Document management
- Performance metrics display
- Command-line arguments

---

## RAG (Retrieval-Augmented Generation)

### [rag.md](rag.md)
**File**: `rag.py`
**Purpose**: Standard RAG implementation with FAISS vector indexing
**Key Features**:
- Document retrieval using semantic search
- FAISS index management
- Sentence transformer embeddings
- Context formatting for LLM

### [enhanced_rag.md](enhanced_rag.md)
**File**: `enhanced_rag.py`
**Purpose**: Advanced RAG with hybrid search and re-ranking
**Key Features**:
- Hybrid search (semantic + keyword)
- MMR for result diversity
- Cross-encoder re-ranking
- Multiple retrieval strategies

### [vectorize_documents.md](vectorize_documents.md)
**File**: `vectorize_documents.py`
**Purpose**: Document vectorization and index building utility
**Key Features**:
- Document chunking
- Embedding generation
- FAISS index creation
- Metadata management

### [rebuild_index.md](rebuild_index.md)
**File**: `rebuild_index.py`
**Purpose**: FAISS index rebuilding and maintenance
**Key Features**:
- Index corruption recovery
- Bulk document reprocessing
- Index verification
- Backup and restore

---

## Chatbot Modes

### [enhanced_chatbot.md](enhanced_chatbot.md)
**File**: `enhanced_chatbot.py`
**Purpose**: Single LLM chatbot with RAG integration
**Key Features**:
- Groq API integration (Llama 3.3 70B)
- RAG context retrieval
- Intent analysis
- Rule-based fallback
- Prompt templates

### [orchestrator.md](orchestrator.md)
**File**: `agents/orchestrator.py`
**Purpose**: Multi-agent system coordinator
**Key Features**:
- Agent routing and coordination
- Intent classification integration
- Parallel agent execution
- Performance tracking
- UIFormatter integration

---

## Specialized Agents

### [delay_agent.md](delay_agent.md)
**File**: `agents/delay_agent.py`
**Purpose**: Delivery delay analysis agent
**Key Features**:
- Delay rate calculation
- Severity classification
- On-time performance metrics
- Geographic delay analysis
- Classification-based RAG usage

### [analytics_agent.md](analytics_agent.md)
**File**: `agents/analytics_agent.py`
**Purpose**: Revenue and performance analytics agent
**Key Features**:
- Revenue analysis
- Product performance
- Sales metrics
- Geographic breakdowns
- Top/bottom performers

### [forecasting_agent.md](forecasting_agent.md)
**File**: `agents/forecasting_agent.py`
**Purpose**: Demand forecasting agent
**Key Features**:
- Demand forecasting
- Trend analysis
- Statistical models
- Confidence intervals
- Seasonality detection

### [data_query_agent.md](data_query_agent.md)
**File**: `agents/data_query_agent.py`
**Purpose**: Raw data retrieval agent
**Key Features**:
- Direct database queries
- List/show/get operations
- Filtered data retrieval
- Count queries
- Table formatting

---

## Classification and Formatting

### [intent_classifier.md](intent_classifier.md)
**File**: `intent_classifier.py`
**Purpose**: Query intent classification (policy/data/mixed)
**Key Features**:
- Keyword-based classification
- Policy vs data detection
- Domain identification
- Confidence scoring
- RAG optimization (60-80% faster for data queries)

### [ui_formatter.md](ui_formatter.md)
**File**: `ui_formatter.py`
**Purpose**: Centralized UI response formatting
**Key Features**:
- Consistent response formatting
- Metadata display
- RAG context formatting
- Error formatting
- Visual separators and icons

### [response_formatter.md](response_formatter.md)
**File**: `response_formatter.py`
**Purpose**: Legacy response formatting utility
**Key Features**:
- Basic response formatting
- Metrics display
**Note**: Superseded by `ui_formatter.py`

---

## Performance and Metrics

### [metrics_tracker.md](metrics_tracker.md)
**File**: `metrics_tracker.py`
**Purpose**: Query performance tracking and comparison
**Key Features**:
- Query latency tracking
- Agent execution tracking
- Data source tracking
- Hallucination score calculation
- Agentic vs Enhanced comparison
- Performance metrics display

---

## Utilities

### [extract_features_optimized.md](extract_features_optimized.md)
**File**: `extract_features_optimized.py`
**Purpose**: Feature extraction from SCM data
**Key Features**:
- Delivery feature extraction
- Revenue feature extraction
- Temporal feature extraction
- Geographic feature extraction
- Parallel processing
- Feature caching

---

## Testing

### [test_files.md](test_files.md)
**Files**: `test_*.py`
**Purpose**: Test suite for all components
**Test Files**:
- `test_enhanced_rag.py`: Enhanced RAG testing
- `test_feature_store.py`: Feature extraction testing
- `test_intent_fix.py`: Intent classification validation
- `test_main_rag_integration.py`: Main app integration tests
- `test_rag_comprehensive.py`: Comprehensive RAG tests
- `test_severity_levels.py`: Severity classification tests

---

## Documentation Organization

### By Category

#### Core Application
- [main.md](main.md) - Application entry point

#### RAG System
- [rag.md](rag.md) - Standard RAG
- [enhanced_rag.md](enhanced_rag.md) - Advanced RAG
- [vectorize_documents.md](vectorize_documents.md) - Document processing
- [rebuild_index.md](rebuild_index.md) - Index maintenance

#### Chatbot Modes
- [enhanced_chatbot.md](enhanced_chatbot.md) - Single LLM mode
- [orchestrator.md](orchestrator.md) - Multi-agent mode

#### Agents
- [delay_agent.md](delay_agent.md) - Delay analysis
- [analytics_agent.md](analytics_agent.md) - Revenue analytics
- [forecasting_agent.md](forecasting_agent.md) - Demand forecasting
- [data_query_agent.md](data_query_agent.md) - Data retrieval

#### Infrastructure
- [intent_classifier.md](intent_classifier.md) - Query classification
- [ui_formatter.md](ui_formatter.md) - Response formatting
- [metrics_tracker.md](metrics_tracker.md) - Performance tracking
- [extract_features_optimized.md](extract_features_optimized.md) - Feature extraction

#### Testing
- [test_files.md](test_files.md) - Test suite

### By Functionality

#### Query Processing Flow
1. [main.md](main.md) - Receive user query
2. [intent_classifier.md](intent_classifier.md) - Classify query type
3. [orchestrator.md](orchestrator.md) - Route to agent
4. [delay_agent.md](delay_agent.md) / [analytics_agent.md](analytics_agent.md) / etc. - Process query
5. [rag.md](rag.md) - Retrieve context (if needed)
6. [ui_formatter.md](ui_formatter.md) - Format response
7. [metrics_tracker.md](metrics_tracker.md) - Track performance

#### Document Management Flow
1. [main.md](main.md) - Upload document
2. [vectorize_documents.md](vectorize_documents.md) - Process and vectorize
3. [rag.md](rag.md) - Use in retrieval
4. [rebuild_index.md](rebuild_index.md) - Maintain index

---

## Quick Reference

### Most Important Files
1. **[main.md](main.md)** - Start here to understand the application
2. **[orchestrator.md](orchestrator.md)** - Understand multi-agent system
3. **[intent_classifier.md](intent_classifier.md)** - Learn about query routing
4. **[rag.md](rag.md)** - Understand document retrieval

### For Development
- **Adding new agent**: See [delay_agent.md](delay_agent.md) as template
- **Modifying RAG**: See [rag.md](rag.md) and [enhanced_rag.md](enhanced_rag.md)
- **Changing UI**: See [main.md](main.md) and [ui_formatter.md](ui_formatter.md)
- **Performance optimization**: See [metrics_tracker.md](metrics_tracker.md) and [intent_classifier.md](intent_classifier.md)

### For Testing
- **Run tests**: See [test_files.md](test_files.md)
- **Add tests**: Follow patterns in test files
- **Validate changes**: Use test suite before deployment

---

## File Naming Convention

All documentation files follow this pattern:
- Python file: `filename.py`
- Documentation: `filename.md`
- Location: `docs/filename.md`

Example:
- Python: `intent_classifier.py`
- Docs: `docs/intent_classifier.md`

---

## How to Use This Documentation

### For New Developers
1. Read [main.md](main.md) to understand application structure
2. Read [orchestrator.md](orchestrator.md) to understand agentic mode
3. Read [enhanced_chatbot.md](enhanced_chatbot.md) to understand enhanced mode
4. Read [intent_classifier.md](intent_classifier.md) to understand query routing

### For Feature Development
1. Identify relevant module(s)
2. Read documentation for those modules
3. Review integration points
4. Check test files for examples

### For Debugging
1. Check error logs to identify failing module
2. Read documentation for that module
3. Review error handling section
4. Check integration points for dependencies

### For Performance Tuning
1. Read [metrics_tracker.md](metrics_tracker.md) for monitoring
2. Read [intent_classifier.md](intent_classifier.md) for optimization
3. Review performance characteristics in each module
4. Check comparison tables (Agentic vs Enhanced)

---

## Documentation Sections

Each documentation file includes:

1. **Purpose**: What the module does
2. **Key Components**: Main classes and functions
3. **Core Methods**: Detailed method descriptions
4. **Usage Examples**: Code examples
5. **Dependencies**: Required libraries and modules
6. **Integration Points**: How it connects to other modules
7. **Error Handling**: How errors are managed
8. **Performance**: Speed and resource usage
9. **Best Practices**: Recommended usage patterns

---

## Version Information

**Documentation Version**: 1.0
**Last Updated**: February 10, 2026
**Application Version**: Latest
**Python Version**: 3.9+

---

## Contributing to Documentation

When updating code:
1. Update corresponding .md file
2. Add new examples if API changes
3. Update integration points if dependencies change
4. Keep version information current

---

## Support

For questions about:
- **Application usage**: See [main.md](main.md)
- **Agent development**: See agent documentation files
- **RAG system**: See RAG-related files
- **Testing**: See [test_files.md](test_files.md)

---

**End of Documentation Index**
