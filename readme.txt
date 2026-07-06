Agentic AI Demo
================

This project is a SQL assistant that uses a local MySQL database and an external AI gateway.

For a fresh Windows setup in PowerShell, follow the steps below.

Prerequisites
-------------
- Windows PowerShell 5.1 or PowerShell 7+
- Python 3.12
- MySQL Server running locally
- A Tiger AI Gateway API key

1) Open PowerShell in the project folder
---------------------------------------
cd "<path to your project folder>"

2) Create and activate a virtual environment
-------------------------------------------
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

3) Install Python dependencies
------------------------------
python -m pip install --upgrade pip
pip install uv
uv sync

4) Create a local environment file
----------------------------------
Create a file named .env in the project root with the following values:

TIGER_AI_GATEWAY_API_KEY=xxxxx
MYSQL_PASSWORD=Root@123

5) Make sure MySQL is ready
---------------------------
- Start your MySQL server.
- Start -> Services -> Look for Mysql**

Note: Contact Tiger IThelpdesk for any issues.

6) Create retail database & Load the sample data into MySQL
----------------------------------
uv run .\database\load_data.py

7) Run the CLI
--------------
uv run .\src\app.py

You will see:
ask> 

Type a question and press Enter. Example:
ask> Show me the top 5 products by sales

To exit the CLI, type quit or exit.
