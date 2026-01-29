"""Simple demo of agent info feature"""
import sys
import os

# Set encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Suppress startup emoji
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

from dotenv import load_dotenv
load_dotenv()

from main import SCMChatbotApp

sys.stdout = old_stdout

print("SCM Chatbot - Agent Info Demo")
print("="*70)
print()

# Initialize with agent info enabled
app = SCMChatbotApp(use_enhanced=True, use_rag=False, show_agent=True)
app.setup('train')

# Test query
query = "What is the delivery delay rate?"
print(f"Query: {query}")
print("="*70)
print()

response = app.query(query)
print(response)
print()
print("="*70)
