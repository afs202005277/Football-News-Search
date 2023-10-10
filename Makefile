# Run the scripts to extract and process the data to the SQL database
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
REQUIREMENTS = requirements.txt

run: $(VENV)/bin/activate
	$(PYTHON) team_info.py
	$(PYTHON) summary.py

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt


# Clean up
clean:
	sudo rm -f ./scraping/db/db.sqlite

# Help text
help:
	@echo "Simple Makefile that handles the data following the data pipeline defined:"
	@echo "  run     - Run the scripts to extract and process the data to the SQL database (may take some time)"
	@echo "  partial - Run the scripts (partially) to extract and process the data to the SQL database"
	@echo "  clean   - Deletes the SQL database generated"
	@echo "  help    - Display this help message"

