"""Pure calculation excerpts from MoneyLab's clock_alignment.py.

No network access, account connection, or operating-system clock changes.
Inputs represent estimated clock offsets, not guaranteed one-way latency.
Inputs must already be validated: finite numeric times/offsets and finite,
nonnegative uncertainties in seconds. This excerpt is not a full clock protocol.
See PUBLICATION.md for provenance.
"""
import statistics


def combine(samples):
    if len(samples)<3:raise ValueError('clock_samples')
    offsets=[s['offset'] for s in samples];mid=statistics.median(offsets)
    if max(offsets)-min(offsets)>.05:raise ValueError('clock_unstable')
    low=max(s['offset']-s['uncertainty'] for s in samples)
    high=min(s['offset']+s['uncertainty'] for s in samples)
    if low>high:raise ValueError('clock_intervals_disagree')
    return (low+high)/2,(high-low)/2+.002


def timing_parts(arrived,received,market,sample):
    offset=sample['main_minus_sub'];utc=sample['utc_minus_main']
    return {'raw_transport_ms':(arrived-received)*1000,
        'transport_ms':(arrived-received-offset)*1000,
        'broker_sub_ms':(received+offset+utc-market)*1000,
        'market_age_ms':(arrived+utc-market)*1000}
