import os
import sys
import shutil
import pathlib
import json
import copy
from urllib.parse import unquote
from create_db import create_db
from bs4 import BeautifulSoup, Tag, NavigableString


def write_db(filepath, fg_data):
    id = 1
    with open(filepath, mode='w', encoding='UTF-8', errors='strict', buffering=1) as file:
        file.write('<root version="2.9">\n')
        file.write('	<powerdesc>\n')
        for entry in fg_data:
            string_id = "00000"[0:len("00000")-len(str(id))] + str(id)
            file.write(f'		<id-{string_id}>\n')
            file.write(f'			<action type="string">{entry["action"]}</action>\n')
            file.write('			<description type="formattedtext">\n')
            file.write(f'				{entry["description"]}\n')
            file.write('			</description>\n')
            file.write(f'			<flavor type="string">{entry["flavor"]}</flavor>\n')
            file.write(f'			<keywords type="string">{entry["keywords"]}</keywords>\n')
            file.write('			<linkedpowers>\n')
            file.write('			</linkedpowers>\n')
            file.write('			<locked type="number">1</locked>\n')
            file.write(f'			<name type="string">{entry["name"]}</name>\n')
            file.write(f'			<range type="string">{entry["range"]}</range>\n')
            file.write(f'			<recharge type="string">{entry["recharge"]}</recharge>\n')
            file.write(f'			<shortdescription type="string">{entry["shortdescription"]}</shortdescription>\n')
            file.write(f'			<source type="string">{entry["source"]}</source>\n')
            file.write(f'		</id-{string_id}>\n')
            id = id + 1
        file.write('	</powerdesc>\n')
        file.write('</root>')

def replace_line_breaks(soup):
    while soup.p.br:
        soup.p.br.replace_with('\n')

def construct_description(tags):
    description = []
    shortdescription = []
    for t in tags:
        p_tags = t.find_all('p', class_=['powerstat', 'flavor'])
        if p_tags:
            desc, sdesc = construct_description(p_tags)
            description += desc
            shortdescription+= sdesc
        else:
            soup = BeautifulSoup(str(t), features="html.parser")
            if soup.p:
                soup.p.wrap(soup.new_tag('p'))
                soup.p.p.unwrap()
                # Replace any line breaks with new p tags or newline characters
                description += [str(soup).replace("<br/>", "</p>\n<p>")]
                replace_line_breaks(soup)
                shortdescription += [soup.text]
    return description, shortdescription



if __name__ == '__main__':

    # Pull data from Portable Compendium
    data_source = {}
    sql_sections = []

    db = []

    try:
        db = create_db('ddiPower.sql', "','")
    except:
        print("Error reading data source.")

    print(f"{len(db)} entries recovered")

    # Convert data to FG format
    print("converting to FG format...")

    # Initialize all modules databases
    Powers_fg = [{}]*len(db)

    if not db:
        print("NO DATA FOUND IN SOURCES, MAKE SURE YOU HAVE COPIED YOUR 4E PORTABLE COMPENDIUM DATA TO SOURCES!")
        input('Press enter to close.')
        sys.exit(0)

    for i, row in enumerate(db):

        fg_entry = {}

        # Retrieve the data with dedicated columns
        fg_entry['name'] = row['Name'].replace('\\', '')
        fg_entry['recharge'] = row['Usage']
        fg_entry['published'] = row['Source'].replace('\\', '').split(", ")

        # Parse the HTML text 
        html = row['Txt']
        html = html.replace('\\r\\n','\r\n').replace('\\','')
        parsed_html = BeautifulSoup(html, features="html.parser")

        # Power source doesn't always match with "{Class} {Kind} {Level}".
        # Ergo, get it directly from the power's header.
        power_source = parsed_html.find('span', class_='level')
        fg_entry['source'] = power_source.text

        # Get the Power statline:  Recharge, Keywords, Action, and Range.
        # We already have Recharge & Action; get Keywords & Range.
        powerstat = parsed_html.find('p', class_='powerstat')

        # If a power has a bullet, check for keywords after the bullet but
        # before the line break.
        keywords = []
        power_bullet = powerstat.find('img', attrs={'src': 'images/bullet.gif'})
        if power_bullet:
            for tag in power_bullet.next_siblings:
                if tag.name == "br":
                    break
                elif tag.name == "b":
                    keywords.append(tag.text)
        
        fg_entry['keywords'] = ", ".join(keywords)

        # Find the Action, immediately after the stat line break.
        powerstat_br = powerstat.find('br')
        powerstat_action = powerstat_br.find_next_sibling('b')
        fg_entry['action'] = powerstat_action.text

        # Find the range, if present; it's always after the Action.
        powerstat_rg_type = powerstat_action.find_next_sibling('b')
        range_str = ""
        if powerstat_rg_type:
            powerstat_rg = powerstat_rg_type.next_sibling
            rg_text = powerstat_rg.text if powerstat_rg else ""
            range_str = f"{powerstat_rg_type.text}{rg_text}"

        fg_entry['range'] = range_str

        # Acquire flavor text, if present. Flavor text is always in italics.
        flavortext = ""
        if flavor_tag := parsed_html.select_one('.flavor > i'):
            flavortext = flavor_tag.text
        fg_entry['flavor'] = flavortext

        # Everything in a 'p' tag after the stat line is mechanics text.
        # Mechanics are either 'powerstat' or 'flavor'.
        # Description will include all mechanics text + Published line.
        power_mechanics = powerstat.find_next_siblings('p', class_=['powerstat', 'flavor'])

        try:
            description, shortdescription = construct_description(power_mechanics)

            # Grab the Published line without external links, in class-less p tag
            published_in = parsed_html.find('p', class_='publishedIn')
            pub_soup = BeautifulSoup(str(published_in), features="html.parser")
            pub_soup.p.wrap(pub_soup.new_tag('p'))
            pub_soup.p.p.replace_with(pub_soup.p.p.text)
            description.append(str(pub_soup))
            shortdescription.append(pub_soup.text)
        except:
            print(f"Problem with {row['Name']}")
            raise

        fg_entry['description'] = "\n".join(description)
        fg_entry['shortdescription'] = "\n".join(shortdescription)

        # Append a copy of generated entry
        Powers_fg[i] = copy.deepcopy(fg_entry)

    print(str(len(Powers_fg)) + " entries converted to FG as Powers")

    # Write FG XML database files
    write_db('export/powers/data/db.xml', Powers_fg)

    print("Database files written. Job done.")

    try:
        os.remove('export/powers/4e_Power_PortableCompendium.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    shutil.make_archive('export/powers/4e_Power', 'zip', 'export/powers/data/')
    os.rename('export/powers/4e_Power.zip', 'export/powers/4e_Power_PortableCompendium.mod')

    print("\nDatabase added and module generated!")
    print("You can find it in the 'export\\power' folder\n")

    input('Press enter to close.')
