"""
Main Application File - Python 3.14
"""

import sys
import logging
import argparse
import os

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import codecs

    # Only wrap if not already wrapped
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()  # Load .env file from current directory
except ImportError:
    # dotenv not installed, will use system environment variables only
    pass

print("🚀 SCM Chatbot Starting...")

# Setup SIMPLE logging (no config.dictConfig needed)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Check for API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    logger.info(f"✅ GROQ_API_KEY loaded successfully")
else:
    logger.warning("⚠️  GROQ_API_KEY not set! Enhanced AI features will be disabled.")

# Import needs logging configured above first, hence the late import.
from scm_chatbot.core.dataset import SCMDataset  # noqa: E402


class SCMChatbotApp:
    """Main SCM Chatbot Application"""

    def __init__(
        self,
        use_enhanced: bool = True,
        use_rag: bool = True,
        show_agent: bool = True,
        use_agentic: bool = False,
        init_all_modes: bool = False,
    ):
        self.dataset = SCMDataset()
        self.analytics = None
        self.enhanced_chatbot = None
        self.orchestrator = None
        self.feature_store = None
        self.document_manager = None
        self.data_pipeline = None
        self.use_enhanced = use_enhanced
        self.use_rag = use_rag
        self.rag_module = None
        self.show_agent = show_agent
        self.use_agentic = use_agentic
        self.init_all_modes = init_all_modes

        logger.info(
            f"Initializing SCM Chatbot (Enhanced: {use_enhanced}, RAG: {use_rag}, Show Agent: {show_agent}, Agentic: {use_agentic}, Init All Modes: {init_all_modes})..."
        )

    # ── Backward-compatible access to the loaded data (ui.py and others read
    # these directly) - delegates to self.dataset, which now owns loading. ──
    @property
    def orders(self):
        return self.dataset.orders

    @property
    def customers(self):
        return self.dataset.customers

    @property
    def products(self):
        return self.dataset.products

    @property
    def order_items(self):
        return self.dataset.order_items

    @property
    def payments(self):
        return self.dataset.payments

    def load_data(self, data_path: str = "train") -> bool:
        """Load and preprocess CSV data (delegates to SCMDataset)"""
        return self.dataset.load(data_path)

    def initialize_analytics(self):
        """Initialize analytics"""
        logger.info("Initializing analytics...")

        try:
            from scm_chatbot.tools.analytics import SCMAnalytics

            self.analytics = SCMAnalytics(self.dataset)
            logger.info("✅ Analytics initialized")
            return True

        except Exception as e:
            logger.error(f"⚠️  Analytics failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    def initialize_rag(self):
        """Initialize RAG module for semantic search"""
        if not self.use_rag:
            logger.info("RAG module disabled by configuration")
            return False

        try:
            logger.info("🔄 Attempting to initialize RAG module...")

            # Check dependencies first
            try:
                from sentence_transformers import SentenceTransformer
                import faiss
            except ImportError as e:
                logger.warning("⚠️  RAG dependencies missing. Install with:")
                logger.warning("   pip install sentence-transformers faiss-cpu")
                logger.info(
                    "📊 Continuing without RAG - agents will use analytics only"
                )
                self.use_rag = False
                self.rag_module = None
                return False

            from scm_chatbot.rag.enhanced_rag import create_enhanced_rag_system
            from pathlib import Path

            # Create enhanced RAG system with all improvements
            logger.info("🚀 Initializing Enhanced RAG System...")
            vector_db, self.rag_module = create_enhanced_rag_system(
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                enable_reranking=True,  # Cross-encoder re-ranking
                enable_compression=True,  # Contextual compression
                enable_hybrid=True,  # Hybrid search (Vector + BM25)
            )

            # Load pre-built index with PDF policy documents
            vector_index_path = Path("data/vector_index")
            if vector_index_path.exists():
                logger.info(
                    f"📚 Loading pre-built vector index from {vector_index_path}..."
                )
                vector_db.load_index(str(vector_index_path))
                logger.info(
                    f"✅ Loaded {len(vector_db.documents)} document chunks from policy PDFs"
                )
                logger.info("✨ Enhanced RAG features enabled:")
                logger.info("   • Re-ranking with cross-encoder (+15-25% accuracy)")
                logger.info("   • Contextual compression (-30% token usage)")
                logger.info("   • Hybrid search (vector + BM25 keywords)")
                logger.info(f"   ⚙️  Similarity threshold: 2.0 (optimized)")
                logger.info(f"   📚 Agents will use Enhanced RAG + Analytics")
                return True
            else:
                logger.warning("⚠️  Vector index not found at data/vector_index")
                logger.warning(
                    "   Run: python rebuild_index.py or python vectorize_documents.py"
                )
                logger.info("📊 Continuing without RAG")
                self.use_rag = False
                self.rag_module = None
                return False

        except Exception as e:
            logger.warning(f"⚠️  RAG initialization failed: {e}")
            logger.info("📊 Continuing without RAG - agents will use analytics only")
            # Don't show full traceback unless debug mode
            import traceback

            logger.debug(traceback.format_exc())
            self.use_rag = False
            self.rag_module = None
            return False

    def initialize_enhanced_chatbot(self):
        """Initialize enhanced chatbot with LLM and RAG"""
        if not self.use_enhanced and not self.init_all_modes:
            logger.info("Enhanced chatbot disabled")
            return False

        try:
            logger.info("Initializing Enhanced Chatbot...")
            from scm_chatbot.llm.enhanced_chatbot import EnhancedSCMChatbot

            self.enhanced_chatbot = EnhancedSCMChatbot(
                analytics_engine=self.analytics,
                rag_module=self.rag_module if hasattr(self, "rag_module") else None,
            )

            logger.info("✅ Enhanced Chatbot initialized successfully")
            return True

        except ImportError as e:
            logger.error(f"Failed to import EnhancedSCMChatbot: {e}")
            logger.info(
                "⚠️  Enhanced chatbot not available. Use --agentic flag for multi-agent mode"
            )
            self.use_enhanced = False
            self.enhanced_chatbot = None
            return False
        except Exception as e:
            logger.error(f"Error initializing enhanced chatbot: {e}")
            self.use_enhanced = False
            self.enhanced_chatbot = None
            return False

    def initialize_orchestrator(self):
        """Initialize multi-agent orchestrator"""
        # Allow initialization if either use_agentic OR init_all_modes is True
        if not self.use_agentic and not self.init_all_modes:
            logger.info("Agentic mode disabled")
            return False

        try:
            logger.info("Initializing Agent Orchestrator...")
            from scm_chatbot.agents.orchestrator import AgentOrchestrator

            self.orchestrator = AgentOrchestrator(
                analytics_engine=self.analytics,
                data_wrapper=self.dataset,
                rag_module=self.rag_module,
                use_langchain=True,
                feature_store=self.feature_store,
            )

            logger.info("✅ Agent Orchestrator initialized")
            return True

        except Exception as e:
            logger.error(f"⚠️  Orchestrator initialization failed: {e}")
            import traceback

            traceback.print_exc()
            self.use_agentic = False
            return False

    def initialize_feature_store(self):
        """Initialize Feature Store for ML caching"""
        try:
            logger.info("Initializing Feature Store...")
            from scm_chatbot.services.feature_store import FeatureStore, MLFeatures

            self.feature_store = FeatureStore(use_redis=False)
            self.ml_features = MLFeatures(self.feature_store)

            logger.info("✅ Feature Store initialized")
            return True
        except Exception as e:
            logger.error(f"⚠️  Feature Store initialization failed: {e}")
            return False

    def initialize_document_manager(self):
        """Initialize Document Manager for business docs"""
        try:
            logger.info("Initializing Document Manager...")
            from scm_chatbot.services.document_manager import DocumentManager

            self.document_manager = DocumentManager(
                docs_path="data/business_docs", rag_module=self.rag_module
            )

            logger.info("✅ Document Manager initialized")
            return True
        except Exception as e:
            logger.error(f"⚠️  Document Manager initialization failed: {e}")
            return False

    def initialize_data_pipeline(self):
        """Initialize Data Pipeline connectors"""
        try:
            logger.info("Initializing Data Pipeline...")
            from scm_chatbot.services.data_connectors import DataPipeline

            self.data_pipeline = DataPipeline()

            # Add example connectors here if configured
            # Example:
            # from scm_chatbot.services.data_connectors import PostgreSQLConnector
            # pg = PostgreSQLConnector(host='localhost', ...)
            # self.data_pipeline.add_connector('postgresql', pg)

            logger.info("✅ Data Pipeline initialized (connectors need configuration)")
            return True
        except Exception as e:
            logger.error(f"⚠️  Data Pipeline initialization failed: {e}")
            return False

    def setup(self, data_path: str = "train"):
        """Setup application"""
        if not self.load_data(data_path):
            return False

        # Initialize analytics (required)
        if not self.initialize_analytics():
            logger.warning("Analytics initialization failed, continuing anyway...")

        # Initialize RAG if requested
        if self.use_rag:
            self.initialize_rag()

        # Initialize Feature Store
        self.initialize_feature_store()

        # Initialize Document Manager (depends on RAG)
        self.initialize_document_manager()

        # Initialize Data Pipeline
        self.initialize_data_pipeline()

        # If init_all_modes is True (for UI), initialize both orchestrator and enhanced chatbot
        if self.init_all_modes:
            logger.info("Initializing all modes for UI switching...")
            self.initialize_orchestrator()
            self.initialize_enhanced_chatbot()
        else:
            # Initialize agentic orchestrator if requested (takes priority)
            if self.use_agentic:
                self.initialize_orchestrator()
            # Otherwise initialize enhanced chatbot if requested
            elif self.use_enhanced:
                self.initialize_enhanced_chatbot()

        logger.info("✅ Setup complete!")
        return True

    def query_stream(self, user_input: str, mode: str = None, use_rag: bool = True):
        """
        Process query with optional mode specification, yielding response text
        incrementally as it becomes available.

        Enhanced mode streams token-by-token (via enhanced_chatbot.query_stream).
        Agentic mode has no incremental output to stream — the orchestrator must
        finish running its tools/agents before an answer exists — so it yields
        its full answer in one piece.

        Args:
            user_input: The user's query string
            mode: Optional mode specification ('agentic', 'enhanced').
                  If None, uses priority-based routing.
            use_rag: Whether to use RAG (only applies to enhanced mode)

        Yields:
            Response text chunks
        """
        try:
            # Mode-based routing if mode is specified; otherwise priority-based
            # routing (orchestrator first, then enhanced chatbot).
            target_mode = mode or (
                "agentic"
                if self.orchestrator
                else "enhanced" if self.enhanced_chatbot else None
            )

            if target_mode == "agentic":
                if self.orchestrator:
                    yield self.orchestrator.query(
                        user_input, show_agent=self.show_agent
                    )
                else:
                    yield "⚠️ Agentic mode not available. Orchestrator not initialized."
                return

            if target_mode == "enhanced":
                if self.enhanced_chatbot:
                    yield from self.enhanced_chatbot.query_stream(
                        user_input, show_agent=self.show_agent, use_rag=use_rag
                    )
                else:
                    yield "⚠️ Enhanced mode not available. Enhanced chatbot not initialized."
                return

            if mode:
                yield f"⚠️ Unknown mode: {mode}. Valid modes: 'agentic', 'enhanced'"
                return

            yield """⚠️ No query processing mode available.

Please ensure either:
- **Agentic Mode** (Multi-Agent System) is initialized
- **Enhanced Mode** (LLM-powered) is initialized

Check your API keys and system configuration."""

        except Exception as e:
            logger.error(f"Query error: {e}")
            import traceback

            traceback.print_exc()
            yield f"❌ Error: {str(e)}"

    def query(self, user_input: str, mode: str = None, use_rag: bool = True) -> str:
        """
        Process query with optional mode specification (non-streamed convenience
        wrapper around query_stream, kept for CLI/test callers).

        Returns:
            Response string
        """
        return "".join(self.query_stream(user_input, mode=mode, use_rag=use_rag))

    def run_cli(self):
        """CLI mode"""
        print("\n" + "=" * 60)
        print("🤖 SCM Chatbot - Interactive CLI")
        print("=" * 60)
        print("\nType 'quit' to exit\n")

        while True:
            try:
                user_input = input("\n🧑 You: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Goodbye!")
                    break

                if not user_input:
                    continue

                response = self.query(user_input)
                print(f"\n🤖 Bot:\n{response}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break

    def run_ui(self):
        """Launch the Gradio UI (delegated to ui module)"""
        from scm_chatbot.ui.ui import run_ui

        run_ui(self)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="SCM Chatbot with Enhanced AI Capabilities"
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "ui"],
        default="ui",
        help="Interface mode: cli or ui (default: ui)",
    )
    parser.add_argument(
        "--data",
        choices=["train", "test"],
        default="train",
        help="Dataset to use: train or test (default: train)",
    )
    parser.add_argument(
        "--agentic",
        action="store_true",
        default=False,
        help="Use multi-agent agentic mode (takes priority over enhanced)",
    )
    parser.add_argument(
        "--enhanced",
        action="store_true",
        default=True,
        help="Use enhanced chatbot with LLM (default: True)",
    )
    parser.add_argument(
        "--rag",
        action="store_true",
        default=True,
        help="Enable RAG (Retrieval-Augmented Generation) for semantic search (default: True)",
    )
    parser.add_argument(
        "--no-rag",
        dest="rag",
        action="store_false",
        help="Disable RAG and use analytics only",
    )
    parser.add_argument(
        "--hide-agent",
        action="store_true",
        default=False,
        help="Hide agent execution info from responses",
    )
    parser.add_argument(
        "--init-all",
        action="store_true",
        default=False,
        help="Initialize all modes (orchestrator + enhanced) for UI mode switching",
    )

    args = parser.parse_args()

    # Determine which mode to use
    use_enhanced = args.enhanced
    show_agent = not args.hide_agent

    # If agentic mode is enabled, disable enhanced mode
    if args.agentic:
        use_enhanced = False

    # Determine init_all_modes
    init_all_modes = args.init_all

    # If UI mode and no specific mode flags, automatically init all modes
    if args.mode == "ui" and not args.agentic:
        init_all_modes = True

    app = SCMChatbotApp(
        use_enhanced=use_enhanced,
        use_rag=args.rag,
        show_agent=show_agent,
        use_agentic=args.agentic,
        init_all_modes=init_all_modes,
    )

    if not app.setup(data_path=args.data):
        print("\n❌ Setup failed!")
        return

    if args.mode == "cli":
        app.run_cli()
    else:
        app.run_ui()


if __name__ == "__main__":
    main()
