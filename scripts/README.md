# Aktualizace Downloads

Workflow `.github/workflows/downloads.yml` denně v 00:00 UTC (02:00 SELČ,
01:00 SEČ) načítá počty stažení z GNOME Extensions API a aktualizuje odkazy
`Downloads` v profilovém `README.md`. Lze ho spustit i ručně v GitHub Actions.
GitHub může plánovaný běh spustit se zpožděním.

Skript rozpoznává odkazy podle ID rozšíření v URL, nezávisle na umístění
popisku nebo tučném názvu projektu. Historie obsahuje automatické aktualizace
do 19. října 2026, ale jejich původní skript ani plánovač v repozitáři nejsou.
Aktualizace je proto nyní spravovaná přímo zde.

Při chybě API zůstane README beze změny a běh skončí chybou. Pokud odkazy
Downloads chybí, skript také skončí chybou, aby změna formátu nezastavila
aktualizace bez upozornění. Po publikaci změny workflow výslovně spustí
generování `cv/README.pdf`, protože push přes `GITHUB_TOKEN` další workflow
automaticky nespouští.

Lokální aktualizace a testy:

```sh
python3 scripts/update_downloads.py
python3 -m unittest discover -s scripts -p 'test_update_downloads.py' -v
```
