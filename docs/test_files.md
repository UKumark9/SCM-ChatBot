# Test Files Documentation

## Overview
Collection of test scripts for validating different components of the SCM chatbot system.

---

## test_enhanced_rag.py

### Purpose
Tests enhanced RAG functionality including hybrid search, MMR, and re-ranking.

### Key Tests
- `test_semantic_retrieval()`: Basic vector similarity search
- `test_keyword_retrieval()`: BM25 keyword search
- `test_hybrid_retrieval()`: Combined semantic + keyword
- `test_mmr_retrieval()`: Maximal Marginal Relevance
- `test_reranking()`: Cross-encoder re-ranking

### Usage
```bash
python test_enhanced_rag.py
```

### Expected Output
```
✅ Semantic retrieval: PASS
✅ Keyword retrieval: PASS
✅ Hybrid retrieval: PASS
✅ MMR retrieval: PASS
✅ Re-ranking: PASS

All tests passed!
```

---

## test_feature_store.py

### Purpose
Tests feature extraction and feature store functionality.

### Key Tests
- `test_delivery_features()`: Delivery feature extraction
- `test_revenue_features()`: Revenue feature extraction
- `test_temporal_features()`: Time-based features
- `test_caching()`: Feature caching mechanism
- `test_batch_processing()`: Large dataset processing

### Usage
```bash
python test_feature_store.py
```

### Expected Output
```
Testing delivery features...
✅ Extracted 1,234 features

Testing revenue features...
✅ Extracted revenue metrics

Testing temporal features...
✅ Extracted date/time features

All tests passed!
```

---

## test_intent_fix.py

### Purpose
Tests intent classification functionality and validates policy/data/mixed query classification.

### Key Tests
- `test_policy_queries()`: Policy question classification
- `test_data_queries()`: Data question classification
- `test_mixed_queries()`: Mixed question classification
- `test_confidence_scores()`: Classification confidence
- `test_domain_detection()`: Domain identification

### Test Cases
```python
# Policy queries
"What are severity levels?" → POLICY
"Define delay classification" → POLICY

# Data queries
"What is the delay rate?" → DATA
"Show delayed orders" → DATA

# Mixed queries
"Compare actual vs target" → MIXED
```

### Usage
```bash
python test_intent_fix.py
```

### Expected Output
```
Testing Policy Queries:
✅ "What are severity levels?" → POLICY (confidence: 0.75)
✅ "Define delay classification" → POLICY (confidence: 0.80)

Testing Data Queries:
✅ "What is delay rate?" → DATA (confidence: 0.50)
✅ "Show delayed orders" → DATA (confidence: 0.60)

Testing Mixed Queries:
✅ "Compare actual vs target" → MIXED (confidence: 0.70)

All classifications correct!
Success Rate: 100%
```

### Validation Metrics
- **Accuracy**: Classification correctness
- **Confidence**: Classification confidence scores
- **Coverage**: All query types tested
- **Consistency**: Repeated queries get same results

---

## test_main_rag_integration.py

### Purpose
Integration test for main application with RAG functionality.

### Key Tests
- `test_agentic_mode()`: Multi-agent system
- `test_enhanced_mode()`: Single LLM mode
- `test_rag_integration()`: RAG retrieval
- `test_mode_switching()`: UI mode toggle
- `test_document_upload()`: Document management

### Usage
```bash
python test_main_rag_integration.py
```

---

## test_rag_comprehensive.py

### Purpose
Comprehensive RAG testing including edge cases and error scenarios.

### Key Tests
- `test_basic_retrieval()`: Standard RAG retrieval
- `test_empty_query()`: Empty query handling
- `test_no_results()`: No matching documents
- `test_large_query()`: Long query text
- `test_special_characters()`: Query with special chars
- `test_index_corruption()`: Error handling

### Usage
```bash
python test_rag_comprehensive.py
```

---

## test_severity_levels.py

### Purpose
Tests severity level classification for delivery delays.

### Key Tests
- `test_critical_delay()`: >5 days delayed
- `test_major_delay()`: 3-5 days delayed
- `test_minor_delay()`: 1-2 days delayed
- `test_on_time()`: 0 days delayed
- `test_edge_cases()`: Boundary conditions

### Test Cases
```python
classify_delay_severity(6) → "Critical"
classify_delay_severity(4) → "Major"
classify_delay_severity(2) → "Minor"
classify_delay_severity(0) → "On-Time"
```

### Usage
```bash
python test_severity_levels.py
```

### Expected Output
```
Testing Severity Classification:
✅ 6 days → Critical
✅ 4 days → Major
✅ 2 days → Minor
✅ 0 days → On-Time

Edge Cases:
✅ 5 days → Major (boundary)
✅ 3 days → Major (boundary)
✅ 1 day → Minor (boundary)

All tests passed!
```

---

## Running All Tests

### Sequential
```bash
python test_enhanced_rag.py
python test_feature_store.py
python test_intent_fix.py
python test_main_rag_integration.py
python test_rag_comprehensive.py
python test_severity_levels.py
```

### With pytest (if configured)
```bash
pytest test_*.py -v
```

## Test Coverage

### Components Tested
- ✅ RAG retrieval (standard and enhanced)
- ✅ Intent classification
- ✅ Feature extraction
- ✅ Severity classification
- ✅ Main application integration
- ✅ Mode switching
- ✅ Document management

### Components Not Tested
- ❌ Gradio UI interaction (manual testing)
- ❌ External API calls (mocked)
- ❌ Database migrations
- ❌ Performance benchmarks (separate suite)

## Best Practices

1. **Run tests before deployment**
2. **Add tests for new features**
3. **Update tests when fixing bugs**
4. **Use test data, not production data**
5. **Clean up test artifacts after run**

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: |
          python test_intent_fix.py
          python test_severity_levels.py
          python test_rag_comprehensive.py
```

## Debugging Failed Tests

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Run Single Test
```python
# In test file
if __name__ == "__main__":
    test_policy_queries()  # Run just one test
```

### Check Test Data
```python
# Verify test data is correct
print(test_data)
assert len(test_data) > 0
```
