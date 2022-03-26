import os
import sys
import shutil
import pathlib
import json
import re


# This function recover a power and convert it to FG values as properly as it can
def power_gen(header, body, action_type):
    fg_power = {}
    if action_type.endswith('s'):
        action_type = action_type[:-1]
    fg_power['action'] = action_type.capitalize()

    # Parse head
    # Power Type
    powertype_oc = str(header).split('<b>', 1)[0].replace('<p class="flavor alt">', '').replace(' ', '')
    if powertype_oc:
        powertype_oc = powertype_oc.replace('<pclass="flavorIndent">', '')
        powertype_fg = get_powertype(powertype_oc)
        if len(powertype_fg) > 1 and powertype_fg not in ['MR', 'MC', 'CA', 'RA', 'MA', 'RC', 'mr']:
            if powertype_fg in 'mM':
                powertype_fg = 'm'
            else:
                powertype_fg = ''
        fg_power['powertype'] = powertype_fg
    text = header.text
    # Name
    fg_power['name'] = ''
    for tag in header:
        if isinstance(tag, Tag) and tag.name == 'b':
            if not fg_power['name']:
                fg_power['name'] = tag.text
    # FG somehow considers "keywords" all text between parenthesis and "recharge" everything after star glyph
    # Keywords
    search_results = re.finditer(r'\(.*?\)', text)
    for item in search_results:
        parenthesis_info = item.group(0)
        fg_power['keywords'] = sanitize_dices(parenthesis_info.replace('(', '').replace(')', ''))

    # Recharge
    fg_power['recharge'] = ''
    full_html_header = str(header)
    has_recharge = full_html_header.find('images/symbol/x.gif')
    if has_recharge != -1:
        recharge = full_html_header.partition('<img src="images/symbol/x.gif"/>')
        recharge = recharge[2].replace('<b>', '').replace('</b>', '').replace('</p>', '').replace('<br/>', '')
        recharge = sanitize_dices(recharge)
        fg_power['recharge'] = recharge

    # Parse body parts
    # Description
    fg_power['shortdescription'] = ''
    for tag in body:
        fg_power['shortdescription'] = fg_power['shortdescription'] + tag.text + '\n'
    # Clean dice glyphs from description
    fg_power['shortdescription'] = sanitize_dices(fg_power['shortdescription'])

    # Range is not always available but when it is, it's a start of description (some edge cases will be missed here)
    desc = fg_power['shortdescription']
    rng = None
    if ';' in desc:
        if 'Melee ' in desc:
            sections = desc.split("; ", 1)
            if len(sections) == 2:
                fg_power['range'] = sections[0]
                fg_power['shortdescription'] = sections[1]
        elif 'Reach ' in desc:
            sections = desc.split("; ", 1)
            if len(sections) == 2:
                fg_power['range'] = sections[0]
                fg_power['shortdescription'] = sections[1]
        elif 'Ranged ' in desc:
            sections = desc.split("; ", 1)
            if len(sections) == 2:
                fg_power['range'] = sections[0]
                fg_power['shortdescription'] = sections[1]
        elif 'Close burst ' in desc:
            sections = desc.split("; ", 1)
            if len(sections) == 2:
                fg_power['range'] = sections[0]
                fg_power['shortdescription'] = sections[1]
        elif 'Close blast ' in desc:
            sections = desc.split("; ", 1)
            if len(sections) == 2:
                fg_power['range'] = sections[0]
                fg_power['shortdescription'] = sections[1]
        elif 'Area burst ' in desc:
            sections = desc.split("; ", 1)
            if len(sections) == 2:
                fg_power['range'] = sections[0]
                fg_power['shortdescription'] = sections[1]
        elif 'Targets ' in desc:
            sections = desc.split("; ", 1)
            if len(sections) == 2:
                fg_power['range'] = sections[0]
                fg_power['shortdescription'] = sections[1]

    # At last, return a FG compatible NPC Power
    return fg_power


