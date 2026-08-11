"""
Data Connectors - Real-time Data Pipeline Integration
Supports PostgreSQL, MongoDB, MySQL, and streaming data sources
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Base class for database connectors"""

    def __init__(self, connection_config: Dict[str, str]):
        self.config = connection_config
        self.connection = None
        self.connected = False

    def connect(self):
        """Establish database connection"""
        raise NotImplementedError

    def disconnect(self):
        """Close database connection"""
        raise NotImplementedError

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        raise NotImplementedError

    def test_connection(self) -> bool:
        """Test database connectivity"""
        raise NotImplementedError


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL database connector"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        config = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        super().__init__(config)
        self.engine = None

    def connect(self):
        """Connect to PostgreSQL"""
        try:
            import psycopg2
            from sqlalchemy import create_engine

            # Create connection string
            conn_string = f"postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}"

            self.engine = create_engine(conn_string)
            self.connection = self.engine.connect()
            self.connected = True

            logger.info(f"✅ Connected to PostgreSQL: {self.config['database']}")
            return True

        except ImportError:
            logger.error("PostgreSQL dependencies not installed. Run: pip install psycopg2-binary sqlalchemy")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False

    def disconnect(self):
        """Disconnect from PostgreSQL"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        self.connected = False
        logger.info("Disconnected from PostgreSQL")

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query"""
        if not self.connected:
            self.connect()

        try:
            df = pd.read_sql(query, self.engine)
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return pd.DataFrame()

    def test_connection(self) -> bool:
        """Test connection"""
        try:
            if not self.connected:
                return self.connect()

            # Simple test query
            result = self.execute_query("SELECT 1")
            return not result.empty
        except:
            return False

    def get_tables(self) -> List[str]:
        """List all tables in database"""
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        """
        df = self.execute_query(query)
        return df['table_name'].tolist() if not df.empty else []

    def get_realtime_orders(self, last_n_hours: int = 24) -> pd.DataFrame:
        """Get recent orders for real-time analytics"""
        query = f"""
        SELECT * FROM orders
        WHERE order_purchase_timestamp >= NOW() - INTERVAL '{last_n_hours} hours'
        ORDER BY order_purchase_timestamp DESC
        """
        return self.execute_query(query)


class MongoDBConnector:
    """MongoDB connector for NoSQL data"""

    def __init__(self, host: str, port: int, database: str, collection: str,
                 username: Optional[str] = None, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.database = database
        self.collection_name = collection
        self.username = username
        self.password = password
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False

    def connect(self):
        """Connect to MongoDB"""
        try:
            from pymongo import MongoClient

            # Build connection string
            if self.username and self.password:
                conn_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"
            else:
                conn_string = f"mongodb://{self.host}:{self.port}/"

            self.client = MongoClient(conn_string)
            self.db = self.client[self.database]
            self.collection = self.db[self.collection_name]
            self.connected = True

            logger.info(f"✅ Connected to MongoDB: {self.database}.{self.collection_name}")
            return True

        except ImportError:
            logger.error("MongoDB dependencies not installed. Run: pip install pymongo")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
        self.connected = False
        logger.info("Disconnected from MongoDB")

    def find(self, query: Dict, limit: int = 1000) -> pd.DataFrame:
        """Execute find query and return DataFrame"""
        if not self.connected:
            self.connect()

        try:
            cursor = self.collection.find(query).limit(limit)
            data = list(cursor)
            df = pd.DataFrame(data)
            logger.info(f"Query executed successfully, returned {len(df)} documents")
            return df
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return pd.DataFrame()

    def aggregate(self, pipeline: List[Dict]) -> pd.DataFrame:
        """Execute aggregation pipeline"""
        if not self.connected:
            self.connect()

        try:
            cursor = self.collection.aggregate(pipeline)
            data = list(cursor)
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            return pd.DataFrame()

    def test_connection(self) -> bool:
        """Test connection"""
        try:
            if not self.connected:
                return self.connect()
            # Test by counting documents
            count = self.collection.count_documents({})
            logger.info(f"MongoDB test successful, found {count} documents")
            return True
        except:
            return False


class MySQLConnector(DatabaseConnector):
    """MySQL database connector"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        config = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        super().__init__(config)
        self.engine = None

    def connect(self):
        """Connect to MySQL"""
        try:
            import pymysql
            from sqlalchemy import create_engine

            # Create connection string
            conn_string = f"mysql+pymysql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}"

            self.engine = create_engine(conn_string)
            self.connection = self.engine.connect()
            self.connected = True

            logger.info(f"✅ Connected to MySQL: {self.config['database']}")
            return True

        except ImportError:
            logger.error("MySQL dependencies not installed. Run: pip install pymysql sqlalchemy")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            return False

    def disconnect(self):
        """Disconnect from MySQL"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        self.connected = False
        logger.info("Disconnected from MySQL")

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query"""
        if not self.connected:
            self.connect()

        try:
            df = pd.read_sql(query, self.engine)
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return pd.DataFrame()

    def test_connection(self) -> bool:
        """Test connection"""
        try:
            if not self.connected:
                return self.connect()
            result = self.execute_query("SELECT 1")
            return not result.empty
        except:
            return False


