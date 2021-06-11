# Python Project: Arknights Database/akdb

Scrapes operator statistics data from the Fandom page for mobile game Arknights.  
Created as final project for the Python for Everybody course

Required pip modules: sqlite, matplotlib, numpy

## Scripts:

akdb.py: Uses BeatifulSoup to retrieve operator data from Fandom webpages and store them in the akdb.sqlite database

akdb_dump.py: Prints out operator name, rarity, archetype, and tags

akdb_graph.py: Plot average statistics for each operator class with matplotlib


## Database Structure:

ak_op: Operators table, contains operator id, name, class id, faction id, archetype id, and statistics at each elite level: Hitpoints/hp, damage/atk, defense/def, resistance/res, redeploy time/redeploy, deployment point cost/dp_cost, block count/block, attack speed/aspd.

archetypes: Links each archetype id to a string with the archetype name

classes: Links each class id to a string with class name.

factions: Links each faction id to a string with faction name.

positions: Links position id to a string with position name.

tag_relation: Links each operator id with each tag is has on separate entries.

tags: Links each tag id to a string with tag name.
