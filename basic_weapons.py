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

    # List of possible Weapon properties
    properties_list = ['^Brutal 1', '^Brutal 2', '^Defensive', '^Heavy Thrown', '^High Crit', '^Light Thrown', '^Load Free', '^Load Minor', '^Load Move', '^Load Standard', '^Off-Hand', '^Reach[^i]', '^Small', '^Stout', '^Versatile',\
        '^Accurate', '^Blinking', '^Deadly', '^Distant', '^Empowered Crit', '^Forceful', '^Mighty', '^Mobile', '^Reaching', '^Shielding', '^Undeniable', '^Unerring', '^Unstoppable',\
        'Energized \(acid\)', 'Energized \(cold\)', 'Energized \(fire\)', 'Energized \(force\)', 'Energized \(lightning\)', 'Energized \(necrotic\)', 'Energized \(psychic\)', 'Energized \(radiant\)', 'Energized \(thunder\)']

    for i, row in enumerate(db):

        # Parse the HTML text 
        html = row['Txt']
        html = html.replace('\\r\\n','\r\n').replace('\\','')
        parsed_html = BeautifulSoup(html, features="html.parser")

        # Retrieve the data with dedicated columns
        name_str =  row['Name'].replace('\\', '')

        # Initialize the other tag data
        class_str = ''
        cost_str = ''
        damage_str = ''
        flavor_str = ''
        group_str = ''
        mitype_str = ''
        profbonus_str = ''
        properties_str = ''
        range_str = ''
        special_str = ''
        subclass_str = ''
        weight_str = ''

        # Class - Basic weapons and Superior implements
        # brute force the Class/Subclass
        if class_lbl := parsed_html.find(string=re.compile('^(Simple|Military|Superior|Improvised).*')):
            class_lbl = re.sub(' *$', '', class_lbl)
            if class_lbl == 'Simple one-handed melee weapon':
                class_str = 'Simple Melee Weapons'
                subclass_str = 'One-Handed'
            elif class_lbl == 'Simple two-handed melee weapon':
                class_str = 'Simple Melee Weapons'
                subclass_str = 'Two-Handed'
            elif class_lbl == 'Military one-handed melee weapon':
                class_str = 'Military Melee Weapons'
                subclass_str = 'One-Handed'
            elif class_lbl == 'Military two-handed melee weapon':
                class_str = 'Military Melee Weapons'
                subclass_str = 'Two-Handed'
            elif class_lbl == 'Superior one-handed melee weapon':
                class_str = 'Superior Melee Weapons'
                subclass_str = 'One-Handed'
            elif class_lbl == 'Superior two-handed melee weapon':
                class_str = 'Superior Melee Weapons'
                subclass_str = 'Two-Handed'
            elif class_lbl == 'Superior double melee weapon':
                class_str = 'Superior Melee Weapons'
                subclass_str = 'Double'
            elif class_lbl == 'Improvised one-handed melee weapon':
                class_str = 'Improvised Melee Weapons'
                subclass_str = 'One-Handed'
            elif class_lbl == 'Improvised two-handed melee weapon':
                class_str = 'Improvised Melee Weapons'
                subclass_str = 'Two-Handed'
            elif class_lbl == 'Simple one-handed ranged weapon':
                class_str = 'Simple Ranged Weapons'
                subclass_str = 'One-Handed'
            elif class_lbl == 'Simple two-handed ranged weapon':
                class_str = 'Simple Ranged Weapons'
                subclass_str = 'Two-Handed'
            elif class_lbl == 'Military one-handed ranged weapon':
                class_str = 'Military Ranged Weapons'
                subclass_str = 'One-Handed'
            elif class_lbl == 'Military two-handed ranged weapon':
                class_str = 'Military Ranged Weapons'
                subclass_str = 'Two-Handed'
            elif class_lbl == 'Superior one-handed ranged weapon':
                class_str = 'Superior Ranged Weapons'
                subclass_str = 'One-Handed'
            elif class_lbl == 'Superior two-handed ranged weapon':
                class_str = 'Superior Ranged Weapons'
                subclass_str = 'Two-Handed'
            elif class_lbl == 'Improvised one-handed ranged weapon':
                class_str = 'Improvised Ranged Weapons'
                subclass_str = 'One-Handed'
            elif class_lbl == 'Improvised two-handed ranged weapon':
                class_str = 'Improvised Ranged Weapons'
                subclass_str = 'Two-Handed'
            elif class_lbl == 'Superior':
                class_str = 'Superior Implements'
            # Garotte typo
            elif class_lbl == 'Superior two-handed  weapon':
                class_str = 'Superior Melee Weapons'
                subclass_str = 'Two-Handed'
            else:
                class_str = class_lbl
            mitype_str = 'weapon'

        # Class - Simple implements
        # these would normally end up in Basic Items, but creating them as a Basic Weapons lets them appear in the character 'Combat' tab
        if re.search('^(Holy Symbol|Ki Focus|Orb Implement|Rod Implement|Staff Implement|Tome Implement|Totem|Wand Implement)$', name_str):
            class_str = 'Simple Implement'
            mitype_str = 'weapon'

        # Records to be processed
        if mitype_str != '':
            print(str(i) + ' ' + name_str)

            # Cost
            if cost_lbl := parsed_html.find(string=re.compile('^Cost:.*')):
                cost_str = re.sub('(Cost: |\.00|,| $)', '', cost_lbl.string)
            elif cost_lbl := parsed_html.find(string='Price'):
                cost_str = re.sub('(: |\.00|,| $)', '', cost_lbl.parent.next_sibling)

            # Damage
            if damage_lbl := parsed_html.find(string='Damage'):
                damage_str = damage_lbl.parent.next_sibling.replace(': ', '')

            # Group
            if group_lbl := parsed_html.find(string='Group'):
                group_str = group_lbl.parent.next_sibling.next_sibling.next_sibling.replace(' (', '')

            # Flavor (Description)
            # implements have a description tag
            if flavor_lbl := parsed_html.find(string='Description'):
                flavor_str = flavor_lbl.parent.next_sibling.replace(': ', '')
            # otherwise look for a 'detail' div
            elif detail_div := parsed_html.find('div', id='detail'):
                for el_str in detail_div.stripped_strings:
                    # if we hit these we have gone too far
                    if re.search('^(Properties|Published|' + group_str + ')', el_str):
                        break
                    # skip over these ones
                    if re.search('^(:|Cost|Damage|Group|Range|Weight|Proficient|' + name_str + '|' + class_lbl + ')', el_str):
                        continue
                    # otherwise append non-empty values to the Flavor
                    if re.sub('\s', '', el_str) != '':
                        flavor_str += '\\n' if flavor_str != '' else ''
                        flavor_str += re.sub('^[:\s]*', '', el_str)
            # clean up extraneous spaces
            flavor_str = re.sub('\s\s', ' ', flavor_str.strip())

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
                weight_str = '{:g}'.format(float(weight_lbl.parent.next_sibling.replace(': ', '').replace('1/10', '0.1').replace('1/2', '0.5').replace(' lb.', '').replace(' lb', '')))
            # might be inside a single tag
            elif weight_lbl := parsed_html.find(string=re.compile('^Weight:.*')):
                weight_str = '{:g}'.format(float(weight_lbl.string.replace('Weight: ', '').replace('1–', '').replace('6–', '').replace('—', '0').replace('1/10', '0.1').replace('1/2', '0.5').replace(' lb.', '').replace(' lb', '')))

            # Special (Published In)
            if special_lbl := parsed_html.find('p', class_='publishedIn'):
                special_str = re.sub('\s\s', ' ', special_lbl.text)

            # Build the item entry
            export_item = {}
            export_item['class'] = class_str
            export_item['cost'] = cost_str
            export_item['damage'] = damage_str
            export_item['flavor'] = flavor_str
            export_item['group'] = group_str
            export_item['mitype'] = mitype_str
            export_item['name'] = name_str
            export_item['profbonus'] = profbonus_str
            export_item['properties'] = properties_str
            export_item['range'] = range_str
            export_item['special'] = special_str
            export_item['subclass'] = subclass_str
            export_item['weight'] = weight_str

            # Append a copy of generated entry
            export_list.append(copy.deepcopy(export_item))

    print(str(len(db)) + " entries parsed.")
    print(str(len(export_list)) + " export entries.")

    # Write FG XML database files
    write_id = write_db('export/basic_weapons/data/db.xml', export_list)

    print(write_id + " module entries written. Job done.")

    try:
        os.remove('export/basic_weapons/4E_Basic_Weapons.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/basic_weapons/4E_Basic_Weapons', 'zip', 'export/basic_weapons/data/')
        os.rename('export/basic_weapons/4E_Basic_Weapons.zip', 'export/basic_weapons/4E_Basic_Weapons.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\basic_weapons' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\basic_weapon\\data' folder to create the mod.")
        print("Rename the complete filename (including path) to '4E_Basic_Weapons.mod'.\n")

    input('Press enter to close.')
