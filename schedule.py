import bisect
from initialize import initialize
from itertools import combinations
import logging
import numpy as np
from person import Person

# Time increment between times is 30 min
nTimesToStore = 20         # Show this many times
dayOfInterest = 'Saturday'  # Show times for this day
nPracticeInc = 6            # 30 min increments in a practice
nToPracticeInc = 1          # 30 min increments to get to practice from class
nFromPracticeInc = 2        # 30 min increments to get from practice to class
GroupSizePM = 1             # Try group1 size of 
                            # int(len(people)/2), int(len(people)/2) - 1, ..., int(len(people)/2) - GroupSizePM 
file_dir = './tsv/'
files = [
        'Kyle.tsv',
        'Hinton.tsv',
        'Jake.tsv',
        'Jonathan.tsv',
        'Hannah.tsv',
        'Sahil.tsv',
        'Emily.tsv',
        'Sam.tsv',
        'Alanna.tsv',
        'Griffin.tsv',
        'Xia.tsv',
        'Matt.tsv',
        ]

# 1. Import data
initialize()
module_log = logging.getLogger(__name__)
module_log.info('Importing info')
people = []
for f in files:
    people.append(Person.initFromFile(file_dir + f))

# 2. Make sure days and times are the same and all avail entries valid
module_log.info('Error checking data')
days = people[0].days
times = people[0].times
for i, p in enumerate(people):
    if not p.seats >= 0:
        module_log.error(f'Number of seats must be greater than or equal to zero. See file {i}')
    if sorted(p.days) != sorted(days):
        module_log.error(f'Not all days the same. See file {i}.')
    if sorted(p.times) != sorted(times):
        module_log.error(f'Not all times the same. See file {i}.')
    for a in p.avail:
        for x in a:
            isclose = np.isclose(x,0) or np.isclose(x,1) or np.isclose(x,2)
            if not isclose:
                module_log.error(f'Not all avail values valid in file {i}.')

# 3. Add availability restrictions
nTimes = len(people[0].avail[0])
for p in people:
    for a in p.avail:
        # Adjust for getting to practice
        for i in range(nTimes-nToPracticeInc,0,-1):
            if np.isclose(a[i],2):
                for j in range(nToPracticeInc):
                    a[i+j+1] = 2.0
        # Adjust for getting from practice
        for i in range(nFromPracticeInc + nPracticeInc, nTimes):
            if np.isclose(a[i],2):
                for j in range(nFromPracticeInc + nPracticeInc):
                    a[i-j-1] = 2.0

# 4. Enumerate groups, order on goodness of fit based on 2 norm
# There may be other better measures of goodness of fit, especially considering
# that the 2 norm of the 2 norms of each group may skew the weighting per person.
# Haven't thought about it much. This was done in a day.
module_log.info('Performing group calculations')
bestTimes = [[1E6, 1, 1, 1]]*nTimesToStore
names = [p.name for p in people]
ncalc = 0
N = int(len(people)/2) 
if N <= GroupSizePM:
    module_log.error('Group 1 size <= GroupSizePM, idiot')
# For each group size
for grpDiff in range(GroupSizePM+1):
    # For each group
    for group1 in combinations(names,int(len(people)/2 - grpDiff)):
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

        # If groups don't have enough seats, skip
        ng1 = len(group1)
        ng2 = len(group2)
        nseats1 = 0
        nseats2 = 0
        for p in group1People:
            nseats1 = nseats1 + p.seats 
        for p in group2People:
            nseats2 = nseats2 + p.seats 
        if nseats1 < ng1 or nseats2 < ng2:
            continue
    
        # For each group 1 time
        for t in range(nTimes-nPracticeInc):
            # Construct time vector
            g1vec = np.zeros(ng1)
            g2vec = np.zeros(ng2)
            # Get avail value from time, name
            badfor1 = []
            for i in range(ng1):
                # get index of day of interest
                dayIdx = group1People[i].days.index(dayOfInterest) 
                avalue = group1People[i].avail[dayIdx][t]
                if avalue > 0:
                    badfor1.append(group1People[i].name)
                g1vec[i] = avalue

            # For each group 2 time
            for t2 in range(t + nPracticeInc,nTimes - nPracticeInc):
                # Get avail value from time, name
                badfor2 = []
                for i in range(ng2):
                    # get index of day of interest
                    dayIdx = group2People[i].days.index(dayOfInterest) 
                    avalue = group2People[i].avail[dayIdx][t2]
                    if avalue > 0:
                        badfor2.append(group2People[i].name)
                    g2vec[i] = avalue
                
                # Compute the norm of the availability vector
                g1norm = (1.0/np.sqrt(ng1))*np.linalg.norm(g1vec)
                g2norm = (1.0/np.sqrt(ng2))*np.linalg.norm(g2vec)
                totalNorm = np.linalg.norm(np.array([g1norm, g2norm]))
    
                # If the 2 norm of group norms is less than one of best values, insert into list
                # This is ass code. Very inefficient, but im in a hurry
                ncalc = ncalc + 1
                for i in range(nTimesToStore):
                    if totalNorm < bestTimes[i][0]:
                        bestTimes.append([totalNorm, times[t], group1, badfor1, 
                            times[t2], group2, badfor2])
                        bestTimes.sort(key=lambda x: x[0])
                        del bestTimes[-1]
                        break

module_log.info('Done')
print(f'Computed {ncalc} valid group/time combinations')
print('2-norm, Group 1 time, Group 1 people, Time is bad for, Group 2 time,\
        Group 2 people, Time is bad for')
for t in bestTimes:
    print(t)
