# 4e-module-generator-portable-compendium
A set of scripts for converting data from the D&amp;D 4e Portable Compendium into Fantasy Grounds modules.

The original "4E Module Generator - Portable Compendium" package was provided by VegaFontana on the [Fantasy Grounds 4e Forums](https://www.fantasygrounds.com/forums/showthread.php?60524-4E-Module-Generator-Portable-compendium-gt-Fantasy-Grounds) under a GNU GPL-3.0 License.  This repository modifies and builds off of that package to improve how it parses Portable Compendium data and generates Fantasy Grounds modules from that data.

**\*\*THIS PACKAGE DOES _NOT_ INCLUDE D&D 4E COMPENDIUM DATA.\*\***

It is designed to work with `.sql` data files from the Beta 30 version of the 4e Portable Compendium.

## How to Use
1. Copy the `ddiFeat.sql`, `ddiPower.sql`, and `ddiMonster.sql` files from `/path/to/portablecompendium/sql/`.

2. Paste the `.sql`files inside the `sources` folder of the generator located at "4E Module Generator - Portable Compendium/sources/".

3. Execute the `_run_all.bat` file (double click should be fine).
   Then three executable will be launched and three consoles should appear (one per module generated) with live status updates. 
   Once finished, they will each ask you to press "Enter" to close them.
   - Alternatively, if you have Python 3.8 or greater installed on your computer, you can instead run each script via Python.

4. Check the `export` folder in each directory for the newly-created mod files
   (e.g. `4e_NPC_PortableCompendium.mod` in `export/npc`)

5. Copy these 3 modules from their export folders into your FG modules folder (default should be `.../Fantasy Gounds/Data/modules`) and load them in your campaign!

6. Don't forget to grant your players access to the basic items / feats / powers modules to ease character creation.

## Development
Install the required packages and begin to develop!
```bash
pip install -r requirements.txt
```

To package each script in its own `.exe` file, run the following command for each python script (`feat.py`, `npc.py`, and `power.py`):
```
pyinstaller ${script_name} --onefile --distpath .
```
