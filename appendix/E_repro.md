## Appendix E. Reproducibility

Every number in the paper and in this appendix is produced by Python scripts from sources that
require no API keys: FRED and NBER Macrohistory (`fredgraph.csv`), the IMF's International
Financial Statistics via DBnomics, the central banks of Brazil (SGS) and Peru (BCRPData), the
BCRA and Argentina's official data service, and hand-digitised series — Sargent's (1982) tables
for Austria, Hungary, Germany and Poland, Sachs's (1986) for Bolivia, the *Federal Reserve
Bulletin* tables for Belgium and Italy, Bogetić et al. (2022) for Yugoslavia and Hanke–Kwok
(2009) for Zimbabwe — each stored as a plain-text file with its source, page numbers, splices
and any printing errata documented in the file header.

One script per test regenerates the figures and the tables in this appendix directly from those
sources; the census is a single machine-readable file whose row-level notes record the
verification trail. The full repository — data, digitised files, estimation code and this
appendix's generator — is available from the author, and a public version is in preparation.
