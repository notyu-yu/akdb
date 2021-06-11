import sqlite3
import statistics
import matplotlib.pyplot as plt
import numpy as np

# Open database and create cursor
conn = sqlite3.connect('akdb.sqlite')
cur = conn.cursor()

# Enter rank and statistics to graph
studied_rank = 'e2'
attribute_lst = ['hp', 'atk', 'def', 'res', 'redeploy', 'dp_cost', 'block', 'aspd']

# Get field names to look up in database
field_name_lst = [(studied_rank + '_' + i) for i in attribute_lst]

# Dictionaries for each class's statistics and id's
class_stat_dict = {}
class_id_dict = {}

# Create key entries in class statistics and id dictionaries
cur.execute('SELECT id, class from classes')
for output_row in cur:
    class_stat_dict[output_row[0]] = {}
    class_id_dict[output_row[0]] = output_row[1]
    for field in field_name_lst:
        class_stat_dict[output_row[0]][field] = []

# Fill in statistic values in class stats dictionary
for field in field_name_lst:
    cur.execute('SELECT class_id, %s FROM ak_op WHERE %s IS NOT NULL' % (field, field))
    for output_row in cur:
        class_stat_dict[output_row[0]][field].append(output_row[1])

# List of average statistics for each class
result_lst = None

# Calculate averages for each field for each class and append them to result list
for class_id in class_id_dict.keys():
    if result_lst is None:
        result_lst = [(['class'] + field_name_lst)]
    class_res_lst = [class_id_dict[class_id]]
    for field in field_name_lst:
        class_res_lst.append(statistics.mean(class_stat_dict[class_id][field]))
    result_lst.append(class_res_lst)

# Graph with matplotlib
width = 0.8 / (len(result_lst[0])-1)
x = np.arange(len(result_lst)-1)

for i in range(len(result_lst)-1):
    class_lst = result_lst[1+i]
    plt.bar(x - 0.4 + width * i, class_lst[1:], width, label=class_lst[0])

plt.yscale('log')
plt.ylabel('Value')
plt.title('Average Statistcs for each Operator Class')

plt.xticks(x + width / (len(result_lst[0])-1), result_lst[0][1:])
plt.legend(loc='best')
plt.show()

# Old code to use gline
'''
fhand = open('ak_gline.js', 'w+')
fhand.write('gline = [ ')
for i in range(len(result_lst)):
    fhand.write('[')
    for item in result_lst[i]:
        if type(item) == str:
            fhand.write("'"+str(item)+"',")
        else:
            fhand.write(str(item)+",")
    fhand.write("],\n")

fhand.write("];\n")

fhand.close()
'''

cur.close()
