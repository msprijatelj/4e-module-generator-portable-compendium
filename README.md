# 4e-module-generator-portable-compendium
A set of scripts for converting data from the D&amp;D 4e Portable Compendium into Fantasy Grounds modules.

This package was originally provided by VegaFontana on the [Fantasy Grounds 4e Forums](https://www.fantasygrounds.com/forums/showthread.php?60524-4E-Module-Generator-Portable-compendium-gt-Fantasy-Grounds).  It is provided here with modifications.

## How to Use
1. Copy the ddiFeat.sql, ddiPower.sql and ddiMonster.sql, files from "PathYoYourPortableCompendium/sql/".

2. Then paste them inside the sources folder of the generator located at "4E Module Generator - Portable Compendium/sources/".

3. Execute the "4E Module Generator - Portable Compendium/_run_all.bat" file (double clic should be fine).
   Then three executable will be launched and three consoles should appear (once per modules generated) with info of the parsing happening.

4. Each consoles will ask you to press enter to close them once finished.

5. Finally you will be able to find the generated modules in the "4E Module Generator - Portable Compendium/export" folder in each specific repositories
   (i.e. "4e_NPC_PortableCompendium.mod" in "4E Module Generator/export/npc")

6. Just copy these 3 modules from their export folders into your FG modules folder (default should be ".../Fantasy Gounds/Data/modules") and load them in your campain!

7. Don't forget to give access to your players to the basic items / feats / powers modules to ease character creation.