from string import strip, split

def read_csv(filename, types = float):
    """Read CSV formatted data from a text file. read_csv takes each line of the
    input, removes the newline, splits at the commas, and return a list of
    lines, each of which contains a list of the split values on the line.
    """
    f = file(filename, "r")

    data = []
    line = f.readline()
    while len(line) > 0:
        if len(line) > 0 and line[0] != "#": # skip comments
            line = strip(line)
            line = split(line, ",")
            line = map(lambda x: float(x), line)
            data.append(line)
        line = f.readline()
        
    f.close()
    return data


def absolve(data, col = 0):
    """The Xede highspeed timestamps only have a range of a little over ten minutes.
    After such time, they overflow back to zero. absolve will convert long, cicular
    timestamps to absolute ones (relative to the first sample).
    """
    TIME_DELTA = 600 # ten minutes
    start_time = 0
    for i in range(1,len(data)):
        # we jumped back at least TIME_DELTA
        if float(data[i-1][col]) - start_time - float(data[i][col]) > TIME_DELTA: 
            if float(data[i][col]) > 15.0: # near zero
                raise ValueError, "values did not overflow to zero" 
            start_time = float(data[i-1][0])

        if start_time: # this cannot happen first iteration
            data[i][0] = float(data[i][0]) + start_time      

    return data

if __name__ == "__main__":
    d = read_csv("homie.csv")
    absolve(d)
    for i in d:
       print "%s, %s, %s, %s, %s" % (i[0], i[1], i[2], i[3], i[4])

