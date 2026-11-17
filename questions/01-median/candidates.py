"""The three supplied implementations with distinct names for comparison."""


def median_a(nums):
    nums.sort()
    n = len(nums)
    mid = n // 2
    if n % 2 == 0:
        return (nums[mid - 1] + nums[mid]) // 2
    return nums[mid]


def median_b(nums):
    s = sorted(nums)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def median_c(nums):
    if not nums:
        return None
    s = sorted(nums)
    n = len(s)
    if n % 2:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2
