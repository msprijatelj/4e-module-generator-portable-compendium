import os
import sys
import shutil
import copy
import re
from helpers.create_db import create_db
from bs4 import BeautifulSoup, Tag, NavigableString

def write_db(filepath, fg_data):
    with open(filepath, mode='w', encoding='UTF-8', errors='strict', buffering=1) as file:
        # item counter
        id = 0

        file.write('<root version="2.9">\n')
        file.write('\t<item>\n')
        for entry in fg_data:
            id += 1
            entrry_id = "00000"[0:len("00000")-len(str(id))] + str(id)
            file.write(f'\t\t<id-{entrry_id}>\n')

            for tag in sorted(entry.keys()):
                if entry[tag] != '':
                    # choose the write statement depending on the 'type' attribute
                    if re.search('^(powers|props)$', tag):
                        file.write(f'\t\t\t<{tag}>{entry[tag]}</{tag}>\n')
                    elif re.search('^(ac|bonus|checkpenalty|level|min_enhance|profbonus|range|speed|weight)$', tag):
                        file.write(f'\t\t\t<{tag} type="number">{entry[tag]}</{tag}>\n')
                    else:
                        file.write(f'\t\t\t<{tag} type="string">{entry[tag]}</{tag}>\n')

            file.write(f'\t\t</id-{entrry_id}>\n')
        file.write('\t</item>\n')
        file.write('</root>')
        return str(id)

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

    for i, row in enumerate(db):

        # Parse the HTML text 
        html = row['Txt']
        html = html.replace('\\r\\n','\r\n').replace('\\','')
        parsed_html = BeautifulSoup(html, features="html.parser")

        # Retrieve the data with dedicated columns
        name_str =  row['Name'].replace('\\', '')

        class_str = ''
        cost_str = ''
        flavor_str = ''
        mitype_str = ''
        special_str = ''
        weight_str = ''

        # Class - Basic items
        # exclude basic implements as they are in the weapons script
        if not(re.search('(Implement$|Holy Symbol|Ki Focus|Totem)', name_str)):
            if class_lbl := parsed_html.find(string='Category'):
                class_str = class_lbl.parent.next_sibling.replace(': ', '')
                # label as Gear if missing 'Category' value
                if class_str == '':
                    class_str = 'Gear'
                mitype_str = 'other'

        if mitype_str != '':
            print(str(i) + ' ' + name_str)

            # Cost
            if cost_lbl := parsed_html.find(string=re.compile('^Cost:.*')):
                cost_str = re.sub('(Cost: |\.00|,| $)', '', cost_lbl.string)
            if cost_lbl := parsed_html.find(string='Price'):
                cost_str = re.sub('(: |\.00|,| $)', '', cost_lbl.parent.next_sibling)

            # Flavor (Description)
            if flavor_lbl := parsed_html.find(string='Description'):
                for el_str in flavor_lbl.parent.next_siblings:
                    if el_str.string:
                        # if we hit this we have gone too far
                        if re.search('vs AC', el_str.string):
                            break
                        # otherwise append non-empty values to the Flavor
                        if re.sub('\s', '', el_str.string) != '':
                            flavor_str += '\\n' if flavor_str != '' else ''
                            flavor_str += re.sub('^[:\s]*', '', el_str.string)
            # clean up extraneous spaces
            flavor_str = re.sub('\s\s', ' ', flavor_str.strip())

            # Special (Published In)
            if special_lbl := parsed_html.find('p', class_='publishedIn'):
                special_str = re.sub('\s\s', ' ', special_lbl.text)

            # Weight
            if weight_lbl := parsed_html.find(string='Weight'):
                weight_str = '{:g}'.format(float(weight_lbl.parent.next_sibling.replace(': ', '').replace('1/10', '0.1').replace('1/2', '0.5').replace(' lb.', '').replace(' lb', '')))

            # Build the item entry
            export_item = {}
            export_item['class'] = class_str
            export_item['cost'] = cost_str
            export_item['flavor'] = flavor_str
            export_item['mitype'] = mitype_str
            export_item['name'] = name_str
            export_item['special'] = special_str
            export_item['weight'] = weight_str

            # Append a copy of generated entry
            export_list.append(copy.deepcopy(export_item))

    print(str(len(db)) + " entries parsed.")
    print(str(len(export_list)) + " export entries.")

    # Write FG XML database files
    write_id = write_db('export/basic_items/data/db.xml', export_list)

    print(str(write_id) + " module entries written. Job done.")

    try:
        os.remove('export/basic_items/4E_Basic_Items.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/basic_items/4E_Basic_Items', 'zip', 'export/basic_items/data/')
        os.rename('export/basic_items/4E_Basic_Items.zip', 'export/basic_items/4E_Basic_Items.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\basic_items' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\basic_item\\data' folder to create the mod.")
        print("Rename the complete filename (including path) to '4E_Basic_Items.mod'.\n")

    input('Press enter to close.')
