class Plan:
    def __init__(self, name: str, max_works_per_month: int, max_concurrent: int, priority: int):
        self.name = name
        self.max_works_per_month = max_works_per_month
        self.max_concurrent = max_concurrent
        self.priority = priority

class PlanFactory:
    @staticmethod
    def create(name: str) -> "Plan":
        if name == "premium":
            return Plan("premium", 12, 3, 1)
        return Plan("free", 3, 1, 2)
