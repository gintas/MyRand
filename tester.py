import zlib

# Constants.
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 768


def main():
    """Main suite."""
    import myrand
    #test(myrand.LCG)
    #test(myrand.BBS)
    test(myrand.NewRandom)
    #test(rand.NewRandom, iterations=1000000)
    #test(rand.NewRandom, iterations=10000000)


def test(cls, seed=123123123, iterations=200000):
    """Run a suite of tests on the given random number generator class.

    `iterations` indicates how many random numbers to generate.

    Prints results to standard output. Creates a PNG image file named after the
    class.
    """
    test_name = cls.__name__
    print 'TEST: %s (%d iterations)' % (test_name, iterations)
    print cls.__doc__
    print '---'

    rng = cls(seed=seed)
    s = ''

    lsb_bins = {}
    msb_bins = {}
    for i in range(256):
        lsb_bins[i] = msb_bins[i] = 0
    for i in xrange(iterations):
        x = rng.randint()
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

    print 'Period length:', find_period(s)

    print 'Gzip factor:', gzip_factor(s)

    plot_filename = test_name.lower() + '.png'
    print 'Drawing plot (%s)...' % plot_filename
    draw_plot(s, filename=plot_filename)
    print '--------------------------------------------------'


def linreg(X, Y):
    """Calculate linear regression between X and Y."""
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


def gzip_factor(s):
    """Check how well a string compresses.

    Returns a float. If the factor is significantly below 1, the string
    probably has significant patterns.
    """
    return float(len(zlib.compress(s))) / len(s)


def to_bits(s):
    """Convert an 8-bit string to a list of bits."""
    bits = []
    for c in s:
        x = ord(c)
        for i in range(8):
            bits.append(x % 2)
            x = x >> 1
    return bits


def draw_plot(s, filename='result.png'):
    """Draw a B&W plot of the bits from a given 8-bit string."""
    n_pixels = IMAGE_HEIGHT * IMAGE_WIDTH
    plottable = s[:n_pixels // 8]

    try:
        import Image
    except ImportError:
        print 'PIL not available! Unable to draw plot.'
        return
    img = Image.new('1', (IMAGE_WIDTH, IMAGE_HEIGHT))
    img.putdata(to_bits(plottable))
    img.save(filename)


if __name__ == '__main__':
    main()
