VERBOSE_FLAG=-v # Set to empty for less info or to -q for quiet
END_YEAR=2015

# Canned recipe for targets that only need to have their timestamps updated
# when their dependencies change, such as a library dependency for a script

define lib
touch $@
endef

# Canned recipe for running python scripts. The script should be the first
# dependency, and the other dependencies should be positional arguments in
# order. The script should allow you to specify the output file with a -o flag,
# and to specify verbosity with a -v flag. If you're using a Python script that
# doesn't follow this pattern, you can of course write the recipe directly.
# Additional explicit arguments can be added after the canned recipe if needed.

define py
python $^ -o $@ $(VERBOSE_FLAG)
endef

DATABANK = /path/to/databank

# List all the csv files you want as part of the metadata here
METADATA = data/wordcount.csv data/restrictions.csv data/agencies.csv

data/metadata.csv: scripts/combine_datasets.py $(METADATA)
	$(py)

data/wordcount.csv: scripts/count_words.py driver.py
	$(py)


data/restrictions.csv: scripts/count_restrictions.py driver.py
	$(py)

scripts/count_restrictions.py: scripts/count_matches.py
	$(lib)

data/agencies.csv: scripts/create_agency_map.py $(DATABANK)/parsed_ptar.csv data/index.csv
	$(py)

extracts: data/metadata.csv
	rm -rf $@
	mkdir $@
	$(eval DATE=$(shell python -c "import datetime; print(str(datetime.datetime.now()).split()[0])"))
	python -m zipfile -c $@/cfr_metadata_$(DATE).zip $^
	python -c "import pandas as pd; pd.read_csv('$^').drop(['title', 'part'], axis='columns').groupby(['year', 'department', 'agency']).sum().loc[1997:].to_csv('$@/regulatory_restrictions_by_year_and_agency_$(DATE).csv')"
	python -c "import pandas as pd; pd.read_csv('$^', index_col=['year', 'title', 'part']).groupby(level='year').sum().loc[1997:].to_csv('$@/cfr_totals_by_year_$(DATE).csv')"

driver.py: data/index.csv
	$(lib)

data/index.csv: scripts/create_index.py data/clean
	$(py)

data/clean: scripts/parse_cfr_html.py data/downloaded
	$(py)

data/downloaded: scripts/download.py
	$(py) --end_year $(END_YEAR)
