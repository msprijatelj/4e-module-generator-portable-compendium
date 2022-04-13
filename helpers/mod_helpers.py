import re
import copy

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

def multi_level(soup_in):
    multi_out = []

    # Get Bonus / Cost / Level lists for items with variable bonus
    bonus_list = soup_in.find('table', class_='magicitem').find_all('td', class_='mic2')
    cost_list = soup_in.find('table', class_='magicitem').find_all('td', class_='mic3')
    level_list = soup_in.find('table', class_='magicitem').find_all('td', class_='mic1')

    # Loop through the lists to create a dictionary with three values
    idx = max(len(bonus_list), len(cost_list), len(level_list))
    for item in range(idx):
        multi_dict = {}
        multi_dict['bonus'] = ''
        multi_dict['cost'] = ''
        multi_dict['level'] = ''

        if bonus_str := bonus_list[item].string:
            multi_dict['bonus'] = bonus_str
        if cost_str := cost_list[item].string:
            multi_dict['cost'] = cost_str
        if level_str := level_list[item].string.replace('Lvl ', ''):
            multi_dict['level'] = level_str

        # Append dictionary to output list
        multi_out.append(copy.deepcopy(multi_dict))

    return multi_out

def power_construct(lines_list):

    # List of keywords to be included
    keywords_list = ['Acid', 'Augmentable', 'Aura', 'Charm', 'Cold', 'Conjuration', 'Fear', 'Fire', 'Healing', 'Illusion', 'Implement',\
        'Lightning', 'Necrotic', 'Poison', 'Polymorph', 'Psychic', 'Radiant', 'Sleep', 'Summoning', 'Teleportation', 'Thunder', 'Varies', 'Weapon', 'Zone']

    action_str = ''
    keywords_str = ''
    name_str = ''
    range_str = ''
    recharge_str = ''
    shortdescription_str = ''

    # Loop through list of strings that contains all information for a single power
    for line in lines_list:

        # Action
        action_test = re.search(r'(Free Action|Free|Immediate Interrupt|Immediate Reaction|Minor Action|Minor|Move Action|Move|No Action|Standard Action|Standard)', line)
        if action_test != None:
            action_str = action_test.group(1)

        # Keyword
        # exhaustive check to avoid false positives
        for kwd in keywords_list:
            if keywords_test := re.search(kwd, line):
                keywords_str += ', ' if keywords_str != '' else ''
                keywords_str += kwd

        # Range
        # take only the first entry as some multi-level items increase range with level
        range_test = re.search(r'(Area.*?|Close.*?|Ranged.*?)[;($\.]', line)
        if range_test != None and range_str == '':
           range_str = range_test.group(1).strip()

        # Recharge
        recharge_test = re.search(r'(At-will Attack|At-Will Attack|At-will Utillity|At-Will Utility|At-will|At-Will|Consumable|Daily Attack|Daily Utility|Daily|Encounter)', line)
        if recharge_test != None:
            recharge_str = recharge_test.group(1)

        # Description
        # Check for keywords that indicate a power description line
        shortdescription_test = re.search(r'(^As|^Attack:|Effect|Hit|Level|Make|Miss|Trigger|You)', line)
        # also include any line that doesn't find an action or recharge
        if shortdescription_test != None or (action_test == None and recharge_test == None):
            if shortdescription_str != '':
                shortdescription_str += '\\n'
            shortdescription_str += re.sub('\s\s', ' ', line)

    # Create and return power as a dictionary item
    power_dict = {}
    power_dict['action'] = action_str
    power_dict['keywords'] = keywords_str
    power_dict['name'] = name_str
    power_dict['range'] = range_str
    power_dict['recharge'] = recharge_str
    power_dict['shortdescription'] = shortdescription_str

    return power_dict

def powers_format(soup_in):
    id = 0
    powers_list = []
    in_power = False

    # Find all tags that might contain powers information
    power_tags = soup_in.find_all(class_=['mihead', 'mistat', 'mistat indent', 'mistat indent1'])
    for tag in power_tags:
        # concatenate all the elements within each tag
        tag_str = ' '.join(map(str, tag.stripped_strings))
        # if we find the beginning of a power and one is already under construction then construct and add it to the power list and start a new item
        if re.search(r'^(Attack Power|Power|Utility Power)', tag_str) and in_power:
            power_item = power_construct(new_power)
            powers_list.append(copy.deepcopy(power_item))
            new_power = []
        # else if this is the beginning of the first power then start a new item
        elif re.search(r'^(Attack Power|Power|Utility Power)', tag_str):
            in_power = True
            new_power = []
        if in_power:
            new_power.append(tag_str)
    # construct final power and add it to the power list
    if in_power:
        power_item = power_construct(new_power)
        powers_list.append(copy.deepcopy(power_item))

    # Loop though power list to create all the tags
    powers_out = '\n'
    for power in powers_list:
        id += 1
        entrry_id = "00000"[0:len("00000")-len(str(id))] + str(id)
        powers_out += f'\t\t\t\t<id-{entrry_id}>\n'
        if power["action"] != '':
            powers_out += f'\t\t\t\t\t<action type="string">{power["action"]}</action>\n'
        if power["keywords"] != '':
            powers_out += f'\t\t\t\t\t<keywords type="string">{power["keywords"]}</keywords>\n'
        if power["name"] != '':
            powers_out += f'\t\t\t\t\t<name type="string">{power["name"]}</name>\n'
        if power["range"] != '':
            powers_out += f'\t\t\t\t\t<range type="string">{power["range"]}</range>\n'
        if power["recharge"] != '':
            powers_out += f'\t\t\t\t\t<recharge type="string">{power["recharge"]}</recharge>\n'
        if power["shortdescription"] != '':
            powers_out += f'\t\t\t\t\t<shortdescription type="string">{power["shortdescription"]}</shortdescription>\n'
        powers_out += f'\t\t\t\t</id-{entrry_id}>\n'
    powers_out += '\t\t\t'
    return re.sub('^\s*$', '', powers_out)

def props_format(props_in):
    id = 0

    # Split the input at each \n into a list of properties
    props_list = re.split(r'\\n', props_in)

    # Loop though properties list to create all the tags
    props_out = '\n'
    for p in props_list:
        id += 1
        entrry_id = "00000"[0:len("00000")-len(str(id))] + str(id)
        props_out += f'\t\t\t\t<id-{entrry_id}>\n'
        props_out += f'\t\t\t\t\t<shortdescription type="string">{p}</shortdescription>\n'
        props_out += f'\t\t\t\t</id-{entrry_id}>\n'
    props_out += '\t\t\t'
    return re.sub('^\s*$', '', props_out)
