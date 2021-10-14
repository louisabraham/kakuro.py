from functools import lru_cache, partial
from collections import defaultdict

from set_cover import solve as solve_set_cover


def encode(pattern, cols, lines):
    grid = [[c == "0" for c in line] for line in pattern.split()]
    n = len(grid)

    constraints = []

    # build constraints on lines
    vars = []
    cur = 0
    for i in range(n):
        for j in range(n):
            if grid[i][j]:
                vars.append((i, j))
            if (j == n - 1 or not grid[i][j]) and vars:
                constraints.append((lines[cur], vars))
                cur += 1
                vars = []

    # build constraints on columns
    vars = []
    cur = 0
    for j in range(n):
        for i in range(n):
            if grid[i][j]:
                vars.append((i, j))
            if (i == n - 1 or not grid[i][j]) and vars:
                constraints.append((cols[cur], vars))
                cur += 1
                vars = []

    # map variables to constraints
    var_to_cons = defaultdict(list)
    for c, (_, vars) in enumerate(constraints):
        for var in vars:
            var_to_cons[var].append(c)

    Y = {}
    for i in range(n):
        for j in range(n):
            if not grid[i][j]:
                continue
            for x in range(1, 10):
                # each cell has exactly one value
                Y[i, j, x] = [("pos", i, j)]
                for c in var_to_cons[i, j]:
                    # each value can be used at most once
                    Y[i, j, x].append(("con", c, x))

    # add the "complement" values
    for c, (tot, vars) in enumerate(constraints):
        for t in decomp(45 - tot, 9 - len(vars)):
            Y[c, t] = [("con", c)]
            for x in t:
                Y[c, t].append(("con", c, x))

    # build X from Y
    X = defaultdict(set)
    for y, l in Y.items():
        for x in l:
            X[x].add(y)

    return n, X, Y


@lru_cache(None)
def decomp(n, k, mini=1):
    if n < mini:
        return []
    if k == 1:
        return [(n,)] if n < 10 else []
    ans = []
    for x in range(mini, 10):
        for t in decomp(n - x, k - 1, mini=x + 1):
            ans.append((x,) + t)
    return ans


def pp_sol(n, sol):
    grid = [[0 for _ in range(n)] for _ in range(n)]
    for x in sol:
        if len(x) == 3:
            i, j, x = x
            grid[i][j] = x

    return "\n".join("".join(str(x) for x in line) for line in grid)


def solve(pattern, cols, lines):
    n, X, Y = encode(pattern, cols, lines)
    yield from map(partial(pp_sol, n), solve_set_cover(X, Y))


if __name__ == "__main__":
    pattern = """
                0000X000
                00000000
                00000000
                X0000000
                0000000X
                00000000
                00000000
                000X0000
            """
    cols = [10, 13, 38, 39, 31, 28, 36, 39, 12, 10]
    lines = [14, 8, 38, 36, 35, 35, 37, 36, 6, 11]
    print(next(solve(pattern, cols, lines)))
