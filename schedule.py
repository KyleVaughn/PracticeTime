import numpy as np
from person import Person

file_dir = './tsv/'
files = [
        'Kyle.tsv',
        'Hinton.tsv',
        'Jake.tsv',
        'Jonathan.tsv',
        'Hannah.tsv',
        'Sahil.tsv',
        ]

# Import data
people = []
for f in files:
    people.append(Person.initFromFile(file_dir + f))
for p in people:
    print(p.name)
