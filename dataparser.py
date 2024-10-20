

def getAsciiData(data):
    possible_delimiters = [',', ' ', '\n', '\t'] #whichever of these occurs the most in the data, I will assume is the delimiter
    delimiter_max = 0
    delimiter_curr = ''

    for delimiter in possible_delimiters:
        if (data.count(delimiter) > delimiter_max):
            delimiter_max = data.count(delimiter)
            delimiter_curr = delimiter
    print(f'Delimiter Detected: {delimiter_curr}')
    data_raw = data
    data = data.split(delimiter_curr)

    if '.' in data_raw: #probably dealing with floating point data
        data = [float(point) for point in data if point]
        print('Detected float data') #changed priority here so we can have floats with 'e' for exponents
    elif ('a' in data_raw.lower()) or \
        ('b' in data_raw.lower()) or \
        ('c' in data_raw.lower()) or \
        ('d' in data_raw.lower()) or \
        ('e' in data_raw.lower()) or \
        ('f' in data_raw.lower()):
        print('Detected int, base16 data')
        data = getHexData(data) 
    else: #assuming int data, base10
        data = [int(point) for point in data if point]
        print('Detected int, base10 data')
    return data

def getHexData(data):
    numbits = len(data[0]) * 4
    signbitmask = (2**(numbits-1))
    xormask = (2**numbits)-1
    rtn = []
    for point in data:
        if (point): #use this to discard '' entries
            point = int(point, 16)
            if (point & signbitmask): #we have a negative number
                # 2's complement, flip all bits, add one, multiply by -1
                point ^= xormask
                point += 1
                point *= -1
            rtn.append(point)
    return rtn