# Package workshop — prototyp

Otevři `preview.html` v prohlížeči. Ilustrace respektuje světlý/tmavý režim systému a omezení pohybu. `workshop.svg` je samostatná animace bez JavaScriptu a externích zdrojů, použitelná jako obrázek v README. Odkazy na jednotlivé projekty fungují v samostatně otevřeném SVG a HTML náhledu; při vložení přes `<img>` jednotlivé stroje klikací nejsou.

Tento adresář zachovává původní prototyp a jeho GIF náhledy. Aktuální generátor a dokumentace automatizace jsou v [`scripts/factory/`](../../scripts/factory/README.md), živé podklady v `assets/factory/`. Prototyp se při automatickém obnovování nemění.

`workshop-idle-dark.png` ukazuje klidový stav nového generátoru při nulové aktivitě; jde o demonstrační data, nikoli o aktuální statistiku.

Data byla načtena 19. 10. 2026 přes GitHub Commit Search, dotaz `author:tomasmark79 author-date:2026-09-20..2026-10-19`, všech šest stránek výsledků. Výběr zahrnuje pouze veřejné repozitáře vlastněné uživatelem `tomasmark79`, seřazené podle počtu nalezených autorských commitů. Pět nejaktivnějších má dohromady 98 výsledků. Index vyhledávání může mít zpoždění; nejde o kompletní statistiku GitHub Contributions ani o úspěšné CI buildy. Forky a merge commity nejsou samostatně odfiltrovány.

Četnost balíčků ilustruje relativní aktivitu: 18 slotů ve smyčce se poměrově rozdělí mezi projekty. Všechny balíčky jedou stejnou rychlostí 90 jednotek za sekundu; odjezdy se vypočítají zpětně z rovnoměrně rozložených příjezdů do kompletátoru, takže při napojování zbývá místo a balíčky se nepředbíhají. NixOS vločka se skládá v osmnáctisekundové smyčce; nejde o skutečný průběh sestavení. GIF náhledy mají pevné barevné schéma, SVG přepíná podle `prefers-color-scheme`.

Ověřeno lokálně v headless Chrome: světlý a tmavý režim v HTML i při vložení SVG jako `<img>`, celý animační cyklus, kompletní statická vločka při `prefers-reduced-motion`, šířka 390 px bez vodorovného přetečení. Vykreslení po publikaci na GitHubu zatím ověřeno nebylo.

Pohyb ověřen proti skutečným délkám SVG cest v Chrome po dobu 54 sekund při 30 vzorcích za sekundu: shodná rychlost všech cest (90 jednotek/s s numerickou tolerancí 0,001), nejmenší rozestup na společném pásu 90 jednotek a nejmenší vzdálenost středů balíčků v celé scéně 63,64 jednotky. Balíček má nejvýše 24 jednotek, včetně napojení a přechodů smyčky tak nedochází k překryvu.
