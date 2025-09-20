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
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                date_of_birth DATE,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                customer_tier VARCHAR(20) DEFAULT 'bronze' CHECK (customer_tier IN ('bronze', 'silver', 'gold', 'platinum')),
                UNIQUE(first_name, last_name)
            );
            """,
            
            # Addresses table
            """
            CREATE TABLE IF NOT EXISTS addresses (
                address_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                address_type VARCHAR(20) CHECK (address_type IN ('billing', 'shipping')) DEFAULT 'shipping',
                street_address VARCHAR(255) NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100),
                postal_code VARCHAR(20) NOT NULL,
                country VARCHAR(100) NOT NULL DEFAULT 'United States',
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(street_address, city, state, postal_code, country)
            );
            """,
            
            # Categories table
            """
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                parent_category_id INTEGER REFERENCES categories(category_id),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Products table
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                category_id INTEGER REFERENCES categories(category_id),
                sku VARCHAR(100) UNIQUE NOT NULL,
                price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
                cost_price DECIMAL(10, 2) CHECK (cost_price >= 0),
                weight DECIMAL(8, 2),
                dimensions VARCHAR(50),
                brand VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Inventory table
            """
            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
                quantity_available INTEGER NOT NULL DEFAULT 0 CHECK (quantity_available >= 0),
                quantity_reserved INTEGER NOT NULL DEFAULT 0 CHECK (quantity_reserved >= 0),
                reorder_level INTEGER DEFAULT 10,
                warehouse_location VARCHAR(100),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Orders table
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                order_number VARCHAR(50) UNIQUE NOT NULL,
                order_status VARCHAR(20) DEFAULT 'pending' CHECK (order_status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'returned')),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                shipping_address_id INTEGER REFERENCES addresses(address_id),
                billing_address_id INTEGER REFERENCES addresses(address_id),
                subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
                tax_amount DECIMAL(10, 2) DEFAULT 0 CHECK (tax_amount >= 0),
                shipping_cost DECIMAL(10, 2) DEFAULT 0 CHECK (shipping_cost >= 0),
                discount_amount DECIMAL(10, 2) DEFAULT 0 CHECK (discount_amount >= 0),
                total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
                payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded', 'partial_refund')),
                notes TEXT
            );
            """,
            
            # Order Items table
            """
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(product_id),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
                total_price DECIMAL(10, 2) NOT NULL CHECK (total_price >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Payments table
            """
            CREATE TABLE IF NOT EXISTS payments (
                payment_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                payment_method VARCHAR(20) CHECK (payment_method IN ('credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay', 'bank_transfer')),
                payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'cancelled', 'refunded')),
                amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
                transaction_id VARCHAR(255),
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processor_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Shipping table
            """
            CREATE TABLE IF NOT EXISTS shipping (
                shipping_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                carrier VARCHAR(100),
                tracking_number VARCHAR(255),
                shipping_method VARCHAR(50),
                estimated_delivery DATE,
                actual_delivery_date TIMESTAMP,
                shipping_status VARCHAR(20) DEFAULT 'pending' CHECK (shipping_status IN ('pending', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'failed_delivery', 'returned_to_sender')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Product Reviews table
            """
            CREATE TABLE IF NOT EXISTS reviews (
                review_id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(user_id),
                order_id INTEGER REFERENCES orders(order_id),
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                title VARCHAR(255),
                review_text TEXT,
                is_verified_purchase BOOLEAN DEFAULT FALSE,
                is_approved BOOLEAN DEFAULT FALSE,
                helpful_votes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Support Tickets table (for CS agents)
            """
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                order_id INTEGER REFERENCES orders(order_id),
                ticket_number VARCHAR(50) UNIQUE NOT NULL,
                subject VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
                status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')),
                category VARCHAR(50) CHECK (category IN ('order_inquiry', 'product_issue', 'shipping_problem', 'payment_issue', 'return_request', 'technical_support', 'other')),
                assigned_agent_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            );
            """,
            
            # Support Ticket Messages table
            """
            CREATE TABLE IF NOT EXISTS ticket_messages (
                message_id SERIAL PRIMARY KEY,
                ticket_id INTEGER REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
                sender_type VARCHAR(10) CHECK (sender_type IN ('customer', 'agent', 'system')),
                sender_id INTEGER,
                message_text TEXT NOT NULL,
                is_internal BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Returns table
            """
            CREATE TABLE IF NOT EXISTS returns (
                return_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                user_id INTEGER REFERENCES users(user_id),
                return_number VARCHAR(50) UNIQUE NOT NULL,
                return_reason VARCHAR(100) CHECK (return_reason IN ('defective', 'wrong_item', 'not_as_described', 'changed_mind', 'damaged_shipping', 'other')),
                return_status VARCHAR(20) DEFAULT 'requested' CHECK (return_status IN ('requested', 'approved', 'rejected', 'in_transit', 'received', 'processed', 'refunded')),
                return_type VARCHAR(20) DEFAULT 'refund' CHECK (return_type IN ('refund', 'exchange', 'store_credit')),
                requested_amount DECIMAL(10, 2) CHECK (requested_amount >= 0),
                approved_amount DECIMAL(10, 2) CHECK (approved_amount >= 0),
                return_shipping_cost DECIMAL(10, 2) DEFAULT 0,
                notes TEXT,
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            );
            """,
            
            # Return Items table
            """
            CREATE TABLE IF NOT EXISTS return_items (
                return_item_id SERIAL PRIMARY KEY,
                return_id INTEGER REFERENCES returns(return_id) ON DELETE CASCADE,
                order_item_id INTEGER REFERENCES order_items(order_item_id),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                reason VARCHAR(255),
                condition_received VARCHAR(50) CHECK (condition_received IN ('new', 'like_new', 'good', 'fair', 'poor', 'damaged')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Coupons/Discounts table
            """
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_id SERIAL PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                description VARCHAR(255),
                discount_type VARCHAR(20) CHECK (discount_type IN ('percentage', 'fixed_amount', 'free_shipping')),
                discount_value DECIMAL(10, 2) NOT NULL CHECK (discount_value >= 0),
                minimum_order_amount DECIMAL(10, 2) DEFAULT 0,
                usage_limit INTEGER,
                used_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                valid_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Order Coupons junction table
            """
            CREATE TABLE IF NOT EXISTS order_coupons (
                order_coupon_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
                coupon_id INTEGER REFERENCES coupons(coupon_id),
                discount_applied DECIMAL(10, 2) NOT NULL CHECK (discount_applied >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # ============= MULTI-AGENT SYSTEM TABLES =============
            
            # CS Agents table (for Authentication & Account Lookup Agents)
            """
            CREATE TABLE IF NOT EXISTS cs_agents (
                agent_id SERIAL PRIMARY KEY,
                agent_name VARCHAR(100) NOT NULL,
                agent_email VARCHAR(255) UNIQUE NOT NULL,
                agent_type VARCHAR(50) CHECK (agent_type IN ('human', 'ai', 'hybrid')),
                specialization VARCHAR(100), -- e.g., 'billing', 'technical', 'returns'
                max_concurrent_tickets INTEGER DEFAULT 10,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # User Sessions table (for Authentication Agent)
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address INET,
                user_agent TEXT,
                is_authenticated BOOLEAN DEFAULT FALSE,
                authentication_method VARCHAR(50), -- 'email', 'phone', 'sms_code', etc.
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Knowledge Base table (for Knowledge Retrieval Agent - RAG)
            """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                kb_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(100), -- 'faq', 'policy', 'troubleshooting', etc.
                tags TEXT[], -- Array of tags for better retrieval
                pinecone_vector_id VARCHAR(255), -- Reference to vector in Pinecone
                content_hash VARCHAR(64), -- SHA-256 hash for change detection
                source_url VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES cs_agents(agent_id)
            );
            """,
            
            # Conversation Sessions table (for Orchestrator Agent)
            """
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                conversation_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                ticket_id INTEGER REFERENCES support_tickets(ticket_id),
                session_token VARCHAR(255) REFERENCES user_sessions(session_token),
                conversation_state JSONB, -- Stores complex state data
                current_intent VARCHAR(100), -- 'order_inquiry', 'complaint', 'return_request', etc.
                confidence_score DECIMAL(3, 2), -- Intent detection confidence
                requires_human BOOLEAN DEFAULT FALSE,
                escalation_reason VARCHAR(255),
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP
            );
            """,
            
            # Agent Tasks table (for Orchestrator Agent routing)
            """
            CREATE TABLE IF NOT EXISTS agent_tasks (
                task_id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversation_sessions(conversation_id),
                agent_type VARCHAR(50) NOT NULL, -- 'authentication', 'lookup', 'knowledge', 'llm', 'sentiment', 'escalation'
                task_status VARCHAR(20) DEFAULT 'pending' CHECK (task_status IN ('pending', 'in_progress', 'completed', 'failed')),
                input_data JSONB,
                output_data JSONB,
                execution_time_ms INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT
            );
            """,
            
            # Sentiment Analysis table (for Sentiment Analysis Agent)
            """
            CREATE TABLE IF NOT EXISTS sentiment_analysis (
                sentiment_id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversation_sessions(conversation_id),
                message_id INTEGER REFERENCES ticket_messages(message_id),
                sentiment_score DECIMAL(3, 2), -- -1.0 to 1.0 (negative to positive)
                emotion VARCHAR(50), -- 'angry', 'frustrated', 'happy', 'neutral', 'confused'
                confidence DECIMAL(3, 2), -- 0.0 to 1.0
                keywords TEXT[], -- Emotional keywords detected
                escalation_trigger BOOLEAN DEFAULT FALSE,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Escalation Rules table (for Escalation Detection Agent)
            """
            CREATE TABLE IF NOT EXISTS escalation_rules (
                rule_id SERIAL PRIMARY KEY,
                rule_name VARCHAR(100) NOT NULL,
                condition_type VARCHAR(50), -- 'sentiment_threshold', 'keyword_match', 'response_time', 'complexity_score'
                condition_value JSONB, -- Flexible condition parameters
                priority_boost INTEGER DEFAULT 1, -- How much to increase ticket priority
                auto_assign_agent_id INTEGER REFERENCES cs_agents(agent_id),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Escalation Events table (for tracking escalations)
            """
            CREATE TABLE IF NOT EXISTS escalation_events (
                escalation_id SERIAL PRIMARY KEY,
                ticket_id INTEGER REFERENCES support_tickets(ticket_id),
                conversation_id INTEGER REFERENCES conversation_sessions(conversation_id),
                rule_id INTEGER REFERENCES escalation_rules(rule_id),
                trigger_reason VARCHAR(255),
                escalation_type VARCHAR(50), -- 'sentiment', 'complexity', 'timeout', 'manual'
                escalated_from_agent_id INTEGER REFERENCES cs_agents(agent_id),
                escalated_to_agent_id INTEGER REFERENCES cs_agents(agent_id),
                escalated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            );
            """,
            
            # Knowledge Usage Tracking (for LLM Response Agent)
            """
            CREATE TABLE IF NOT EXISTS knowledge_usage (
                usage_id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversation_sessions(conversation_id),
                kb_id INTEGER REFERENCES knowledge_base(kb_id),
                relevance_score DECIMAL(3, 2), -- How relevant was this knowledge
                was_helpful BOOLEAN, -- User feedback on helpfulness
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # LLM Response Tracking table
            """
            CREATE TABLE IF NOT EXISTS llm_responses (
                response_id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversation_sessions(conversation_id),
                message_id INTEGER REFERENCES ticket_messages(message_id),
                prompt_template VARCHAR(255),
                knowledge_sources INTEGER[], -- Array of kb_ids used
                response_time_ms INTEGER,
                token_count INTEGER,
                model_name VARCHAR(100),
                confidence_score DECIMAL(3, 2),
                was_accepted BOOLEAN, -- Whether customer accepted the response
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,

            # Create indexes for better performance
            """
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
            CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
            CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
            CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
            CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
            CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_id);
            CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
            CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
            CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
            
            -- Multi-agent system indexes
            CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user ON conversation_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_conversation_sessions_state ON conversation_sessions(requires_human);
            CREATE INDEX IF NOT EXISTS idx_agent_tasks_conversation ON agent_tasks(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(task_status);
            CREATE INDEX IF NOT EXISTS idx_sentiment_conversation ON sentiment_analysis(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_sentiment_escalation ON sentiment_analysis(escalation_trigger);
            CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);
            CREATE INDEX IF NOT EXISTS idx_knowledge_usage_conversation ON knowledge_usage(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_escalation_events_ticket ON escalation_events(ticket_id);
            CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
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