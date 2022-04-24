import os
import sys
import shutil
import copy
import re
from bs4 import BeautifulSoup, Tag, NavigableString
from helpers.create_db import create_db
from helpers.mod_helpers import write_db
from helpers.mod_helpers import multi_level
from helpers.mod_helpers import power_construct
from helpers.mod_helpers import powers_format
from helpers.mod_helpers import props_format

if __name__ == '__main__':

    # Pull data from Portable Compendium
    db = []
    try:
        db = create_db('ddiItem.sql', "','")
    except:
        print("Error reading data source.")

    print(f"{len(db)} entries recovered")

    # Convert data to FG format
    print("converting to FG format...")

    # Initialize all modules databases
    export_list = []

    if not db:
        print("NO DATA FOUND IN SOURCES, MAKE SURE YOU HAVE COPIED YOUR 4E PORTABLE COMPENDIUM DATA TO SOURCES!")
        input('Press enter to close.')
        sys.exit(0)

    for i, row in enumerate(db, start=1):

        # Parse the HTML text 
        html = row['Txt']
        html = html.replace('\\r\\n','\r\n').replace('\\','')
        parsed_html = BeautifulSoup(html, features="html.parser")

        # Retrieve the data with dedicated columns
        name_str =  row['Name'].replace('\\', '')
        category_str = row['Category'].replace('\\', '')
        rarity_str =  row['Rarity'].replace('\\', '')

        bonus_str = ''
        class_str = ''
        cost_str = ''
        enhancement_str = ''
        flavor_str = ''
        group_str = ''
        level_str = ''
        mitype_str = ''
        powers_str = ''
        prerequisite_str = ''
        properties_str = ''
        props_str = ''
        special_str = ''
        subclass_str = ''

        # Class
        if (re.search('^(Armor)$', category_str) and re.search('^(Common|Uncommon|Rare)', rarity_str)):
            class_str = rarity_str
            mitype_str = 'armor'

        if mitype_str != '':
            print(str(i) + ' ' + name_str)

            # Bonus / Cost / Level
            multi_bonus = True
            try:
                multi_list = multi_level(parsed_html)
            except:
                multi_bonus = False
                multi_list = []
                multi_dict = {}
                multi_dict['bonus'] = ''
                multi_dict['cost'] = ''
                multi_dict['level'] = ''
                multi_list.append(copy.deepcopy(multi_dict))

            # Enhancement
            if enhancement_lbl := parsed_html.find(string=re.compile('^(Enhancement|Enhancement Bonus):$')):
                enhancement_str = enhancement_lbl.parent.next_sibling.get_text(separator = '\\n', strip = True)

            # Flavor
            if flavor_lbl := parsed_html.find('p', class_='miflavor'):
                flavor_str = re.sub('\s\s', ' ', flavor_lbl.get_text(separator = '\\n', strip = True))

            # Subclass (Armor)
            if subclass_lbl := parsed_html.find(string='Armor: '):
                subclass_str = subclass_lbl.parent.next_sibling.get_text(separator = '\\n', strip = True)
                subclass_str = re.sub('\s\s', ' ', subclass_str.strip())

            # Powers
            powers_str = powers_format(parsed_html)

            # Prerequisite
            if prerequisite_lbl := parsed_html.find(string=re.compile('^(Prerequisite|Requirement):$')):
                prerequisite_str = prerequisite_lbl.parent.next_sibling.get_text(separator = '\\n', strip = True)

            # Properties
            if properties_lbl := parsed_html.find(string=re.compile('^(Property|Properties)')):
                properties_str = re.sub('\s\s', ' ', properties_lbl.parent.next_sibling.get_text(separator = '\\n', strip = True))
                properties_str = re.sub(r':\\n', ': ', properties_str)
                # non-weapon items need a separate 'props' list for the 'Abilities' tab
                if mitype_str != 'weapon':
                    props_str = props_format(properties_str)
                    properties_str = ''

            # Special (Published In)
            if special_lbl := parsed_html.find('p', class_='publishedIn'):
                special_str = re.sub('\s\s', ' ', special_lbl.text)

            # Build the item entry
            for item in multi_list:
                export_item = {}
                export_item['bonus'] = item['bonus']
                export_item['class'] = class_str
                export_item['cost'] = item['cost']
                export_item['enhancement'] = enhancement_str
                export_item['flavor'] = flavor_str
                export_item['group'] = group_str
                export_item['level'] = item['level']
                export_item['mitype'] = mitype_str
                export_item['name'] = name_str + ' ' + item['bonus'] if item['bonus'] != '' else name_str
                export_item['powers'] = powers_str
                export_item['prerequisite'] = prerequisite_str
                export_item['properties'] = properties_str
                export_item['props'] = props_str
                export_item['special'] = special_str
                export_item['subclass'] = category_str + ': ' + subclass_str if category_str != '' else subclass_str

                # Append a copy of generated entry
                export_list.append(copy.deepcopy(export_item))

    print(str(len(db)) + " entries parsed.")
    print(str(len(export_list)) + " export entries.")

    # Write FG XML database files
    write_id = write_db('export/magic_armors/data/db.xml', export_list)

    print(str(write_id) + " module entries written. Job done.")

    try:
        os.remove('export/mods/4E_Magic_Armors.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/mods/4E_Magic_Armors', 'zip', 'export/magic_armors/data/')
        os.rename('export/mods/4E_Magic_Armors.zip', 'export/mods/4E_Magic_Armors.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\mods' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\magic_armor\\data' folder to create the mod.")
        print("Rename the complete filename (including path) to '4E_Magic_Armors.mod'.\n")

    input('Press enter to close.')
