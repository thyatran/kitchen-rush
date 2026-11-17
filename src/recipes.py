import json
from collections import Counter
from pathlib import Path


class RecipeBook:
    def __init__(self, path):
        self.recipes = json.loads(Path(path).read_text())

    def match(self, ingredients):
        actual = Counter((item.name, item.state) for item in ingredients)
        for name, requirements in self.recipes.items():
            expected = Counter((item['name'], item['state']) for item in requirements)
            if actual == expected:
                return name
        return None

    def can_add(self, ingredients, candidate):
        actual = Counter((item.name, item.state) for item in [*ingredients, candidate])
        return any(not (actual - Counter((i['name'], i['state']) for i in recipe))
                   for recipe in self.recipes.values())
