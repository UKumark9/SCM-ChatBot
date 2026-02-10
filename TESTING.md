# Testing Guide

## Test Suite Overview

All tests are located in the `tests/` directory and use **pytest**.

### Test Files

| File | Scope |
|------|-------|
| `tests/test_all.py` | Comprehensive test suite covering all modules |
| `tests/test_agent_info.py` | Agent metadata and routing information |
| `tests/test_api_key.py` | API key loading and validation |
| `tests/test_delays.py` | Delay agent analysis accuracy |
| `tests/test_enhanced_ai.py` | Enhanced single-LLM mode responses |
| `tests/test_llm_fix.py` | LLM-specific regression tests |
| `tests/test_query.py` | Query parsing and intent detection |
| `tests/test_response_levels.py` | Adaptive response complexity levels |
| `tests/test_serialization.py` | Pandas/NumPy JSON serialization |
| `tests/test_suite.py` | Test suite runner and aggregation |
| `tests/test_updated_model.py` | Updated model behavior tests |
| `tests/verify_fix.py` | Targeted fix verification tests |

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run a Specific Test File

```bash
pytest tests/test_delays.py -v
```

### Run a Specific Test Function

```bash
pytest tests/test_delays.py::test_delay_rate -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

### Run with HTML Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```bash
# Serialization logic
pytest tests/test_serialization.py -v

# Query intent parsing
pytest tests/test_query.py -v

# API key handling
pytest tests/test_api_key.py -v
```

### Integration Tests

Test component interactions:

```bash
# Enhanced AI with data
pytest tests/test_enhanced_ai.py -v

# Agent routing and responses
pytest tests/test_agent_info.py -v

# Delay analysis pipeline
pytest tests/test_delays.py -v
```

### Response Quality Tests

Validate output format and content:

```bash
# Response complexity levels (simple/moderate/complex)
pytest tests/test_response_levels.py -v

# Model output validation
pytest tests/test_updated_model.py -v
```

## RAG Evaluation

The RAG system has a dedicated evaluation module (`rag_evaluation.py`) that measures:

- **Retrieval Precision** -- How relevant are the retrieved documents
- **Retrieval Recall** -- How many relevant documents are found
- **Answer Relevance** -- How well the generated answer matches the query
- **Faithfulness** -- Whether the answer is grounded in retrieved documents

Run RAG evaluation:

```bash
python rag_evaluation.py
```

Results are saved to `data/rag_evaluation_results.json`.

## CI/CD Pipeline

The GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) runs:

1. **Lint** -- Black formatting check + Flake8 linting
2. **Test** -- Full pytest suite with coverage
3. **RAG Validation** -- RAG retrieval quality checks
4. **Performance** -- Response latency benchmarks
5. **Docker Build** -- Container build verification
6. **Deploy** -- Deployment stage (on main branch)
7. **Release** -- Tagged releases

### Running CI Checks Locally

```bash
# Lint check
black --check .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Tests
pytest tests/ -v --cov=.

# Docker build
docker build -t scm-chatbot .
```

## Writing New Tests

Place new test files in `tests/` following the naming convention `test_<module>.py`.

```python
"""Tests for <module_name>"""
import pytest

def test_basic_functionality():
    """Test description"""
    # Arrange
    ...
    # Act
    result = function_under_test()
    # Assert
    assert result == expected

@pytest.fixture
def sample_data():
    """Fixture providing test data"""
    import pandas as pd
    return pd.DataFrame({...})

def test_with_fixture(sample_data):
    """Test using fixture data"""
    assert len(sample_data) > 0
```

## Environment Variables for Testing

Some tests require the Groq API key. Tests that call the API will skip gracefully if the key is not set.

```bash
# Run tests with API key
GROQ_API_KEY=your_key pytest tests/ -v

# Run only tests that don't need API access
pytest tests/test_serialization.py tests/test_query.py -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure virtual environment is activated and `pip install -r requirements.txt` was run |
| Tests skip with "API key not set" | Set `GROQ_API_KEY` in `.env` or as environment variable |
| FAISS index errors | Run `python rebuild_index.py` to regenerate the vector index |
| Slow test execution | Run specific test files instead of the full suite |
