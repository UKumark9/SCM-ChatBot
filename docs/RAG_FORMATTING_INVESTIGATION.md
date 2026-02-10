# RAG Formatting Investigation - Enhanced vs Agentic Mode

**Date**: February 10, 2026
**Issue**: Why doesn't Enhanced mode show formatted policy document boxes (📚)?

---

## TL;DR - Key Finding

✅ **Enhanced mode IS using RAG correctly** - the policy information is retrieved and used
❌ **Enhanced mode does NOT format it visibly** - the LLM incorporates it into natural language response
✅ **Agentic mode shows formatted boxes** - uses UIFormatter for explicit document display

---

## Investigation

### How RAG Works in Enhanced Mode

**File**: `enhanced_chatbot.py:348-354`

```python
# Format RAG context if available
context_section = ""
if context and len(context.strip()) > 0:
    context_section = f"""Policy Documents (from knowledge base):
{context}

---
"""

# This context is included in the LLM prompt
user_prompt = self.templates.ANSWER_WITH_CONTEXT.format(
    context_section=context_section,  # ← RAG context here
    analytics_data=analytics_summary,
    query=query
)
```

**What happens**:
1. RAG retrieves policy documents
2. Context is included in LLM prompt
3. LLM reads the policy documents
4. **LLM weaves policy info into natural language response**
5. User sees LLM's response (policy info is "invisible" but used)

### Example: "Compare actual delay rate with target policy"

**What the LLM receives in its prompt**:
```
Policy Documents (from knowledge base):
[Policy document about on-time delivery target >95%, delay rate <5%]

---

Analytics Results:
{
  "delay_rate_percentage": 6.28,
  "on_time_rate": 93.72,
  ...
}

User Question: Compare actual delay rate with target policy
```

**What the LLM generates**:
```
Actual delay rate: 6.28%
Target delay rate: < 5%  ← (Extracted from policy docs)
On-Time Delivery Rate target: > 95%  ← (Extracted from policy docs)
Actual on-time rate: 93.72%
```

**What the user sees**:
- Just the LLM's natural language response
- **NO visible policy document boxes**
- But the information IS from the policy documents

---

## How RAG Works in Agentic Mode

**File**: `agents/delay_agent.py` (and other agents)

```python
# Retrieve RAG context
if should_use_rag and self.rag_module:
    rag_context = self.rag_module.retrieve_context(user_query)

    # Format it with UIFormatter for display
    formatted_context = UIFormatter.format_rag_context(rag_context)

    # Append to response
    response += formatted_context
```

**What happens**:
1. RAG retrieves policy documents
2. **UIFormatter creates formatted boxes**
3. Formatted boxes appended to response
4. User sees explicit policy document sections

### Example Output from Agentic Mode:

```
The delivery delay rate is 6.28%.

### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Performance Standards Policy | Relevance: 0.85

Target Performance:
• On-Time Delivery Rate: >95%
• Maximum Acceptable Delay: <5%

───────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────
🤖 Agent: Delay Agent | 📚 RAG | ✅ Success
────────────────────────────────────────────────────────────
```

---

## Why the Difference?

### Enhanced Mode Design Philosophy
- **Single LLM approach**: Let the LLM synthesize all information
- **Natural language**: Policy info woven into response
- **Seamless integration**: User doesn't see "seams" between sources
- **Pros**: More natural, conversational responses
- **Cons**: Less transparency about what came from policy docs

### Agentic Mode Design Philosophy
- **Explicit sources**: Show where information comes from
- **Transparency**: User sees policy documents directly
- **Modular**: Separate data, policy, and agent reasoning
- **Pros**: Clear source attribution, better for auditing
- **Cons**: More "mechanical" looking responses

---

## Evidence That RAG IS Working in Enhanced Mode

### Test Query: "Compare actual delay rate with target policy"

**With RAG Enabled**:
```
Actual delay rate: 6.28%
Target delay rate: < 5%  ✅ (Found this from RAG!)
Average delay duration: 10.45 days, exceeding target of < 2.5 days  ✅ (Found from RAG!)
On-Time Delivery Rate target: > 95%  ✅ (Found from RAG!)
```

**Without RAG Enabled**:
```
Actual delay rate: 6.28%
Target policy not specified in analytics results  ❌ (Cannot find without RAG!)
```

**Conclusion**: RAG IS working - the LLM found and used policy targets, it just doesn't show them in formatted boxes.

