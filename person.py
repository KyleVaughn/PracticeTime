import pandas
import numpy

class Person:
    def __init__(self, name, seats, days, times, avail):
        self.name = name
        self.seats = seats
        self.days = days
        self.times = times
        self.avail = avail

    @ classmethod
    def initFromFile(cls,filepath):
        df = pandas.read_csv(filepath, sep='\t')
        # Name
        name = df.iloc[4,1]
        # Seats
        seats = int(df.iloc[5,1])
        # Days
        days = df.iloc[7, 1:].values.tolist()
        # Times
        times = df.iloc[8:, 0].values.tolist()
        # Availability
        avail = []
        for i in range(len(days)):
            avail.append(df.iloc[8:, (1+i)].to_numpy(dtype=numpy.float16))
        
        return cls(name, seats, days, times, avail)