class DataPipeline:
    """
    Data Pipeline Manager
    Orchestrates data ingestion from multiple sources
    """

    def __init__(self):
        self.connectors = {}
        self.last_sync = {}

    def add_connector(self, name: str, connector: DatabaseConnector):
        """Add a data connector"""
        self.connectors[name] = connector
        logger.info(f"Added connector: {name}")

    def test_all_connections(self) -> Dict[str, bool]:
        """Test all registered connectors"""
        results = {}
        for name, connector in self.connectors.items():
            try:
                results[name] = connector.test_connection()
            except Exception as e:
                logger.error(f"Test failed for {name}: {e}")
                results[name] = False
        return results

    def sync_data(self, source: str, query: str, target_table: str = None) -> pd.DataFrame:
        """
        Sync data from source to local storage

        Args:
            source: Connector name
            query: SQL query or MongoDB query dict
            target_table: Optional table name to save to CSV

        Returns:
            DataFrame with synced data
        """
        if source not in self.connectors:
            logger.error(f"Connector not found: {source}")
            return pd.DataFrame()

        connector = self.connectors[source]

        try:
            # Execute query based on connector type
            if isinstance(connector, MongoDBConnector):
                df = connector.find(query)
            else:
                df = connector.execute_query(query)

            # Save to CSV if target specified
            if target_table and not df.empty:
                csv_path = f"data/pipeline/{target_table}.csv"
                Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(csv_path, index=False)
                logger.info(f"✅ Saved {len(df)} rows to {csv_path}")

            # Update last sync time
            self.last_sync[source] = datetime.now().isoformat()

            return df

        except Exception as e:
            logger.error(f"Data sync failed for {source}: {e}")
            return pd.DataFrame()

    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        status = {
            'total_connectors': len(self.connectors),
            'connectors': {},
            'last_sync': self.last_sync
        }

        for name, connector in self.connectors.items():
            status['connectors'][name] = {
                'connected': connector.connected if hasattr(connector, 'connected') else False,
                'type': connector.__class__.__name__
            }

        return status


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = DataPipeline()

    # Add PostgreSQL connector (example)
    # pg_connector = PostgreSQLConnector(
    #     host='localhost',
    #     port=5432,
    #     database='scm_db',
    #     user='user',
    #     password='password'
    # )
    # pipeline.add_connector('postgresql', pg_connector)

    # Add MongoDB connector (example)
    # mongo_connector = MongoDBConnector(
    #     host='localhost',
    #     port=27017,
    #     database='scm_db',
    #     collection='orders'
    # )
    # pipeline.add_connector('mongodb', mongo_connector)

    # Test connections
    # results = pipeline.test_all_connections()
    # print(f"Connection tests: {results}")

    # Sync data
    # df = pipeline.sync_data('postgresql', 'SELECT * FROM orders LIMIT 100', 'recent_orders')
    # print(f"Synced {len(df)} rows")

    print("Data Pipeline initialized (connectors need configuration)")
