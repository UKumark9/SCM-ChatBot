# ui_formatter.py - UI Response Formatting Utility

## Purpose
Centralized formatting utility for consistent, professional output across all agents and RAG responses. Provides structured formatting with metadata, separators, and readability enhancements.

## Key Components

### Class: UIFormatter
Static utility class for response formatting.

## Core Methods

### `format_response(result)`
Main formatter for agent responses with metadata.

**Parameters:**
- `result` (dict): Agent response dictionary

**Required Keys in result:**
- `response` (str): Main response text
- `agent` (str): Agent name (optional)
- `success` (bool): Success status (optional)
- `used_rag` (bool): Whether RAG was used (optional)
- `metrics` (dict): Performance metrics (optional)

**Returns:** str (formatted response)

**Output Format:**
```
[Response text]

────────────────────────────────────────────────────────────
🤖 Agent: [Agent Name] | ✅ Success
📁 Sources: [Database | RAG | Both]
⏱️ Time: [execution_time]s
🎯 Confidence: [confidence]%
────────────────────────────────────────────────────────────
```

**Example:**
```python
result = {
    'response': 'The delivery delay rate is 6.28%',
    'agent': 'Delay Agent',
    'success': True,
    'used_rag': False,
    'metrics': {'execution_time': 3.21}
}

formatted = UIFormatter.format_response(result)
# Returns formatted response with metadata footer
```

### `format_rag_context(context, max_docs=3)`
Formats RAG-retrieved policy documents.

**Parameters:**
- `context` (str): Raw RAG context text
- `max_docs` (int): Maximum documents to display

**Returns:** str (formatted RAG context)

**Output Format:**
```
### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Document 1 | Relevance: 0.85

[Document excerpt...]

───────────────────────────────────────────────────────────
📄 Document 2 | Relevance: 0.72

[Document excerpt...]

───────────────────────────────────────────────────────────
```

**Features:**
- Document numbering
- Relevance scores
- Visual separators
- Clean formatting

**Example:**
```python
context = rag.retrieve_context("What are severity levels?")
formatted = UIFormatter.format_rag_context(context)
# Returns beautifully formatted policy documents
```

### `format_error(error_message, agent_name=None)`
Formats error messages consistently.

**Parameters:**
- `error_message` (str): Error description
- `agent_name` (str): Agent that encountered error (optional)

**Returns:** str (formatted error)

**Output Format:**
```
❌ Error

[Error message]

────────────────────────────────────────────────────────────
🤖 Agent: [Agent Name] | ❌ Failed
⏱️ Please try again or rephrase your question
────────────────────────────────────────────────────────────
```

**Example:**
```python
error = UIFormatter.format_error(
    "Database connection failed",
    agent_name="Analytics Agent"
)
```

### `format_metrics(metrics)`
Formats performance metrics display.

**Parameters:**
- `metrics` (dict): Metrics dictionary

**Expected Keys:**
- `execution_time` (float): Query time in seconds
- `latency_ms` (int): Latency in milliseconds
- `data_sources` (list): Sources used
- `hallucination_score` (float): Confidence score

**Returns:** str (formatted metrics)

**Output Format:**
```
📊 Performance Metrics:
  • Execution Time: 3.21s
  • Latency: 3210ms
  • Sources: Database, RAG
  • Confidence: 95%
```

### `format_list(items, title=None, numbered=True)`
Formats lists with optional title and numbering.

**Parameters:**
- `items` (list): Items to format
- `title` (str): Optional list title
- `numbered` (bool): Use numbers vs bullets

**Returns:** str (formatted list)

**Examples:**
```python
# Numbered list
items = ["Item 1", "Item 2", "Item 3"]
UIFormatter.format_list(items, title="Results", numbered=True)
# Output:
# Results:
# 1. Item 1
# 2. Item 2
# 3. Item 3

# Bulleted list
UIFormatter.format_list(items, numbered=False)
# Output:
# • Item 1
# • Item 2
# • Item 3
```

### `format_table(data, headers)`
Formats data as markdown table.

**Parameters:**
- `data` (list of lists): Table data
- `headers` (list): Column headers

**Returns:** str (markdown table)

**Example:**
```python
headers = ["State", "Delay Rate", "Orders"]
data = [
    ["CA", "8.5%", "1250"],
    ["TX", "6.2%", "980"],
    ["NY", "7.1%", "1100"]
]

table = UIFormatter.format_table(data, headers)
# Output:
# | State | Delay Rate | Orders |
# |-------|------------|--------|
# | CA    | 8.5%       | 1250   |
# | TX    | 6.2%       | 980    |
# | NY    | 7.1%       | 1100   |
```

### `create_separator(char='─', length=60)`
Creates visual separator line.

**Parameters:**
- `char` (str): Character to use
- `length` (int): Line length

**Returns:** str (separator line)

**Example:**
```python
sep = UIFormatter.create_separator()
# Returns: "────────────────────────────────────────────────────────────"
```

### `format_percentage(value, decimal_places=1)`
Formats numbers as percentages.

