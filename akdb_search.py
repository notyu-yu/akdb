import sqlite3
from collections import defaultdict
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Search Operator Database')
parser.add_argument('-name', action='store', default='%', help='Search operator name')
parser.add_argument('-rarity', action='store', default='%', help='Search by rarity')
parser.add_argument('-archetype', action='store', default='%', help='Search by archetype')
parser.add_argument('-tags', action='store', nargs='*', default=None, help='Search by tags, seperate with space')
args = parser.parse_args()

# Open database file
conn = sqlite3.connect('akdb.sqlite')
cur = conn.cursor()

# Filter operators by name, rarity, and archetype
cur.execute('''
SELECT ak_op.name, ak_op.rarity, archetypes.archetype, tags.tag
FROM ak_op JOIN archetypes JOIN classes JOIN factions
JOIN positions JOIN tag_relation JOIN tags ON
ak_op.class_id=classes.id AND
ak_op.faction_id=factions.id AND
ak_op.position_id=positions.id AND
ak_op.archetype_id=archetypes.id AND
ak_op.id=tag_relation.op_id AND
tags.id=tag_relation.tag_id
WHERE name LIKE ? AND rarity LIKE ? AND archetype LIKE ?
''', (args.name,args.rarity,args.archetype))

# Dictionary to store operator tags
op_dict = defaultdict(lambda:[])

# Put each operator tag in dictionary entry
for row in cur:
    op_dict[row[:3]].append(row[3])

# Resulting dictionary after filtering by tags
result_dict = {}

# Filter operators by tags
if args.tags:
    for key, value in op_dict.items():
        tags_match = True
        for tag in args.tags:
            if tag not in value:
                tags_match = False
        if tags_match:
            result_dict[key] = value
else:
    result_dict = op_dict

# Print out the operator info
for key, value in result_dict.items():
    print("Operator: %s, Rarity: %s, Archetype: %s, " % key + f"Tags:{', '.join(value)}" )

cur.close()
