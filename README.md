# Futoshiki

Python script to solve [futoshiki puzzles](https://en.wikipedia.org/wiki/Futoshiki)


## Logic

Initially the script attempts to use human-like logic (AB elimination and restricting values using inequalities). If this fails, it guesses values with a breadth first search, filling in numbers it can deduce with the human-like logic, until it reaches a solution.


## Example usage

    $ python solve_futoshiki.py puzzle1.txt
    Puzzle:
    . .>. . .
          v
    . . . . .
        v
    . . .<. .

    . . .>. .
    ^     v ^
    .<. . .>.


    Solution:
    1 4>3 2 5
          v
    5 3 2 1 4
            v
    2 1 4<5 3

    3 2 5>4 1
    ^     v ^
    4<5 1 3>2