# Replace dice glyps with FG compatible strings
def sanitize_dices(given_string):
    given_string = given_string.replace('<img src="images/symbol/1a.gif"/>', '[1]').replace('<img src="images/symbol/2a.gif"/>', '[2]')
    given_string = given_string.replace('<img src="images/symbol/3a.gif"/>', '[3]').replace('<img src="images/symbol/4a.gif"/>', '[4]')
    given_string = given_string.replace('<img src="images/symbol/5a.gif"/>', '[5]').replace('<img src="images/symbol/6a.gif"/>', '[6]')
    return given_string


def get_powertype(glyph):
    # return FG key based on offline compendium keys
    fg_glyph = ''
    if 'images/symbol/S2.gif' in glyph:
        fg_glyph = fg_glyph + 'm'
    if 'images/symbol/Z2a.gif' in glyph:
        fg_glyph = fg_glyph + 'M'
    if 'images/symbol/S3.gif' in glyph:
        fg_glyph = fg_glyph + 'r'
    if 'images/symbol/Z3a.gif' in glyph:
        fg_glyph = fg_glyph + 'R'
    if 'images/symbol/Z1.gif' in glyph:
        fg_glyph = fg_glyph + 'c'
    if 'images/symbol/Z1a.gif' in glyph:
        fg_glyph = fg_glyph + 'C'
    if 'images/symbol/Z4a.gif' in glyph:
        fg_glyph = fg_glyph + 'A'
    if 'images/symbol/aura.png' in glyph:
        fg_glyph = fg_glyph + 'Z'
    return fg_glyph


# Function that detects if given tag is the final stat block
def is_last_statblock(tag):
    text = str(tag.text)
    # Check for presence of three stats strings simultaneously
    if 'Str' in text and 'Str' in text and 'Dex' in text and 'Wis' in text:
        return True
    # Check for presence of Alignment and Language
    elif 'Alignment' in text and 'Language' in text:
        return True
    # Check for presence of equipment or skills
    elif text.startswith('Equipment:') or text.startswith('Skills'):
        return True
    # If nothing matches, chances are really low that this is a final statblock
    else:
        return False


# Find action from header tag
def retrieve_action(tag):
    action_header = str(tag.text)
    # Get first word after first parenthesis
    if action_header.find('(standard') != -1:
        return 'Standard'
    if action_header.find('(immediate') != -1:
        return 'Triggered'
    if action_header.find('(opportunity') != -1:
        return 'Triggered'
    if action_header.find('( when') != -1:
        return 'Triggered'
    if action_header.find('(minor') != -1:
        return 'Minor'
    if action_header.find('(move') != -1:
        return 'Move'
    if action_header.find('(free') != -1:
        return 'Free'
    return 'Trait'


# This function return levels for all 25 conjured monsters since it's lacking in their original description/type
def get_conjured_level(name):
    if 'Shuffling Zombie' in name:
        return 'Level 0 Conjured'
    elif 'Onyx Dog' in name:
        return 'Level 4 Conjured'
    elif 'Obsidian Steed' in name:
        return 'Level 4 Conjured'
    elif 'Opal Carp' in name:
        return 'Level 6 Conjured'
    elif 'Pearl Sea Horse' in name:
        return 'Level 8 Conjured'
    elif 'Jade Macetail Behemeth' in name:
        return 'Level 8 Conjured'
    elif 'Conjured Critter (Gray Bag)' in name:
        return 'Level 8 Conjured'
    elif 'Marble Elephant' in name:
        return 'Level 10 Conjured'
    elif 'Jade Sea Snake' in name:
        return 'Level 10 Conjured'
    elif 'Ivory Goat of Travail' in name:
        return 'Level 10 Conjured'
    elif 'Ebony Fly' in name:
        return 'Level 10 Conjured'
    elif 'Bloodstone Spider' in name:
        return 'Level 10 Conjured'
    elif 'Golden Lion' in name:
        return 'Level 12 Conjured'
    elif 'Amber Monkey' in name:
        return 'Level 13 Conjured'
    elif 'Emerald Frog' in name:
        return 'Level 14 Conjured'
    elif 'Tantron' in name:
        return 'Level 16 Conjured Brute'
    elif 'Mercury Wasp Swarm' in name:
        return 'Level 16 Conjured'
    elif 'Serpentine Owl' in name:
        return 'Level 17 Conjured'
    elif 'Conjured Beast (Rust Bag)' in name:
        return 'Level 18 Conjured'
    elif 'Bronze Griffon' in name:
        return 'Level 19 Conjured'
    elif 'Guenhwyvar' in name:
        return 'Level 21 Conjured Skirmisher'
    elif 'Electrum Serpent' in name:
        return 'Level 21 Conjured'
    elif 'Tourmaline Turtle' in name:
        return 'Level 23 Conjured'
    elif 'Coral Dragon' in name:
        return 'Level 25 Conjured'
    elif 'Conjured Beast (Vermilion Bag)' in name:
        return 'Level 28 Conjured'
    else:
        return ''


