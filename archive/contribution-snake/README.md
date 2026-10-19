# Archiv: NixOS contribution snake

Verze s NixOS logy a postupným růstem hada, archivovaná 19. 10. 2026 před přechodem na motiv buildovací dílny.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/github-contribution-grid-snake-growing-full-dark.svg" />
  <img alt="Archivovaná animace hada s NixOS logy" src="assets/github-contribution-grid-snake-growing-full.svg" />
</picture>

## Co je uložené

- `assets/`: skutečně vygenerované SVG ve světlé a tmavé variantě, převzaté beze změny z commitu `98f738a51036719cc27cf09b2408a3eadd4353c7` větve `output` repozitáře `tomasmark79/tomasmark79`.
- `snake.yml`: původní GitHub Actions workflow. Mimo `.github/workflows/` se nespouští.
- `readme-snippet.html`: původní vložení do profilového README včetně značek pro vynechání při PDF exportu.
- `generator-source.tar.gz`: kompletní strom zdrojového kódu forku [tomasmark79/snk](https://github.com/tomasmark79/snk/tree/094d5f2dd3475f03744cf29cb4ad8bb202623cb9) z commitu `094d5f2dd3475f03744cf29cb4ad8bb202623cb9`, včetně jeho dokumentace a lockfilu. Archiv obsahuje zdrojové soubory, nikoli historii Gitu nebo stažené závislosti.

Commit generátoru je snapshot aktuálního `main` v okamžiku archivace. Původní workflow odkazuje na pohyblivý `main`; samotný SVG výstup neprokazuje, který commit generátoru jej vytvořil.

## Obnovení

Pro zobrazení uložené animace stačí vrátit blok `<picture>` do hlavního README a použít cesty `archive/contribution-snake/assets/...`. Tak zobrazení nezávisí na budoucím obsahu větve `output`.

Pro obnovení denního generování zkopíruj `snake.yml` zpět do `.github/workflows/snake.yml`. Pro zachování této verze generátoru nahraď `tomasmark79/snk/svg-only@main` odkazem `tomasmark79/snk/svg-only@094d5f2dd3475f03744cf29cb4ad8bb202623cb9`. Blok v `readme-snippet.html` pak může znovu zobrazovat aktualizované výstupy větve `output`.

Archivace větev `output` ani fork generátoru nemaže. Přesun workflow vypne jeho spouštění na GitHubu teprve po publikaci změny na výchozí větev.
