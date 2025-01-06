# Projekt 3 - Engeto Online Python Akademie

Tento projekt slouží k načítání volebních dat z webu a jejich exportu do CSV souboru. Scraper získává informace o obcích, volebních datech a výsledcích voleb z konkrétního odkazu.

## Požadavky

Pro běh programu je nutné mít nainstalovány následující knihovny:

- `beautifulsoup4` - pro parsování HTML stránky
- `requests` - pro HTTP požadavky
- `csv` - pro zápis do CSV souboru

## Instalace závislostí

Pokud máte Python nainstalován, vytvořte si virtuální prostředí a nainstalujte potřebné knihovny pomocí souboru `requirements.txt`.

1. Vytvořte virtuální prostředí:
    ```bash
    python -m venv .venv
    ```

2. Aktivujte virtuální prostředí:
    - Na Windows:
      ```bash
      .venv\Scripts\activate
      ```
    - Na MacOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

3. Nainstalujte požadavky:
    ```bash
    pip install -r requirements.txt
    ```

## Použití

Pro spuštění scraperu použijte následující příkaz:

```bash
python main.py 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=5&xnumnuts=4101' 'output_file.csv'

Toto lze využít pro jakýkoliv územní celek například i pro: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101

