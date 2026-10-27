## GNOME extensions

- **Keyboard Informer** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/kbd-informer) [5776↓](https://extensions.gnome.org/extension/8500/keyboard-informer/) — Shows active keyboard modifiers in the top panel and on-screen notifications when lock keys change state.
- **Blur Wallpaper** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/blur-wallpaper) [1100↓](https://extensions.gnome.org/extension/9556/blur-wallpaper-with-adjustable-intensity/) — Adjusts wallpaper blur independently for the desktop and Activities overview, with support for light and dark wallpapers.
- **My Vision** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/my-vision) [380↓](https://extensions.gnome.org/extension/9014/my-vision/) — Saves and switches monitor configurations from Quick Settings or keyboard shortcuts, with profiles tied to physical monitors and laptop lid conditions.
- **Window Shuffle** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/window-shuffle) [125↓](https://extensions.gnome.org/extension/10853/window-shuffle/) — Distributes windows across workspaces, one per workspace, and collects them back onto the current workspace.
- **TranslatePlace** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/TranslatePlace) [15↓](https://extensions.gnome.org/extension/11231/translateplace/) — Translates selected text through your own AI server, with two target languages, keyboard shortcuts, and local history.

## Translation

Translate selected text with your own AI translation server and extensions for your desktop, browser, or email client.

- **Translation API** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/translation-api) — The shared server, using Ollama and `translategemma:4b` by default.
- **TranslatePlace** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/TranslatePlace) — A GNOME Shell extension with two target languages, configurable shortcuts, local history, and optional automatic replacement of selected text.
- **WebTranslatePlace** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/WebTranslatePlace) — Extensions for selected drafts in Chrome/Chromium and Firefox, selected email text in Thunderbird, and Discord messages. Includes draft history and two target languages. Supports replacing selections while composing and viewing translations separately while reading email.

Start with the Translation API README to install Ollama, download the model, and run the server on your computer. Then follow your chosen extension's README. Both extensions connect to `http://127.0.0.1:5001` by default. WebTranslatePlace also has Safari and GNOME Web targets; Safari requires live verification, and GNOME Web is experimental with known failures.

## Backups

- **SafeData** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/safedata) — A backup script for LVM volumes and regular directories. Supports rsync and tar backups with include, exclude, or all filtering rules while preserving extended filesystem metadata.

## Infrastructure

- **NixBerry** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/nixberry) — Build and manage servers from declarative configuration. Join the [Matrix channel](https://matrix.to/#/#nixberry:matrix.org).
- **Outsource** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/outsource) — A simple wizard for creating RDP, SSH, and virt-viewer launchers in GNOME.

## Development

- **NixonCpp** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/NixonCpp) — A starting point for command-line applications in C++20+.
- **Emcx** [![GitHub](assets/github.svg)](https://github.com/tomasmark79/emcx) — A build of upstream Midnight Commander master with a small set of functional and identity [patches](https://github.com/tomasmark79/emcx/blob/main/nix/README.md).

## Music and creative projects

- [**Sound & Space**](https://music.digitalspace.name) — My digital space for sharing sounds and creative work.
- [**DreamScaler**](https://tomasmark79.github.io/DreamScalerWeb) — A standalone app and LED strip that bring musical scales, harmony, and dynamic colors to your keys.

<!-- readme-pdf:exclude:start -->
<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/factory/workshop-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/factory/workshop-light.svg" />
  <img alt="The package workshop — my most active public projects over the last 30 days" src="assets/factory/workshop.svg" width="100%" />
</picture>
</p>
<!-- readme-pdf:exclude:end -->
