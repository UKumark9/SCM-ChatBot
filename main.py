"""
Main Application File - Python 3.14
"""

import sys
from pathlib import Path
import logging
import argparse
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import codecs
    # Only wrap if not already wrapped
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

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
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if GROQ_API_KEY:
    logger.info(f"✅ GROQ_API_KEY loaded successfully")
else:
    logger.warning("⚠️  GROQ_API_KEY not set! Enhanced AI features will be disabled.")


class SCMChatbotApp:
    """Main SCM Chatbot Application"""

    def __init__(self, use_enhanced: bool = True, use_rag: bool = True, show_agent: bool = True, use_agentic: bool = False, init_all_modes: bool = False):
        self.orders = None
        self.customers = None
        self.products = None
        self.order_items = None
        self.payments = None
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

        logger.info(f"Initializing SCM Chatbot (Enhanced: {use_enhanced}, RAG: {use_rag}, Show Agent: {show_agent}, Agentic: {use_agentic}, Init All Modes: {init_all_modes})...")
    
    def load_data(self, data_path: str = "train"):
        """Load and preprocess CSV data"""
        logger.info(f"Loading {data_path} data...")
    
        try:
            import pandas as pd
            from datetime import datetime

            base_path = Path(f"data/{data_path}")

            # Load raw data
            logger.info("Loading CSV files...")
            self.customers = pd.read_csv(base_path / "df_Customers.csv")
            self.orders = pd.read_csv(base_path / "df_Orders.csv")
            self.order_items = pd.read_csv(base_path / "df_OrderItems.csv")
            self.payments = pd.read_csv(base_path / "df_Payments.csv")
            self.products = pd.read_csv(base_path / "df_Products.csv")

            logger.info(f"✅ Loaded {len(self.customers):,} customers")
            logger.info(f"✅ Loaded {len(self.orders):,} orders")
            logger.info(f"✅ Loaded {len(self.order_items):,} order items")
            logger.info(f"✅ Loaded {len(self.payments):,} payments")
            logger.info(f"✅ Loaded {len(self.products):,} products")

            # CRITICAL: Check what columns we actually have
            logger.info(f"Order columns: {self.orders.columns.tolist()}")

            # Process orders data
            logger.info("Processing orders data...")

            # Find date columns (flexible naming)
            possible_date_cols = {
                'purchase': ['order_purchase_timestamp', 'purchase_timestamp', 'order_date'],
                'approved': ['order_approved_at', 'approved_at', 'approval_date'],
                'delivered_carrier': ['order_delivered_carrier_date', 'delivered_carrier_date', 'carrier_date'],
                'delivered_customer': ['order_delivered_timestamp', 'order_delivered_customer_date', 'delivered_customer_date', 'delivery_date', 'delivered_date'],
                'estimated': ['order_estimated_delivery_date', 'estimated_delivery_date', 'estimated_date']
            }

            # Map actual columns
            date_col_map = {}
            for key, possible_names in possible_date_cols.items():
                for name in possible_names:
                    if name in self.orders.columns:
                        date_col_map[key] = name
                        break
                    
            logger.info(f"Found date columns: {date_col_map}")

            # Convert date columns to datetime
            for key, col in date_col_map.items():
                self.orders[col] = pd.to_datetime(self.orders[col], errors='coerce')
                logger.info(f"  Converted {col} to datetime")

            # Calculate delivery delays (if we have the necessary columns)
            if 'delivered_customer' in date_col_map and 'estimated' in date_col_map:
                logger.info("Calculating delivery metrics...")

                delivered_col = date_col_map['delivered_customer']
                estimated_col = date_col_map['estimated']

                # Filter to delivered orders only
                delivered_mask = (
                    self.orders[delivered_col].notna() &
                    self.orders[estimated_col].notna()
                )

                delivered_orders = self.orders[delivered_mask].copy()

                # Calculate delay in days
                delivered_orders['delay_days'] = (
                    delivered_orders[delivered_col] - 
                    delivered_orders[estimated_col]
                ).dt.days

                # Mark as delayed if delivered AFTER estimated date
                delivered_orders['is_delayed'] = delivered_orders['delay_days'] > 0
                delivered_orders['is_on_time'] = delivered_orders['delay_days'] <= 0

                # Initialize in main dataframe
                self.orders['delay_days'] = 0
                self.orders['is_delayed'] = False
                self.orders['is_on_time'] = False

                # Update with calculated values
                self.orders.loc[delivered_mask, 'delay_days'] = delivered_orders['delay_days'].values
                self.orders.loc[delivered_mask, 'is_delayed'] = delivered_orders['is_delayed'].values
                self.orders.loc[delivered_mask, 'is_on_time'] = delivered_orders['is_on_time'].values

                # Log statistics
                total_delivered = delivered_orders.shape[0]
                total_delayed = delivered_orders['is_delayed'].sum()
                delay_rate = (total_delayed / total_delivered * 100) if total_delivered > 0 else 0

                logger.info(f"✅ Processed {total_delivered:,} delivered orders")
                logger.info(f"✅ Found {total_delayed:,} delayed orders ({delay_rate:.2f}% delay rate)")
            else:
                logger.warning("⚠️  Could not find delivery date columns - delay analysis will be limited")
                self.orders['delay_days'] = 0
                self.orders['is_delayed'] = False
                self.orders['is_on_time'] = True

            # Add time-based columns
            if 'purchase' in date_col_map:
                purchase_col = date_col_map['purchase']
                self.orders['order_month'] = self.orders[purchase_col].dt.to_period('M')
                self.orders['order_year'] = self.orders[purchase_col].dt.year

                # Rename for consistency with analytics
                if purchase_col != 'order_purchase_timestamp':
                    self.orders['order_purchase_timestamp'] = self.orders[purchase_col]

            # Merge customer state into orders
            logger.info("Merging customer data...")
            if 'customer_id' in self.orders.columns and 'customer_id' in self.customers.columns:
                # Find customer state column
                state_col = None
                for possible in ['customer_state', 'state', 'customer_uf']:
                    if possible in self.customers.columns:
                        state_col = possible
                        break
                    
                if state_col:
                    customer_info = self.customers[['customer_id', state_col]].drop_duplicates('customer_id')

                    # Rename to standard name
                    customer_info = customer_info.rename(columns={state_col: 'customer_state'})

                    # Merge
                    self.orders = self.orders.merge(
                        customer_info,
                        on='customer_id',
                        how='left',
                        suffixes=('', '_merged')
                    )

                    logger.info(f"✅ Merged customer state information")
                else:
                    logger.warning("⚠️  Could not find customer state column")
                    self.orders['customer_state'] = 'Unknown'

            logger.info("✅ Data processing complete")
            return True

        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def initialize_analytics(self):
        """Initialize analytics"""
        logger.info("Initializing analytics...")

        try:
            from tools.analytics import SCMAnalytics

            class DataWrapper:
                def __init__(self, orders, customers, products, order_items, payments):
                    self.orders = orders
                    self.customers = customers
                    self.products = products
                    self.order_items = order_items
                    self.payments = payments

                def get_summary_statistics(self):
                    """Get summary statistics for the report"""
                    return {
                        "total_orders": len(self.orders),
                        "total_customers": len(self.customers),
                        "total_products": len(self.products),
                        "total_order_items": len(self.order_items),
                        "total_payments": len(self.payments),
                        "date_range": {
                            "start": str(self.orders['order_purchase_timestamp'].min()),
                            "end": str(self.orders['order_purchase_timestamp'].max())
                        }
                    }

            data_wrapper = DataWrapper(
                self.orders, self.customers, self.products,
                self.order_items, self.payments
            )

            self.analytics = SCMAnalytics(data_wrapper)
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
                logger.info("📊 Continuing without RAG - agents will use analytics only")
                self.use_rag = False
                self.rag_module = None
                return False

            from enhanced_rag import create_enhanced_rag_system
            from pathlib import Path

            # Create enhanced RAG system with all improvements
            logger.info("🚀 Initializing Enhanced RAG System...")
            vector_db, self.rag_module = create_enhanced_rag_system(
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                enable_reranking=True,      # Cross-encoder re-ranking
                enable_compression=True,     # Contextual compression
                enable_hybrid=True           # Hybrid search (Vector + BM25)
            )

            # Load pre-built index with PDF policy documents
            vector_index_path = Path("data/vector_index")
            if vector_index_path.exists():
                logger.info(f"📚 Loading pre-built vector index from {vector_index_path}...")
                vector_db.load_index(str(vector_index_path))
                logger.info(f"✅ Loaded {len(vector_db.documents)} document chunks from policy PDFs")
                logger.info("✨ Enhanced RAG features enabled:")
                logger.info("   • Re-ranking with cross-encoder (+15-25% accuracy)")
                logger.info("   • Contextual compression (-30% token usage)")
                logger.info("   • Hybrid search (vector + BM25 keywords)")
                logger.info(f"   ⚙️  Similarity threshold: 2.0 (optimized)")
                logger.info(f"   📚 Agents will use Enhanced RAG + Analytics")
                return True
            else:
                logger.warning("⚠️  Vector index not found at data/vector_index")
                logger.warning("   Run: python rebuild_index.py or python vectorize_documents.py")
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
            from enhanced_chatbot import EnhancedSCMChatbot

            self.enhanced_chatbot = EnhancedSCMChatbot(
                analytics_engine=self.analytics,
                rag_module=self.rag_module if hasattr(self, 'rag_module') else None
            )

            logger.info("✅ Enhanced Chatbot initialized successfully")
            return True

        except ImportError as e:
            logger.error(f"Failed to import EnhancedSCMChatbot: {e}")
            logger.info("⚠️  Enhanced chatbot not available. Use --agentic flag for multi-agent mode")
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
            from agents.orchestrator import AgentOrchestrator

            # Create data wrapper
            class DataWrapper:
                def __init__(self, orders, customers, products, order_items, payments):
                    self.orders = orders
                    self.customers = customers
                    self.products = products
                    self.order_items = order_items
                    self.payments = payments

                def get_summary_statistics(self):
                    """Get summary statistics for the report"""
                    return {
                        "total_orders": len(self.orders),
                        "total_customers": len(self.customers),
                        "total_products": len(self.products),
                        "total_order_items": len(self.order_items),
                        "total_payments": len(self.payments),
                        "date_range": {
                            "start": str(self.orders['order_purchase_timestamp'].min()),
                            "end": str(self.orders['order_purchase_timestamp'].max())
                        }
                    }

            data_wrapper = DataWrapper(
                self.orders, self.customers, self.products,
                self.order_items, self.payments
            )

            self.orchestrator = AgentOrchestrator(
                analytics_engine=self.analytics,
                data_wrapper=data_wrapper,
                rag_module=self.rag_module,
                use_langchain=True,
                feature_store=self.feature_store
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
            from modules.feature_store import FeatureStore, MLFeatures

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
            from modules.document_manager import DocumentManager

            self.document_manager = DocumentManager(
                docs_path="data/business_docs",
                rag_module=self.rag_module
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
            from modules.data_connectors import DataPipeline

            self.data_pipeline = DataPipeline()

            # Add example connectors here if configured
            # Example:
            # from modules.data_connectors import PostgreSQLConnector
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
    
    def query(self, user_input: str, mode: str = None, use_rag: bool = True) -> str:
        """
        Process query with optional mode specification.

        Args:
            user_input: The user's query string
            mode: Optional mode specification ('agentic', 'enhanced').
                  If None, uses priority-based routing.
            use_rag: Whether to use RAG (only applies to enhanced mode)

        Returns:
            Response string
        """
        try:
            # Mode-based routing if mode is specified
            if mode:
                if mode == 'agentic':
                    if self.orchestrator:
                        return self.orchestrator.query(user_input, show_agent=self.show_agent)
                    else:
                        return "⚠️ Agentic mode not available. Orchestrator not initialized."
                elif mode == 'enhanced':
                    if self.enhanced_chatbot:
                        return self.enhanced_chatbot.query(user_input, show_agent=self.show_agent, use_rag=use_rag)
                    else:
                        return "⚠️ Enhanced mode not available. Enhanced chatbot not initialized."
                else:
                    return f"⚠️ Unknown mode: {mode}. Valid modes: 'agentic', 'enhanced'"

            # Priority-based routing (existing behavior)
            # Use orchestrator if available (priority)
            if self.orchestrator:
                return self.orchestrator.query(user_input, show_agent=self.show_agent)

            # Use enhanced chatbot if available
            if self.enhanced_chatbot:
                return self.enhanced_chatbot.query(user_input, show_agent=self.show_agent)

            # No mode available
            return """⚠️ No query processing mode available.

Please ensure either:
- **Agentic Mode** (Multi-Agent System) is initialized
- **Enhanced Mode** (LLM-powered) is initialized

Check your API keys and system configuration."""

        except Exception as e:
            logger.error(f"Query error: {e}")
            import traceback
            traceback.print_exc()
            return f"❌ Error: {str(e)}"


    def run_cli(self):
        """CLI mode"""
        print("\n" + "="*60)
        print("🤖 SCM Chatbot - Interactive CLI")
        print("="*60)
        print("\nType 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("\n🧑 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
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
        from ui import run_ui
        run_ui(self)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SCM Chatbot with Enhanced AI Capabilities')
    parser.add_argument('--mode', choices=['cli', 'ui'], default='ui',
                       help='Interface mode: cli or ui (default: ui)')
    parser.add_argument('--data', choices=['train', 'test'], default='train',
                       help='Dataset to use: train or test (default: train)')
    parser.add_argument('--agentic', action='store_true', default=False,
                       help='Use multi-agent agentic mode (takes priority over enhanced)')
    parser.add_argument('--enhanced', action='store_true', default=True,
                       help='Use enhanced chatbot with LLM (default: True)')
    parser.add_argument('--rag', action='store_true', default=True,
                       help='Enable RAG (Retrieval-Augmented Generation) for semantic search (default: True)')
    parser.add_argument('--no-rag', dest='rag', action='store_false',
                       help='Disable RAG and use analytics only')
    parser.add_argument('--hide-agent', action='store_true', default=False,
                       help='Hide agent execution info from responses')
    parser.add_argument('--init-all', action='store_true', default=False,
                       help='Initialize all modes (orchestrator + enhanced) for UI mode switching')

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
    if args.mode == 'ui' and not args.agentic:
        init_all_modes = True

    app = SCMChatbotApp(
        use_enhanced=use_enhanced,
        use_rag=args.rag,
        show_agent=show_agent,
        use_agentic=args.agentic,
        init_all_modes=init_all_modes
    )

    if not app.setup(data_path=args.data):
        print("\n❌ Setup failed!")
        return

    if args.mode == 'cli':
        app.run_cli()
    else:
        app.run_ui()


if __name__ == "__main__":
    main()