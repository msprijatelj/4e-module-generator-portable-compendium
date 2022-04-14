import os
import sys
import shutil
import copy
import re
from bs4 import BeautifulSoup, Tag, NavigableString
from helpers.create_db import create_db

from helpers.armor_helpers import armor_list_sorter
from helpers.armor_helpers import create_armor_reference
from helpers.armor_helpers import create_armor_library
from helpers.armor_helpers import create_armor_table
from helpers.armor_helpers import extract_armor_list

from helpers.equipment_helpers import equipment_list_sorter
from helpers.equipment_helpers import create_equipment_reference
from helpers.equipment_helpers import create_equipment_library
from helpers.equipment_helpers import create_equipment_table
from helpers.equipment_helpers import extract_equipment_list

from helpers.weapons_helpers import weapons_list_sorter
from helpers.weapons_helpers import create_weapons_reference
from helpers.weapons_helpers import create_weapons_library
from helpers.weapons_helpers import create_weapons_table
from helpers.weapons_helpers import extract_weapons_list


def write_lib(filepath, xml_in):
    with open(filepath, mode='w', encoding='UTF-8', errors='strict', buffering=1) as file:
        file.write(xml_in)

    return

if __name__ == '__main__':

    library_str = '4E Compendium PHB'

    # Pull data from Portable Compendium
    items_db = []
    try:
        items_db = create_db('ddiItem.sql', "','")
    except:
        print("Error reading data source.")

    print(f"{len(items_db)} entries recovered")

    # Convert data to FG format
    print("converting to FG format...")

    if not items_db:
        print("NO DATA FOUND IN SOURCES, MAKE SURE YOU HAVE COPIED YOUR 4E PORTABLE COMPENDIUM DATA TO SOURCES!")
        input('Press enter to close.')
        sys.exit(0)

    #===========================
    # WEAPONS
    #===========================

    # Extract all the Equipment data into a list
    weapons_list = extract_weapons_list(items_db)

    # Call the three functions to generate the _ref, _lib & _tbl xml
    weapons_ref = create_weapons_reference(weapons_list)
    weapons_lib = create_weapons_library('a0003', library_str, 'Items - Weapons')
    weapons_tbl = create_weapons_table(weapons_list, library_str)

    #===========================
    # ARMOR
    #===========================

    # Extract all the Armor data into a list
    armor_list = extract_armor_list(items_db)

    # Call the three functions to generate the _ref, _lib & _tbl xml
    armor_ref = create_armor_reference(armor_list)
    armor_lib = create_armor_library('a0001', library_str, 'Items - Armor')
    armor_tbl = create_armor_table(armor_list, library_str)

    #===========================
    # EQUIPMENT
    #===========================

    # Extract all the Equipment data into a list
    equipment_list = extract_equipment_list(items_db)

    # Call the three functions to generate the _ref, _lib & _tbl xml
    equipment_ref = create_equipment_reference(equipment_list)
    equipment_lib = create_equipment_library('a0002', library_str, 'Items - Equipment')
    equipment_tbl = create_equipment_table(equipment_list, library_str)

    #===========================
    # XML
    #===========================

    export_xml = ''
    # Open the document
    export_xml +=('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
    export_xml +=('<root version="2.9">\n')

    # Open the Reference part
    # These are the individual cards that appear when you click on a table entry
    export_xml +=('\t<reference static="true">\n')

    # Weapons
    export_xml +=('\t\t<weapon>\n')
    export_xml += weapons_ref
    export_xml +=('\t\t</weapon>\n')

    # Armor
    export_xml +=('\t\t<armor>\n')
    export_xml += armor_ref
    export_xml +=('\t\t</armor>\n')

    # Equipment 
    export_xml +=('\t\t<equipment>\n')
    export_xml += equipment_ref
    export_xml +=('\t\t</equipment>\n')

    # Close the Reference part
    export_xml +=('\t</reference>\n')

    # Open the Library part
    # This controls the right-hand menu on the Modules screen
    export_xml +=('\t<library>\n')
    export_xml +=('\t\t<lib4ecompendiumphb>\n')
    export_xml +=(f'\t\t\t<name type="string">{library_str}</name>\n')
    export_xml +=('\t\t\t<categoryname type="string">4E Core</categoryname>\n')
    export_xml +=('\t\t\t<entries>\n')


    export_xml += armor_lib
    export_xml += equipment_lib
    export_xml += weapons_lib

    # Close the Library part
    export_xml +=('\t\t\t</entries>\n')
    export_xml +=('\t\t</lib4ecompendiumphb>\n')
    export_xml +=('\t</library>\n')

    # Tables part
    # This controls the table that appears when you click on a Library menu

    export_xml += weapons_tbl
    export_xml += armor_tbl
    export_xml += equipment_tbl

    # Close the document
    export_xml +=('</root>\n')

    # Write FG XML database files
    write_lib('export/compendium_phb/data/client.xml',export_xml)

    print("Module entries written. Job done.")

    try:
        os.remove('export/mods/4E_Compendium_PHB.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/mods/4E_Compendium_PHB', 'zip', 'export/compendium_phb/data/')
        os.rename('export/mods/4E_Compendium_PHB.zip', 'export/mods/4E_Compendium_PHB.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\mods' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\compendium_phb\\data' folder to create the mod.")
        print("Rename the complete filename (including path) to '4E_Compendium_PHB.mod'.\n")

    input('Press enter to close.')