def write_db(filepath, fg_data):
    id = 1
    with open(filepath, mode='w', encoding='UTF-8', errors='strict', buffering=1) as file:
        file.write('<root version="2.9">\n')
        file.write('	<npc>\n')
        for entry in fg_data:
            string_id = "00000"[0:len("00000")-len(str(id))] + str(id)
            file.write(f'		<id-{string_id}>\n')
            file.write(f'			<ac type="number">{entry["ac"]}</ac>\n')
            if "alignment" in entry.keys():
                file.write(f'			<alignment type="string">{entry["alignment"]}</alignment>\n')
            if "ap" in entry.keys():
                file.write(f'			<ap type="number">{entry["ap"]}</ap>\n')
            file.write(f'			<charisma type="number">{entry["charisma"]}</charisma>\n')
            file.write(f'			<constitution type="number">{entry["constitution"]}</constitution>\n')
            file.write(f'			<dexterity type="number">{entry["dexterity"]}</dexterity>\n')
            if "equipment" in entry.keys():
                file.write(f'			<equipment type="string">{entry["equipment"]}</equipment>\n')
            if "flavor" in entry.keys():
                file.write(f'			<flavor type="string">{entry["flavor"]}</flavor>\n')
            file.write(f'			<fortitude type="number">{entry["fortitude"]}</fortitude>\n')
            file.write(f'			<hp type="string">{entry["hp"]}</hp>\n')
            file.write(f'			<init type="number">{entry["init"]}</init>\n')
            file.write(f'			<intelligence type="number">{entry["intelligence"]}</intelligence>\n')
            if "languages" in entry.keys():
                file.write(f'			<languages type="string">{entry["languages"]}</languages>\n')
            file.write(f'			<levelrole type="string">{entry["levelrole"]}</levelrole>\n')
            file.write(f'			<name type="string">{entry["name"]}</name>\n')
            file.write(f'			<npctype type="string">Creature</npctype>\n')
            file.write(f'			<perceptionval type="number">{entry["perceptionval"]}</perceptionval>\n')
            file.write(f'			<powers>\n')
            pid = 1
            for power in entry["powers"]:
                string_pid = "00000"[0:len("00000")-len(str(pid))] + str(pid)
                file.write(f'				<id-{string_pid}>\n')
                file.write(f'					<action type="string">{power["action"]}</action>\n')
                if "keywords" in power.keys():
                    file.write(f'					<keywords type="string">{power["keywords"]}</keywords>\n')
                clean_power_name = power["name"].replace('&', '&amp;')
                file.write(f'					<name type="string">{clean_power_name}</name>\n')
                if "powertype" in power.keys():
                    file.write(f'					<powertype type="string">{power["powertype"]}</powertype>\n')
                if "range" in power.keys():
                    file.write(f'					<range type="string">{power["range"]}</range>\n')
                if "recharge" in power.keys():
                    file.write(f'					<recharge type="string">{power["recharge"]}</recharge>\n')
                power_desc = power["shortdescription"].replace(u'\xa0', ' ')
                file.write(f'					<shortdescription type="string">{repr(power_desc)[1:-1]}</shortdescription>\n')
                file.write(f'				</id-{string_pid}>\n')
                pid = pid + 1
            file.write(f'			</powers>\n')
            file.write(f'			<reflex type="number">{entry["reflex"]}</reflex>\n')
            if "save" in entry.keys():
                file.write(f'			<save type="number">{entry["save"]}</save>\n')
            if "senses" in entry.keys():
                file.write(f'			<senses type="string">{entry["senses"]}</senses>\n')
            if "skills" in entry.keys():
                file.write(f'			<skills type="string">{entry["skills"]}</skills>\n')
            if "specialdefenses" in entry.keys():
                specialdefenses = entry["specialdefenses"].replace(u'\xa0', ' ')
                file.write(f'			<specialdefenses type="string">{repr(specialdefenses)[1:-1]}</specialdefenses>\n')
            if "speed" in entry.keys():
                file.write(f'			<speed type="string">{entry["speed"]}</speed>\n')
            file.write(f'			<strength type="number">{entry["strength"]}</strength>\n')
            if "type" in entry.keys():
                file.write(f'			<type type="string">{entry["type"]}</type>\n')
            file.write(f'			<will type="number">{entry["will"]}</will>\n')
            file.write(f'			<wisdom type="number">{entry["wisdom"]}</wisdom>\n')
            file.write(f'			<xp type="number">{entry["xp"]}</xp>\n')
            file.write(f'		</id-{string_id}>\n')
            id = id + 1
        file.write('	</npc>\n')
        file.write('</root>')


