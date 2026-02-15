# main.py - SCM Chatbot Application Entry Point

## Purpose
Main application file that initializes and runs the Supply Chain Management (SCM) Chatbot with Gradio web interface. Provides both Agentic (Multi-Agent) and Enhanced (Single LLM) modes for query processing.

## Key Components

### Class: SCMChatbotApp
Main application class that orchestrates the entire chatbot system.

**Initialization Parameters:**
- `init_all_modes` (bool): Initialize both Agentic and Enhanced modes
- `use_agentic` (bool): Enable multi-agent orchestrator
- `use_enhanced` (bool): Enable single LLM chatbot
- `use_rag` (bool): Enable RAG (Retrieval-Augmented Generation)

### Core Methods

#### `__init__(init_all_modes=False, use_agentic=True, use_enhanced=False, use_rag=True)`
Initializes the chatbot application with selected modes.

#### `initialize_database()`
- Connects to SQLite database (scm_data.db)
- Creates data wrapper for analytics engine
- Returns: bool (success/failure)

#### `initialize_analytics()`
- Initializes SCMAnalytics engine
- Sets up data analysis capabilities
- Returns: bool (success/failure)

#### `initialize_rag()`
- Initializes RAG module for document retrieval
- Loads vector index from data/vector_index/
- Returns: bool (success/failure)

#### `initialize_orchestrator()`
- Initializes multi-agent orchestrator
- Sets up specialized agents (Delay, Analytics, Forecasting, Data Query)
- Integrates intent classification
- Returns: bool (success/failure)

#### `initialize_enhanced_chatbot()`
- Initializes single LLM chatbot (Enhanced mode)
- Integrates with Groq API
- Returns: bool (success/failure)

#### `query(user_input, mode=None, use_rag=True)`
Main query processing method.

**Parameters:**
- `user_input` (str): User's question
- `mode` (str): "agentic" or "enhanced"
- `use_rag` (bool): Whether to use RAG for Enhanced mode

**Returns:** str (formatted response)

**Flow:**
1. Determines mode (agentic/enhanced)
2. Routes to appropriate handler
3. Returns formatted response

#### `create_ui()`
Creates Gradio web interface with:
- Chat interface
- Mode selector (Agentic vs Enhanced)
- RAG toggle (for Enhanced mode only)
- Document management tab
- Performance metrics tab

**UI Components:**
- **Chat Tab**: Main conversation interface
- **Document Management**: Upload/delete policy documents
- **Performance Metrics**: Compare Agentic vs Enhanced performance

### Helper Methods

#### `chat_with_mode(message, history, mode, rag_config)`
Handles chat interactions with mode-specific routing.

#### `respond(message, chat_history, mode, rag_config)`
Processes user message and returns bot response.

#### `update_mode_sections(mode)`
Updates UI visibility based on selected mode.

#### `upload_documents(files)`
Handles document upload and automatic vectorization.

#### `delete_document(file_name)`
Deletes document and updates vector index.

## Dependencies

### External Libraries
- `gradio`: Web UI framework
- `sqlite3`: Database connection
- `argparse`: Command-line arguments
- `logging`: Application logging

### Internal Modules
- `data_wrapper`: Database abstraction
- `analytics_engine`: Data analysis
- `rag`: Document retrieval
- `enhanced_chatbot`: Single LLM mode
- `agents.orchestrator`: Multi-agent mode
- `metrics_tracker`: Performance tracking

## Command-Line Arguments

```bash
python main.py [OPTIONS]
```

**Options:**
- `--init-all`: Initialize both Agentic and Enhanced modes
- `--agentic`: Initialize only Agentic mode (default)
- `--enhanced`: Initialize only Enhanced mode
- `--no-rag`: Disable RAG module
- `--share`: Create shareable Gradio link

## Usage Examples

### Start with both modes (recommended for demos):
```bash
python main.py --init-all
```

### Start with Agentic mode only:
```bash
python main.py --agentic
```

### Start with Enhanced mode only:
```bash
python main.py --enhanced
```

### Disable RAG:
```bash
python main.py --no-rag
```

## Application Flow

1. **Initialization:**
   - Parse command-line arguments
   - Initialize database
   - Initialize analytics engine
   - Initialize RAG module (if enabled)
   - Initialize selected mode(s)

2. **Query Processing:**
   - User enters query in UI
   - Mode selector determines routing
   - Query processed by Agentic or Enhanced mode
   - Response formatted and displayed

3. **Document Management:**
   - Upload documents via UI
   - Automatic vectorization
   - Index updated for RAG retrieval

4. **Performance Tracking:**
   - Metrics collected during queries
   - Performance comparison displayed
   - Agentic vs Enhanced statistics

## Configuration

### Environment Variables
- `GROQ_API_KEY`: Required for LLM features (Enhanced mode)

### File Paths
- Database: `data/scm_data.db`
- Vector Index: `data/vector_index/`
- Documents: `data/business_docs/documents/`
- Metadata: `data/business_docs/documents_metadata.json`

## Error Handling

- **Database Connection Error**: Logs error, continues with limited functionality
- **RAG Initialization Error**: Disables RAG, falls back to analytics-only
- **LLM API Error**: Falls back to rule-based responses
- **Document Upload Error**: Returns error message to user

## Performance Notes

### Agentic Mode
- **Speed**: 3-18s depending on query type
- **Optimization**: Skips RAG for data questions (60-80% faster)
- **Best for**: Production use, fast responses

### Enhanced Mode
- **With RAG**: 45-60s (comprehensive)
- **Without RAG**: 25-35s (data-focused)
- **Best for**: Demos, comprehensive analysis

## Logging

Logs written to console and file with levels:
- INFO: Initialization, query processing
- WARNING: Missing dependencies, fallbacks
- ERROR: Exceptions, failed operations

## Exit Codes

- `0`: Successful execution
- `1`: Critical initialization failure
