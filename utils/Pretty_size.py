from math import log


def prettier_size(n, pow_=0, b=1024, u='B', pre=[''] + [p + 'i' for p in 'KMGTPEZY']):
    r, f = min(int(log(max(n * b ** pow_, 1), b)), len(pre) - 1), '{:,.%if} %s%s'
    return (f % (abs(r % (-r - 1)), pre[r], u)).format(n * b ** pow_ / b ** float(r))