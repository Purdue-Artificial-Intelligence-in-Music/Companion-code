import os

def clear_terminal():
    os.system('cls||clear')

def pr(item):
    print(item, end="")

def print_one_directional_bar(width: int = 15, portion_filled: float = 0.0):
    num_filled = int(width * 2 * portion_filled)
    num_total = width * 3 - 1
    pr("|")
    counter_total = 0
    counter_filled = 0
    while counter_total < num_total:
        if counter_total % 3 == 2:
            pr(".")
        else:
            if counter_filled < num_filled:
                pr("=")
                counter_filled += 1
            else:
                pr(" ")
        counter_total += 1
    pr("|")
    return 2 + num_total

def print_two_directional_bar(width: int = 5, portion_filled: float = 0.0):
    num_filled = abs(int(width * 2 * portion_filled))
    if portion_filled != 0.0 and num_filled < 1:
        num_filled = 1
    num_blank = 2 * width - num_filled
    num_total = 3 * width - 1
    pr("|")
    if portion_filled < 0.0:
        counter_total = 0
        counter_filled = 0
        while counter_total < num_total:
            if counter_total % 3 == 2:
                pr(".")
            else:
                if counter_filled < num_blank:
                    pr(" ")
                    counter_filled += 1
                else:
                    pr("=")
            counter_total += 1
        pr("|")
        counter_total = 0
        while counter_total < num_total:
            if counter_total % 3 == 2:
                pr(".")
            else:
                pr(" ")
            counter_total += 1
    else:
        counter_total = 0
        while counter_total < num_total:
            if counter_total % 3 == 2:
                pr(".")
            else:
                pr(" ")
            counter_total += 1
        pr("|")
        counter_total = 0
        counter_filled = 0
        while counter_total < num_total:
            if counter_total % 3 == 2:
                pr(".")
            else:
                if counter_filled < num_filled:
                    pr("=")
                    counter_filled += 1
                else:
                    pr(" ")
            counter_total += 1
    pr("|")
    return 3 + 2 * num_total