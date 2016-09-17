

class Calculator(object):
    @classmethod
    def sum_of_collection(cls, nums, start, end, step):
        res = 0
        if len(nums) > 0:
            for anum in nums[start:end:step]:
                res += anum
        return res


