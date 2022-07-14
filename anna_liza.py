import json

def load_file(path, split_lines):
    with open(path) as f:
        return [json.loads(line) for line in f] if split_lines else json.load(f)

# This function is ugly, I admit, but its ugliness makes the program a LOT faster
# Do not refactor without profiling the resulting program
def merge(online1, online2):
    i1 = i2 = 0
    len1, len2 = len(online1), len(online2)
    # The list 'result' has to avoid appending to it (function calls have a significant overhead)
    # The 'lenr' variable contains the actual length of the used part of the list
    result = [None] * (len1 + len2)
    lenr = 0
    # Gradually iterate throughout the lists, always incrementing the index of the list whose current value is smaller
    # The variables with '1' suffix should refer to the list which has smaller value at the current index
    while i1 < len1 and i2 < len2:
        if online1[i1] > online2[i2]:
            i1, i2, online1, online2, len1, len2 = i2, i1, online2, online1, len2, len1
        elif online1[i1] == online2[i2]:
            # 'i1' is incremented always; if the current values are equal, 'i2' should be incremented as well
            i2 += 1
        # The first item of the tuple should always contain the smaller (or equal) of the two values
        # Since we always increment the index of the list whose current value is smaller (i.e. 'i1'),
        # 'online2[i2]' is the first value of online2 which is greater than online1[i1], therefore
        # 'online2[i2 - 1]' (if 'i2' > 0) is smaller than or equal to 'online1[i1]'
        if i2 > 0:
            result[lenr] = online1[i1] - online2[i2 - 1] 
            lenr += 1
        i1 += 1
    if i1 < len1:
        i2, online1, online2, len2 = i1, online2, online1, len1
    while i2 < len2 and online1:
        result[lenr] = online2[i2] - online1[-1]
        lenr += 1
        i2 += 1
    return result[:lenr]

def rank_pair(onlines1, onlines2, maxT):
    boths = [0] * (maxT + 1)
    for delta in merge(onlines1, onlines2):
        for T in range(delta, maxT + 1):
            boths[T] += 1
    one = len(onlines1) + len(onlines2) - boths[0]
    return ([both / one for both in boths] if one > 0 else [0] * (maxT + 1), one)

def rank(onlines, maxT):
    return [(id1, id2, *rank_pair(o1, o2, maxT)) for id1, o1 in onlines.items() for id2, o2 in onlines.items() if id1 < id2]

def count_inclusions(ranking, maxT):
    inclusions = {(id1, id2): 0 for id1, id2, _, _ in ranking}
    for T in range(maxT + 1):
        visited = set()
        for id1, id2, _, _ in sorted(ranking, key = lambda pair: -pair[2][T]):
            if id1 not in visited and id2 not in visited:
                inclusions[id1, id2] += 1
            visited.update({id1, id2})
    return inclusions

def filter_ranking(ranking, maxT):
    inclusions = count_inclusions(ranking, maxT)
    return sorted(((id1, id2, sum(ranks) / len(ranks), one, inclusions[id1, id2]) for id1, id2, ranks, one in ranking), key = lambda pair: -pair[2])

def compute_ranking(onlines, maxT):
    return filter_ranking(rank(onlines, maxT), maxT)

def print_ranking(names, ranking, min_inclusions, max_inclusions):
    print('{:^20}+{:^20} | online | together | included'.format('suspect 1', 'suspect 2'))
    for id1, id2, rank, one, inclusions in ranking:
        if inclusions >= min_inclusions:
            print('{:^20}+{:^20} |{:>4}:{:0>2} |{:>7.1f} % |{:>4}/{:>2}'.format(names[id1], names[id2], int(one / 60), one % 60, rank * 100, inclusions, max_inclusions))

def input_int(msg, minimum, maximum, default):
    try:
        return min(maximum, max(minimum, int(input('{} ({}-{}, default {}): '.format(msg, minimum, maximum, default)))))
    except:
        return default

names = load_file('names.txt', split_lines = False)
loaded = load_file('onlines.txt', split_lines = True)

last_time = len(loaded) - 1
last_week = max(0, last_time - 7 * 1440)
while input('Continue? [Y/N] ').strip().lower().startswith('y'):
    maxT = input_int('Maximal T argument', 0, 30, 9)
    min_inclusions = input_int('Filter strictness', 0, maxT + 1, maxT + 1)
    analysed_begin = input_int('Begining of the analysed period', 0, last_time, last_week)
    analysed_end = input_int('End of the analysed period', 0, last_time, last_time)
    analysed = loaded[analysed_begin:analysed_end + 1]

    onlines = {id: [i for i, data in enumerate(analysed) if int(id) in data] for id in names}

    print_ranking(names, compute_ranking(onlines, maxT = maxT), min_inclusions = min_inclusions, max_inclusions = maxT + 1)
