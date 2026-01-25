"""
User Interface Module for SCM Chatbot
Provides Gradio-based chat interface
"""

import logging
from typing import List, Tuple, Optional
from datetime import datetime
import time

try:
    import gradio as gr
except ImportError:
    logging.warning("Gradio not installed")

logger = logging.getLogger(__name__)


class ChatbotUI:
    """Gradio-based chat interface for SCM Chatbot"""
    
    def __init__(self, agent_orchestrator, performance_monitor, config: dict):
        self.agent = agent_orchestrator
        self.performance_monitor = performance_monitor
        self.config = config
        self.conversation_history = []
    
    def chat(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """Process chat message and return response"""
        try:
            start_time = time.time()
            
            # Validate message
            if not message or not message.strip():
                return "", history
            
            # Get response from agent
            response = self.agent.process_query(message)
            
            # Record performance
            duration = time.time() - start_time
            self.performance_monitor.record_query_time(duration)
            
            # Update history
            history.append((message, response))
            
            # Keep only last N messages
            max_history = self.config.get('max_conversation_length', 20)
            if len(history) > max_history:
                history = history[-max_history:]
            
            return "", history
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            self.performance_monitor.record_error()
            error_message = "I apologize, but I encountered an error processing your request. Please try again."
            history.append((message, error_message))
            return "", history
    
    def clear_chat(self):
        """Clear chat history"""
        self.conversation_history = []
        return []
    
    def get_examples(self) -> List[str]:
        """Get example queries for users"""
        return [
            "What is the current delivery delay rate?",
            "Show me the revenue trends",
            "Which products are selling best?",
            "Analyze customer behavior patterns",
            "Forecast demand for the next 30 days",
            "What are the inventory risks?",
            "Evaluate supplier performance",
            "Generate a comprehensive report"
        ]
    
    def create_interface(self) -> gr.Blocks:
        """Create Gradio interface"""
        
        with gr.Blocks(
            title=self.config.get('name', 'SCM Chatbot'),
            theme=gr.themes.Soft()
        ) as interface:
            
            # Header
            gr.Markdown(f"""
            # 🤖 {self.config.get('name', 'SCM Intelligent Chatbot')}
            ### AI-Powered Supply Chain Management Assistant
            
            Ask questions about:
            - 📦 Delivery delays and performance
            - 💰 Revenue and sales analytics
            - 🏪 Product performance
            - 👥 Customer behavior
            - 📈 Demand forecasting
            - 📊 Inventory management
            - 🏭 Supplier evaluation
            """)
            
            # Chat interface
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                show_label=True,
                avatar_images=("👤", "🤖")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask anything about your supply chain...",
                    scale=4,
                    show_label=False
                )
                submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            # Example questions
            gr.Examples(
                examples=self.get_examples(),
                inputs=msg,
                label="Example Questions"
            )
            
            # Info section
            with gr.Accordion("ℹ️ System Information", open=False):
                gr.Markdown("""
                ### How to Use:
                1. Type your question in the text box
                2. Click "Send" or press Enter
                3. The AI will analyze your query and provide insights
                
                ### Available Features:
                - Real-time delivery delay analysis
                - Revenue and sales trend tracking
                - Product performance metrics
                - Customer behavior analysis
                - Demand forecasting with ML
                - Inventory risk assessment
                - Supplier performance evaluation
                - Comprehensive SCM reports
                
                ### Tips:
                - Be specific in your questions for better results
                - You can ask follow-up questions
                - Use example questions as templates
                """)
            
            # Performance metrics (optional)
            with gr.Accordion("📊 Performance Metrics", open=False):
                metrics_display = gr.JSON(label="System Metrics")
                refresh_metrics_btn = gr.Button("Refresh Metrics")
                
                def get_performance_metrics():
                    return self.performance_monitor.get_metrics()
                
                refresh_metrics_btn.click(
                    fn=get_performance_metrics,
                    outputs=metrics_display
                )
            
            # Event handlers
            submit_btn.click(
                fn=self.chat,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            )
            
            msg.submit(
                fn=self.chat,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            )
            
            clear_btn.click(
                fn=lambda: [],
                outputs=chatbot
            )
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface"""
        interface = self.create_interface()
        
        launch_config = {
            "share": self.config.get('share', False),
            "server_port": self.config.get('port', 7860),
            "server_name": "0.0.0.0"
        }
        launch_config.update(kwargs)
        
        logger.info(f"Launching UI on port {launch_config['server_port']}")
        interface.launch(**launch_config)


def create_streamlit_ui(agent_orchestrator, performance_monitor):
    """Alternative Streamlit UI (for reference)"""
    try:
        import streamlit as st
        
        st.set_page_config(
            page_title="SCM Chatbot",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 Supply Chain Management Chatbot")
        st.markdown("### AI-Powered Analytics and Insights")
        
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your supply chain..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response
            with st.chat_message("assistant"):
                start_time = time.time()
                response = agent_orchestrator.process_query(prompt)
                duration = time.time() - start_time
                performance_monitor.record_query_time(duration)
                
                st.markdown(response)
            
            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Sidebar with metrics
        with st.sidebar:
            st.header("System Metrics")
            metrics = performance_monitor.get_metrics()
            st.metric("Total Queries", metrics['total_queries'])
            st.metric("Avg Response Time", f"{metrics['average_response_time']:.2f}s")
            st.metric("Error Rate", f"{metrics['error_rate']:.2f}%")
            
            if st.button("Clear Chat"):
                st.session_state.messages = []
                st.rerun()
        
    except ImportError:
        logger.warning("Streamlit not installed")
        return None
