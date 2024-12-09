"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Jaroslav Tvrz
email: j.tvrz77@gmail.com
"""

import argparse
import sys
from bs4 import BeautifulSoup
import requests
import csv
import re

# Funkce pro načtení stránky
def scrape_page(link):
    """
    Načte stránku z daného odkazu a vrátí její HTML obsah jako BeautifulSoup objekt.

    Args:
        link (str): URL stránky, kterou chceme stáhnout.

    Returns:
        BeautifulSoup: HTML obsah stránky zpracovaný pomocí BeautifulSoup.
    """
    response = requests.get(link)  # Poslání požadavku na stránku
    soup = BeautifulSoup(response.text, "html.parser")  # Vytvoření BeautifulSoup objektu
    return soup

# Funkce pro získání dat o obcích
def get_town_data(main_link):
    """
    Získá seznam ID a názvů obcí z dané hlavní stránky.

    Args:
        main_link (str): URL hlavní stránky, která obsahuje seznam obcí.

    Returns:
        tuple: Dvě seznamy, jeden pro ID obcí a druhý pro jejich názvy.
    """
    town_id_list = []
    town_name_list = []
    soup = scrape_page(main_link)  # Načteme stránku
    town_id = soup.find_all("td", class_="cislo")  # Najdeme všechny ID obcí
    town_name = soup.find_all("td", class_="overflow_name")  # Najdeme názvy obcí

    # Přidáme data do seznamů
    for i in town_id:
        town_id_list.append(i.text.strip())
    for n in town_name:
        town_name_list.append(n.text.strip())

    print(f"Počet obcí načtených: {len(town_id_list)}")  # Výpis počtu načtených obcí
    return town_id_list, town_name_list

# Funkce pro získání volebních informací
def get_election_info(town_id_list, xkraj, xnumnuts):
    """
    Získá volební data pro seznam obcí na základě jejich ID, kraje a okrsku.

    Args:
        town_id_list (list): Seznam ID obcí.
        xkraj (str): Kód kraje.
        xnumnuts (str): Kód okrsku.

    Returns:
        tuple: Tři seznamy, jeden pro voliče, jeden pro vydané obálky a jeden pro platné hlasy.
    """
    print(f"Získávám volební data pro {len(town_id_list)} obcí...")
    voters = []
    envelopes = []
    valid_votes = []

    # Pro každou obec načteme volební data
    for i, town_id in enumerate(town_id_list):
        print(f"Načítám data pro obec s ID: {town_id}")
        link = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={xkraj}&xobec={town_id}&xvyber={xnumnuts}"
        soup = scrape_page(link)

        # Načteme specifické volební údaje
        voters_in_the_list = soup.find_all("td", class_="cislo", headers="sa2")
        issued_envelopes = soup.find_all("td", class_="cislo", headers="sa3")
        valid_votes_data = soup.find_all("td", class_="cislo", headers="sa6")

        # Uložíme data do seznamů
        for i in voters_in_the_list:
            voters_text = i.text.replace("\xa0", "")
            voters.append(voters_text)
        for e in issued_envelopes:
            envelopes_text = e.text.replace("\xa0", "")
            envelopes.append(envelopes_text)
        for v in valid_votes_data:
            valid_votes_text = v.text.replace("\xa0", "")
            valid_votes.append(valid_votes_text)

    return voters, envelopes, valid_votes

# Funkce pro získání informací o politických stranách
def get_info_about_political_parties(town_id_list, xkraj, xnumnuts):
    """
    Získá hlasování pro politické strany v každé obci na základě ID obcí, kraje a okrsku.

    Args:
        town_id_list (list): Seznam ID obcí.
        xkraj (str): Kód kraje.
        xnumnuts (str): Kód okrsku.

    Returns:
        dict: Slovník, kde klíče jsou názvy politických stran a hodnoty jsou seznamy jejich hlasů v jednotlivých obcích.
    """
    print("Získávám informace o politických stranách...")
    party_votes = {}

    # Pro každou obec načteme data o politických stranách
    for town_id in town_id_list:
        link = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={xkraj}&xobec={town_id}&xvyber={xnumnuts}"
        soup = scrape_page(link)

        # Načteme hlasy pro dvě skupiny stran
        valid_votes_p1 = soup.find_all("td", class_="cislo", headers="t1sa2 t1sb3")
        valid_votes_p2 = soup.find_all("td", class_="cislo", headers="t2sa2 t2sb3")
        political_parties_1 = soup.find_all("td", class_="overflow_name", headers="t1sa1 t1sb2")
        political_parties_2 = soup.find_all("td", class_="overflow_name", headers="t2sa1 t2sb2")

        # Přidáme hlasování pro strany
        for i, one_party in enumerate(political_parties_1):
            party_name = one_party.text.strip()
            votes = valid_votes_p1[i].text.strip().replace("\xa0", "")
            if party_name not in party_votes:
                party_votes[party_name] = []
            party_votes[party_name].append(votes)

        for i, one_party in enumerate(political_parties_2):
            party_name = one_party.text.strip()
            votes = valid_votes_p2[i].text.strip().replace("\xa0", "")
            if party_name not in party_votes:
                party_votes[party_name] = []
            party_votes[party_name].append(votes)

    return party_votes

# Hlavní funkce pro zpracování volebních dat
def election_scraper(main_link, output_file):
    """
    Hlavní funkce pro extrakci volebních dat a uložení výsledků do CSV souboru.

    Args:
        main_link (str): URL hlavní stránky pro získání volebních dat.
        output_file (str): Název výstupního CSV souboru.
    """
    # Extrahujeme z URL hodnoty xkraj a xnumnuts
    match = re.search(r"xkraj=(\d+)&xnumnuts=(\d+)", main_link)
    if not match:
        print("Chyba: Neplatný formát odkazu!")
        sys.exit(1)

    xkraj = match.group(1)  # kraj
    xnumnuts = match.group(2)  # okrsek

    # Načteme data o obcích, volební data a data o politických stranách
    town_id_list, town_name_list = get_town_data(main_link)
    voters, envelopes, valid_votes = get_election_info(town_id_list, xkraj, xnumnuts)
    party_votes = get_info_about_political_parties(town_id_list, xkraj, xnumnuts)

    # Zajištění, že všechny seznamy mají stejnou délku
    length = len(town_id_list)
    assert len(town_name_list) == length
    assert len(voters) == length
    assert len(envelopes) == length
    assert len(valid_votes) == length

    # Otevření CSV souboru pro zápis
    with open(output_file, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        # Zápis hlavičky CSV souboru
        headers = ["Obec", "ID obce", "Voliči", "Vydané obálky", "Platné hlasy"]
        for party in party_votes.keys():
            headers.append(party)  # Přidáme název strany
        writer.writerow(headers)

        # Zápis dat do CSV souboru
        for i in range(length):
            row = [
                town_name_list[i],  # Název obce
                town_id_list[i],  # ID obce
                voters[i],  # Počet voličů
                envelopes[i],  # Počet vydaných obálek
                valid_votes[i]  # Počet platných hlasů
            ]

            # Přidání hlasů pro každou politickou stranu
            for party in party_votes.keys():
                votes = party_votes[party][i] if i < len(party_votes[party]) else ""
                row.append(votes.replace(" ", ""))  # Čistý text bez mezer mezi čísly

            writer.writerow(row)
    print("Dokončeno, CSV soubor vytvořen.")


# Zpracování argumentů z příkazové řádky
def main():
    """
    Hlavní funkce pro zpracování argumentů z příkazové řádky a spuštění scraperu.
    """
    if len(sys.argv) != 3:
        print("Chyba: Prosím, zadejte URL a název výstupního souboru jako argumenty!")
        print(f"Usage: python scraper.py 'URL' 'output_file.csv'")
        sys.exit(1)

    main_link = sys.argv[1]  # URL jako první argument
    output_file = sys.argv[2]  # Název výstupního souboru jako druhý argument
    election_scraper(main_link, output_file)

if __name__ == "__main__":
    main()
