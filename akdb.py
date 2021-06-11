# Import modules
import sqlite3
import re
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import ssl
import time

# Avoid ssl certification errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Opens database file and create cursor
conn = sqlite3.connect('akdb.sqlite')
cur = conn.cursor()

# Creates tables in database if they don't already exist
cur.executescript('''
DROP TABLE IF EXISTS ak_op;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS factions;
DROP TABLE IF EXISTS positions;
DROP TABLE IF EXISTS archetypes;
DROP TABLE IF EXISTS tag_relation;
DROP TABLE IF EXISTS tags;

CREATE TABLE IF NOT EXISTS ak_op (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name VARCHAR(128) UNIQUE,
    class_id INTEGER,
    faction_id INTEGER,
    rarity INTEGER,
    position_id INTEGER,
    archetype_id INTEGER,
    e0_hp INTEGER,
    e0_atk INTEGER,
    e0_def INTEGER,
    e0_res INTEGER,
    e0_redeploy INTEGER,
    e0_dp_cost INTEGER,
    e0_block INTEGER,
    e0_aspd FLOAT(24),
    e1_hp INTEGER,
    e1_atk INTEGER,
    e1_def INTEGER,
    e1_res INTEGER,
    e1_redeploy INTEGER,
    e1_dp_cost INTEGER,
    e1_block INTEGER,
    e1_aspd FLOAT(24),
    e2_hp INTEGER,
    e2_atk INTEGER,
    e2_def INTEGER,
    e2_res INTEGER,
    e2_redeploy INTEGER,
    e2_dp_cost INTEGER,
    e2_block INTEGER,
    e2_aspd FLOAT(24));

CREATE TABLE IF NOT EXISTS classes (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    class VARCHAR(128) UNIQUE);

CREATE TABLE IF NOT EXISTS factions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    faction VARCHAR(128) UNIQUE);

CREATE TABLE IF NOT EXISTS positions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    position VARCHAR(128) UNIQUE);

CREATE TABLE IF NOT EXISTS archetypes(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    archetype VARCHAR(128) UNIQUE);

CREATE TABLE IF NOT EXISTS tag_relation (
    op_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (op_id, tag_id));

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    tag VARCHAR(128) UNIQUE);
''')

# Fetch the html file of the operator list page and parse it with BeatifulSoup
uh = urllib.request.urlopen('https://mrfz.fandom.com/wiki/Operator_List#All')
data = uh.read().decode()
soup = BeautifulSoup(data, 'html.parser')

# Find tables in html file
tables = soup.find_all('table')

# Go through each operator in operator list and put their statistics in database
for table in tables:
    # Get operators in each row
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        # Skip rows that are not proper operator entries
        if len(cols) < 5: continue

        # Get the operator names from column 2 in the <a href...> tag
        op_name = str(cols[1].find('a').string)

        print('Retrieving Operator:', op_name)

        # Get operator class, faction and rarity from list entry
        op_class = cols[2].find('a').get('title')
        op_faction = cols[3].find('a').get('title')
        op_rarity = str(cols[4].find('span').string).count('★')

        # Get the link for operator's wiki entry
        op_link = 'https://mrfz.fandom.com' + cols[1].find('a').get('href')

        # Parse operator's wiki entry html with BeautifulSoup
        op_data = urllib.request.urlopen(op_link).read().decode()
        op_soup = BeautifulSoup(op_data, 'html.parser')

        # Get operator statistics table and the rows in it
        op_tables = op_soup.find_all('table')
        op_rows = op_tables[0].find('tbody').find_all('tr')

        # Get operator's position, tags, and archetype from the stats table
        op_position = op_rows[1].find_all('td')[1].text.strip()
        op_tags = [i.text for i in op_rows[2].find_all('td')[1].find_all('div') if i.text]
        op_archetype = op_rows[3].find_all('td')[1].text.strip()

        # Get the table for operator's numerical statistics and its rows
        for op_table in op_tables:
            if 'HP.png' in str(op_table):
                op_stats_table = op_table
                break
        op_stat_rows = op_stats_table.find_all('tr')

        # Create and fill a dictionary with keys being the statistc name and values being statistic value at each elite level 
        op_stats_dict = {}
        for stat_row in op_stat_rows[1:]:
            stat_name = stat_row.find('th').text.strip()
            stat_list = [j.strip() for j in [i.text for i in stat_row.find_all('td')] if (j.strip() and '+' not in j and '–' not in j)][1:]
            op_stats_dict[stat_name] = stat_list

        # Insert operator class, faction, archetype, and position into corresponding tables if they don't already exist, and get the corresponding id's for each field
        cur.execute('''INSERT OR IGNORE INTO classes (class)
        VALUES (?)''', (op_class,))
        cur.execute('SELECT id FROM classes WHERE class=?', (op_class,))
        class_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO factions (faction)
        VALUES (?)''', (op_faction,))
        cur.execute('SELECT id FROM factions WHERE faction=?', (op_faction,))
        faction_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO archetypes (archetype)
        VALUES (?)''', (op_archetype,))
        cur.execute('SELECT id FROM archetypes WHERE archetype=?', (op_archetype,))
        archetype_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO positions (position)
        VALUES (?)''', (op_position,))
        cur.execute('SELECT id FROM positions WHERE position=?', (op_position,))
        position_id = cur.fetchone()[0]

        # Insert operator name and corresponding id's to the operator table and get operator's assigned id
        cur.execute('''INSERT OR IGNORE INTO ak_op
        (name, class_id, faction_id, rarity, position_id, archetype_id)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (op_name, class_id, faction_id, op_rarity, position_id, archetype_id))
        cur.execute('SELECT id FROM ak_op WHERE name=?', (op_name,))
        op_id = cur.fetchone()[0]

        # Insert statistics at each elite level into the operators table
        for i in range(len(op_stats_dict['HP'])):
            elite = 'e' + str(i) + '_'
            fields = [(elite+dk.lower().replace(' ', '_')) for dk in op_stats_dict.keys()]
            stat_nums = [op_stats_dict[dk][i] for dk in op_stats_dict.keys()]
            stat_nums = [int(i) for i in stat_nums[:-1] if i.isdigit()] + [float(stat_nums[-1])]
            cur.execute('''UPDATE ak_op SET
            %s=?, %s=?, %s=?, %s=?, %s=?, %s=?, %s=?, %s=?
            WHERE id=%s''' % tuple(fields + [op_id]),
            tuple(stat_nums))

        # Insert each operator tag into the tags table if it's not already there, and insert operator id and each tag id as seperate entries in the tag relations table
        for tag in op_tags:
            cur.execute('''INSERT OR IGNORE INTO tags (tag)
            VALUES (?)''', (tag,))
            cur.execute('SELECT id FROM tags WHERE tag=?', (tag,))
            tag_id = cur.fetchone()[0]
            cur.execute('''INSERT OR IGNORE INTO tag_relation (op_id, tag_id)
            VALUES (?, ?)''', (op_id, tag_id))

        # Commit changes
        conn.commit()

        # Pause for 0.5 seconds before next request
        time.sleep(0.5)

# Close cursor
cur.close()
