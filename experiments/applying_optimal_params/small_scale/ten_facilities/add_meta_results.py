import os
import math
import pandas as pd

from os.path import dirname, abspath

current_directory = dirname(abspath(__file__))

results = f'{current_directory}/results.csv'

data = pd.read_csv(results,header=0,index_col=False)

z1_ideal = max(data['hybrid Z1'])
z2_ideal = min(data['hybrid Z2'])
z3_ideal = min(data['hybrid Z3'])


initial_index = 1
local_solutions = []
output = []

'''
part of this code is commented as it is written 
for the general case when there is more than one experiment
'''

for index,row in data.iterrows():
  # if row['solution index'] == initial_index:
    local_solutions.append(row)
    initial_index += 1
  # else:
    
ci = lambda solution: math.sqrt(
    (solution['hybrid Z1']-z1_ideal)**2+
    (solution['hybrid Z2']-z2_ideal)**2+
    (solution['hybrid Z3']-z3_ideal)**2
  )

c = sum(ci(solution) for solution in local_solutions)

# catch the case when only there is one local solution
mid = c*(1/len(local_solutions))

denumerator = (len(local_solutions)-1) if len(local_solutions) > 1 else 1

sns = math.sqrt(
    sum((mid-ci(solution))**2 for solution in local_solutions)\
    /denumerator
  )

max_z1 = max(solution['hybrid Z1'] for solution in local_solutions)
min_z1 = min(solution['hybrid Z1'] for solution in local_solutions)

max_z2 = max(solution['hybrid Z2'] for solution in local_solutions)
min_z2 = min(solution['hybrid Z2'] for solution in local_solutions)

max_z3 = max(solution['hybrid Z3'] for solution in local_solutions)
min_z3 = min(solution['hybrid Z3'] for solution in local_solutions)

dm = math.sqrt((max_z1-min_z1)**2+(max_z2-min_z2)**2+(max_z3-min_z3)**2)

output.append({
    'tabu size':local_solutions[0]['tabu size'],
    'T':local_solutions[0]['T'],
    'Tf':local_solutions[0]['Tf'],
    'K':local_solutions[0]['K'],
    'alpha':local_solutions[0]['alpha'],
    'neighbors percentage':local_solutions[0]['neighbor_percentage'],
    'running time':local_solutions[0]['optimization running time'],
    'mid':mid,
    'sns':sns,
    'dm':dm,
})


    # local_solutions = [row]
    # initial_index = 2


output_df = pd.DataFrame.from_dict(output,orient='columns')

output_df = output_df.sort_values(by=['tabu size','T','Tf','K','alpha','neighbors percentage','running time'],ignore_index=True)

output_df_deduplicated = output_df.drop_duplicates(subset=['tabu size','T','Tf','K','alpha','neighbors percentage'],keep='first')

output_df_deduplicated.to_csv(f'{current_directory}/results_meta.csv')