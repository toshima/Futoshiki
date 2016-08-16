
# sentinel return values
NO_SOLUTION = object()
MULTIPLE_SOLUTIONS = object()

EMPTY = "."
UP = "^"
DOWN = "v"
LEFT = "<"
RIGHT = ">"


class PuzzleState(dict):
    def __init__(self, size, arrows, display_offset=1):
        self.size = size
        self.squares = [(x, y) for x in range(self.size)
                        for y in range(self.size)]

        self.arrows = arrows
        for (x1, y1), (x2, y2) in arrows:
            if abs(x1 - x2) + abs(y1 - y2) != 1:
                raise ValueError()
        self.display_offset = display_offset

    def copy(self):
        puz = PuzzleState(self.size, self.arrows, self.display_offset)
        puz.update(**self)
        return puz

    def is_complete(self):
        return len(self) == self.size * self.size

    def is_valid(self):
        for (x, y), value in self.iteritems():
            for z in [x, y, value]:
                if not 0 <= z < self.size:
                    return False

        for k1, k2 in self.arrows:
            if k1 in self and k2 in self and self[k1] >= self[k2]:
                return False

        for x in range(self.size):
            seen = set()
            for y in range(self.size):
                if (x, y) in self:
                    value = self[(x, y)]
                    if value in seen:
                        return False
                    seen.add(value)

        for y in range(self.size):
            seen = set()
            for x in range(self.size):
                if (x, y) in self:
                    value = self[(x, y)]
                    if value in seen:
                        return False
                    seen.add(value)

        return True

    def __str__(self):
        out = ""
        for x in range(self.size):
            for y in range(self.size):
                xy = x, y
                if xy in self:
                    out += str(self[xy] + self.display_offset)
                else:
                    out += EMPTY

                if y < self.size - 1:
                    right = (x, y+1)
                    if (xy, right) in self.arrows:
                        out += LEFT
                    elif (right, xy) in self.arrows:
                        out += RIGHT
                    else:
                        out += " "
            out += "\n"

            if x < self.size - 1:
                for y in range(self.size):
                    xy = x, y
                    down = (x+1, y)
                    if (xy, down) in self.arrows:
                        out += UP
                    elif (down, xy) in self.arrows:
                        out += DOWN
                    else:
                        out += " "
                    out += " "
            out += "\n"
        return out


def test_puzzle_state():
    arrows = [
        ((1, 2), (0, 2)),
        ((1, 3), (2, 3)),
        ((3, 0), (3, 1)),
        ((3, 1), (4, 1)),
        ((3, 2), (4, 2)),
        ((4, 0), (3, 0)),
        ((4, 4), (4, 3)),
    ]

    puz = PuzzleState(5, arrows)
    puz[(0, 2)] = 3
    puz[(0, 3)] = 0
    puz[(4, 2)] = 2
    assert puz.is_valid()

    puz[(1, 2)] = 4
    assert not puz.is_valid()


def parse_puzzle(text, display_offset=1):
    lines = text.strip().split('\n')
    assert len(lines) % 2 == 1
    for i, line in enumerate(lines):
        if i % 2:
            if len(line) > len(lines):
                raise ValueError("Line {} is too long".format(i))
        else:
            if len(line) != len(lines):
                raise ValueError("Line {} is the wrong length".format(i))
        lines[i] = str.ljust(line, len(lines))

    initial = set()
    arrows = set()
    n = len(lines) / 2 + 1
    if n > 9:
        raise ValueError("Cannot parse a puzzle larger than 9x9")

    for x in xrange(n):
        for y in xrange(n):
            c = lines[2*x][2*y]
            if '1' <= c <= str(n):
                value = int(c)
                initial.add(((x, y), value-display_offset))
            elif c != EMPTY:
                raise ValueError("Invalid char at {}, {}".format(2*x, 2*y))

            for dx, dy in [(1, 0), (0, 1)]:
                if 2*x+dx < len(lines) and 2*y+dy < len(lines):
                    c = lines[2*x+dx][2*y+dy]
                    if c == UP:
                        arrows.add(((x, y), (x+1, y)))
                    elif c == DOWN:
                        arrows.add(((x+1, y), (x, y)))
                    elif c == LEFT:
                        arrows.add(((x, y), (x, y+1)))
                    elif c == RIGHT:
                        arrows.add(((x, y+1), (x, y)))
                    elif c != ' ':
                        raise ValueError("Invalid char at {}, {}".format(2*x+dx, 2*y+dx))

    return n, arrows, initial


