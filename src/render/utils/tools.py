"""tools for utils."""
# -*- coding: utf-8 -*-

from __future__ import absolute_import


INFINITY = float('inf')


def safeMin(args):
    """Return min item from args, not include None, and inf."""
    args = [arg for arg in args if arg not in (None, INFINITY)]
    if args:
        return min(args)


def safeMax(args):
    """Return max item from args, not include None, and inf."""
    args = [arg for arg in args if arg not in (None, INFINITY)]
    if args:
        return max(args)


def safeSum(values):
    """Return max item from args, not include None, and inf."""
    return sum([v for v in values if v not in (None, INFINITY)])


def any(args):
    for arg in args:
        if arg:
            return True
    return False


def sort_stacked(series_list):
    stacked = [s for s in series_list if 'stacked' in s.options]
    not_stacked = [s for s in series_list if 'stacked' not in s.options]
    return stacked + not_stacked


# Convience functions
def closest(number, neighbors):
    distance = None
    closestNeighbor = None
    for neighbor in neighbors:
        d = abs(neighbor - number)
        if distance is None or d < distance:
            distance = d
            closestNeighbor = neighbor
    return closestNeighbor
