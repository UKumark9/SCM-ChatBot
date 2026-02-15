# response_formatter.py - Response Formatting Utility

## Purpose
Utility for formatting agent responses with metrics, timing, and metadata. Provides structured response formatting for better user experience.

## Key Components

### Class: ResponseFormatter
Static utility class for response formatting with metrics.

## Core Methods

### `format_response(response_text, metrics=None, agent_name=None)`
Formats response with optional metrics and agent info.

**Parameters:**
- `response_text` (str): Main response content
- `metrics` (dict): Performance metrics (optional)
- `agent_name` (str): Agent name (optional)

**Returns:** str (formatted response)

**Example:**
```python
formatted = ResponseFormatter.format_response(
    response_text="Delay rate is 6.28%",
    metrics={'execution_time': 3.21, 'latency_ms': 3210},
    agent_name="Delay Agent"
)
```

**Output Format:**
```
[Response text]

Performance:
• Time: 3.21s
• Latency: 3210ms
• Agent: Delay Agent
```

## Helper Methods

### `format_metrics_section(metrics)`
Formats metrics dictionary into readable section.

**Parameters:**
- `metrics` (dict): Metrics data

**Expected Keys:**
- `execution_time`: Query execution time (seconds)
- `latency_ms`: Latency in milliseconds
- `data_sources`: List of sources used
- `hallucination_score`: Confidence score (0-1)
- `rag_used`: Whether RAG was used

**Returns:** str (formatted metrics)

### `add_separator(length=60, char='─')`
Adds visual separator line.

**Parameters:**
- `length` (int): Separator length
- `char` (str): Character to use

**Returns:** str (separator line)

## Usage Examples

### Basic Formatting
```python
from response_formatter import ResponseFormatter

response = ResponseFormatter.format_response(
    "The delay rate is 6.28%",
    metrics={'execution_time': 3.21},
    agent_name="Delay Agent"
)
```

### With Full Metrics
```python
metrics = {
    'execution_time': 3.21,
    'latency_ms': 3210,
    'data_sources': ['database'],
    'hallucination_score': 0.1,
    'rag_used': False
}

response = ResponseFormatter.format_response(
    "Detailed analysis...",
    metrics=metrics,
    agent_name="Analytics Agent"
)
```

## Dependencies

### Internal Modules
- None (standalone utility)

### External Libraries
- None (pure Python)

## Note

This module is largely superseded by `ui_formatter.py` which provides more comprehensive formatting with icons and better visual structure. Consider using `UIFormatter` for new implementations.

## Integration Points

### Could Be Used By
- Any agent or module needing response formatting
- Custom formatting requirements

### Recommendation
Use `UIFormatter` instead for consistent formatting across the application.
