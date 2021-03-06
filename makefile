# prep: data/clean data/metadata.csv driver.py
VERBOSE_FLAG=-v # Set to empty for less info or to -q for quiet

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

METADATA = data/wordcount.csv data/restrictions.csv

.PHONY: data/clean data/raw

data/metadata.csv: scripts/combine_datasets.py $(METADATA)
	$(py)

data/wordcount.csv: scripts/count_words.py driver.py
	$(py)

data/restrictions.csv: scripts/count_restrictions.py driver.py
	$(py)

scripts/count_restrictions.py: scripts/count_matches.py
	$(lib)

driver.py: data/clean
	$(lib)

data/clean: scripts/clean.py data/raw
	python $^ $@

data/raw: scripts/download.py
	python $^ $@
#
# #legislative_code/clean: scripts/download_legislative_code.py
# #	python $^ $@





# constitution/clean: scripts/download_constitution.py
# 	python $^ $@
