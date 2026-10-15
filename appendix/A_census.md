## Appendix A. The census: coding protocol and full table

**Universe.** All stabilisations of high inflation — sustained rates above roughly 20 per cent a
year — between 1921 and 2025. The pre-1995 universe is fixed by the prior literature (Sargent
1982, 1984; Dornbusch and Fischer 1986; Kiguel and Liviatan 1992; Végh 1992; Reinhart and Végh
1994; Calvo and Végh 1999); post-1995 episodes are added by the author on the same criterion. An
episode enters when a government announced a programme intended to stop the inflation, whether or
not it worked; failures are observations, not noise.

**Coding protocol.** Each episode is coded on four package components, from observable acts of
policy only — executed budgets, statute, published parities — never from the inflation outcome:

- **Fiscal (0/1/2).** 2 = strong anchor: an executed fiscal adjustment of roughly three points of
  GDP or more, or a statutory closure of central-bank credit to the government (independent
  central bank with a lending prohibition, currency board, cash-budget rule). 1 = partial or
  transitory: adjustment announced and partly executed, or executed and later reversed. 0 = no
  credible fiscal component: no adjustment executed and monetary financing continued.
- **Monetary reform (0/1).** A new currency or a formal monetary reform (new central bank,
  redenomination with institutional content).
- **Exchange-rate anchor (0/1).** A pegged or administered parity announced as part of the
  package.
- **Incomes policy (0/1).** Price or wage freezes and controls.

Outcomes are coded as durable success (inflation stopped and stayed below moderate rates for at
least three years), gradual success, temporary success (stopped, then unravelled), in progress,
or failure (inflation returned within roughly a year). Dates are the month of the public
announcement of the package's fiscal core, following the same rule in every case (for Belgium
and Zimbabwe, where a later legal act exists, both dates are documented in the working file).

Thirty-two of the 34 rows are verified against primary or standard secondary sources; row-level
source notes live in the machine-readable census file (`data/censo/censo_episodios.csv`) that
accompanies the replication materials. A Fisher exact test of strong anchor against failure on
the 32 disinflations rejects independence at p = 0.006; the same test for the absence of any
credible fiscal component gives p = 0.004.

{{TABLA_CENSO}}

*T = type (D disinflation, R reflation). Component codes: F = fiscal (0/1/2), M = monetary reform, X = exchange-rate anchor, I = incomes
policy. Monthly data: the source of the monthly price (and where available money) series used in
appendices B–C; "none exists" and "print/paywalled only" mark the three episodes that enter the
census table alone.*
