# Run the scripts to extract and process the data to the SQL database
PYTHON = python3
PIP = pip3
REQUIREMENTS = requirements.txt

run: 
	$(PYTHON) team_info.py
	$(PYTHON) summary.py
	$(PYTHON) scraping/record/record.py
	$(PYTHON) scraping/ojogo/ojogo.py
	$(PYTHON) scraping/abola/abola.py
	$(PYTHON) scraping/abola/abola_noticias_recentes.py

partial: 
	$(PYTHON) team_info.py
	$(PYTHON) summary.py
	$(PYTHON) scraping/record/record.py 2015
	$(PYTHON) scraping/abola/abola_noticias_recentes.py

install: 
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)


# Clean up
clean:
	rm -f ./scraping/db/merged_db.sqlite

# Help text
help:
	@echo "Simple Makefile that handles the data following the data pipeline defined:"
	@echo "  install - Install the requirements needed (please run this first)"
	@echo "  run     - Run the scripts to extract and process the data to the SQL database (may take some time)"
	@echo "  partial - Run the scripts (partially) to extract and process the data to the SQL database"
	@echo "  clean   - Deletes the SQL database generated"
	@echo "  help    - Display this help message"

