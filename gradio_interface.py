"""
Gradio UI Interface
Web-based interface for the SCM Chatbot
"""

import gradio as gr
from typing import Any
import logging

logger = logging.getLogger(__name__)


def create_gradio_interface(app: Any) -> gr.Blocks:
    """
    Create Gradio interface for the chatbot
    
    Args:
        app: SCMChatbotApp instance
        
    Returns:
        Gradio Blocks interface
    """
    
    def chat_function(message: str, history: list) -> str:
        """Process chat message"""
        if not message.strip():
            return "Please enter a message."
        
        try:
            response = app.query(message)
            return response
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_statistics():
        """Get overall statistics"""
        try:
            stats = []
            
            # Delay stats
            if 'delay' in app.analytics_tools:
                delay_data = app.analytics_tools['delay'].get_delay_summary()
                stats.append(f"📦 **Delivery Performance**")
                stats.append(f"- Total Orders: {delay_data['total_orders']:,}")
                stats.append(f"- Delay Rate: {delay_data['delay_rate_percent']}%")
                stats.append(f"- Avg Delay: {delay_data['avg_delay_days']} days\n")
            
            # Revenue stats
            if 'revenue' in app.analytics_tools:
                revenue_data = app.analytics_tools['revenue'].get_revenue_summary()
                stats.append(f"💰 **Revenue**")
                stats.append(f"- Total: ${revenue_data['total_revenue']:,.2f}")
                stats.append(f"- Avg Order: ${revenue_data['avg_order_value']:,.2f}\n")
            
            # Inventory stats
            if 'inventory' in app.analytics_tools:
                inv_data = app.analytics_tools['inventory'].get_inventory_summary()
                stats.append(f"📊 **Inventory**")
                stats.append(f"- Total Products: {inv_data['total_products']:,}")
                stats.append(f"- Low Stock: {inv_data['low_stock_items']:,} ({inv_data['low_stock_rate_percent']}%)\n")
            
            return "\n".join(stats)
        except Exception as e:
            return f"Error loading statistics: {str(e)}"
    
    # Create interface
    with gr.Blocks(title="SCM Chatbot", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("""
        # 🤖 AI-Powered Supply Chain Management Chatbot
        ### Ask questions about orders, inventory, suppliers, and logistics
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Chat",
                    height=500,
                    show_label=True,
                    avatar_images=(None, "🤖")
                )
                
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Ask me about delays, revenue, inventory, forecasts...",
                    lines=2
                )
                
                with gr.Row():
                    submit = gr.Button("Send", variant="primary")
                    clear = gr.Button("Clear Chat")
                
                gr.Markdown("""
                ### Example Questions:
                - What is the delivery delay rate?
                - Show me revenue statistics
                - How many products are low in stock?
                - What is the demand forecast for next month?
                - Tell me about supplier performance
                """)
            
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Quick Stats")
                stats_display = gr.Markdown(get_statistics())
                refresh_stats = gr.Button("🔄 Refresh Stats")
        
        # Event handlers
        def user(user_message, history):
            return "", history + [[user_message, None]]
        
        def bot(history):
            user_message = history[-1][0]
            bot_message = chat_function(user_message, history)
            history[-1][1] = bot_message
            return history
        
        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        submit.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)
        refresh_stats.click(get_statistics, None, stats_display)
    
    return interface


def create_simple_interface(app: Any) -> gr.Interface:
    """Create simple Gradio interface (alternative)"""
    
    def chat(message):
        return app.query(message)
    
    interface = gr.Interface(
        fn=chat,
        inputs=gr.Textbox(
            label="Your Question",
            placeholder="Ask about delays, revenue, inventory...",
            lines=3
        ),
        outputs=gr.Textbox(label="Response", lines=10),
        title="🤖 AI Supply Chain Management Chatbot",
        description="Ask questions about supply chain operations, analytics, and insights",
        examples=[
            ["What is the delivery delay rate?"],
            ["Show me revenue statistics"],
            ["How many low stock items do we have?"],
            ["What's the demand forecast?"],
            ["Tell me about supplier performance"]
        ],
        theme=gr.themes.Soft()
    )
    
    return interface
