import copy
import re
from bs4 import BeautifulSoup, Tag, NavigableString

def equipment_list_sorter(entry_in):
    section_id = entry_in["section_id"]
    name = entry_in["name"]
    return (section_id, name)

def create_equipment_reference(list_in):
    xml_out = ''
    section_str = ''
    entry_str = ''
    name_lower = ''

    # Create individual item entries
    for entry_dict in sorted(list_in, key=equipment_list_sorter):
        name_lower = re.sub('\W', '', entry_dict["name"].lower())

        xml_out += (f'\t\t\t<{name_lower}>\n')
        xml_out += (f'\t\t\t\t<name type="string">{entry_dict["name"]}</name>\n')
        xml_out += (f'\t\t\t\t<weight type="number">{entry_dict["weight"]}</weight>\n')
        xml_out += (f'\t\t\t\t<cost type="number">{entry_dict["cost"]}</cost>\n')
        xml_out += (f'\t\t\t\t<type type="string">{entry_dict["type"]}</type>\n')
        xml_out += (f'\t\t\t\t<subtype type="string">{entry_dict["subtype"]}</subtype>\n')
        xml_out += (f'\t\t\t\t<description type="formattedtext">{entry_dict["description"]}\n\t\t\t\t</description>\n')
        xml_out += (f'\t\t\t</{name_lower}>\n')

    return xml_out

def create_equipment_library(id_in, library_in, name_in):
    xml_out = ''
    xml_out += (f'\t\t\t\t<{id_in}equipment>\n')
    xml_out += ('\t\t\t\t\t<librarylink type="windowreference">\n')
    xml_out += ('\t\t\t\t\t\t<class>reference_classequipmenttablelist</class>\n')
    xml_out += (f'\t\t\t\t\t\t<recordname>equipmentlists.core@{library_in}</recordname>\n')
    xml_out += ('\t\t\t\t\t</librarylink>\n')
    xml_out += (f'\t\t\t\t\t<name type="string">{name_in}</name>\n')
    xml_out += (f'\t\t\t\t</{id_in}equipment>\n')

    return xml_out

def create_equipment_table(list_in, library_in):
    xml_out = ''
    item_id = 0
    section_id = 0

    # Item List part
    # This controls the table that appears when you click on a Library menu
    xml_out += ('\t<equipmentlists>\n')
    xml_out += ('\t\t<core>\n')
    xml_out += ('\t\t\t<description type="string">Equipment Table</description>\n')
    xml_out += ('\t\t\t<groups>\n')

    # Create individual item entries
    for entry_dict in sorted(list_in, key=equipment_list_sorter):
        item_id += 1
        name_lower = re.sub('\W', '', entry_dict["name"].lower())

        #Check for new section
        if entry_dict["section_id"] != section_id:
            section_id = entry_dict["section_id"]
            if section_id != 1:
                section_str = "000"[0:len("000")-len(str(section_id - 1))] + str(section_id - 1)
                xml_out += ('\t\t\t\t\t</equipments>\n')
                xml_out += (f'\t\t\t\t</section{section_str}>\n')
            section_str = "000"[0:len("000")-len(str(section_id))] + str(section_id)
            xml_out += (f'\t\t\t\t<section{section_str}>\n')
            xml_out += (f'\t\t\t\t\t<description type="string">{entry_dict["type"]}</description>\n')
            xml_out += (f'\t\t\t\t\t<subdescription type="string">{entry_dict["subtype"]}</subdescription>\n')
            xml_out += ('\t\t\t\t\t<equipments>\n')

        xml_out += (f'\t\t\t\t\t\t<{name_lower}>\n')
        xml_out += ('\t\t\t\t\t\t\t<link type="windowreference">\n')
        xml_out += ('\t\t\t\t\t\t\t\t<class>referenceequipment</class>\n')
        xml_out += (f'\t\t\t\t\t\t\t\t<recordname>reference.equipment.{name_lower}@{library_in}</recordname>\n')
        xml_out += ('\t\t\t\t\t\t\t</link>\n')
        xml_out += (f'\t\t\t\t\t\t\t<name type="string">{entry_dict["name"]}</name>\n')
        xml_out += (f'\t\t\t\t\t\t\t<weight type="number">{entry_dict["weight"]}</weight>\n')
        xml_out += (f'\t\t\t\t\t\t\t<cost type="number">{entry_dict["cost"]}</cost>\n')
        xml_out += (f'\t\t\t\t\t\t</{name_lower}>\n')

    # Close out the last section
    xml_out += ('\t\t\t\t\t</equipments>\n')
    xml_out += (f'\t\t\t\t</section{section_str}>\n')

    # Close out Item List part
    xml_out += ('\t\t\t</groups>\n')
    xml_out += ('\t\t</core>\n')
    xml_out += ('\t</equipmentlists>\n')

    return xml_out

def extract_equipment_list(db_in):
    equipment_out = []

    print('\n\n\n=========== EQUIPMENT ===========')
    for i, row in enumerate(db_in, start=1):

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


        # Type & Subtype
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
            if cost_lbl := parsed_html.find(string='Price'):
                cost_str = cost_lbl.parent.next_sibling
            elif cost_lbl := parsed_html.find(string='Cost'):
                cost_str = cost_lbl.parent.next_sibling
            elif cost_lbl := parsed_html.find(string=re.compile('^Cost:.*')):
                cost_str = cost_lbl.string

            if cost_str != '':
                # Divide by 100 if cost is in cp
                if re.search(r'cp', cost_str):
                    cost_str = '0.0' + re.sub('[^\.\d]', '', cost_str)
                # Divide by 10 if cost is in sp
                elif re.search(r'sp', cost_lbl):
                    cost_str = '0.' + re.sub('[^\.\d]', '', cost_str)
                else:
                    cost_str = re.sub('[^\.\d]', '', cost_str)

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
                descrption_str = description_str if description_str == '' else description_str + '\\n'
                description_str += re.sub('\s\s', ' ', description_lbl.text)

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
            equipment_out.append(copy.deepcopy(export_dict))

    print(str(len(db_in)) + " entries parsed.")
    print(str(len(equipment_out)) + " entries exported.")

    return equipment_out
