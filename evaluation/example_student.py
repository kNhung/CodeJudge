def sum_list(nums):
    """Return the sum of a list of numbers."""
    total = 0
    for n in nums:
        total += n
    return total

if __name__ == "__main__":
    print(sum_list([1,2,3]))
