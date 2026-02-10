# enhanced_chatbot.py - Enhanced Single LLM Chatbot

## Purpose
Implements a single LLM-based chatbot that combines RAG context retrieval with analytics data processing. Uses Groq API with Llama 3.3 70B model for response generation.

## Key Components

### Class: PromptTemplates
Stores prompt templates for LLM interactions.

**Templates:**
- `SYSTEM_PROMPT`: System role definition
- `ANSWER_WITH_CONTEXT`: Main response generation prompt
- `CONVERSATIONAL_PROMPT`: Conversational response format

### Class: EnhancedSCMChatbot
Main chatbot class with LLM and RAG integration.

**Initialization Parameters:**
- `analytics_engine`: SCMAnalytics instance for data queries
- `rag_module`: RAGModule instance for document retrieval (optional)
- `use_llm` (bool): Enable/disable LLM features (default: True)

## Core Methods

### `__init__(analytics_engine, rag_module=None, use_llm=True)`
Initializes enhanced chatbot with analytics and optional RAG.

**Setup:**
- Initializes Groq LLM client
- Configures prompt templates
- Sets up conversation history tracking
- Validates GROQ_API_KEY environment variable

### `query(user_query, show_agent=True, use_rag=True)`
Main query processing method.

**Parameters:**
- `user_query` (str): User's question
- `show_agent` (bool): Show agent metadata in response
- `use_rag` (bool): Enable/disable RAG retrieval

**Returns:** str (formatted response)

**Process:**
1. Analyzes query intent
2. Gathers analytics data based on intent
3. Retrieves RAG context (if enabled)
4. Generates LLM response or falls back to rule-based
5. Formats response with metadata

**Example:**
```python
chatbot = EnhancedSCMChatbot(analytics_engine, rag_module)
response = chatbot.query("What is the delay rate?", use_rag=True)
# Returns: "The delivery delay rate is 6.28%"
```

### `analyze_query_intent(query)`
Determines query type and required analytics.

**Parameters:**
- `query` (str): User's question

**Returns:** dict with intent information

**Intent Types:**
- `delivery`: Delivery and delay queries
- `revenue`: Revenue and financial queries
- `forecasting`: Demand forecasting queries
- `geographic`: Location-based queries
- `product`: Product-specific queries
- `general`: General queries

**Complexity Levels:**
- `simple`: Single metric (e.g., "What is delay rate?")
- `moderate`: Multiple metrics (e.g., "Show delay analysis")
- `complex`: Insights/recommendations (e.g., "Why delays increasing?")

### `gather_analytics_data(intent)`
Retrieves analytics data based on query intent.

**Parameters:**
- `intent` (dict): Intent analysis result

**Returns:** dict with analytics data

**Data Types:**
- Delivery metrics (delay rate, on-time %, counts)
- Revenue analytics (total, by product/state)
- Geographic breakdowns
- Product-level statistics

### `generate_llm_response(query, context, analytics_data, intent)`
Generates response using Groq LLM.

**Parameters:**
- `query` (str): User's question
- `context` (str): RAG-retrieved policy documents
- `analytics_data` (dict): Analytics metrics
- `intent` (dict): Query intent analysis

**Returns:** str (LLM-generated response)

**Features:**
- **Source Priority**: Policy questions use RAG, data questions use analytics
- **Complexity Matching**: Simple questions get brief answers
- **Context Integration**: Combines policy documents with live data

**LLM Configuration:**
- Model: llama-3.3-70b-versatile
- Temperature: 0.3 (factual responses)
- Max Tokens: 1024

**Prompt Structure:**
```
Policy Documents (if available):
[RAG context]

Analytics Results:
[Database metrics]

User Question: [query]

Guidelines:
- For "What is/are" policy questions → Answer from Policy Documents only
- For metric questions → Answer from Analytics Results
- Match response complexity to question type
```

### `generate_rule_based_response(query, intent, analytics_data)`
Fallback response generation without LLM.

**Parameters:**
- `query` (str): User's question
- `intent` (dict): Query intent
- `analytics_data` (dict): Analytics metrics

**Returns:** str (formatted response)

**Use Cases:**
- LLM unavailable (API error, no key)
- Simple metrics queries
- Deterministic responses needed

### `retrieve_context(user_query)`
Retrieves RAG context for query.

**Parameters:**
- `user_query` (str): User's question

**Returns:** str (formatted policy documents)

**Process:**
1. Calls RAG module
2. Retrieves top 3 relevant documents
3. Returns formatted context

## Helper Methods

### `_extract_key_metric(analytics_data, intent, query)`
Extracts only relevant metric for simple questions.

**Purpose:** Reduce prompt size and improve response focus

