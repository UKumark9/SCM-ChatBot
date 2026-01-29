"""
Quick script to check which modes are initialized
"""
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent))

print("Checking SCM Chatbot Modes...")
print("="*60)

# Try to import and initialize
try:
    from main import SCMChatbotApp
    import os

    # Check API key
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print("✅ GROQ_API_KEY found")
    else:
        print("⚠️  GROQ_API_KEY not set (Enhanced and Agentic modes will be limited)")

    # Create app with init_all_modes
    print("\nInitializing with all modes...")
    app = SCMChatbotApp(
        use_enhanced=True,
        use_rag=False,
        show_agent=True,
        use_agentic=True,
        init_all_modes=True
    )

    # Check data
    print("\nAttempting data setup...")
    if app.setup(data_path="train"):
        print("✅ Data loaded successfully")
    else:
        print("❌ Data loading failed")

    # Check modes
    print("\n" + "="*60)
    print("Mode Availability Check:")
    print("="*60)

    if app.orchestrator:
        print("✅ Agentic Mode (Orchestrator): AVAILABLE")
    else:
        print("❌ Agentic Mode (Orchestrator): NOT AVAILABLE")

    if app.enhanced_chatbot:
        print("✅ Enhanced Mode (Chatbot): AVAILABLE")
    else:
        print("❌ Enhanced Mode (Chatbot): NOT AVAILABLE")

    if app.analytics:
        print("✅ Legacy Mode (Analytics): AVAILABLE")
    else:
        print("❌ Legacy Mode (Analytics): NOT AVAILABLE")

    print("\n" + "="*60)

    # Test a simple query if possible
    if app.analytics:
        print("\nTesting query routing...")
        try:
            response = app.query("What is the delivery delay rate?", mode="legacy")
            print("✅ Query execution works")
            print(f"\nSample response (first 100 chars):\n{response[:100]}...")
        except Exception as e:
            print(f"⚠️  Query test failed: {e}")

    print("\n" + "="*60)
    print("Summary:")
    print("="*60)

    available_modes = []
    if app.orchestrator:
        available_modes.append("Agentic")
    if app.enhanced_chatbot:
        available_modes.append("Enhanced")
    if app.analytics:
        available_modes.append("Legacy")

    if len(available_modes) == 3:
        print("✅ ALL MODES AVAILABLE - UI mode switching ready!")
    elif len(available_modes) > 0:
        print(f"⚠️  Partial initialization - Available: {', '.join(available_modes)}")
    else:
        print("❌ NO MODES AVAILABLE - Check errors above")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMissing dependencies? Run: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Initialization error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
