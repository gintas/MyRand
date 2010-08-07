import os

def linreg(X, Y):
    # Taken from http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
    from math import sqrt
    if len(X) != len(Y):  raise ValueError, 'unequal length'

    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in map(None, X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    a, b = (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det

    meanerror = residual = 0.0
    for x, y in map(None, X, Y):
        meanerror = meanerror + (y - Sy/N)**2
        residual = residual + (y - a * x - b)**2
    RR = 1 - residual/meanerror
    ss = residual / (N-2)
    Var_a, Var_b = ss * N / det, ss * Sxx / det

    #print "y=ax+b"
    #print "N= %d" % N
    #print "a= %g \\pm t_{%d;\\alpha/2} %g" % (a, N-2, sqrt(Var_a))
    #print "b= %g \\pm t_{%d;\\alpha/2} %g" % (b, N-2, sqrt(Var_b))
    #print "R^2= %g" % RR
    #print "s^2= %g" % ss

    return a, b


def examine_buckets(bins, iterations):
    print 'bucket range:', min(bins.keys()), max(bins.keys())
    print 'bucket count:', len(bins.keys())
    print 'bucket spread:', min(bins.values()), max(bins.values()), '(avg %d)' % (iterations / 256)
    x = [p[0] for p in bins.items()]
    y = [p[1] for p in bins.items()]
    a, b = linreg(x, y)
    print 'linear regression: a=%.03f, b=%.03f' % (a, b)


def find_period(s, block=256):
    part = s[:block]
    pos = s[block:].find(part)
    if pos != -1:
        return pos + block
    else:
        return 'n/a'


def to_bits(s):
    bits = []
    for c in s:
        x = ord(c)
        for i in range(8):
            bits.append(x % 2)
            x = x >> 1
    return bits


def draw_plot(s, filename='result.png'):
    IMAGE_WIDTH = 1024
    IMAGE_HEIGHT = 768
    n_pixels = IMAGE_HEIGHT * IMAGE_WIDTH
    plottable = s[:n_pixels // 8]

    import Image
    img = Image.new('1', (IMAGE_WIDTH, IMAGE_HEIGHT))
    img.putdata(to_bits(plottable))
    img.save(filename)


def test(cls, seed=123, iterations=100000):
    test_name = cls.__name__
    print 'Testing:', test_name
    print 'Iterations:', iterations

    r = cls(seed=seed)
    s = ''

    lsb_bins = {}
    msb_bins = {}
    for i in range(256):
        lsb_bins[i] = msb_bins[i] = 0
    for i in xrange(iterations):
        x = r.randint()
        lsb_bins[x % 256] += 1
        msb_bins[(x >> 24) % 256] += 1

        for j in range(4):
            s += chr(x % 256)
            x = x >> 8

    print '== LSB =='
    examine_buckets(lsb_bins, iterations)
    print '== MSB =='
    examine_buckets(msb_bins, iterations)
    print '==='

    print 'Period:', find_period(s)

    import gzip
    fn = '/tmp/rand.gz'
    f = gzip.open(fn, 'wb') # TODO: tempfile
    f.write(s)
    f.close()

    gzipped_len = os.stat(fn).st_size
    print 'Gzip factor:', float(gzipped_len) / (iterations * 4)
    print 'Drawing plot...'
    draw_plot(s, filename=test_name.lower() + '.png')
    print '--------------------------------------------------'


def main():
    import rand
    test(rand.BBS)
    test(rand.LCG)
    test(rand.DigitMul)
    #test(rand.DigitMul, iterations=1000000)
    #test(rand.DigitMul, iterations=10000000)


if __name__ == '__main__':
    main()
