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
        db = create_db('ddiPoison.sql', "','")
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

        class_str = ''
        cost_str = ''
        flavor_str = ''
        level_str = ''
        mitype_str = ''
        powers_str = ''
        shortdescription_str = ''
        special_str = ''

        # Class
        category_str = 'Poison'
        class_str = 'Poison'
        mitype_str = 'other'

        if mitype_str != '':
            print(str(i) + ' ' + name_str)

            multi_bonus = False
            multi_list = []
            multi_dict = {}
            multi_dict['bonus'] = ''
            multi_dict['cost'] = ''
            multi_dict['level'] = ''

            # Cost
            if cost_tag := parsed_html.find(string=re.compile('^' + category_str)):
                if cost_lbl := cost_tag.parent.next_sibling:
                    multi_dict['cost'] = re.search(r'([\d,]*( gp)*$)', cost_lbl).group(1)

            # Level
            if level_lbl := parsed_html.find('span', class_='level'):
                multi_dict['level'] = re.search(r'(\d+)', level_lbl.string).group(1)

            multi_list.append(copy.deepcopy(multi_dict))

            # Flavor
            if flavor_lbl := parsed_html.find('p', class_='flavor'):
                flavor_str = re.sub('\s\s', ' ', flavor_lbl.get_text(separator = '\\n', strip = True))

            # Powers
            tags = parsed_html.find_all(id='detail')
            for tag in tags:
                # concatenate all the elements within each tag
                tag_str = ' '.join(map(str, tag.stripped_strings))
#                print(tag_str)
                # add any lines that look like a power
                power_test = re.search(r'(Attack.*?)(Special|Published)', tag_str)
                if power_test != None:
#                    print(power_test.group(1))
                    shortdescription_str += power_test.group(1) if shortdescription_str == '' else '\\n' + power_test.group(1)
                    shortdescription_str = re.sub('(\s*(First|Second|Aftereffect))', r'\\n\2', shortdescription_str.strip())

                if shortdescription_str != '':
                    powers_str = '\n'
                    powers_str += f'\t\t\t\t<id-00001>\n'
                    powers_str += f'\t\t\t\t\t<shortdescription type="string">{shortdescription_str}</shortdescription>\n'
                    powers_str += f'\t\t\t\t</id-00001>\n'
                    powers_str += '\t\t\t'

            # Special
            tags = parsed_html.find_all(id='detail')
            for tag in tags:
                # concatenate all the elements within each tag
                tag_str = ' '.join(map(str, tag.stripped_strings))
                special_test = re.search(r'Special: (.*?)Published', tag_str)
                if special_test != None:
                    special_str += special_test.group(1)

            # Special (Published In)
            if special_lbl := parsed_html.find(string=re.compile('^Published')):
                special_str += special_lbl.text if special_str == '' else '\\n' + special_lbl.text
                # Granny's Grief workaround
                special_str += special_lbl.next_sibling.string if special_lbl.next_sibling != None else 'Dungeon Magazine 211'

            # Build the item entry
            for item in multi_list:
                export_item = {}
                export_item['class'] = class_str
                export_item['cost'] = item['cost']
                export_item['flavor'] = flavor_str
                export_item['level'] = item['level']
                export_item['mitype'] = mitype_str
                if multi_bonus and item['bonus'] == '':
                    export_item['name'] = name_str + ' (Level ' + item['level'] + ')'
                else:
                    export_item['name'] = name_str + ' ' + item['bonus'] if item['bonus'] != '' else name_str
                export_item['powers'] = powers_str
                export_item['special'] = special_str

                # Append a copy of generated entry
                export_list.append(copy.deepcopy(export_item))

    print(str(len(db)) + " entries parsed.")
    print(str(len(export_list)) + " export entries.")

    # Write FG XML database files
    write_id = write_db('export/poisons/data/db.xml', export_list)

    print(str(write_id) + " module entries written. Job done.")

    try:
        os.remove('export/mods/4E_Poisons.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/mods/4E_Poisons', 'zip', 'export/poisons/data/')
        os.rename('export/mods/4E_Poisons.zip', 'export/mods/4E_Poisons.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\mods' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\magic_poison\\data' folder to create the mod.")
        print("Rename the complete filename (including path) to '4E_Poisons.mod'.\n")

    input('Press enter to close.')
