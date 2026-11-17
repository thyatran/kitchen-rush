from dataclasses import dataclass


@dataclass
class Ingredient:
    name: str
    state: str = 'raw'

    @property
    def label(self):
        return f'{self.state} {self.name}'


@dataclass
class Dish:
    name: str

    @property
    def label(self):
        return self.name
