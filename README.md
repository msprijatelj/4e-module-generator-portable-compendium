# ATTENTION: This repo is NOT actively maintained!
I highly recommend using [skelekon's converter](https://github.com/skelekon/4e-portable-compendium-module-maker), as it is actively maintained and converts a much larger selection of data, with features that I never got the chance to implement in this repository. Check it out; I hope it helps your games!

If you still wish to use this repo's converter, instructions remain below:

-------------------

# 4e-module-generator-portable-compendium
A set of scripts for converting data from the D&amp;D 4e Portable Compendium into Fantasy Grounds modules.

The original "4E Module Generator - Portable Compendium" package was provided by VegaFontana on the [Fantasy Grounds 4e Forums](https://www.fantasygrounds.com/forums/showthread.php?60524-4E-Module-Generator-Portable-compendium-gt-Fantasy-Grounds) under a GNU GPL-3.0 License.  This repository modifies and builds off of that package to improve how it parses Portable Compendium data and generates Fantasy Grounds modules from that data.

**\*\*THIS PACKAGE DOES _NOT_ INCLUDE D&amp;D 4E COMPENDIUM DATA.\*\***

It is designed to work with `.sql` data files from the Beta 30 version of the 4e Portable Compendium.

## How to Use
1. Copy the `ddiFeat.sql`, `ddiPower.sql`, `ddiItem.sql`, `ddiPoison.sql`, and `ddiMonster.sql` files from `/path/to/portablecompendium/sql/`.

2. Paste the `.sql` files inside the `sources` folder of the generator located at `4e-module-generator-portable-compendium/sources/`.

3. Execute the `_run_all.bat` file (double click should be fine).
   Each executable will be launched with a console window for each (one per module generated) with live status updates. 
   Once finished, they will each ask you to press "Enter" to close them.
   - Alternatively, if you have Python 3.8 or greater installed on your computer, you can instead run each script at the root directory via Python.

4. Check the `export/mods` folder in each directory for the newly-created mod files
   (e.g. `4e_NPC_PortableCompendium.mod` in `export/mods`)

5. Copy these modules from the `export/mods` folder into your FG modules folder (default should be `.../Fantasy Gounds/Data/modules`) and load them in your campaign!

6. Don't forget to grant your players access to the basic items / feats / powers modules to ease character creation.

## Output Mods in Fantasy Grounds
The Basic Armor, Basic Weapons, and Equipment mods will be packaged and accessible in libraries within their respective mods through the Modules tab.  This will allow for creating custom magic weapons and armor by clicking and dragging the relevant basic equipment onto a magic item.

Imported Magic Armors, Magic Weapons, Magic Items, and Poisons will be found in the Items tab.

Imported NPCs will be found in the NPCs tab.

Imported Feats and Powers will be found in their respective tabs.

## Development
Install the required packages and begin to develop!
```bash
pip install -r requirements.txt
```

To package each script in its own `.exe` file, run the following command for each python script within the root folder (`feat.py`, `npc.py`, `power.py`, etc.):
```
pyinstaller ${script_name} --onefile --distpath .
```
