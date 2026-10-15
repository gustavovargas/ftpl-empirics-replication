## Appendix B. Break-test specifications, windows and data

**Break detection.** For each episode the price series (and the money series where one exists) is
converted to monthly log-differences over the episode window. The primary estimator is Bai–Perron
single-break estimation by exact dynamic programming (`ruptures.Dynp`, kernel (rbf) cost,
minimum segment three months), so that shifts in both the level and the volatility of monthly
inflation count toward the break. The robustness estimator is a Zivot–Andrews-type endogenous
break date: the candidate month that minimises the t-statistic of the autoregressive coefficient
in a unit-root regression with a level break and one augmentation lag, with 15 per cent trimming.
Multiple-break detection (PELT, penalised) is run alongside to confirm that the single dominant
break is not an artefact of forcing one break on a multi-regime series. Distances are measured in
months from the detected break to the announcement date coded in appendix A.

**Durability.** For every disinflation, three statistics of monthly inflation around the reform
month (t = 0): the inherited rate (median over t −6 to −1), the freeze effect (minimum over t 0
to +6), and the settlement (median over t +7 to +12). Where plans followed one another quickly,
the settlement window is cut off at the month before the next plan. The settlement-to-inherited
ratio is the durability measure plotted in Figure 3 of the paper.

**Event study (Test 2).** Real balances are money divided by prices, each episode indexed to 100
at its reform month and averaged across episodes by month-offset over a window of −24 to +18
months. No winsorisation is applied; the panel mean and the per-episode paths are both shown.

**Windows and series.** The window start and end dates below bound every statistic. Windows avoid
documented measurement artefacts rather than inconvenient results: Ukraine's window excludes the
one-off Soviet price liberalisation of January 1992 and starts February 1992; Ukraine's and
Russia's windows end May 1998, before the August 1998 crisis; Chile's starts January 1974, after
the price liberalisation of late 1973; Convertibility's starts April 1990, after the Bonex
hyperinflation; Zimbabwe's December 2008 is missing because the currency ceased to trade
(log-differences across the gap are discarded, here and in Poland 1924).