**Parameters:**
- `value` (float): Value to format (0-100 or 0-1)
- `decimal_places` (int): Decimal precision

**Returns:** str (formatted percentage)

**Example:**
```python
UIFormatter.format_percentage(6.28)  # "6.3%"
UIFormatter.format_percentage(0.0628)  # "6.3%"
```

## Helper Methods

### `_get_status_icon(success)`
Returns appropriate icon for status.

**Parameters:**
- `success` (bool): Success status

**Returns:** str ("✅" or "❌")

### `_get_source_text(used_rag, used_database=True)`
Generates source description text.

**Parameters:**
- `used_rag` (bool): RAG was used
- `used_database` (bool): Database was used

**Returns:** str (source description)

**Examples:**
- `used_rag=True, used_database=True`: "Database, RAG"
- `used_rag=True, used_database=False`: "RAG"
- `used_rag=False, used_database=True`: "Database"

### `_truncate_text(text, max_length=500)`
Truncates long text with ellipsis.

**Parameters:**
- `text` (str): Text to truncate
- `max_length` (int): Maximum length

**Returns:** str (truncated text)

## Icons and Symbols

### Status Icons
- ✅ Success
- ❌ Error/Failure
- ⚠️ Warning

### Category Icons
- 🤖 Agent
- 📁 Sources
- ⏱️ Time/Performance
- 🎯 Confidence/Accuracy
- 📚 Documents/RAG
- 📄 Individual Document
- 📊 Metrics/Statistics

### Separators
- `─` Horizontal line (60 chars)
- `═` Double line (for emphasis)
- `•` Bullet point
- `→` Arrow/Direction

## Usage Examples

### Example 1: Agent Response
```python
from ui_formatter import UIFormatter

# Agent result
result = {
    'response': 'The current delivery delay rate is 6.28%.',
    'agent': 'Delay Agent',
    'success': True,
    'used_rag': False,
    'classification': {'query_type': 'data'},
    'metrics': {
        'execution_time': 3.21,
        'latency_ms': 3210
    }
}

# Format
formatted = UIFormatter.format_response(result)
print(formatted)
```

**Output:**
```
The current delivery delay rate is 6.28%.

────────────────────────────────────────────────────────────
🤖 Agent: Delay Agent | ✅ Success
📁 Sources: Database
⏱️ Time: 3.21s
────────────────────────────────────────────────────────────
```

### Example 2: RAG Context
```python
# RAG retrieval
context = rag.retrieve_context("What are severity levels?")

# Format for display
formatted = UIFormatter.format_rag_context(context)
print(formatted)
```

**Output:**
```
### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Document 1 | Relevance: 0.85

Severity Levels:
• Critical Delay: >5 business days
• Major Delay: 3-5 business days
• Minor Delay: 1-2 business days

───────────────────────────────────────────────────────────
```

### Example 3: Error Handling
```python
try:
    result = agent.query(query)
except Exception as e:
    error = UIFormatter.format_error(str(e), agent_name="Analytics Agent")
    print(error)
```

## Integration Points

### Used By
- `agents/orchestrator.py`: Formats all agent responses
- `agents/delay_agent.py`: Formats delay analysis results
- `agents/analytics_agent.py`: Formats revenue analytics
- `agents/forecasting_agent.py`: Formats forecasts
- `agents/data_query_agent.py`: Formats data results
- `enhanced_chatbot.py`: Could be integrated for consistent formatting

### Design Principles
1. **Consistency**: Same format across all agents
2. **Readability**: Clear separators and structure
3. **Information Density**: Show relevant metadata without clutter
4. **Visual Appeal**: Icons and formatting for better UX
5. **Accessibility**: Plain text, no fancy Unicode

## Customization

### Change Separator Style
```python
# Default
UIFormatter.create_separator()  # ─────────────

# Custom
UIFormatter.create_separator(char='═')  # ═════════════
UIFormatter.create_separator(length=40)  # ────────────────────────
```

### Custom Icons
Modify icon methods to use different symbols:
```python
def _get_status_icon(success):
    return "✓" if success else "✗"  # Different icons
```

### Adjust Metrics Display
Customize `format_metrics()` to show/hide specific metrics:
```python
def format_metrics(metrics):
    # Show only execution time
    return f"⏱️ Time: {metrics['execution_time']:.2f}s"
```

## Performance Considerations

### String Concatenation
- Uses f-strings for efficiency
- Minimal overhead (~1ms per format call)

### Memory Usage
- Stateless methods (no instance state)
- Minimal memory footprint

### Thread Safety
- All methods are static
- No shared state
- Thread-safe by design

## Best Practices

1. **Always use UIFormatter** for agent responses (consistency)
2. **Include metadata** when available (transparency)
3. **Format errors** consistently (better UX)
4. **Use appropriate icons** for context (visual clarity)
5. **Keep separators aligned** (professional appearance)

## Future Enhancements

### Potential Additions
- Color support (with terminal color codes)
- HTML/rich text formatting
- Customizable themes
- Localization support
- Responsive width (adapt to terminal size)
- Markdown rendering enhancements
