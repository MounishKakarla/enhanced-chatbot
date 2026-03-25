from sqlalchemy import create_engine, text
import pandas as pd

def get_engine(db_type, user, password, host, database, port):
    if db_type == "mysql":
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    elif db_type == "postgres":
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    else:
        url = f"sqlite:///{database}"
    return create_engine(url)

def run_query(engine, query):
    """Executes code and returns a DataFrame. Strictly Read-Only."""
    try:
        # Security: Basic check for modification keywords
        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE"]
        if any(word in query.upper() for word in forbidden):
            return "❌ Error: Modification queries are not allowed in this chatbot."

        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            return df
    except Exception as e:
        return f"❌ SQL Error: {str(e)}"

def get_schema_preview(engine):
    from sqlalchemy import inspect
    inspector = inspect(engine)
    schema = {}
    for table in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns(table)]
        schema[table] = columns
    return schema