| Episode | Reform date | Window | Price series | Money series |
|---|---|---|---|---|
| Austria 1922 | 2 Oct 1922 | 1921-01–1924-06 | Retail prices (Sargent 1982, Table A3; Young) | Note circulation (Table A2; misprint for Aug 1924 corrected from Table A6) |
| Germany 1923 | 15 Nov 1923 | 1922-01–1924-12 | WPI 1913=100 (Sargent 1982, Table G1) | Reichsbank notes (Table G4) |
| Hungary 1924 | 14 Mar 1924 | 1921-07–1925-03 | Price index (Sargent 1982, Table H3; splice retail→wholesale Dec 1923) | Notes in circulation (Table H2) |
| Belgium 1926 | 16 Jul 1926 | 1924-04–1928-12 | WPI pre-war=100 (FRB Bulletin, 4 issues, cross-validated) | — |
| France 1926 | 23 Jul 1926 | 1922-01–1928-12 | WPI (NBER M04057FRM360NNBR) | — (exchange rate: NBER M1404BUSM306NNBR) |
| Japan 1931 | 13 Dec 1931 | 1929-01–1936-12 | WPI 1934-36=100 (Shibamoto–Shizume 2014) | M1 (same source; effective exchange rate also used) |
| United States 1933 | Apr 1933 | 1929-01–1937-12 | PPI (FRED PPIACO) | M2 Friedman–Schwartz (FRED M1444AUSM027SNBR) |
| Israel 1985 | 1 Jul 1985 | 1983-01–1990-12 | CPI (FRED/OECD ISRCPIALLMINMEI) | M1 (FRED MANMM101ILM189S) |
| Bolivia 1985 | 29 Aug 1985 | 1984-01–1986-09 | Monthly inflation, INE (Sachs 1986, Table 1c) | — |
| Mexico 1987 | 15 Dec 1987 | 1985-12–1992-12 | CPI (FRED/OECD MEXCPIALLMINMEI) | M1 (FRED MANMM101MXM189S) |
| Poland 1990 | 1 Jan 1990 | 1988-01–1994-12 | CPI (IMF IFS M.PL.PCPI_IX) | — |
| Peru 1990 | 8 Aug 1990 | 1988-01–1993-12 | CPI Lima (BCRP PN01270PM) | — (BCRP monetary accounts begin 1992) |
| Brazil 1994 | 1 Jul 1994 | 1992-01–1997-12 | CPI (FRED/OECD BRACPIALLMINMEI) | M1 spliced to reais (BCB SGS 1824) |
| Bulgaria 1997 | 1 Jul 1997 | 1995-01–2001-12 | CPI (IMF IFS M.BG.PCPI_IX) | — |
| Turkey 2001 | 14 Apr 2001 | 1998-01–2005-12 | CPI (FRED/OECD TURCPIALLMINMEI) | M3 (FRED MABMM301TRM189S) |
| Poland 1924 | 11 Jan 1924 | 1921-01–1925-04 | WPI 1914=100 (Sargent 1982, Table P3; ends Apr 1924) | Notes, marks→złoty spliced at 1.8m (Table P2; Dec 1920 duplicate row and a Jun 1924 exchange misprint documented) |
| Italy 1947 | 30 Sep 1947 | 1947-01–1949-09 | WPI 1938=100 (FRB Bulletin, 5 issues, latest revision) | — |
| Chile 1975 | 24 Apr 1975 | 1974-01–1979-12 | CPI (FRED/OECD CHLCPIALLMINMEI) | — |
| Austral 1985 | 14 Jun 1985 | 1983-06–1988-07 | CPI Mendoza (DEIE, via datos.gob.ar) | — |
| Convertibility 1991 | 1 Apr 1991 | 1990-04–1996-12 | CPI Mendoza (DEIE) | — |
| Yugoslavia 1994 | 24 Jan 1994 | 1992-01–1994-12 | Retail prices (Bogetić et al. 2022, Table 1; Feb 1994 carry-over noted) | — |
| Ukraine 1994 | 11 Oct 1994 | 1992-02–1998-05 | CPI (IMF IFS M.UA.PCPI_IX; digit-identical to Ukrstat) | — |
| Russia 1995 | 6 Jul 1995 | 1993-01–1998-05 | CPI (IMF IFS, FRED RUSCPIALLMINMEI) | — |
| Ecuador 2000 | 9 Jan 2000 | 1997-01–2004-12 | CPI (IMF IFS M.EC.PCPI_IX) | — |
| Zimbabwe 2009 | 13 Feb 2009 | 2007-03–2012-12 | RBZ official to Jul 2008, OMIR-implied to 14 Nov 2008 (Hanke–Kwok 2009); USD CPI from Jan 2009 (IFS) | — |
| Argentina 2023 | 12 Dec 2023 | 2021-01–2026-09 | CPI national (INDEC via datos.gob.ar) | Monetary base (BCRA, daily averaged) |
| Cruzado 1986 | 28 Feb 1986 | 1984-03–1987-05 | IPCA (BCB SGS 433) | M1 spliced across five currencies (SGS 1824) |
| Bresser 1987 | 12 Jun 1987 | 1986-04–1988-12 | IPCA | M1 (same splice) |
| Primavera 1988 | 3 Aug 1988 | 1986-09–1989-06 | CPI Mendoza (DEIE) | — |
| Verão 1989 | 15 Jan 1989 | 1987-07–1990-02 | IPCA | M1 |
| Collor 1990 | 16 Mar 1990 | 1989-02–1991-12 | IPCA | M1 (the confiscation drained broad liquidity; measured M1 rose on conversion) |

**Aggregates.** The money series is the broadest monthly aggregate available for each episode. In
the 1920s hyperinflations bank deposits had collapsed with the currency, so central-bank notes
approximate broad money; later episodes use M1 or M3 as listed. The Argentine plans of 1985–91
are measured on the Mendoza provincial CPI, the only monthly price series spanning them; it
tracks the known national figures closely at the plan dates (e.g. Austral: June 1985 +28.9 per
cent, July +4.0).

**Velocity (section 7 of the paper).** M2 velocity is FRED M2V, quarterly, 1959–2025; Divisia M4
velocity is nominal GDP over the Center for Financial Stability Divisia M4. ADF and
Zivot–Andrews unit-root tests as implemented in `arch`; the AR(1) half-life is ln(0.5)/ln(ρ) from
an OLS autoregression; regime means from Bai–Perron (l2 cost) on the level with four breaks.