def solve(puz, verbose=False):
    n = puz.size
    queue = [puz]
    while queue:
        top = queue.pop()
        solution = solve_no_guess(top, verbose)
        if solution == MULTIPLE_SOLUTIONS:

            # puzzle cannot be solved without guessing, so guess values
            # and add to search tree
            for value in range(n):
                for x in range(n):
                    for y in range(n):
                        copy = top.copy()
                        copy[(x, y)] = value
                        if copy.is_valid():
                            queue.insert(0, copy)
        elif solution != NO_SOLUTION:
            # puzzle is solved
            return solution

    return NO_SOLUTION


def solve_no_guess(puz, verbose=False):
    if not puz.is_valid():
        return NO_SOLUTION

    subsets = [subset for subset in power_set(range(puz.size))
               if 0 < len(subset) < puz.size]

    possible = {}
    for xy in puz.squares:
        possible[xy] = {puz[xy]} if xy in puz else set(range(puz.size))

    while not puz.is_complete():
        change = False
        empty_squares = [xy for xy in puz.squares if xy not in puz]
        for xy1, xy2 in puz.arrows:
            if not possible[xy1] or not possible[xy2]:
                return NO_SOLUTION
            if xy1 not in puz:
                upper_bound = puz.get(xy2, max(possible[xy2]))
                for value in range(puz.size):
                    if value >= upper_bound and value in possible[xy1]:
                        change = True
                        possible[xy1].remove(value)
            if xy2 not in puz:
                lower_bound = puz.get(xy1, min(possible[xy1]))
                for value in range(puz.size):
                    if value <= lower_bound and value in possible[xy2]:
                        change = True
                        possible[xy2].remove(value)

            if verbose:
                print "Possible values:", xy1, ','.join(map(str, possible[xy1]))
                print "Possible values:", xy2, ','.join(map(str, possible[xy2]))

        for x in range(puz.size):
            for subset in subsets:
                union = set.union(*(possible[(x, y)] for y in subset))
                if len(union) < len(subset):
                    return NO_SOLUTION

                elif len(union) == len(subset):
                    for y in range(puz.size):
                        if y not in subset and possible[(x, y)] & union:
                            change = True
                            possible[(x, y)] -= union
                            if verbose:
                                print "Possible values", (x, y), \
                                    ','.join(map(str, possible[(x, y)]))

        for y in range(puz.size):
            for subset in subsets:
                union = set.union(*(possible[(x, y)] for x in subset))
                if len(union) < len(subset):
                    return NO_SOLUTION

                elif len(union) == len(subset):
                    for x in range(puz.size):
                        if x not in subset and possible[(x, y)] & union:
                            change = True
                            possible[(x, y)] -= union
                            if verbose:
                                print "Possible values", (x, y), \
                                    ','.join(map(str, possible[(x, y)]))

        for xy in empty_squares:
            if len(possible[xy]) == 1:
                (value, ) = possible[xy]
                puz[xy] = value
            if not puz.is_valid() or not possible[xy]:
                return NO_SOLUTION

        if verbose:
            print "current state:"
            print puz

        if not change:
            return MULTIPLE_SOLUTIONS

    return puz


class NoSolution(Exception):
    pass


class MultipleSolutions(Exception):
    pass


def power_set(l):
    if not l:
        yield set()
    else:
        for x in power_set(l[1:]):
            yield x | {l[0]}
            yield x


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("puzzle")
    parser.add_argument("-v", "--verbose", action='store_true')
    args = parser.parse_args()

    with open(args.puzzle, 'r') as f:
        puzzle = f.read()

    size, arrows, initial = parse_puzzle(puzzle)
    puz = PuzzleState(size, arrows)
    for xy, value in initial:
        puz[xy] = value

    print "Puzzle:"
    print puz

    solution = solve(puz, verbose=args.verbose)
    if solution == NO_SOLUTION:
        print "No solution"
    elif solution == MULTIPLE_SOLUTIONS:
        print "Multiple solutions"
    else:
        assert solution.is_valid() and solution.is_complete()
        print "Solution:"
        print solution
