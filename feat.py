import os
import sys
import shutil
import pathlib
import json


def write_db(filepath, fg_data):
    id = 1
    with open(filepath, mode='w', encoding='UTF-8', errors='strict', buffering=1) as file:
        file.write('<root version="2.9">\n')
        file.write('	<feat>\n')
        for entry in fg_data:
            string_id = "00000"[0:len("00000")-len(str(id))] + str(id)
            file.write(f'		<id-{string_id}>\n')
            file.write('			<description type="formattedtext">\n')
            file.write(f'				<p></p>\n')
            file.write('			</description>\n')
            file.write(f'			<flavor type="string">{entry["flavor"]}</flavor>\n')
            file.write('			<linkedpowers>\n')
            file.write('			</linkedpowers>\n')
            file.write('			<locked type="number">1</locked>\n')
            file.write(f'			<name type="string">{entry["name"]}</name>\n')
            desc = entry["shortdescription"].replace(u'\xa0', ' ').replace('&','&amp;')
            file.write(f'			<shortdescription type="string">{repr(desc)[1:-1]}</shortdescription>\n')
            file.write(f'		</id-{string_id}>\n')
            id = id + 1
        file.write('	</feat>\n')
        file.write('</root>')


if __name__ == '__main__':

    # Pull data from Portable Compendium
    data_source = {}
    sql_sections = []
    for path in pathlib.Path("sources/").iterdir():
        if path.is_file() and 'ddiFeat' in path.stem:
            with open(path, encoding="utf8") as inp:
                for section in inp.read().split("INSERT INTO `Feat` VALUES"):
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
    Feat_fg = []

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

        # Parse header data from parsed_html [0] (split if needed)
        composed_name = parsed_html[0].text
        start = composed_name.find('[')
        end = composed_name.find(']')
        if start != -1 and end != -1:
            name = composed_name[0:start-1]
            context = composed_name[start+1:end]
        else:
            name = composed_name
            context = ""
        fg_entry['name'] = name
        fg_entry['flavor'] = context

        # Recover Feat core data always located in parsed_html [1]
        shortdescription = ""
        for content in parsed_html[1].contents:
            html_content = str(content)
            if '<br/>' in html_content:
                shortdescription = shortdescription + "\n"
            elif isinstance(content, NavigableString):
                shortdescription = shortdescription + str(content)
            elif isinstance(content, Tag):
                shortdescription = shortdescription + content.text

        # Check if there is linked powers (we want to ignore them since they are handled by an other module)
        i = 0
        power_start = -1
        power_end = -1
        for tag in parsed_html:
            if isinstance(tag, Tag):
                if tag.name in 'h1' and power_start == -1:
                    if 'player' not in tag.attrs['class'][0]:
                        power_start = i
                elif tag.name in 'p':
                    if 'powerstat' in tag.attrs['class'][0] or 'flavor' in tag.attrs['class'][0]:
                        power_end = i
            i = i + 1

        # Add remaining information to Feat core data (shortdescription), ignore power section if present.
        if power_start != -1 and power_end != -1 and power_start < power_end:
            # get sub section from power_end
            remaining_info = parsed_html[power_end+1:len(parsed_html)]
        else:
            # get sub section from [2]
            remaining_info = parsed_html[2:len(parsed_html)]

        shortdescription_end = ""
        for content in remaining_info:
            html_content = str(content)
            if '<br/>' in html_content:
                shortdescription_end = shortdescription_end + "\n"
            elif isinstance(content, NavigableString):
                shortdescription_end = shortdescription_end + str(content)
            elif isinstance(content, Tag):
                shortdescription_end = shortdescription_end + content.text
        fg_entry['shortdescription'] = shortdescription + shortdescription_end

        # Check what type of feat (Epic, Paragon, Heroic otherwise)
        Feat_fg.append(fg_entry.copy())

    print(str(len(Feat_fg)) + " entries converted to FG as Feats")

    # Write FG XML database files
    write_db(f'export/feats/data/db.xml', Feat_fg)

    print("Database files written. Job done.")

    try:
        os.remove('export/mods/4e_Feat_PortableCompendium.mod')
    except FileNotFoundError:
        print("Cleanup not needed.")
    try:
        shutil.make_archive('export/mods/4e_Feat', 'zip', 'export/feats/data/')
        os.rename('export/mods/4e_Feat.zip', 'export/mods/4e_Feat_PortableCompendium.mod')
        print("\nDatabase added and module generated!")
        print("You can find it in the 'export\\mods' folder\n")
    except Exception as e:
        print(f"Error creating zipped .mod file:\n{e}")
        print("\nManually zip the contents of the 'export\\feats\\data' folder to create the mod.")
        print("Rename the complete filename (including extension) to '4e_Feat_PortableCompendium.mod'.\n")

    input('Press enter to close.')
