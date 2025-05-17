# db_plugins/sqlite_adapter.py
from sqlalchemy import create_engine, inspect, text
from .base_adapter import BaseDBAdapter

class SQLiteAdapter(BaseDBAdapter):
    def __init__(self, db):
        self.db = db

    def get_schema_metadata(self):
        engine = create_engine(self.db)
        inspector = inspect(engine)
        schema_info = {}
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            schema_info[table_name] = {
                "columns": [
                    {"name": col["name"], "type": str(col["type"]), "nullable": col["nullable"]}
                    for col in columns
                ],
                "foreign_keys": foreign_keys,
                "primary_key": inspector.get_pk_constraint(table_name)["constrained_columns"]
            }
        return schema_info

    def execute_query(self, query: str):
        """
        Executes the generated SQL query stored in state.query and returns the result.
        """
        if not query:
            return {"result": "No query found to execute."}

        try:
            engine = create_engine(self.db)
            with engine.connect() as connection:
                result_proxy = connection.execute(text(query))
                rows = result_proxy.fetchall()
                column_names = result_proxy.keys()

                # Format results as a list of dictionaries
                results = [dict(zip(column_names, row)) for row in rows]
                return {
                    "result": results
                }
        except Exception as e:
            return {
                "result": f"Query execution failed: {str(e)}"
            }
        

# # Optional test block
# if __name__ == "__main__":

#     # Step 2: Initialize adapter and agent
#     sqlite_adapter = SQLiteAdapter("sqlite:///northwind.db")
#     schema_metadata = sqlite_adapter.get_schema_metadata()
#     print(schema_metadata)
