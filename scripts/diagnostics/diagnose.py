"""
Diagnostic script to see exactly what's happening during initialization
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

print("="*70)
print("🔍 SCM Chatbot Diagnostic")
print("="*70)

print("\n[1] Python Environment")
print("-"*70)
print(f"Python Version: {sys.version}")
print(f"Python Path: {sys.executable}")
print(f"Current Directory: {Path.cwd()}")

print("\n[2] Checking Dependencies")
print("-"*70)
dependencies = [
    'pandas', 'numpy', 'langchain', 'langchain_groq',
    'langchain_core', 'groq', 'gradio'
]

missing = []
for dep in dependencies:
    try:
        __import__(dep)
        print(f"✅ {dep}")
    except ImportError:
        print(f"❌ {dep} - NOT INSTALLED")
        missing.append(dep)

if missing:
    print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
    print(f"Install with: pip install {' '.join(missing)}")
else:
    print("\n✅ All core dependencies installed!")

print("\n[3] Checking Data Files")
print("-"*70)
data_path = Path("data/train")
if data_path.exists():
    files = list(data_path.glob("*.csv"))
    if files:
        print(f"✅ Found {len(files)} CSV files in data/train/")
        for f in files:
            print(f"   - {f.name}")
    else:
        print("❌ No CSV files in data/train/")
else:
    print(f"❌ data/train/ directory not found at: {data_path.absolute()}")

print("\n[4] Checking Environment Variables")
print("-"*70)
import os
if os.getenv('GROQ_API_KEY'):
    key = os.getenv('GROQ_API_KEY')
    print(f"✅ GROQ_API_KEY is set ({key[:10]}...)")
else:
    print("⚠️  GROQ_API_KEY not set (LLM features will be limited)")

print("\n[5] Testing Initialization")
print("-"*70)

if not missing:
    try:
        print("Attempting to initialize app with all modes...")
        from main import SCMChatbotApp

        app = SCMChatbotApp(
            use_enhanced=True,
            use_rag=False,
            show_agent=True,
            use_agentic=True,
            init_all_modes=True
        )

        print("✅ App object created")
        print(f"   - init_all_modes: {app.init_all_modes}")
        print(f"   - use_agentic: {app.use_agentic}")
        print(f"   - use_enhanced: {app.use_enhanced}")

        # Try setup
        print("\nAttempting data setup...")
        success = app.setup(data_path="train")

        print(f"\n{'='*70}")
        print("FINAL STATUS:")
        print(f"{'='*70}")
        print(f"Setup Success: {success}")
        print(f"Orchestrator Initialized: {app.orchestrator is not None}")
        print(f"Enhanced Chatbot Initialized: {app.enhanced_chatbot is not None}")
        print(f"Analytics Initialized: {app.analytics is not None}")

        if app.orchestrator:
            print("\n✅ ORCHESTRATOR IS AVAILABLE!")
        else:
            print("\n❌ ORCHESTRATOR FAILED TO INITIALIZE")
            print("Check the error messages above for details")

    except Exception as e:
        print(f"\n❌ Initialization failed with error:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  Skipping initialization test due to missing dependencies")

print("\n" + "="*70)
print("Diagnostic complete. Review the results above.")
print("="*70)
