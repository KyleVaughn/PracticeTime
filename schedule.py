import bisect
from initialize import initialize
from itertools import combinations
import logging
import numpy as np
from person import Person

# Assumed that time increment between times is 30 min

nTimesToStore = 1000
dayOfInterest = 'Saturday'
nPracticeInc = 6
nToPracticeInc = 1
nFromPracticeInc = 2

file_dir = './tsv/'
files = [
        'Kyle.tsv',
        'Hinton.tsv',
        'Jake.tsv',
        'Jonathan.tsv',
        'Hannah.tsv',
        'Sahil.tsv',
        'Emily.tsv',
        'Lauren.tsv',
        'Leah.tsv',
        'Sam.tsv',
        'Alanna.tsv',
        'Griffin.tsv',
        'Xia.tsv',
        'Matt.tsv',
        ]

module_log = logging.getLogger(__name__)

initialize()

# Import data
module_log.info('Importing info')
people = []
for f in files:
    people.append(Person.initFromFile(file_dir + f))

# Make sure days and times are the same and all avail entries valid
days = people[0].days
times = people[0].times
for i, p in enumerate(people):
    if sorted(p.days) != sorted(days):
        module_log.error(f'Not all days the same. See file {i}.')
    if sorted(p.times) != sorted(times):
        module_log.error(f'Not all times the same. See file {i}.')
    for a in p.avail:
        for x in a:
            isclose = np.isclose(x,0) or np.isclose(x,1) or np.isclose(x,2)
            if not isclose:
                module_log.error(f'Not all avail values valid in file {i}.')

# Add availability restrictions
nTimes = len(people[0].avail[0])
for p in people:
    for a in p.avail:
        # Adjust for getting to and from practice
        for i in range(nTimes-nToPracticeInc,0,-1):
            if np.isclose(a[i],2):
                for j in range(nToPracticeInc):
                    a[i+j+1] = 2.0

        for i in range(nFromPracticeInc + nPracticeInc, nTimes):
            if np.isclose(a[i],2):
                for j in range(nFromPracticeInc + nPracticeInc):
                    a[i-j-1] = 2.0

# Enumerate groups
module_log.info('Performing group calculations')
bestTimes = [[1E6, 1, 1, 1]]*nTimesToStore
names = [p.name for p in people]
ncalc = int(0)
for group1 in combinations(names,int(len(people)/2)):
    group1 = list(group1)
    group2 = [n for n in names if (n not in group1)]

    # Generate people list from name list
    group1People = []
    for n in group1:
        namesIdx = names.index(n)
        group1People.append(people[namesIdx])
    group2People = []
    for n in group2:
        namesIdx = names.index(n)
        group2People.append(people[namesIdx])

    # for each time, compute norm for each group. 
    # If the 2 norm of group norms is less than one of best values, insert into list
    for t in range(nTimes-nPracticeInc):
        # Construct time vector
        ng1 = len(group1)
        ng2 = len(group2)
        g1vec = np.zeros(ng1)
        g2vec = np.zeros(ng2)
        # Get avail value from time, name
        for i in range(ng1):
            # get index of day of interest
            dayIdx = group1People[i].days.index(dayOfInterest) 
            g1vec[i] = group1People[i].avail[dayIdx][t] 

        for t2 in range(t + nPracticeInc,nTimes - nPracticeInc):
            for i in range(ng2):
                # get index of day of interest
                dayIdx = group2People[i].days.index(dayOfInterest) 
                g2vec[i] = group2People[i].avail[dayIdx][t2] 
            
            # Compute the norm of the vector
            g1norm = (1.0/np.sqrt(ng1))*np.linalg.norm(g1vec)
            g2norm = (1.0/np.sqrt(ng2))*np.linalg.norm(g2vec)
#            print(g1vec, g2vec, g1norm, g2norm)
            totalNorm = np.linalg.norm(np.array([g1norm, g2norm]))

            # If the 2 norm of group norms is less than one of best values, insert into list
            # This is ass code, but im in a hurry
            ncalc = ncalc + 1
            for i in range(nTimesToStore):
                if totalNorm < bestTimes[i][0]:
                    bestTimes.append([totalNorm, times[t], group1, times[t2], group2])
                    bestTimes.sort(key=lambda x: x[0])
                    del bestTimes[-1]
                    break

module_log.info('Done')
print(f'Computed {ncalc} group/time combinations')
for t in bestTimes:
    print(t)
