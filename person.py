import pandas
import numpy

class Person:
    def __init__(self, name, days, times, avail):
        self.name = name
        self.days = days
        self.times = times
        self.avail = avail

    @ classmethod
    def initFromFile(cls,filepath):
        df = pandas.read_csv(filepath, sep='\t')
        # Name
        name = df.iloc[4,1]
        # Days
        days = df.iloc[6, 1:].values.tolist()
        # Times
        times = df.iloc[7:, 0].values.tolist()
        # Availability
        avail = []
        for i in range(len(days)):
            avail.append(df.iloc[7:, (1+i)].to_numpy(dtype=numpy.float16))
        
        return cls(name, days, times, avail)
