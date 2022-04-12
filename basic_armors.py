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

        ac_str = ''
        checkpenalty_str = ''
        class_str = ''
        cost_str = ''
        flavor_str = ''
        min_enhance_str = ''
        mitype_str = ''
        special_str = ''
        speed_str = ''
        subclass_str = ''
        weight_str = ''

        # Class - Basic armors
        # use Subclass to denote Light/Heavy
        if class_lbl := parsed_html.find(string='Type'):
            class_str = class_lbl.parent.next_sibling.replace(': ', '')
            if re.search('(Cloth|Leather|Hide)', class_str):
                subclass_str = 'Light'
            elif re.search('Chainmail|Scale|Plate', class_str):
                subclass_str = 'Heavy'
            mitype_str = 'armor'

        # Class - Barding
        # use Subclass to denote Light/Heavy
        if re.search('^(Light|Heavy) Barding.*', name_str):
            class_str = 'Barding'
            subclass_str = re.search(r'(Light|Heavy)', name_str).group(1)
            mitype_str = 'armor'

        if mitype_str != '':
            print(str(i) + ' ' + name_str)

            # AC
            if ac_lbl := parsed_html.find(string='AC Bonus'):
                ac_str = int(ac_lbl.parent.next_sibling.replace(': ', ''))

            # Check Penalty
            if checkpenalty_lbl := parsed_html.find(string='Check'):
                checkpenalty_str = int(checkpenalty_lbl.parent.next_sibling.replace(': ', ''))

            # Cost
            if cost_lbl := parsed_html.find(string='Cost'):
                cost_str = re.sub('(: |\.00|,|\.$)', '', cost_lbl.parent.next_sibling)
            elif cost_lbl := parsed_html.find(string='Price'):
                cost_str = re.sub('(: |\.00|,| $)', '', cost_lbl.parent.next_sibling)

            # Flavor (Description)
            if flavor_lbl := parsed_html.find(string='Description'):
                for el_str in flavor_lbl.parent.next_siblings:
                    if el_str.string:
                        # if we hit this we have gone too far
                        if re.search('^(AC|Weight)', el_str.string):
                            break
                        # otherwise append non-empty values to the Flavor
                        if re.sub('\s', '', el_str.string) != '':
                            flavor_str += '\\n' if flavor_str != '' else ''
                            flavor_str += re.sub('^[:\s]*', '', el_str.string)
            # clean up extraneous spaces
            flavor_str = re.sub('\s\s', ' ', flavor_str.strip())

            # Minimum Enhancement Value
            if min_enhance_lbl := parsed_html.find(string='Minimum Enhancement Value'):
                min_enhance_str = int(min_enhance_lbl.parent.next_sibling.replace(': ', ''))

            # Special (Properties)
            if special_lbl := parsed_html.find(string='Special'):
                special_str = special_lbl.parent.next_sibling.replace(': ', '')

            # Special (Published In)
            if special_lbl := parsed_html.find('p', class_='publishedIn'):
                special_str += '\\n' if special_str != '' else ''
                special_str += special_lbl.text

            # Speed Penalty
            if speed_lbl := parsed_html.find(string='Speed'):
                speed_str = int(speed_lbl.parent.next_sibling.replace(': ', ''))

            # Weight
            if weight_lbl := parsed_html.find(string='Weight'):
                weight_str = '{:g}'.format(float(weight_lbl.parent.next_sibling.replace(': ', '').replace('1/10', '0.1').replace('1/2', '0.5').replace(' lb.', '').replace(' lb', '')))

            # Build the item entry
            export_item = {}
            export_item['ac'] = ac_str
            export_item['checkpenalty'] = checkpenalty_str
            export_item['class'] = class_str
            export_item['cost'] = cost_str
            export_item['flavor'] = flavor_str
            export_item['min_enhance'] = min_enhance_str
            export_item['mitype'] = mitype_str
            export_item['name'] = name_str
            export_item['special'] = special_str
            export_item['speed'] = speed_str
            export_item['subclass'] = subclass_str
            export_item['weight'] = weight_str

            # Append a copy of generated entry
            export_list.append(copy.deepcopy(export_item))

    print(str(len(db)) + " entries parsed.")
    print(str(len(export_list)) + " export entries.")

    # Write FG XML database files
    write_id = write_db('export/basic_armors/data/db.xml', export_list)

    print(str(write_id) + " module entries written. Job done.")

    try:
        os.remove('export/basic_armors/4E_Basic_Armors.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/basic_armors/4E_Basic_Armors', 'zip', 'export/basic_armors/data/')
        os.rename('export/basic_armors/4E_Basic_Armors.zip', 'export/basic_armors/4E_Basic_Armors.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\basic_armors' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\basic_armor\\data' folder to create the mod.")
        print("Rename the complete filename (including path) to '4E_Basic_Armors.mod'.\n")

    input('Press enter to close.')
