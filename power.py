import os
import sys
import shutil
import pathlib
import json


def write_db(filepath, fg_data):
    id = 1
    with open(filepath, mode='w', encoding='UTF-8', errors='strict', buffering=1) as file:
        file.write('<root version="2.9">\n')
        file.write('	<powerdesc>\n')
        for entry in fg_data:
            string_id = "00000"[0:len("00000")-len(str(id))] + str(id)
            file.write(f'		<id-{string_id}>\n')
            file.write(f'			<action type="string">{entry["action"]}</action>\n')
            file.write('			<description type="formattedtext">\n')
            file.write(f'				<p></p>\n')
            file.write('			</description>\n')
            file.write(f'			<flavor type="string">{entry["flavor"]}</flavor>\n')
            file.write(f'			<keywords type="string">{entry["keywords"]}</keywords>\n')
            file.write('			<linkedpowers>\n')
            file.write('			</linkedpowers>\n')
            file.write('			<locked type="number">1</locked>\n')
            file.write(f'			<name type="string">{entry["name"]}</name>\n')
            file.write(f'			<range type="string">{entry["range"]}</range>\n')
            file.write(f'			<recharge type="string">{entry["recharge"]}</recharge>\n')
            desc = entry["shortdescription"].replace(u'\xa0', ' ')
            file.write(f'			<shortdescription type="string">{repr(desc)[1:-1]}</shortdescription>\n')
            file.write(f'			<source type="string">{entry["source"]}</source>\n')
            file.write(f'		</id-{string_id}>\n')
            id = id + 1
        file.write('	</powerdesc>\n')
        file.write('</root>')


