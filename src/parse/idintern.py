class IdIntern:
    """
    Intern IDs and produce a much smaller unique integer that makes it
    easier to identify in debug structures.
    """
    id_to_num: dict[int, int]
    num_to_id: dict[int, int]
    next: int
    
    def __init__(self):
        self.id_to_num = {}
        self.num_to_id = {}
        self.next = 1

    def intern_id(self, id: int):
        if id in self.id_to_num:
            return self.id_to_num[id]
        else:
            next = self._get_next()
            self.id_to_num[id] = next
            self.num_to_id[next] = id
            return next
        
    def get_id_or_none(self, id: int):
        if id in self.id_to_num:
            return self.id_to_num[id]
        else:
            return None

    def _get_next(self):
        next = self.next
        self.next += 1
        return next