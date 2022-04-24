import os
import sys
import shutil
import copy
import re
from bs4 import BeautifulSoup, Tag, NavigableString
from helpers.create_db import create_db

def list_sorter(entry):
    section_id = entry["section_id"]
    name = entry["name"]
    return (section_id, name)

def write_lib(filepath, entry_list):
    with open(filepath, mode='w', encoding='UTF-8', errors='strict', buffering=1) as file:

        section_str = ''
        entry_str = ''
        name_lower = ''

        file.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        file.write('<root version="2.9">\n')

        # Reference part
        # These are the individual cards that appear when you click on a table entry
        file.write('\t<reference static="true">\n')
        file.write('\t\t<weapon>\n')

        # Create individual item entries
        for entry_dict in sorted(entry_list, key=list_sorter):
            name_lower = re.sub('\W', '', entry_dict["name"].lower())

            file.write(f'\t\t\t<{name_lower}>\n')
            file.write(f'\t\t\t\t<name type="string">{entry_dict["name"]}</name>\n')
            file.write(f'\t\t\t\t<type type="string">{entry_dict["type"]}</type>\n')
            file.write(f'\t\t\t\t<prof type="string">{entry_dict["prof"]}</prof>\n')
            file.write(f'\t\t\t\t<heft type="string">{entry_dict["heft"]}</heft>\n')
            file.write(f'\t\t\t\t<profbonus type="number">{entry_dict["profbonus"]}</profbonus>\n')
            file.write(f'\t\t\t\t<damage type="string">{entry_dict["damage"]}</damage>\n')
            file.write(f'\t\t\t\t<range type="number">{entry_dict["range"]}</range>\n')
            file.write(f'\t\t\t\t<cost type="number">{entry_dict["cost"]}</cost>\n')
            file.write(f'\t\t\t\t<weight type="number">{entry_dict["weight"]}</weight>\n')
            file.write(f'\t\t\t\t<group type="string">{entry_dict["group"]}</group>\n')
            file.write(f'\t\t\t\t<properties type="string">{entry_dict["properties"]}</properties>\n')
            file.write(f'\t\t\t\t<description type="formattedtext">{entry_dict["description"]}\n\t\t\t\t</description>\n')
            file.write(f'\t\t\t</{name_lower}>\n')

        # Close out the Reference part
        file.write('\t\t</weapon>\n')
        file.write('\t</reference>\n')

        # Library part - not dynamic
        # This controls the right-hand menu on the Modules screen
        file.write('\t<library>\n')
        file.write('\t\t<lib4ebasicweapons>\n')
        file.write('\t\t\t<name type="string">4E Basic Weapons</name>\n')
        file.write('\t\t\t<categoryname type="string">4E Core</categoryname>\n')
        file.write('\t\t\t<entries>\n')
        file.write('\t\t\t\t<a0001weapons>\n')
        file.write('\t\t\t\t\t<librarylink type="windowreference">\n')
        file.write('\t\t\t\t\t\t<class>reference_classweapontablelist</class>\n')
        file.write('\t\t\t\t\t\t<recordname>weaponlists.core@4E Basic Weapons</recordname>\n')
        file.write('\t\t\t\t\t</librarylink>\n')
        file.write('\t\t\t\t\t<name type="string">Items - Weapons</name>\n')
        file.write('\t\t\t\t</a0001weapons>\n')
        file.write('\t\t\t</entries>\n')
        file.write('\t\t</lib4ebasicweapons>\n')
        file.write('\t</library>\n')

        # counters for Item List
        section_id = 0
        item_id = 0

        # Item List part
        # This controls the table that appears when you click on a Library menu
        file.write('\t<weaponlists>\n')
        file.write('\t\t<core>\n')
        file.write('\t\t\t<description type="string">Weapons Table</description>\n')
        file.write('\t\t\t<groups>\n')

        # Create individual item entries
        for entry_dict in sorted(entry_list, key=list_sorter):
            item_id += 1
            
            entry_str = "00000"[0:len("00000")-len(str(item_id))] + str(item_id)
            name_lower = re.sub('\W', '', entry_dict["name"].lower())

            #Check for new section
            if entry_dict["section_id"] != section_id:
                section_id = entry_dict["section_id"]
                if section_id != 1:
                    section_str = "000"[0:len("000")-len(str(section_id - 1))] + str(section_id - 1)
                    file.write('\t\t\t\t\t</weapons>\n')
                    file.write(f'\t\t\t\t</section{section_str}>\n')
                section_str = "000"[0:len("000")-len(str(section_id))] + str(section_id)
                file.write(f'\t\t\t\t<section{section_str}>\n')
                file.write(f'\t\t\t\t\t<description type="string">{entry_dict["prof"]} {entry_dict["type"]} Weapons</description>\n')
                file.write(f'\t\t\t\t\t<subdescription type="string">{entry_dict["heft"]}</subdescription>\n')
                file.write('\t\t\t\t\t<weapons>\n')

            file.write(f'\t\t\t\t\t\t<a{entry_str}{name_lower}>\n')
            file.write('\t\t\t\t\t\t\t<link type="windowreference">\n')
            file.write('\t\t\t\t\t\t\t\t<class>referenceweapon</class>\n')
            file.write(f'\t\t\t\t\t\t\t\t<recordname>reference.weapon.{name_lower}@4E Basic Weapons</recordname>\n')
            file.write('\t\t\t\t\t\t\t</link>\n')
            file.write(f'\t\t\t\t\t\t\t<name type="string">{entry_dict["name"]}</name>\n')
            file.write(f'\t\t\t\t\t\t\t<profbonus type="number">{entry_dict["profbonus"]}</profbonus>\n')
            file.write(f'\t\t\t\t\t\t\t<range type="number">{entry_dict["range"]}</range>\n')
            file.write(f'\t\t\t\t\t\t\t<cost type="string">{entry_dict["cost"]}</cost>\n')
            file.write(f'\t\t\t\t\t\t\t<weight type="string">{entry_dict["weight"]}</weight>\n')
            file.write(f'\t\t\t\t\t\t\t<group type="string">{entry_dict["group"]}</group>\n')
            file.write(f'\t\t\t\t\t\t\t<properties type="string">{entry_dict["properties"]}</properties>\n')
            file.write(f'\t\t\t\t\t\t\t<damage type="string">{entry_dict["damage"]}</damage>\n')
            file.write(f'\t\t\t\t\t\t</a{entry_str}{name_lower}>\n')

        # Close out the last section
        file.write('\t\t\t\t\t</weapons>\n')
        file.write(f'\t\t\t\t</section{section_str}>\n')

        # Close out Item List part
        file.write('\t\t\t</groups>\n')
        file.write('\t\t</core>\n')
        file.write('\t</weaponlists>\n')

        file.write('</root>\n')

        return str(item_id)

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

    # List of possible Weapon properties
    properties_list = ['^Brutal 1', '^Brutal 2', '^Defensive', '^Heavy Thrown', '^High Crit', '^Light Thrown', '^Load Free', '^Load Minor', '^Load Move', '^Load Standard', '^Off-Hand', '^Reach[^i]', '^Small', '^Stout', '^Versatile']

    for i, row in enumerate(db, start=1):

        # Parse the HTML text 
        html = row['Txt']
        html = html.replace('\\r\\n','\r\n').replace('\\','')
        parsed_html = BeautifulSoup(html, features="html.parser")

        # Retrieve the data with dedicated columns
        name_str =  row['Name'].replace('\\', '')

        # Initialize the other tag data
        category_str = ''
        cost_str = ''
        damage_str = ''
        description_str = ''
        group_str = ''
        heft_str = ''
        prof_str = ''
        profbonus_str = ''
        properties_str = ''
        range_str = ''
        section_id = 100
        type_str = ''
        weight_str = ''

        # Type - Basic weapons and Superior implements
        # brute force the Type/Heft
        if type_lbl := parsed_html.find(string=re.compile('^(Simple|Military|Superior|Improvised.*handed.*weapon).*')):
            type_lbl = re.sub(' *$', '', type_lbl)
            if type_lbl == 'Simple one-handed melee weapon':
                section_id = 1
                prof_str = 'Simple'
                type_str = 'Melee'
                heft_str = 'One-Handed'
            elif type_lbl == 'Simple two-handed melee weapon':
                section_id = 2
                prof_str = 'Simple'
                type_str = 'Melee'
                heft_str = 'Two-Handed'
            elif type_lbl == 'Military one-handed melee weapon':
                section_id = 3
                prof_str = 'Military'
                type_str = 'Melee'
                heft_str = 'One-Handed'
            elif type_lbl == 'Military two-handed melee weapon':
                section_id = 4
                prof_str = 'Military'
                type_str = 'Melee'
                heft_str = 'Two-Handed'
            elif type_lbl == 'Superior one-handed melee weapon':
                section_id = 5
                prof_str = 'Superior'
                type_str = 'Melee'
                heft_str = 'One-Handed'
            elif type_lbl == 'Superior two-handed melee weapon':
                section_id = 6
                prof_str = 'Superior'
                type_str = 'Melee'
                heft_str = 'Two-Handed'
            # Garotte typo
            elif type_lbl == 'Superior two-handed  weapon':
                section_id = 6
                prof_str = 'Superior'
                type_str = 'Melee'
                heft_str = 'Two-Handed'
            elif type_lbl == 'Superior double melee weapon':
                section_id = 7
                prof_str = 'Superior'
                type_str = 'Melee'
                heft_str = 'Double'
            elif type_lbl == 'Improvised one-handed melee weapon':
                section_id = 8
                prof_str = 'Improvised'
                type_str = 'Melee'
                heft_str = 'One-Handed'
            elif type_lbl == 'Improvised two-handed melee weapon':
                section_id = 9
                prof_str = 'Improvised'
                type_str = 'Melee'
                heft_str = 'Two-Handed'
            elif type_lbl == 'Simple one-handed ranged weapon':
                section_id = 10
                prof_str = 'Simple'
                type_str = 'Ranged'
                heft_str = 'One-Handed'
            elif type_lbl == 'Simple two-handed ranged weapon':
                section_id = 11
                prof_str = 'Simple'
                type_str = 'Ranged'
                heft_str = 'Two-Handed'
            elif type_lbl == 'Military one-handed ranged weapon':
                section_id = 12
                prof_str = 'Military'
                type_str = 'Ranged'
                heft_str = 'One-Handed'
            elif type_lbl == 'Military two-handed ranged weapon':
                section_id = 13
                prof_str = 'Military'
                type_str = 'Ranged'
                heft_str = 'Two-Handed'
            elif type_lbl == 'Superior one-handed ranged weapon':
                section_id = 14
                prof_str = 'Superior'
                type_str = 'Ranged'
                heft_str = 'One-Handed'
            elif type_lbl == 'Superior two-handed ranged weapon':
                section_id = 15
                prof_str = 'Superior'
                type_str = 'Ranged'
                heft_str = 'Two-Handed'
            elif type_lbl == 'Improvised one-handed ranged weapon':
                section_id = 16
                prof_str = 'Improvised'
                type_str = 'Ranged'
                heft_str = 'One-Handed'
            elif type_lbl == 'Improvised two-handed ranged weapon':
                section_id = 17
                prof_str = 'Improvised'
                type_str = 'Ranged'
                heft_str = 'Two-Handed'
            else:
                section_id = 100
                type_str = type_lbl

        # Records to be processed
        if section_id < 99:
            print(str(i) + ' ' + name_str)

            # Cost
            if cost_lbl := parsed_html.find(string=re.compile('^Cost:.*')):
                cost_str = re.sub('[^\.\d]', '', cost_lbl.string.replace('5 sp', '0.5 gp'))
            elif cost_lbl := parsed_html.find(string='Price'):
                cost_str = re.sub('[^\.\d]', '', cost_lbl.parent.next_sibling.replace('5 sp', '0.5 gp'))

            # Damage
            if damage_lbl := parsed_html.find(string='Damage'):
                damage_str = damage_lbl.parent.next_sibling.replace(': ', '')

            # Description
            # implements have a description tag
            if description_lbl := parsed_html.find(string='Description'):
                description_str = description_lbl.parent.next_sibling.replace(': ', '')
            # otherwise look for a 'detail' div
            elif detail_div := parsed_html.find('div', id='detail'):
                for el_str in detail_div.stripped_strings:
                    # if we hit these we have gone too far
                    if re.search('^(Properties|Published|' + group_str + ')', el_str):
                        break
                    # skip over these ones
                    if re.search('^(:|Cost|Damage|Group|Range|Weight|Proficient|' + name_str + '|' + type_lbl + ')', el_str):
                        continue
                    # otherwise append non-empty values to the Description
                    if re.sub('\s', '', el_str) != '':
                        description_str += '\\n' if description_str != '' else ''
                        description_str += re.sub('^[:\s]*', '', el_str)

            # Description (Published In)
            if description_lbl := parsed_html.find('p', class_='publishedIn'):
                description_str += re.sub('\s\s', ' ', description_lbl.text) if description_str == '' else '\\n' + re.sub('\s\s', ' ', description_lbl.text)

            # clean up extraneous spaces
            description_str = re.sub('\s\s', ' ', description_str.strip())

            # Group
            if group_lbl := parsed_html.find(string='Group'):
                group_str = group_lbl.parent.next_sibling.next_sibling.next_sibling.replace(' (', '')

            # Proficiency Bonus
            if profbonus_lbl := parsed_html.find(string=re.compile('^Proficient:.*')):
                profbonus_str = int(profbonus_lbl.string.replace('Proficient: ', ''))

            # Properties
            # might get false positives as it's just checking each property regex against the whole text
            for prop in properties_list:
                if properties_lbl := parsed_html.find(string=re.compile(prop + '.*')):
                    properties_str += '\\n' if properties_str != '' else ''
                    properties_str += prop.replace('[^i]', '').replace('\\', '').replace('^', '')

            # Range
            # strip the heading and long range bracket
            if range_lbl := parsed_html.find(string=re.compile('^Range:.*')):
                range_str = re.sub('(Range: |-|/.*)', '', range_lbl.string)
                if range_str != '':
                    range_str = int(range_str)

            # Weight
            # might have a separate bold label
            if weight_lbl := parsed_html.find(string='Weight'):
                weight_str = weight_lbl.parent.next_sibling.replace(': ', '').replace('1/10', '0.1').replace('1/2', '0.5').replace(' lb.', '').replace(' lb', '')
            # might be inside a single tag
            elif weight_lbl := parsed_html.find(string=re.compile('^Weight:.*')):
                weight_str = weight_lbl.string.replace('Weight: ', '').replace('1–', '').replace('6–', '').replace('—', '0').replace('1/10', '0.1').replace('1/2', '0.5').replace(' lb.', '').replace(' lb', '')

            # Build the item dictionary
            export_dict = {}
            export_dict['cost'] = float(cost_str) if cost_str != '' else 0
            export_dict['damage'] = damage_str
            export_dict['description'] = re.sub('’', '\'', description_str)
            export_dict['group'] = group_str
            export_dict['heft'] = heft_str
            export_dict['name'] = re.sub('’', '\'', name_str)
            export_dict['prof'] = prof_str
            export_dict['profbonus'] = profbonus_str
            export_dict['properties'] = properties_str
            export_dict['range'] = range_str
            export_dict['section_id'] = section_id
            export_dict['type'] = type_str
            export_dict['weight'] = float(weight_str) if weight_str != '' else 0

            # Append a copy of generated item dictionary
            export_list.append(copy.deepcopy(export_dict))

    print(str(len(db)) + " entries parsed.")
    print(str(len(export_list)) + " export entries.")

    # Write FG XML database files
    write_id = write_lib('export/basic_weapons/data/client.xml', export_list)

    print(write_id + " module entries written. Job done.")

    try:
        os.remove('export/mods/4E_Basic_Weapons.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/mods/4E_Basic_Weapons', 'zip', 'export/basic_weapons/data/')
        os.rename('export/mods/4E_Basic_Weapons.zip', 'export/mods/4E_Basic_Weapons.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\mods' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\basic_weapon\\data' folder to create the mod.")
        print("Rename the complete filename (including extension) to '4E_Basic_Weapons.mod'.\n")

    input('Press enter to close.')
