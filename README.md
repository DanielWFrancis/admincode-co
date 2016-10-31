# Corpus

This branch holds the Federal Register corpus, which serves documents from the Federal Register from 2000-on, using the bulk xml version from https://www.gpo.gov/fdsys/bulkdata/FR.

The index is a combination of year, month, day, the type of document, and the index for that type of document for that day. This means the 31st notice in the Federal Register on July 5, 2004 would have the index `(2004, 7, 5, 'notice' 31)`.

This corpus's `stream()` function takes as an argument a sequence of document types to be served. By default all types are served.
