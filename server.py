import os
import subprocess
from fastmcp import FastMCP, tool
from dotenv import load_dotenv

load_dotenv()

class SpannerDDL(FastMCP):
    def _execute_gcloud_command(self, ddl_statement: str) -> str:
        \"\"\"Executes a gcloud command.\"\"\"
        try:
            project = os.environ.get("SPANNER_PROJECT")
            instance = os.environ.get("SPANNER_INSTANCE")
            database = os.environ.get("SPANNER_DATABASE")

            if not all([project, instance, database]):
                return "Error: Missing required environment variables (SPANNER_PROJECT, SPANNER_INSTANCE, SPANNER_DATABASE)."

            result = subprocess.run(
                [
                    "gcloud",
                    "spanner",
                    "databases",
                    "ddl",
                    "update",
                    database,
                    f"--instance={instance}",
                    f"--project={project}",
                    f"--ddl={ddl_statement}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return "DDL statement executed successfully."
        except subprocess.CalledProcessError as e:
            return f"Error executing DDL statement: {e.stderr}"
        except FileNotFoundError:
            return "gcloud could not be found. Please install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install"

    @tool
    def execute_ddl(self, ddl_statement: str) -> str:
        \"\"\"Executes a DDL statement on the Spanner database.

        Args:
            ddl_statement: The DDL statement to execute.

        Returns:
            The result of the DDL statement execution.
        \"\"\"
        destructive_keywords = ["DROP", "TRUNCATE"]
        is_destructive = any(keyword in ddl_statement.upper() for keyword in destructive_keywords)
        if "ALTER TABLE" in ddl_statement.upper() and "DROP COLUMN" in ddl_statement.upper():
            is_destructive = True

        if is_destructive:
            return f"The DDL statement '{ddl_statement}' is destructive. Please confirm the execution by calling the `confirm_ddl` tool."
        else:
            return self._execute_gcloud_command(ddl_statement)

    @tool
    def confirm_ddl(self, ddl_statement: str) -> str:
        \"\"\"Confirms and executes a destructive DDL statement.

        Args:
            ddl_statement: The destructive DDL statement to execute.

        Returns:
            The result of the DDL statement execution.
        \"\"\"
        return self._execute_gcloud_command(ddl_statement)

if __name__ == "__main__":
    SpannerDDL.main()
