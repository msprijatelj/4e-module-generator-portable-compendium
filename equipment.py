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
        file.write('\t\t<equipment>\n')

        # Create individual item entries
        for entry_dict in sorted(entry_list, key=list_sorter):
            name_lower = re.sub('\W', '', entry_dict["name"].lower())

            file.write(f'\t\t\t<{name_lower}>\n')
            file.write(f'\t\t\t\t<name type="string">{entry_dict["name"]}</name>\n')
            file.write(f'\t\t\t\t<weight type="number">{entry_dict["weight"]}</weight>\n')
            file.write(f'\t\t\t\t<cost type="number">{entry_dict["cost"]}</cost>\n')
            file.write(f'\t\t\t\t<type type="string">{entry_dict["type"]}</type>\n')
            file.write(f'\t\t\t\t<subtype type="string">{entry_dict["subtype"]}</subtype>\n')
            file.write(f'\t\t\t\t<description type="formattedtext">{entry_dict["description"]}\n\t\t\t\t</description>\n')
            file.write(f'\t\t\t</{name_lower}>\n')

        # Close out the Reference part
        file.write('\t\t</equipment>\n')
        file.write('\t</reference>\n')

        # Library part - not dynamic
        # This controls the right-hand menu on the Modules screen
        file.write('\t<library>\n')
        file.write('\t\t<lib4eequipment>\n')
        file.write('\t\t\t<name type="string">4E Equipment</name>\n')
        file.write('\t\t\t<categoryname type="string">4E Core</categoryname>\n')
        file.write('\t\t\t<entries>\n')
        file.write('\t\t\t\t<a0001equipment>\n')
        file.write('\t\t\t\t\t<librarylink type="windowreference">\n')
        file.write('\t\t\t\t\t\t<class>reference_classequipmenttablelist</class>\n')
        file.write('\t\t\t\t\t\t<recordname>equipmentlists.core@4E Equipment</recordname>\n')
        file.write('\t\t\t\t\t</librarylink>\n')
        file.write('\t\t\t\t\t<name type="string">Items - Equipment</name>\n')
        file.write('\t\t\t\t</a0001equipment>\n')
        file.write('\t\t\t</entries>\n')
        file.write('\t\t</lib4eequipment>\n')
        file.write('\t</library>\n')

        # counters for Item List
        item_id = 0
        section_id = 0

        # Item List part
        # This controls the table that appears when you click on a Library menu
        file.write('\t<equipmentlists>\n')
        file.write('\t\t<core>\n')
        file.write('\t\t\t<description type="string">Equipment Table</description>\n')
        file.write('\t\t\t<groups>\n')

        # Create individual item entries
        for entry_dict in sorted(entry_list, key=list_sorter):
            item_id += 1
            name_lower = re.sub('\W', '', entry_dict["name"].lower())

            #Check for new section
            if entry_dict["section_id"] != section_id:
                section_id = entry_dict["section_id"]
                if section_id != 1:
                    section_str = "000"[0:len("000")-len(str(section_id - 1))] + str(section_id - 1)
                    file.write('\t\t\t\t\t</equipments>\n')
                    file.write(f'\t\t\t\t</section{section_str}>\n')
                section_str = "000"[0:len("000")-len(str(section_id))] + str(section_id)
                file.write(f'\t\t\t\t<section{section_str}>\n')
                file.write(f'\t\t\t\t\t<description type="string">{entry_dict["type"]}</description>\n')
                file.write(f'\t\t\t\t\t<subdescription type="string">{entry_dict["subtype"]}</subdescription>\n')
                file.write('\t\t\t\t\t<equipments>\n')

            file.write(f'\t\t\t\t\t\t<{name_lower}>\n')
            file.write('\t\t\t\t\t\t\t<link type="windowreference">\n')
            file.write('\t\t\t\t\t\t\t\t<class>referenceequipment</class>\n')
            file.write(f'\t\t\t\t\t\t\t\t<recordname>reference.equipment.{name_lower}@4E Equipment</recordname>\n')
            file.write('\t\t\t\t\t\t\t</link>\n')
            file.write(f'\t\t\t\t\t\t\t<name type="string">{entry_dict["name"]}</name>\n')
            file.write(f'\t\t\t\t\t\t\t<weight type="number">{entry_dict["weight"]}</weight>\n')
            file.write(f'\t\t\t\t\t\t\t<cost type="number">{entry_dict["cost"]}</cost>\n')
            file.write(f'\t\t\t\t\t\t</{name_lower}>\n')

        # Close out the last section
        file.write('\t\t\t\t\t</equipments>\n')
        file.write(f'\t\t\t\t</section{section_str}>\n')

        # Close out Item List part
        file.write('\t\t\t</groups>\n')
        file.write('\t\t</core>\n')
        file.write('\t</equipmentlists>\n')

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

        cost_str = ''
        description_str = ''
        section_id = 100
        special_str = ''
        subtype_str = ''
        type_str = ''
        weight_str = ''


        #Type & Subtype
        if subtype_lbl := parsed_html.find(string='Category'):
            subtype_str = subtype_lbl.parent.next_sibling.replace(': ', '')
            # label as Gear if missing 'Category' value
            if subtype_str == 'Gear' or subtype_str == '':
                subtype_str = 'General items'

        if subtype_str == 'General items':
            section_id = 1
            type_str = 'Adventuring Gear'
        elif subtype_str == 'Component':
            section_id = 2
            type_str = 'Adventuring Gear'
        elif subtype_str == 'Ammunition':
            section_id = 3
            type_str = 'Adventuring Gear'
        elif subtype_str == 'Musical Instrument':
            section_id = 4
            type_str = 'Adventuring Gear'
        elif subtype_str == 'Food':
            section_id = 5
            type_str = 'Food, Drink, Lodging'
        elif subtype_str == 'Drink':
            section_id = 6
            type_str = 'Food, Drink, Lodging'
        elif subtype_str == 'Lodging':
            section_id = 7
            type_str = 'Food, Drink, Lodging'
        elif subtype_str == 'Building':
            section_id = 8
            type_str = 'Food, Drink, Lodging'
        elif subtype_str == 'Mount':
            section_id = 9
            type_str = 'Mounts and Transport'
        elif subtype_str == 'Transportation':
            section_id = 10
            type_str = 'Mounts and Transport'
        elif subtype_str == 'Service':
            section_id = 11
            type_str = 'Service'
        elif subtype_str != '':
            section_id = 12
            type_str = 'unknown'
        elif subtype_str == 'Implement':
            section_id = 13

        if section_id < 99:
            print(str(i) + ' ' + name_str)

            # Cost
            if cost_lbl := parsed_html.find(string=re.compile('^Cost:.*')):
                # Divide by 100 if cost is in cp
                if re.search(r'cp', cost_lbl):
                    cost_str = '0.0' + re.sub('[^\.\d]', '', cost_lbl.string)
                # Divide by 100 if cost is in cp
                elif re.search(r'sp', cost_lbl):
                    cost_str = '0.' + re.sub('[^\.\d]', '', cost_lbl.string)
                else:
                    cost_str = re.sub('[^\.\d]', '', cost_lbl.string)
            if cost_lbl := parsed_html.find(string='Price'):
                # Divide by 100 if cost is in cp
                if re.search(r'cp', cost_lbl.parent.next_sibling):
                    cost_str = '0.0' + re.sub('[^\.\d]', '', cost_lbl.parent.next_sibling)
                # Divide by 100 if cost is in cp
                elif re.search(r'sp', cost_lbl.parent.next_sibling):
                    cost_str = '0.' + re.sub('[^\.\d]', '', cost_lbl.parent.next_sibling)
                else:
                    cost_str = re.sub('[^\.\d]', '', cost_lbl.parent.next_sibling)

            # Description
            if description_lbl := parsed_html.find(string='Description'):
                for el_str in description_lbl.parent.next_siblings:
                    if el_str.string:
                        # if we hit this we have gone too far
                        if re.search('vs AC', el_str.string):
                            break
                        # otherwise append non-empty values to the Flavor
                        if re.sub('\s', '', el_str.string) != '':
                            description_str += '\\n' if description_str != '' else ''
                            description_str += re.sub('^[:\s]*', '', el_str.string)

            # Description (Published In)
            if description_lbl := parsed_html.find('p', class_='publishedIn'):
                description_str += re.sub('\s\s', ' ', description_lbl.text) if description_str == '' else '\\n' + re.sub('\s\s', ' ', description_lbl.text)

            # clean up extraneous spaces
            description_str = re.sub('\s\s', ' ', description_str.strip())

            # Weight
            if weight_lbl := parsed_html.find(string='Weight'):
                weight_str = '{:g}'.format(float(weight_lbl.parent.next_sibling.replace(': ', '').replace('1/10', '0.1').replace('1/2', '0.5').replace(' lb.', '').replace(' lb', '')))

            # Build the item entry
            export_dict = {}
            export_dict['cost'] = float(cost_str) if cost_str != '' else 0
            export_dict['description'] = re.sub('’', '\'', description_str)
            export_dict['name'] = re.sub('’', '\'', name_str)
            export_dict['section_id'] = section_id
            export_dict['special'] = special_str
            export_dict['type'] = type_str
            export_dict['subtype'] = subtype_str
            export_dict['weight'] = float(weight_str) if weight_str != '' else 0

            # Append a copy of generated entry
            export_list.append(copy.deepcopy(export_dict))

    print(str(len(db)) + " entries parsed.")
    print(str(len(export_list)) + " export entries.")

    # Write FG XML database files
    write_id = write_lib('export/equipment/data/client.xml', export_list)

    print(str(write_id) + " module entries written. Job done.")

    try:
        os.remove('export/mods/4E_Equipment.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/mods/4E_Equipment', 'zip', 'export/equipment/data/')
        os.rename('export/mods/4E_Equipment.zip', 'export/mods/4E_Equipment.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\mods' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\equipment\\data' folder to create the mod.")
        print("Rename the complete filename (including path) to '4E_Equipment.mod'.\n")

    input('Press enter to close.')
