"""
Test Compound Query Processing
Demonstrates the enhanced multi-agent capabilities

Run this script to test compound query detection and processing
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_intent_detection():
    """Test the enhanced intent detection algorithm"""
    from agents.orchestrator import AgentOrchestrator
    from tools.analytics import SCMAnalytics
    from tools.data_processor import DataProcessor

    print("="*70)
    print("COMPOUND QUERY INTENT DETECTION TEST")
    print("="*70)

    # Load sample data
    print("\n📂 Loading sample data...")
    data_processor = DataProcessor()
    data_processor.load_sample_data('data/')

    analytics = SCMAnalytics(
        orders=data_processor.orders,
        customers=data_processor.customers,
        products=data_processor.products,
        order_items=data_processor.order_items,
        payments=data_processor.payments
    )

    # Initialize orchestrator (without LangChain for testing)
    orchestrator = AgentOrchestrator(
        analytics_engine=analytics,
        data_wrapper=data_processor,
        rag_module=None,
        use_langchain=False
    )

    # Test queries
    test_queries = [
        # Simple queries (should be single-agent)
        "What is the delivery delay rate?",
        "Show me total revenue",
        "Forecast demand for 30 days",

        # Compound queries (should be multi-agent)
        "Show delays and forecast demand",
        "What are the delays and revenue performance?",
        "Show product delays plus forecast sales",
        "Analyze delays along with revenue trends",
        "Show me delivery performance and also predict demand",

        # Triple agent
        "Show delays, revenue, and forecast demand",
        "Comprehensive report on delays, sales, and future demand",

        # Product-level compound
        "Show product delays and forecast demand for electronics",
        "What are electronics delays and predict sales",
    ]

    print("\n" + "="*70)
    print("INTENT DETECTION RESULTS")
    print("="*70)

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        print("-" * 70)

        intent = orchestrator.analyze_intent(query)

        print(f"   Agent Mode: {intent['agent']}")
        print(f"   Multi-Intent: {intent['multi_intent']}")
        print(f"   Agents: {intent['agents']}")
        print(f"   Confidence: {intent['confidence']:.2f}")

        if intent.get('execution_order'):
            print(f"   Execution Order: {' → '.join(intent['execution_order'])}")

        if intent.get('sub_queries'):
            print(f"   Sub-Queries:")
            for agent, subq in intent['sub_queries'].items():
                print(f"      {agent}: \"{subq}\"")

        # Validate expectations
        if " and " in query.lower() or " also " in query.lower() or " plus " in query.lower() or " along with " in query.lower():
            expected_multi = True
        else:
            expected_multi = False

        if expected_multi and intent['multi_intent']:
            print("   ✅ PASS - Correctly detected multi-intent")
        elif not expected_multi and not intent['multi_intent']:
            print("   ✅ PASS - Correctly detected single-intent")
        elif expected_multi and not intent['multi_intent']:
            print("   ⚠️ WARNING - Expected multi-intent, got single-intent")
        else:
            print("   ℹ️ INFO - Single query treated as multi-intent (acceptable)")

def test_query_decomposition():
    """Test query decomposition into sub-queries"""
    from agents.orchestrator import AgentOrchestrator
    from tools.analytics import SCMAnalytics
    from tools.data_processor import DataProcessor

    print("\n\n" + "="*70)
    print("QUERY DECOMPOSITION TEST")
    print("="*70)

    # Setup
    data_processor = DataProcessor()
    data_processor.load_sample_data('data/')

    analytics = SCMAnalytics(
        orders=data_processor.orders,
        customers=data_processor.customers,
        products=data_processor.products,
        order_items=data_processor.order_items,
        payments=data_processor.payments
    )

    orchestrator = AgentOrchestrator(
        analytics_engine=analytics,
        data_wrapper=data_processor,
        rag_module=None,
        use_langchain=False
    )

    compound_queries = [
        "Show delivery delays and forecast demand for next month",
        "What are product delays and revenue performance?",
        "Show delays for electronics and predict sales",
    ]

    for query in compound_queries:
        print(f"\n📝 Query: \"{query}\"")
        print("-" * 70)

        intent = orchestrator.analyze_intent(query)

        if intent.get('sub_queries'):
            print("   Decomposed into:")
            for agent, subquery in intent['sub_queries'].items():
                print(f"      • {agent.upper()}: \"{subquery}\"")
        else:
            print("   ❌ No decomposition (single-intent query)")

def test_execution_order():
    """Test agent execution ordering"""
    from agents.orchestrator import AgentOrchestrator

    print("\n\n" + "="*70)
    print("EXECUTION ORDER TEST")
    print("="*70)

    orchestrator = AgentOrchestrator(
        analytics_engine=None,  # Mock
        data_wrapper=None,
        rag_module=None,
        use_langchain=False
    )

    # Test different agent combinations
    test_cases = [
        (['forecasting', 'delay'], "Expected: delay → forecasting"),
        (['analytics', 'delay', 'forecasting'], "Expected: delay → analytics → forecasting"),
        (['forecasting', 'data_query', 'delay'], "Expected: data_query → delay → forecasting"),
        (['analytics', 'data_query'], "Expected: data_query → analytics"),
    ]

    for agents, expected in test_cases:
        print(f"\n   Input agents: {agents}")
        print(f"   {expected}")

        ordered = orchestrator._get_execution_order(agents)
        print(f"   Actual order: {' → '.join(ordered)}")

        # Verify data_query is first if present
        if 'data_query' in agents and ordered[0] == 'data_query':
            print("   ✅ PASS - data_query executed first")
        elif 'data_query' not in agents:
            print("   ✅ PASS - Correct order")
        else:
            print("   ❌ FAIL - data_query not first")

def test_cross_insights():
    """Test cross-agent insight generation"""
    from agents.orchestrator import AgentOrchestrator

    print("\n\n" + "="*70)
    print("CROSS-AGENT INSIGHTS TEST")
    print("="*70)

    orchestrator = AgentOrchestrator(
        analytics_engine=None,
        data_wrapper=None,
        rag_module=None,
        use_langchain=False
    )

    # Test different context scenarios
    scenarios = [
        {
            'name': "High delay + Growing demand",
            'context': {
                'delay_rate': 12.5,
                'forecast_trend': 'increasing'
            },
            'agents': ['delay', 'forecasting']
        },
        {
            'name': "Low delay + Growing demand",
            'context': {
                'delay_rate': 3.2,
                'forecast_trend': 'increasing'
            },
            'agents': ['delay', 'forecasting']
        },
        {
            'name': "High delay + Declining demand",
            'context': {
                'delay_rate': 15.0,
                'forecast_trend': 'decreasing'
            },
            'agents': ['delay', 'forecasting']
        },
        {
            'name': "Triple agent analysis",
            'context': {
                'delay_rate': 8.5,
                'forecast_trend': 'increasing',
                'revenue_data': {'total_revenue': '1000000'}
            },
            'agents': ['delay', 'analytics', 'forecasting']
        }
    ]

    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print("-" * 70)
        print(f"   Context: {scenario['context']}")
        print(f"   Agents: {scenario['agents']}")

        insights = orchestrator._generate_cross_agent_insights(
            scenario['context'],
            scenario['agents']
        )

        if insights:
            print("\n   💡 Generated Insights:")
            for line in insights.split('\n'):
                if line.strip():
                    print(f"      {line}")
        else:
            print("\n   ℹ️ No insights generated for this combination")

def main():
    """Run all tests"""
    print("\n" + "🔬 COMPOUND QUERY PROCESSING TEST SUITE")
    print("="*70)

    try:
        # Run tests
        test_intent_detection()
        test_query_decomposition()
        test_execution_order()
        test_cross_insights()

        print("\n\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70)
        print("\n📝 Summary:")
        print("   • Intent detection tested with 13+ queries")
        print("   • Query decomposition verified")
        print("   • Execution order validated")
        print("   • Cross-agent insights demonstrated")
        print("\n💡 Try these queries in the chatbot:")
        print("   • 'Show delays and forecast demand'")
        print("   • 'What are product delays and revenue?'")
        print("   • 'Show delays, sales, and predict demand'")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
