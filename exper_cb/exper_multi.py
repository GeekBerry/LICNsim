import multiprocessing

from itertools import product

from exper_cb.exper_1 import main


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes = 7)

    for normal, graph_mode, lam, cs_mode, evict_mode, evict_time in product(
        (False, True),
        ('ba', 'tree'),  # ('grid', 'ba', 'tree'),
        (20, 60, 100),
        ('LCE', 'LCP', 'LCD'),
        ('FIFO', 'LRU', 'GEOMETRIC'),
        (20, 60, 100),
    ):
        pool.apply_async( main, (graph_mode, lam, cs_mode, evict_mode, evict_time, normal) )

    pool.close()
    pool.join()
