import os
import sys
import shutil
import copy
import re
from bs4 import BeautifulSoup, Tag, NavigableString
from helpers.create_db import create_db

def list_sorter(entry):
    section_id = entry["section_id"]
    ac = entry["ac"]
    min_enhance = entry["min_enhance"]
    name = entry["name"]
    return (section_id, ac, min_enhance, name)

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
        file.write('\t\t<armor>\n')

        # Create individual item entries
        for entry_dict in sorted(entry_list, key=list_sorter):
            name_lower = re.sub('\W', '', entry_dict["name"].lower())

            file.write(f'\t\t\t<{name_lower}>\n')
            file.write(f'\t\t\t\t<name type="string">{entry_dict["name"]}</name>\n')
            file.write(f'\t\t\t\t<ac type="number">{entry_dict["ac"]}</ac>\n')
            file.write(f'\t\t\t\t<min_enhance type="number">{entry_dict["min_enhance"]}</min_enhance>\n')
            file.write(f'\t\t\t\t<checkpenalty type="number">{entry_dict["checkpenalty"]}</checkpenalty>\n')
            file.write(f'\t\t\t\t<speed type="number">{entry_dict["speed"]}</speed>\n')
            file.write(f'\t\t\t\t<weight type="number">{entry_dict["weight"]}</weight>\n')
            file.write(f'\t\t\t\t<special type="string">{entry_dict["special"]}</special>\n')
            file.write(f'\t\t\t\t<cost type="number">{entry_dict["cost"]}</cost>\n')
            file.write(f'\t\t\t\t<type type="string">{entry_dict["type"]}</type>\n')
            file.write(f'\t\t\t\t<prof type="string">{entry_dict["prof"]}</prof>\n')
            file.write(f'\t\t\t\t<description type="formattedtext">{entry_dict["description"]}\n\t\t\t\t</description>\n')
            file.write(f'\t\t\t</{name_lower}>\n')

        # Close out the Reference part
        file.write('\t\t</armor>\n')
        file.write('\t</reference>\n')

        # Library part - not dynamic
        # This controls the right-hand menu on the Modules screen
        file.write('\t<library>\n')
        file.write('\t\t<lib4ebasicarmor>\n')
        file.write('\t\t\t<name type="string">4E Basic Armor</name>\n')
        file.write('\t\t\t<categoryname type="string">4E Core</categoryname>\n')
        file.write('\t\t\t<entries>\n')
        file.write('\t\t\t\t<a0002armor>\n')
        file.write('\t\t\t\t\t<librarylink type="windowreference">\n')
        file.write('\t\t\t\t\t\t<class>reference_classarmortablelist</class>\n')
        file.write('\t\t\t\t\t\t<recordname>armorlists.core@4E Basic Armor</recordname>\n')
        file.write('\t\t\t\t\t</librarylink>\n')
        file.write('\t\t\t\t\t<name type="string">Items - Armor</name>\n')
        file.write('\t\t\t\t</a0002armor>\n')
        file.write('\t\t\t</entries>\n')
        file.write('\t\t</lib4ebasicarmor>\n')
        file.write('\t</library>\n')

        # counters for Item List
        section_id = 0
        item_id = 0

        # Item List part
        # This controls the table that appears when you click on a Library menu
        file.write('\t<armorlists>\n')
        file.write('\t\t<core>\n')
        file.write('\t\t\t<description type="string">Armor Table</description>\n')
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
                    file.write('\t\t\t\t\t</armors>\n')
                    file.write(f'\t\t\t\t</section{section_str}>\n')
                section_str = "000"[0:len("000")-len(str(section_id))] + str(section_id)
                file.write(f'\t\t\t\t<section{section_str}>\n')
                file.write(f'\t\t\t\t\t<description type="string">{entry_dict["prof"]} ({entry_dict["type"]})</description>\n')
                file.write('\t\t\t\t\t<armors>\n')

            file.write(f'\t\t\t\t\t\t<a{entry_str}{name_lower}>\n')
            file.write('\t\t\t\t\t\t\t<link type="windowreference">\n')
            file.write('\t\t\t\t\t\t\t\t<class>referencearmor</class>\n')
            file.write(f'\t\t\t\t\t\t\t\t<recordname>reference.armor.{name_lower}@4E Basic Armor</recordname>\n')
            file.write('\t\t\t\t\t\t\t</link>\n')
            file.write(f'\t\t\t\t\t\t\t<name type="string">{entry_dict["name"]}</name>\n')
            file.write(f'\t\t\t\t\t\t\t<ac type="number">{entry_dict["ac"]}</ac>\n')
            file.write(f'\t\t\t\t\t\t\t<min_enhance type="number">{entry_dict["min_enhance"]}</min_enhance>\n')
            file.write(f'\t\t\t\t\t\t\t<checkpenalty type="number">{entry_dict["checkpenalty"]}</checkpenalty>\n')
            file.write(f'\t\t\t\t\t\t\t<speed type="number">{entry_dict["speed"]}</speed>\n')
            file.write(f'\t\t\t\t\t\t\t<weight type="number">{entry_dict["weight"]}</weight>\n')
            file.write(f'\t\t\t\t\t\t\t<special type="string">{entry_dict["special"]}</special>\n')
            file.write(f'\t\t\t\t\t\t\t<cost type="number">{entry_dict["cost"]}</cost>\n')
            file.write(f'\t\t\t\t\t\t</a{entry_str}{name_lower}>\n')

        # Close out the last section
        file.write('\t\t\t\t\t</armors>\n')
        file.write(f'\t\t\t\t</section{section_str}>\n')

        # Close out Item List part
        file.write('\t\t\t</groups>\n')
        file.write('\t\t</core>\n')
        file.write('\t</armorlists>\n')

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

    for i, row in enumerate(db, start=1):

        # Parse the HTML text 
        html = row['Txt']
        html = html.replace('\\r\\n','\r\n').replace('\\','')
        parsed_html = BeautifulSoup(html, features="html.parser")

        # Retrieve the data with dedicated columns
        name_str =  row['Name'].replace('\\', '')

        # Initialize the other tag data
        ac_str = ''
        checkpenalty_str = ''
        cost_str = ''
        description_str = ''
        min_enhance_str = ''
        prof_str = ''
        section_id = 100
        special_str = ''
        speed_str = ''
        type_str = ''
        weight_str = ''

        # Prof - Armor
        # use Type to denote Light/Heavy
        if prof_lbl := parsed_html.find(string='Type'):
            prof_str = prof_lbl.parent.next_sibling.replace(': ', '')
            if prof_str == 'Cloth':
                section_id = 1
                prof_str = 'Cloth Armor'
                type_str = 'Light'
            elif prof_str == 'Leather':
                section_id = 2
                prof_str = 'Leather Armor'
                type_str = 'Light'
            elif prof_str == 'Hide':
                section_id = 3
                prof_str = 'Hide Armor'
                type_str = 'Light'
            elif prof_str == 'Chainmail':
                section_id = 4
                type_str = 'Heavy'
            elif prof_str == 'Scale':
                section_id = 5
                prof_str = 'Scale Armor'
                type_str = 'Heavy'
            elif prof_str == 'Plate':
                section_id = 6
                prof_str = 'Plate Armor'
                type_str = 'Heavy'
            else:
                section_id = 100

        # Prof - Barding
        # use Type to denote Normal/Huge
        if name_str == 'Light Barding':
            section_id = 7
            prof_str = 'Barding'
            type_str = 'Normal Creature'
        elif name_str == 'Heavy Barding':
            section_id = 7
            prof_str = 'Barding'
            type_str = 'Normal Creature'
        elif name_str == 'Light Barding (Huge creature)':
            section_id = 8
            prof_str = 'Barding'
            type_str = 'Huge Creature'
        elif name_str == 'Heavy Barding (Huge creature)':
            section_id = 8
            prof_str = 'Barding'
            type_str = 'Huge Creature'

        if section_id < 99:
            print(str(i) + ' ' + name_str)

            # AC
            if ac_lbl := parsed_html.find(string='AC Bonus'):
                ac_str = ac_lbl.parent.next_sibling.replace(': ', '')

            # Check Penalty
            if checkpenalty_lbl := parsed_html.find(string='Check'):
                checkpenalty_str = checkpenalty_lbl.parent.next_sibling.replace(': ', '')

            # Cost
            if cost_lbl := parsed_html.find(string='Price'):
                cost_str = re.sub('[^\.\d]', '', cost_lbl.parent.next_sibling)
            elif cost_lbl := parsed_html.find(string='Cost'):
                cost_str = re.sub('[^\.\d]', '', cost_lbl.parent.next_sibling)
            elif cost_lbl := parsed_html.find(string=re.compile('^Cost:.*')):
                cost_str = re.sub('[^\.\d]', '', cost_lbl.string)

            if cost_str != '':
                # Divide by 100 if cost is in cp
                if re.search(r'cp', cost_str):
                    cost_str = '0.0' + re.sub('[^\.\d]', '', cost_str)
                # Divide by 10 if cost is in sp
                elif re.search(r'sp', cost_lbl):
                    cost_str = '0.' + re.sub('[^\.\d]', '', cost_str)

            # Description
            if description_lbl := parsed_html.find(string='Description'):
                for el_str in description_lbl.parent.next_siblings:
                    if el_str.string:
                        # if we hit this we have gone too far
                        if re.search('^(AC|Weight)', el_str.string):
                            break
                        # otherwise append non-empty values to the Description
                        if re.sub('\s', '', el_str.string) != '':
                            description_str += '\\n' if description_str != '' else ''
                            description_str += re.sub('^[:\s]*', '', el_str.string)
            # Description (Published In)
            if special_lbl := parsed_html.find('p', class_='publishedIn'):
                description_str += re.sub('\s\s', ' ', special_lbl.text) if description_str == '' else '\\n' + re.sub('\s\s', ' ', special_lbl.text)
            # clean up extraneous spaces
            description_str = re.sub('\s\s', ' ', description_str.strip())

            # Minimum Enhancement Value
            if min_enhance_lbl := parsed_html.find(string='Minimum Enhancement Value'):
                min_enhance_str = min_enhance_lbl.parent.next_sibling.replace(': ', '')

            # Special (Properties)
            if special_lbl := parsed_html.find(string='Special'):
                special_str = special_lbl.parent.next_sibling.replace(': ', '')

            # Speed Penalty
            if speed_lbl := parsed_html.find(string='Speed'):
                speed_str = speed_lbl.parent.next_sibling.replace(': ', '')

            # Weight
            if weight_lbl := parsed_html.find(string='Weight'):
                weight_str = weight_lbl.parent.next_sibling.replace(': ', '').replace('1/10', '0.1').replace('1/2', '0.5').replace(' lb.', '').replace(' lb', '')

            # Build the item entry
            export_dict = {}
            export_dict['ac'] = int(ac_str) if ac_str != '' else 0
            export_dict['checkpenalty'] = int(checkpenalty_str) if checkpenalty_str != '' else 0
            export_dict['cost'] = float(cost_str) if cost_str != '' else 0
            export_dict['description'] = re.sub('’', '\'', description_str)
            export_dict['min_enhance'] = int(min_enhance_str) if min_enhance_str != '' else 0
            export_dict['name'] = re.sub('’', '\'', name_str)
            export_dict['prof'] = prof_str
            export_dict['section_id'] = section_id
            export_dict['special'] = special_str
            export_dict['speed'] = speed_str
            export_dict['type'] = type_str
            export_dict['weight'] = float(weight_str) if weight_str != '' else 0

            # Append a copy of generated entry
            export_list.append(copy.deepcopy(export_dict))

    print(str(len(db)) + " entries parsed.")
    print(str(len(export_list)) + " export entries.")

    # Write FG XML database files
    write_id = write_lib('export/basic_armor/data/client.xml', export_list)

    print(str(write_id) + " module entries written. Job done.")

    try:
        os.remove('export/mods/4E_Basic_Armor.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/mods/4E_Basic_Armor', 'zip', 'export/basic_armor/data/')
        os.rename('export/mods/4E_Basic_Armor.zip', 'export/mods/4E_Basic_Armor.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\mods' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\basic_armor\\data' folder to create the mod.")
        print("Rename the complete filename (including path) to '4E_Basic_Armor.mod'.\n")

    input('Press enter to close.')
