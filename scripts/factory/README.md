# Package workshop

Profilové README zobrazuje animované SVG v `assets/factory/`. Každý den jej obnovuje `.github/workflows/factory.yml`, plánovaně v 03:37 UTC. GitHub může plánovaný běh zpozdit. Workflow lze spustit také ručně a spouští se po změně skriptů, workflow nebo loga `assets/NixTomasLogo.svg` na `main`. Komora označená `ASSEMBLER` postupně skládá toto logo včetně osobní značky uprostřed; původní přechody a geometrie jsou vložené přímo do výsledného SVG.

Workflow nejprve spustí testy, načte data, vygeneruje automatickou/světlou/tmavou variantu a uloží pouze změněné soubory z `assets/factory/` na `main` jako `github-actions[bot]`. Výstupní commity neodpovídají filtru cest, proto se generování nezacyklí. Nepotřebuje osobní token: používá `github.token` s právem `contents: write`. Ochrana větve musí zápis workflow dovolit; případné zamítnutí skončí chybou běhu. Samotné lokální vytvoření workflow automatizaci na GitHubu neaktivuje, musí být publikováno na výchozí větvi.

## Výběr projektů

`fetch_activity.py` používá GitHub Commit Search s `author:<owner> user:<owner> is:public author-date:<start>..<end>`. Okno je posledních 30 kalendářních dní včetně dneška podle `Europe/Prague`. Načítá všechny stránky, řadí repozitáře podle počtu nalezených autorských commitů a při shodě podle názvu. Vybere nejvýše pět projektů. Kontrola `private` a vlastníka se provádí také nad jednotlivými výsledky. Bot autoři se vynechávají; merge commity a veřejné forky nejsou zvlášť odfiltrované.

Součet na ilustraci patří vybraným pěti projektům, `total_commits` v JSON zahrnuje všechna nalezená veřejná vlastní repa. Jde o indexované autorské commity, nikoli o úplnou tabulku GitHub Contributions nebo stav CI. Vyhledávací index může mít zpoždění.

Pokud je aktivních projektů méně než pět, volná místa doplní veřejná vlastní repa podle posledního pushnutí s nulou commitů. Pokud nejsou ani ta, zůstanou neutrální stanice. Neaktivní stanice nevyrábí balíčky. Při úplné neaktivitě se vypne pohyb celé dílny, pás je prázdný, vločka je neúplná a panel ukazuje `workshop idle`. Nová aktivita ji při dalším úspěšném běhu znovu rozhýbe.

Chyba API ani `incomplete_results` nesmí být zaměněna za neaktivitu. Při selhání se nic nepublikuje a poslední úspěšná ilustrace zůstane beze změny s původním datovým obdobím. Nad 1 000 výsledků se časový rozsah dělí na menší úseky. Pokud má i jediný den přes 1 000 výsledků, běh bezpečně skončí chybou, místo aby publikoval oříznutá data. Selže také při nekonzistentním nebo duplicitním stránkování.

## Lokální obnova

Vyžaduje Python 3.9+ a přihlášené GitHub CLI (`gh`), případně proměnnou `GH_TOKEN`.

```sh
python3 -m unittest discover -s scripts/factory -p 'test_*.py' -v
python3 scripts/factory/fetch_activity.py --owner tomasmark79 --output assets/factory/activity.json
python3 scripts/factory/generate.py
```

Pro reprodukovatelné načtení lze zadat `--end YYYY-MM-DD`. Generátor lze spustit offline s existujícím `--data cesta/activity.json` a vlastním `--output adresar`. `assets/factory/preview.html` je lokální náhled, SVG funguje samostatně bez JavaScriptu a externích zdrojů.

README používá `<picture>` se samostatnými barevnými variantami. Samostatné `workshop.svg` respektuje `prefers-color-scheme`. Všechny varianty respektují `prefers-reduced-motion`; při neaktivitě zůstane klidový stav i s tímto nastavením. Při vložení SVG jako obrázku nejsou jednotlivé stanice klikací. Ilustrace je vynechaná z PDF exportu README existujícími značkami `readme-pdf:exclude`.

Balíčky mají jednotnou rychlost 100 jednotek/s, aby i nejdelší trasa po prodlouženém horním pásu doběhla během 18sekundového cyklu. Četnost určuje poměrové rozdělení 18 slotů za 18 sekund; příjezdy se plánují do společných slotů a odjezdy zpětně podle délky trasy. U velmi malého podílu aktivity může projekt získat nula slotů, i když zůstává uvedený s počtem commitů. Vyšší aktivita nemění rychlost balíčku, proto se na pásu nepředbíhá.

Původní ručně připravený náhled je v `previews/package-workshop/`, archiv hada v `archive/contribution-snake/`. Workflow ani generátor tyto archivy nemění.

Při doručení balíčku vstup assembleru krátce blikne barvou zdrojového projektu. Efekt používá stejné příjezdové sloty jako balíčky, včetně přechodu mezi cykly. Při neaktivitě ani s `prefers-reduced-motion` se nezobrazuje.