if __name__ == '__main__':

    # Pull data from Portable Compendium
    data_source = {}
    sql_sections = []
    for path in pathlib.Path("sources/").iterdir():
        if path.is_file() and 'ddiPower' in path.stem:
            with open(path, encoding="utf8") as inp:
                for section in inp.read().split("INSERT INTO `Power` VALUES"):
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
    Powers_fg = []

    try:
        from BeautifulSoup import BeautifulSoup
    except ImportError:
        from bs4 import BeautifulSoup, Tag, NavigableString

    if not data_source.items():
        print("NO DATA FOUND IN SOURCES, MAKE SURE YOU HAVE COPIED YOUR 4E PORTABLE COMPENDIUM DATA TO SOURCES!")
        input('Press enter to close.')
        sys.exit(0)

    for key, value in data_source.items():
        fg_entry = {}
        parsed_html = BeautifulSoup(value, features="html.parser").contents

        # Recover header data (from parsed_html [0], [1] and [2])
        powername = str(parsed_html[0].next)
        # In older version of the compendium the power span was in front of the power name
        # If it's the case, the name is recovered in a different manner
        if "<span" in powername:
            powername = str(parsed_html[0].next.nextSibling)
        fg_entry['name'] = powername
        fg_entry['source'] = str(parsed_html[0].contents[0].next)

        # Ensure this is a flavor text
        flavor = str(parsed_html[1])
        if '<i>' in flavor:
            flavor = str(parsed_html[1].string)
        else:
            flavor = ''
        fg_entry['flavor'] = flavor

        # Get recharge from first element class since it's sometimes missing
        cls = parsed_html[0].attrs['class'][0]
        if cls in 'atwillpower':
            recharge = 'At-Will'
        elif cls in 'encounterpower':
            recharge = 'Encounter'
        elif cls in 'dailypower':
            recharge = 'Daily'
        fg_entry['recharge'] = recharge

        # Recover action type (Located at LEN-2/LEN-4 of parsed_html[1]/parsed_html[2] contents)
        l = len(parsed_html[2].contents)
        action = str(parsed_html[2].contents[l-2].string)
        if 'Action' in action or 'Immediate' in action:
            ...
        else:
            action = str(parsed_html[2].contents[l-4].string)
            if 'Action' in action or 'Immediate' in action:
                ...
            else:
                # If action can't be found in parsed_html[2] then search it again in parsed_html[1]
                l = len(parsed_html[1].contents)
                action = str(parsed_html[1].contents[l-2].string)
                if 'Action' in action or 'Immediate' in action:
                    ...
                else:
                    action = str(parsed_html[1].contents[l-4].string)
        if 'Action' in action:
            fg_entry['action'] = action = action.split()[0]
        elif'Immediate' in action:
            fg_entry['action'] = action = action

        # Recover range (check if present in parsed_html[2] and go search it in parsed_html[1] otherwise)
        l = len(parsed_html[2].contents)
        rg = str(parsed_html[2].contents[l-2].string) + str(parsed_html[2].contents[l-1].string)
        if 'Close' in rg or 'Melee' in rg or 'Ranged' in rg or 'Personal' in rg:
            ...
        else:
            l = len(parsed_html[1].contents)
            rg = str(parsed_html[1].contents[l-2].string) + str(parsed_html[1].contents[l-1].string)
        fg_entry['range'] = rg

        # Generate keywords (Concat all strings between 02 and LEN-7 of parsed_html[2] contents)
        keywords_concat = ""
        keywords_source = parsed_html[2].contents
        i = 0
        start_index = None
        for content in keywords_source:
            if '✦' in content:
                start_index = i
            elif '<br/>' in str(content):
                end_index = i
            i = i + 1
        if not end_index:
            end_index = len(keywords_source)
        if start_index is not None:
            keywords_source = keywords_source[start_index+1:end_index]
            for content in keywords_source:
                keywords_concat = keywords_concat + str(content.string)
        else:
            keywords_concat = ""
        fg_entry['keywords'] = keywords_concat

        # get all from main content, keep or emulate line breaks. Always starts at base content 03
        shortdescription = ""
        laraget = parsed_html[1].text
        record = False

        # recover keywords
        keywords_concat = ""
        for tag in parsed_html:
            if isinstance(tag, Tag):
                for t in tag.contents:
                    if isinstance(t, Tag) and ('src' in t.attrs) and 'images/bullet.gif' in t.attrs['src']:
                        record = True
                        continue
                    if isinstance(t, Tag) and 'br' in t.name:
                        record = False
                        keywords_concat = keywords_concat[:-2]
                    if record is True:
                        if isinstance(t, Tag):
                            keywords_concat = keywords_concat + str(t.string) + ", "
        fg_entry['keywords'] = keywords_concat

        record = False
        for tag in parsed_html:
            if isinstance(tag, NavigableString):
                shortdescription = shortdescription + str(tag)
            else:
                for content in tag.contents:
                    # for each content, if br give \n otherwise get string value
                    if 'class' in tag.attrs and 'flavor' in str(tag.attrs['class']):
                        if tag.next.name in ['i']:
                            record = False
                        else:
                            record = True
                    if record is True:
                        html_content = str(content)
                        if '<br/>' in html_content:
                            shortdescription = shortdescription + "\n"
                        elif isinstance(content, NavigableString):
                            shortdescription = shortdescription + str(content)
                        elif isinstance(content, Tag):
                            shortdescription = shortdescription + content.text
                        else:
                            print('Ended with something that neither a BR, a NavigableString nor a Tag...?!')
            if record is True:
                shortdescription = shortdescription + "\n"
        record = False
        fg_entry['shortdescription'] = shortdescription

        # Append a copy of generated entry
        Powers_fg.append(fg_entry.copy())

    print(str(len(Powers_fg)) + " entries converted to FG as Powers")

    # Write FG XML database files
    write_db('export/powers/data/db.xml', Powers_fg)

    print("Database files written. Job done.")

    try:
        os.remove('export/powers/4e_Power_PortableCompendium.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    shutil.make_archive('export/powers/4e_Power', 'zip', 'export/powers/data/')
    os.rename('export/powers/4e_Power.zip', 'export/powers/4e_Power_PortableCompendium.mod')

    print("\nDatabase added and module generated!")
    print("You can find it in the 'export\\power' folder\n")

    input('Press enter to close.')