if __name__ == '__main__':

    # Pull data from Portable Compendium
    data_source = {}
    sql_sections = []
    for path in pathlib.Path("sources/").iterdir():
        if path.is_file() and 'ddiMonster' in path.stem:
            with open(path, encoding="utf8") as inp:
                for section in inp.read().split("INSERT INTO `Monster` VALUES"):
                    sql_sections.append(section)
    sql_sections.pop(0)
    for index, section in enumerate(sql_sections):
        html = section.split('.</p>\\r\\n    ', 1)[0] + '.</p>'
        html = '<h1' + html.split('<h1', 1)[1]
        html = html.replace('\\', '')
        data_source[index] = html

    print(str(len(data_source.keys())) + " entries recovered")

    # Convert data to FG format
    print("converting to FG format...")

    # Initialize all modules databases
    Creatures_fg = []

    try:
        from BeautifulSoup import BeautifulSoup
    except ImportError:
        from bs4 import BeautifulSoup, Tag, NavigableString

    if not data_source.items():
        print("NO DATA FOUND IN SOURCES, MAKE SURE YOU HAVE COPIED YOUR 4E OFFLINE COMPENDIUM DATA TO SOURCES!")
        input('Press enter to close.')
        sys.exit(0)

    for key, value in data_source.items():
        fg_entry = {}
        parsed_html = BeautifulSoup(value, features="html.parser").contents

        # Recover creature name
        fg_entry['name'] = str(parsed_html[0].next)

        type_tag = parsed_html[0].find_all("span", class_="type")
        level_tag = parsed_html[0].find_all("span", class_="level")
        exp_tag = parsed_html[0].find_all("span", class_="xp")

        fg_entry['type'] = str(type_tag[0].string)
        # In case of conjured creatures, no level/role/exp is provided by compendium
        if level_tag:
            fg_entry['levelrole'] = str(level_tag[0].next)
        else:
            fg_entry['levelrole'] = get_conjured_level(fg_entry['name'])
        if exp_tag:
            fg_entry['xp'] = str(exp_tag[0].next[4:])
        else:
            fg_entry['xp'] = ""

        # First stat block is either in Tag-01 as <table class="bodytable">, if not then on Tag-02 as <p class="flavor">
        fg_entry['specialdefenses'] = ''
        if isinstance(parsed_html[1], NavigableString):
            statblock = parsed_html[2]
            for tag in parsed_html[2]:
                if isinstance(tag, Tag):
                    if 'Initiative' in tag.text:
                        init_string = str(tag.next_sibling)
                        fg_entry['init'] = init_string[1:len(init_string)-8].replace('+', '')
                    if 'Senses' in tag.text:
                        senses_values = tag.next_sibling.split(";", 1)
                        fg_entry['perceptionval'] = senses_values[0][12:].replace('+', '')
                        if len(senses_values) > 1:
                            fg_entry['senses'] = senses_values[1]
                    if 'HP' in tag.text:
                        hp_value = str(tag.next_sibling).replace('; ', '')
                        hp_value = hp_value.replace('a missed attack never damages a minion.', '')
                        fg_entry['hp'] = hp_value
                    if 'AC' in tag.text:
                        fg_entry['ac'] = str(tag.next_sibling).replace('; ', '')
                    if 'Fortitude' in tag.text:
                        fg_entry['fortitude'] = str(tag.next_sibling).replace(', ', '')
                    if 'Reflex' in tag.text:
                        fg_entry['reflex'] = str(tag.next_sibling).replace(', ', '')
                    if 'Will' in tag.text:
                        fg_entry['will'] = str(tag.next_sibling)
                    if 'Saving Throws' in tag.text:
                        fg_entry['save'] = str(tag.next_sibling)
                    if 'Immune' in tag.text:
                        fg_entry['specialdefenses'] = fg_entry['specialdefenses'] + 'Immune: ' + str(tag.next_sibling) + '\n'
                    if 'Resist' in tag.text:
                        fg_entry['specialdefenses'] = fg_entry['specialdefenses'] + 'Resist: ' + str(tag.next_sibling) + '\n'
                    if 'Vulnerable' in tag.text:
                        fg_entry['specialdefenses'] = fg_entry['specialdefenses'] + 'Vulnerable: ' + str(tag.next_sibling) + '\n'
                    if 'Speed' in tag.text:
                        fg_entry['speed'] = str(tag.next_sibling)
                    if 'Action Points' in tag.text:
                        fg_entry['ap'] = str(tag.next_sibling)
        # Handles situations where tables can be identified by <tbody>
        elif parsed_html[1].name and 'table' in parsed_html[1].name:
            contents_table = parsed_html[1].contents
            contents_cursor = []
            for t in contents_table:
                for c in t.contents:
                    if isinstance(c, Tag):
                        contents_cursor += c.contents
            contents_length = len(contents_cursor)
            tags = contents_cursor
            for tag in tags:
                if isinstance(tag, Tag):
                    if 'Initiative' in tag.text:
                        init_string = str(tag.next_sibling)
                        fg_entry['init'] = init_string.replace('+', '')
                    if 'Perception' in tag.text:
                        fg_entry['perceptionval'] = str(tag.next_sibling).replace('; ', '').replace('+', '')
                    if 'HP' in tag.text:
                        hp_value = str(tag.next_sibling).replace('; ', '')
                        hp_value = hp_value.replace('a missed attack never damages a minion.', '')
                        fg_entry['hp'] = hp_value
                    if 'AC' in tag.text:
                        fg_entry['ac'] = str(tag.next_sibling).replace(', ', '')
                    if 'Fortitude' in tag.text:
                        fg_entry['fortitude'] = str(tag.next_sibling).replace(', ', '')
                    if 'Reflex' in tag.text:
                        fg_entry['reflex'] = str(tag.next_sibling).replace(', ', '')
                    if 'Will' in tag.text:
                        fg_entry['will'] = str(tag.next_sibling).replace(' ; add your level to each defense', '')
                    if 'Saving Throws' in tag.text:
                        fg_entry['save'] = str(tag.next_sibling)
                    if 'Immune' in tag.text:
                        fg_entry['specialdefenses'] = fg_entry['specialdefenses'] + 'Immune: ' + str(tag.next_sibling) + '\n'
                    if 'Resist' in tag.text:
                        fg_entry['specialdefenses'] = fg_entry['specialdefenses'] + 'Resist: ' + str(tag.next_sibling) + '\n'
                    if 'Vulnerable' in tag.text:
                        fg_entry['specialdefenses'] = fg_entry['specialdefenses'] + 'Vulnerable: ' + str(tag.next_sibling) + '\n'
                    if 'Speed' in tag.text:
                        fg_entry['speed'] = str(tag.next_sibling)
                    if 'Action Points' in tag.text:
                        fg_entry['ap'] = str(tag.next_sibling)
                elif isinstance(tag, NavigableString):
                    if any(x in str(tag) for x in ('Low-light vision', 'Darkvision', 'Blindsight', 'All-around', 'Blind', 'Truesight', 'Tremorsense')):
                        fg_entry['senses'] = str(tag)

        # Recover NPC Actions
        # Check if there is a proper action definition with subtitles or if it's all over the place (nested in titles)
        final_statblock = None
        fg_entry['powers'] = []
        action_sections = []
        for tag in parsed_html:
            if tag.name and 'h2' in tag.name:
                action_sections.append(tag)
        if action_sections:
            # Now we iterate over each section to create a power
            for section in action_sections:
                section_end = False
                power_cursor = section.nextSibling
                action_type = section.text.split(' ', 1)[0]
                while not section_end:
                    # Check if next data is matching a power or if section has ended (Next section or final statblock)
                    if power_cursor is None:
                        # Source data is corrupted and the rest of the monster is nested in one of its power.
                        # Not dealing with that since these monsters are broken and don't actually show up Compendium UI
                        final_statblock = None
                        section_end = True
                    elif is_last_statblock(power_cursor):
                        # Final statblock reached
                        final_statblock = power_cursor
                        section_end = True
                    elif power_cursor.name and 'h2' in power_cursor.name:
                        # Next section reached !
                        section_end = True
                    elif power_cursor.name and 'p' in power_cursor.name:
                        # Load data according to cursor position
                        header = power_cursor
                        body = []
                        # For as long as next sibling is a flavor indent, recover data for body
                        while power_cursor.nextSibling is not None and 'flavorIndent' in power_cursor.nextSibling.attrs.get('class', []):
                            body.append(power_cursor.nextSibling)
                            power_cursor = power_cursor.nextSibling
                        power_cursor = power_cursor.nextSibling
                        fg_entry['powers'].append(power_gen(header, body, action_type))
        else:
            # So, this is chaos without section, let's try to sort this out.
            # First action is determined by first flavor alt, let's find it
            power_cursor = None
            for tag in parsed_html:
                if isinstance(tag, Tag):
                    if 'flavor' in tag.attrs.get('class', []) and 'alt' in tag.attrs.get('class', []):
                        if power_cursor is None:
                            power_cursor = tag
            # Now we have a power cursor placed on the first action, let's iterate until we reach the final stat block
            if power_cursor:
                powerblock_end = False
                while not powerblock_end:
                    # Check if next data is matching a power or if power block has ended with final statblock
                    if is_last_statblock(power_cursor):
                        # Final statblock reached
                        final_statblock = power_cursor
                        powerblock_end = True
                    elif power_cursor.name and 'p' in power_cursor.name:
                        # Load data according to cursor position
                        header = power_cursor
                        body = []
                        # We need to determine action type for each power (extracted from header strings)
                        action_type = retrieve_action(header)
                        # For as long as next sibling is a flavor indent, recover data for body
                        while 'flavorIndent' in power_cursor.nextSibling.attrs.get('class', []):
                            body.append(power_cursor.nextSibling)
                            power_cursor = power_cursor.nextSibling
                        power_cursor = power_cursor.nextSibling
                        fg_entry['powers'].append(power_gen(header, body, action_type))
            else:
                print('Something went wrong here, you should always have at least one action per NPC')

        # Start of final_statblock is always determined by power retrieval since there is always at least one action
        while final_statblock and final_statblock.nextSibling:
            if isinstance(final_statblock, Tag):
                for tag in final_statblock.contents:
                    if 'Languages</b>' in str(tag):
                        fg_entry['languages'] = str(tag.next_sibling)
                    if '<b>Skills</b>' in str(tag):
                        fg_entry['skills'] = str(tag.next_sibling)
                    if '<b>Str</b>' in str(tag):
                        fg_entry['strength'] = str(tag.next_sibling).split(" (", 1)[0].replace(' ', '')
                    if '<b>Dex</b>' in str(tag):
                        fg_entry['dexterity'] = str(tag.next_sibling).split(" (", 1)[0].replace(' ', '')
                    if '<b>Wis</b>' in str(tag):
                        fg_entry['wisdom'] = str(tag.next_sibling).split(" (", 1)[0].replace(' ', '')
                    if '<b>Con</b>' in str(tag):
                        fg_entry['constitution'] = str(tag.next_sibling).split(" (", 1)[0].replace(' ', '')
                    if '<b>Int</b>' in str(tag):
                        fg_entry['intelligence'] = str(tag.next_sibling).split(" (", 1)[0].replace(' ', '')
                    if '<b>Cha</b>' in str(tag):
                        fg_entry['charisma'] = str(tag.next_sibling).split(" (", 1)[0].replace(' ', '')
                    if '<b>Equipment</b>' in str(tag):
                        fg_entry['equipment'] = str(tag.next_sibling).replace(' .', '').replace(': ', '')
                    if '<b>Description</b>' in str(tag):
                        fg_entry['flavor'] = str(tag.next_sibling)
                    if '<b>Alignment</b>' in str(tag):
                        fg_entry['alignment'] = str(tag.next_sibling)[0:len(tag.next_sibling)-7]
            final_statblock = final_statblock.nextSibling

            # Statblocks are only composed of p, if a h1 is found it means a disease block is reached
            if final_statblock and isinstance(final_statblock, Tag):
                if 'h1' in final_statblock.name:
                    final_statblock = None

        # Keep in mind that the source data can be corrupted and the rest of the monster is nested in one of its power!
        # I'm not dealing with that since these monsters are broken and don't actually show up Compendium UI.
        # And therefore some monsters will be missing their final_statblock.
        # To avoid errors when things are missing, I add empty placeholders.
        if 'languages' not in fg_entry:
            fg_entry['languages'] = ''
        if 'skills' not in fg_entry:
            fg_entry['skills'] = ''
        if 'strength' not in fg_entry:
            fg_entry['strength'] = ''
        if 'dexterity' not in fg_entry:
            fg_entry['dexterity'] = ''
        if 'wisdom' not in fg_entry:
            fg_entry['wisdom'] = ''
        if 'constitution' not in fg_entry:
            fg_entry['constitution'] = ''
        if 'intelligence' not in fg_entry:
            fg_entry['intelligence'] = ''
        if 'charisma' not in fg_entry:
            fg_entry['charisma'] = ''
        if 'equipment' not in fg_entry:
            fg_entry['equipment'] = ''
        if 'flavor' not in fg_entry:
            fg_entry['flavor'] = ''
        if 'alignment' not in fg_entry:
            fg_entry['alignment'] = ''

        Creatures_fg.append(fg_entry.copy())

    print(str(len(Creatures_fg)) + " entries converted to FG as Creatures_fg")

    # Write FG XML database files
    write_db('export/npc/data/db.xml', Creatures_fg)

    print("Database files written. Job done.")

    try:
        os.remove('export/npc/4e_NPC_PortableCompendium.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    shutil.make_archive('export/npc/4e_NPC', 'zip', 'export/npc/data/')
    os.rename('export/npc/4e_NPC.zip', 'export/npc/4e_NPC_PortableCompendium.mod')

    print("\nDatabase added and module generated!")
    print("You can find it in the 'export\\npc' folder\n")

    input('Press enter to close.')
