from utils import Origin


class Watch:
    brand: str = ''
    ref: str = ''
    price: str = 0
    origin: Origin

    def is_set(self):
        return self.brand != '' and self.ref != '' and self.price != 0

    def __eq__(self, other: 'Watch'):
        return self.ref == other.ref

    def __hash__(self):
        return hash(self.ref)

    def __repr__(self):
        return self.ref
