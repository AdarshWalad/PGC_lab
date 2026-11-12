"""
Cache Coherence Protocol Simulator
Simulates MSI, MESI, and MOESI cache coherence protocols
with adjacent and padded memory layouts.
"""

import random
import sys

# Cache states
# MSI: Modified, Shared, Invalid
# MESI: Modified, Exclusive, Shared, Invalid
# MOESI: Modified, Owned, Exclusive, Shared, Invalid

class CacheBlock:
    def __init__(self):
        self.state = 'I'  # Start Invalid

class BusStats:
    def __init__(self):
        self.bus_transactions = 0
        self.busRd = 0
        self.busRdX = 0
        self.busUpgr = 0
        self.invalidations = 0
        self.writeback = 0
        self.c2c = 0
        self.silent_E_to_M = 0

def simulate_MSI(num_iterations, layout, trace=False):
    core0 = CacheBlock()
    core1 = CacheBlock()
    stats = BusStats()

    for i in range(num_iterations):
        # Alternate: core0 R, core0 W, core1 R, core1 W, ...
        ops = [('core0', 'R'), ('core0', 'W'), ('core1', 'R'), ('core1', 'W')]
        for core_name, op in ops:
            core  = core0 if core_name == 'core0' else core1
            other = core1 if core_name == 'core0' else core0

            prev_state_c0 = core0.state
            prev_state_c1 = core1.state

            if op == 'R':
                if core.state == 'I':
                    # BusRd
                    stats.bus_transactions += 1
                    stats.busRd += 1
                    if other.state == 'M':
                        stats.writeback += 1
                        other.state = 'S'
                        stats.c2c += 1
                    elif other.state == 'S':
                        pass
                    else:
                        pass
                    core.state = 'S'
                    if other.state == 'M':
                        other.state = 'S'
                # else already S or M, no bus transaction

            elif op == 'W':
                if core.state == 'I':
                    stats.bus_transactions += 1
                    stats.busRdX += 1
                    if other.state in ('M', 'S'):
                        stats.invalidations += 1
                        if other.state == 'M':
                            stats.writeback += 1
                        other.state = 'I'
                    core.state = 'M'
                elif core.state == 'S':
                    stats.bus_transactions += 1
                    stats.busUpgr += 1
                    if other.state == 'S':
                        stats.invalidations += 1
                        other.state = 'I'
                    core.state = 'M'
                # else already M, no bus transaction

            if trace and i < 2:
                print(f"  {core_name} {op}  -> C0={core0.state} C1={core1.state}")

    return stats

def simulate_MESI(num_iterations, layout, trace=False):
    core0 = CacheBlock()
    core1 = CacheBlock()
    stats = BusStats()

    for i in range(num_iterations):
        ops = [('core0', 'R'), ('core0', 'W'), ('core1', 'R'), ('core1', 'W'),
               ('core0', 'R'), ('core0', 'W'), ('core1', 'R'), ('core1', 'W')]

        ops = [('core0', 'R'), ('core0', 'W'), ('core1', 'R'), ('core1', 'W')]
        for core_name, op in ops:
            core  = core0 if core_name == 'core0' else core1
            other = core1 if core_name == 'core0' else core0

            if op == 'R':
                if core.state == 'I':
                    stats.bus_transactions += 1
                    stats.busRd += 1
                    if other.state == 'M':
                        stats.writeback += 1
                        stats.c2c += 1
                        other.state = 'S'
                        core.state = 'S'
                    elif other.state == 'E':
                        other.state = 'S'
                        core.state = 'S'
                        stats.c2c += 1
                    elif other.state == 'S':
                        core.state = 'S'
                    else:
                        # Exclusive since no other sharer
                        core.state = 'E'

            elif op == 'W':
                if core.state == 'I':
                    stats.bus_transactions += 1
                    stats.busRdX += 1
                    if other.state in ('M', 'E', 'S'):
                        stats.invalidations += 1
                        if other.state == 'M':
                            stats.writeback += 1
                        other.state = 'I'
                    core.state = 'M'
                elif core.state == 'S':
                    stats.bus_transactions += 1
                    stats.busUpgr += 1
                    if other.state == 'S':
                        stats.invalidations += 1
                        other.state = 'I'
                    core.state = 'M'
                elif core.state == 'E':
                    # Silent E->M upgrade
                    stats.silent_E_to_M += 1
                    core.state = 'M'
                # else M, no action

            if trace and i < 2:
                print(f"  {core_name} {op}  -> C0={core0.state} C1={core1.state}")

    return stats

