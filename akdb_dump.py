import sqlite3
from collections import defaultdict

# Open database file
conn = sqlite3.connect('akdb.sqlite')
cur = conn.cursor()

# Print operator name, rarity, archetype, and tags
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
''')

# Dictionary to store operator tags
op_dict = defaultdict(lambda:[])

# Put each operator tag in dictionary entry
for row in cur:
    op_dict[row[:3]].append(row[3])

# Print out the operator info's
for key, value in op_dict.items():
    print("Operator: %s, Rarity: %s, Archetype: %s, " % key + f"Tags:{', '.join(value)}" )

cur.close()