---

## Should We Change This?

### Option 1: Keep Current Behavior (Recommended)
**Pros**:
- More natural, conversational responses
- Cleaner appearance
- LLM synthesis often better than raw documents
- Works as designed

**Cons**:
- Less transparency
- Users may not realize policy docs were used

### Option 2: Add Formatted Document Boxes to Enhanced Mode
**Changes Required**:
```python
# In enhanced_chatbot.py, after LLM response:
if context and use_rag:
    from ui_formatter import UIFormatter
    formatted_context = UIFormatter.format_rag_context(context)
    response_text += "\n\n" + formatted_context
```

**Pros**:
- More transparency
- Consistent with Agentic mode
- Clear source attribution

**Cons**:
- Duplicates information (LLM already incorporated it)
- Makes responses longer
- Less natural appearance

### Option 3: Add Toggle for "Show Source Documents"
**Implementation**:
```python
def query(self, user_query: str, show_agent: bool = True,
          use_rag: bool = True, show_source_docs: bool = False):
    # ... existing code ...

    if show_source_docs and context:
        formatted_context = UIFormatter.format_rag_context(context)
        response_text += "\n\n" + formatted_context
```

**Pros**:
- Best of both worlds
- User can choose transparency level
- Maintains natural responses by default

**Cons**:
- Additional UI complexity
- Another configuration option

---

## Recommendations

### For Current Implementation: ✅ Keep As-Is
**Reasons**:
1. RAG is working correctly (proven by output differences)
2. Natural language responses are more user-friendly
3. LLM synthesis is often better than raw document text
4. Consistent with "Enhanced" mode philosophy (single LLM synthesizes everything)

### For Documentation: 📝 Update Examples
1. Update documentation to show actual output format
2. Explain that policy info is incorporated, not displayed separately
3. Add comparison: Enhanced vs Agentic formatting styles

### For Future Enhancement: 💡 Consider Option 3
- Add optional "Show Source Documents" toggle
- Default: OFF (natural responses)
- When ON: Append formatted policy boxes
- Best for users who need audit trails

---

## Comparison Table: Enhanced vs Agentic RAG Display

| Aspect | Enhanced Mode | Agentic Mode |
|--------|---------------|--------------|
| **RAG Retrieval** | ✅ Yes | ✅ Yes |
| **Policy Used** | ✅ Yes | ✅ Yes |
| **Display Method** | Natural language synthesis | Formatted document boxes |
| **Transparency** | Low (invisible integration) | High (explicit sections) |
| **Appearance** | Natural, conversational | Structured, formal |
| **Source Attribution** | Implicit | Explicit |
| **User Experience** | Seamless | Informative |
| **Best For** | General users | Auditing, verification |

---

## Testing Confirmation

### Test 1: Policy Question
**Query**: "What are severity levels?"

**Enhanced WITH RAG**: ✅ Returns correct policy definitions (from RAG)
**Enhanced WITHOUT RAG**: ❌ Says "cannot confirm without policy"

**Verdict**: RAG working correctly ✅

### Test 2: Policy Comparison
**Query**: "Compare actual delay rate with target policy"

**Enhanced WITH RAG**: ✅ Shows targets < 5%, > 95% (from RAG)
**Enhanced WITHOUT RAG**: ❌ Says "Target policy not specified"

**Verdict**: RAG working correctly ✅

### Test 3: Data Question
**Query**: "What is the delay rate?"

**Enhanced WITH RAG**: Shows 6.28% + optional policy context
**Enhanced WITHOUT RAG**: Shows 6.28% only

**Verdict**: Both work, RAG adds context ✅

---

## Conclusion

### Summary
✅ **RAG is working correctly in Enhanced mode**
✅ **Policy information is retrieved and used**
✅ **LLM incorporates policy into natural language response**
❌ **Policy documents are NOT formatted in visible boxes** (by design)
🎯 **This is intentional** - Enhanced mode philosophy is seamless LLM synthesis

### For Users
- **Enhanced mode WITH RAG**: Policy info is used but not shown separately
- **Agentic mode WITH RAG**: Policy info shown in formatted boxes
- Both are correct, just different presentation styles

### For Developers
- No bug or issue
- Working as designed
- If you want formatted boxes in Enhanced mode, implement Option 2 or 3 above

---

**End of Investigation Report**