def simulate_MOESI(num_iterations, layout, trace=False):
    core0 = CacheBlock()
    core1 = CacheBlock()
    stats = BusStats()

    for i in range(num_iterations):
        ops = [('core0', 'R'), ('core0', 'W'), ('core1', 'R'), ('core1', 'W')]
        for core_name, op in ops:
            core  = core0 if core_name == 'core0' else core1
            other = core1 if core_name == 'core0' else core0

            if op == 'R':
                if core.state == 'I':
                    stats.bus_transactions += 1
                    stats.busRd += 1
                    if other.state == 'M':
                        # Owner supplies data, no writeback needed
                        other.state = 'O'
                        core.state = 'S'
                        stats.c2c += 1
                    elif other.state == 'O':
                        core.state = 'S'
                        stats.c2c += 1
                    elif other.state == 'E':
                        other.state = 'S'
                        core.state = 'S'
                        stats.c2c += 1
                    elif other.state == 'S':
                        core.state = 'S'
                    else:
                        core.state = 'E'

            elif op == 'W':
                if core.state == 'I':
                    stats.bus_transactions += 1
                    stats.busRdX += 1
                    if other.state in ('M', 'O', 'E', 'S'):
                        stats.invalidations += 1
                        if other.state == 'O':
                            stats.writeback += 1
                        other.state = 'I'
                    core.state = 'M'
                elif core.state in ('S', 'O'):
                    stats.bus_transactions += 1
                    stats.busUpgr += 1
                    if other.state in ('S', 'O'):
                        stats.invalidations += 1
                        other.state = 'I'
                    core.state = 'M'
                elif core.state == 'E':
                    stats.silent_E_to_M += 1
                    core.state = 'M'

            if trace and i < 2:
                print(f"  {core_name} {op}  -> C0={core0.state} C1={core1.state}")

    return stats

def print_stats_table(results):
    print(f"\n{'Totals for 1000 iterations'}")
    print(f"{'layout':<10} {'protocol':<8} {'bus transactions':<20} {'BusRd':<10} {'BusRdX':<10} "
          f"{'BusUpgr':<10} {'invalidations':<15} {'writeback':<12} {'c2c':<6} {'silent E->M'}")
    for (layout, proto, stats) in results:
        print(f"{layout:<10} {proto:<8} {stats.bus_transactions:<20} {stats.busRd:<10} "
              f"{stats.busRdX:<10} {stats.busUpgr:<10} {stats.invalidations:<15} "
              f"{stats.writeback:<12} {stats.c2c:<6} {stats.silent_E_to_M}")

def main():
    num_iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    print(f"State trace, first 2 iterations, adjacent layout (line A: core0 state / core1 state)\n")

    print("MSI:")
    simulate_MSI(num_iterations, 'adjacent', trace=True)
    print("\nMESI:")
    simulate_MESI(num_iterations, 'adjacent', trace=True)
    print("\nMOESI:")
    simulate_MOESI(num_iterations, 'adjacent', trace=True)

    results = []
    for layout in ['adjacent', 'padded']:
        for proto, func in [('MSI', simulate_MSI), ('MESI', simulate_MESI), ('MOESI', simulate_MOESI)]:
            stats = func(num_iterations, layout)
            results.append((layout, proto, stats))

    print_stats_table(results)

if __name__ == '__main__':
    main()
