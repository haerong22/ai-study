from dotenv import load_dotenv
import os
import psycopg
from psycopg import Error

load_dotenv()

DATABASE_URL=os.getenv("SUPABASE_DATABASE_URL")


def create_ecommerce_tables():
    connection = None
    cursor = None
    try:
        connection = psycopg.connect(DATABASE_URL)
        print("Connection successful!")
        cursor = connection.cursor()

        commands = [
            # Users/Customers table
            """
            COMMENT ON TABLE users IS 'Customer and user account information including personal details, registration data, and customer tier status';

COMMENT ON TABLE addresses IS 'Customer billing and shipping addresses with address type classification and default address settings';

COMMENT ON TABLE categories IS 'Product categorization hierarchy with support for parent-child category relationships';

COMMENT ON TABLE products IS 'Product catalog containing all available items with pricing, descriptions, SKUs, and inventory details';

COMMENT ON TABLE inventory IS 'Current stock levels, warehouse locations, and inventory management data for all products';

COMMENT ON TABLE orders IS 'Customer purchase orders containing order details, status, pricing, and payment information';

COMMENT ON TABLE order_items IS 'Individual line items within orders specifying products, quantities, and pricing at time of purchase';

COMMENT ON TABLE payments IS 'Payment processing records including transaction details, payment methods, and payment status tracking';

COMMENT ON TABLE shipping IS 'Shipping and delivery tracking information including carriers, tracking numbers, and delivery status';

COMMENT ON TABLE reviews IS 'Customer product reviews and ratings with verification status and helpful vote tracking';

-- Customer Support Tables
COMMENT ON TABLE support_tickets IS 'Customer service requests and support cases with priority, status, and agent assignment tracking';

COMMENT ON TABLE ticket_messages IS 'Messages and communications within support tickets from customers, agents, and system notifications';

-- Returns and Refunds
COMMENT ON TABLE returns IS 'Product return and refund requests with reason codes, status tracking, and financial details';

COMMENT ON TABLE return_items IS 'Individual items being returned with quantities, reasons, and condition assessment';

-- Promotions and Discounts
COMMENT ON TABLE coupons IS 'Discount codes and promotional offers with usage limits, validity periods, and discount values';

COMMENT ON TABLE order_coupons IS 'Junction table linking orders to applied discount coupons with actual discount amounts';

-- Multi-Agent System Tables
COMMENT ON TABLE cs_agents IS 'Customer service agents including both human and AI agents with specializations and capacity settings';

COMMENT ON TABLE user_sessions IS 'User authentication sessions with security tracking, device information, and session state management';

COMMENT ON TABLE knowledge_base IS 'Knowledge base content for customer support including FAQs, policies, and troubleshooting guides';

COMMENT ON TABLE conversation_sessions IS 'AI conversation state and orchestration data for multi-agent customer support interactions';

COMMENT ON TABLE agent_tasks IS 'Task routing and execution tracking for AI agents with input/output data and performance metrics';

COMMENT ON TABLE sentiment_analysis IS 'Sentiment analysis results of customer interactions with emotion detection and escalation triggers';

COMMENT ON TABLE escalation_rules IS 'Rules and conditions for automatically escalating support tickets based on various criteria';

COMMENT ON TABLE escalation_events IS 'Historical record of ticket escalations including trigger reasons and agent reassignments';

COMMENT ON TABLE knowledge_usage IS 'Tracking of knowledge base article usage and effectiveness in customer support interactions';

COMMENT ON TABLE llm_responses IS 'Large Language Model response generation tracking with performance metrics and quality assessment';

-- =====================================================
-- OPTIONAL: COLUMN DESCRIPTIONS FOR KEY TABLES
-- =====================================================

-- Users table key columns
COMMENT ON COLUMN users.customer_tier IS 'Customer loyalty tier affecting discounts and benefits (bronze, silver, gold, platinum)';
COMMENT ON COLUMN users.is_active IS 'Whether the user account is currently active and able to place orders';

-- Products table key columns
COMMENT ON COLUMN products.sku IS 'Stock Keeping Unit - unique product identifier for inventory management';
COMMENT ON COLUMN products.price IS 'Current selling price in USD';
COMMENT ON COLUMN products.cost_price IS 'Internal cost price for profit margin calculations';

-- Orders table key columns
COMMENT ON COLUMN orders.order_status IS 'Current status of the order in fulfillment process';
COMMENT ON COLUMN orders.payment_status IS 'Current payment processing status';
COMMENT ON COLUMN orders.total_amount IS 'Final order total including tax, shipping, and discounts';

-- Order Items table key columns
COMMENT ON COLUMN order_items.unit_price IS 'Price per unit at the time of order (may differ from current product price)';
COMMENT ON COLUMN order_items.total_price IS 'Total price for this line item (unit_price × quantity)';

-- Support Tickets key columns
COMMENT ON COLUMN support_tickets.priority IS 'Ticket priority level affecting response time expectations';
COMMENT ON COLUMN support_tickets.category IS 'Classification of the support request type';

-- Inventory key columns
COMMENT ON COLUMN inventory.quantity_available IS 'Current stock available for sale';
COMMENT ON COLUMN inventory.quantity_reserved IS 'Stock reserved for pending orders but not yet shipped';
COMMENT ON COLUMN inventory.reorder_level IS 'Minimum stock level that triggers reorder notifications';

-- Multi-agent system key columns
COMMENT ON COLUMN conversation_sessions.current_intent IS 'Detected customer intent for routing to appropriate agent';
COMMENT ON COLUMN conversation_sessions.confidence_score IS 'AI confidence level in intent detection (0.0 to 1.0)';
COMMENT ON COLUMN conversation_sessions.requires_human IS 'Flag indicating if human agent intervention is needed';

COMMENT ON COLUMN sentiment_analysis.sentiment_score IS 'Sentiment score from -1.0 (very negative) to 1.0 (very positive)';
COMMENT ON COLUMN sentiment_analysis.escalation_trigger IS 'Whether this sentiment analysis triggered an escalation';

COMMENT ON COLUMN agent_tasks.agent_type IS 'Type of AI agent handling this task (authentication, lookup, knowledge, etc.)';
COMMENT ON COLUMN agent_tasks.execution_time_ms IS 'Task execution time in milliseconds for performance monitoring';

            """
        ]

        # Execute commands
        for command in commands:
            cursor.execute(command)

        connection.commit()
        print("All tables created successfully.")

    except (Exception, Error) as error:
        print(f"Error during database setup: {error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Connection closed.")

if __name__ == "__main__":
    create_ecommerce_tables()