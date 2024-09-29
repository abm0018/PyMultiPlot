import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from pdb import set_trace

def jetMap(point, IMGBITS=8): #assumes data has been normalized
    scale_factor = (2**IMGBITS) - 1
    if (point <= 1.0/8.0):
        red = 0
        green = 0
        blue = 0.5 + 4.0 * point
    elif (point > 1.0/8.0) and (point <= 3.0/8.0):
        red = 0
        green = 4.0 * (point - 1.0/8.0)
        blue = 1.0
    elif (point > 3.0/8.0) and (point <= 5.0/8.0):
        red = 4.0 * (point - 3.0/8.0)
        green = 1.0
        blue = 2.5 - 4.0 * point
    elif (point > 5.0/8.0) and (point <= 7.0/8.0):
        red = 1.0
        green = 3.5 - 4.0 * point
        blue = 0
    else:
        red = 4.5 - 4.0 * point
        green = 0
        blue = 0        

    red = int((red) * scale_factor)
    green = int((green) * scale_factor)
    blue = int((blue) * scale_factor)

    return (red, green, blue)

def colorMap(data, cmap='jet'):
    rtn = np.empty(shape=(len(data),3))
    if (cmap == 'jet'):
        for i in range(len(data)):
            rtn[i] = jetMap(data[i])
    return rtn

def testCMAP():
    data = np.arange(0,1,1/32)

    red = [(jetMap(point))[0] for point in data]
    green = [(jetMap(point))[1] for point in data]
    blue = [(jetMap(point))[2] for point in data]
    #set_trace()

    plt.plot(data, red, color='red');
    plt.plot(data, green, color='green');
    plt.plot(data, blue, color='blue');

    plt.axvline(x=1.0/8)
    plt.axvline(x=3.0/8)
    plt.axvline(x=5.0/8)
    plt.axvline(x=7.0/8)
    plt.show()

def PILTest():
    img = np.ones(shape=(50, 50, 3), dtype=np.uint8) * 255
    img[0][0] = [255,0,0]
    img[1][0] = [0,255,0]
    img[2][0] = [0,0,255]
    out = Image.fromarray(np.array(img), "RGB")
    out.show()
    out.save('out.png', 'PNG')

def main():
    FS = 30e3
    tstop = 1000e-3

    t = np.arange(0,tstop,1/FS)
    rand_phase = np.random.random(len(t)) * np.pi
    rand_amp = np.random.random(len(t))
    data = np.sin(t * 2 * np.pi * 893) + \
        0.25 * np.sin(t * 2 * np.pi * 1.2e3) + \
        0.75 * np.sin(t * 2 * np.pi * 3.3e3) + \
        0.89 * np.sin(t * 2 * np.pi * 12.8e3) + \
        0.89 * np.sin(t * 2 * np.pi * 7.75e3 + rand_phase)

    fout = open('sample_data2.csv', 'w')
    for point in data:
        fout.write(f'{point},')
    fout.close()

    Y = np.fft.fftshift(np.fft.fft(data))
    Y = abs(Y)
    Y /= max(Y)
    Y = Y[len(Y)//2:]

    N = len(Y)
    fft_freqs = (FS/2) * np.arange(0,1,1/N)
    img_row = colorMap(Y, cmap='jet')

    rows = num_ffts = 1
    cols = fft_len = N
    img = np.ones(shape=(rows, cols, 3), dtype=np.uint8) * 255
    
    #img[0] = img_row

    for row in range(rows):
        img[row] = img_row #just showing each FFT multiple times

    plt.plot(fft_freqs, Y); plt.show()



    img = Image.fromarray(img, 'RGB')
    # img.show()

    img = img.resize((N*10, 100))
    img.show()

if __name__ == '__main__':
    main()