### `_build_agent_info(agent, model, complexity, rag_used)`
Builds metadata section for response.

**Returns:** Formatted string with:
- Agent type
- Model used
- Query complexity
- RAG usage status
- Execution time

## Prompt Templates

### SYSTEM_PROMPT
```
You are an AI assistant for Supply Chain Management analytics.
You provide accurate, data-driven insights based on:
1. Policy documents (guidelines, targets, definitions)
2. Analytics data (actual metrics, counts, rates)

Always cite your sources and distinguish between policy and actual data.
```

### ANSWER_WITH_CONTEXT
Main template with:
- Policy Documents section (RAG context)
- Analytics Results section (database metrics)
- Source Priority guidelines
- Complexity matching rules

## Dependencies

### External Libraries
- `groq`: Groq API client for LLM access
- `os`: Environment variable access
- `logging`: Application logging
- `json`: Data serialization

### Internal Modules
- `analytics_engine`: Data analytics
- `rag`: Document retrieval
- `data_wrapper`: Database abstraction

### Environment Variables
- `GROQ_API_KEY`: Required for LLM features

## Usage Examples

### Basic Query (with RAG)
```python
chatbot = EnhancedSCMChatbot(analytics_engine, rag_module)

# Policy question - uses RAG
response = chatbot.query("What are severity levels?")
# Returns policy definitions

# Data question - uses analytics
response = chatbot.query("What is delay rate?")
# Returns: "The delivery delay rate is 6.28%"
```

### Without RAG
```python
# Disable RAG for faster, data-only responses
response = chatbot.query("What is delay rate?", use_rag=False)
# Time: 25-35s (vs 45-60s with RAG)
```

### Fallback to Rule-Based
```python
# If LLM unavailable, automatically uses rule-based
chatbot = EnhancedSCMChatbot(analytics_engine, use_llm=False)
response = chatbot.query("Show delayed orders")
# Returns formatted data without LLM processing
```

## Performance Characteristics

### With RAG Enabled
- **Time**: 45-60 seconds
- **Sources**: RAG + Database + LLM
- **Use Case**: Comprehensive analysis with policy context

### Without RAG
- **Time**: 25-35 seconds
- **Sources**: Database + LLM
- **Use Case**: Fast data-focused responses

### Rule-Based Fallback
- **Time**: 1-2 seconds
- **Sources**: Database only
- **Use Case**: Simple metric queries, LLM unavailable

## Response Quality

### Strengths
- ✅ Comprehensive responses with context
- ✅ Combines policy and data seamlessly
- ✅ Consistent format across queries
- ✅ Natural language generation

### Limitations
- ❌ Slower than Agentic mode (always uses RAG when enabled)
- ❌ No intent classification (processes everything the same)
- ❌ Higher API costs (full LLM call for every query)

## Comparison with Agentic Mode

| Feature | Enhanced Mode | Agentic Mode |
|---------|--------------|--------------|
| Architecture | Single LLM | Multiple specialized agents |
| RAG Usage | Always (when enabled) | Intelligent (policy queries only) |
| Speed (data query) | 45-60s | 3-5s |
| Speed (policy query) | 45-60s | 15s |
| Complexity | Simple | Complex |
| Best For | Demos, comprehensive analysis | Production, fast responses |

## Error Handling

### LLM API Error
- Logs error with details
- Falls back to rule-based response
- Returns formatted data response

### RAG Retrieval Error
- Continues without context
- Logs warning
- Uses analytics data only

### Analytics Error
- Returns error message
- Logs exception with traceback
- Maintains conversation history

## Conversation History

Tracks all interactions:
```python
{
    'query': "User question",
    'response': "Bot response",
    'intent': {...},
    'agent': 'llm' or 'rule-based'
}
```

**Use Cases:**
- Multi-turn conversations
- Context maintenance
- Performance analysis

## Integration Points

### Used By
- `main.py`: UI query handler (Enhanced mode)

### Uses
- `analytics_engine.py`: Data analytics
- `rag.py`: Document retrieval
- Groq API: LLM processing

## Configuration

### Model Selection
Change model in `generate_llm_response()`:
```python
model="llama-3.3-70b-versatile"  # Current
# Options: llama-3.1-70b, mixtral-8x7b, etc.
```

### Temperature Tuning
Adjust temperature for response style:
```python
temperature=0.3  # Factual (current)
temperature=0.7  # Creative
temperature=0.0  # Deterministic
```

### RAG Top-K
Change number of retrieved documents in `retrieve_context()`:
```python
context = self.rag.retrieve_context(user_query, top_k=3)
```

## Logging

Log levels used:
- INFO: Query processing, mode selection
- WARNING: LLM disabled, API key missing
- ERROR: LLM errors, analytics failures
