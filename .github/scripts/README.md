# Export profilového README do PDF

`readme-pdf.sh` vytvoří `cv/README.pdf` z aktuálního README přes Pandoc a Chrome. GitHub-only bloky mezi značkami `readme-pdf:exclude` vynechává.

Workflow `readme-pdf.yml` používá `publish-readme-pdf.sh` v jednorázovém CI checkoutu. Publikační skript při každém pokusu načte aktuální `origin/main`, resetuje na něj checkout, znovu vygeneruje PDF a pokusí se uložit změněný soubor. Patří pouze do takového pracovního checkoutu, protože `git reset --hard` zahazuje jeho místní změny.

Pokud během renderování někdo pushne další změnu, Git odmítne starší push jako `fetch first`. Skript nejvýše třikrát obnoví zdroje a opakuje celé generování; nerebasuje zastaralé binární PDF. Novější běh téhož workflow také ruší předchozí rozpracovaný běh. Beze změny PDF nevzniká další commit.

Regresní kontrola `python3 .github/scripts/test-publish-readme-pdf.py` používá dočasný lokální bare repozitář a dva klony. Reprodukuje push změny README během prvního renderování a ověřuje, že se na vzdálený repozitář nakonec dostane PDF z novějšího README. Neprovádí síťové zápisy.
