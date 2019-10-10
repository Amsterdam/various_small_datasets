from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Point:
     x: int
     y: int

@dataclass
class C:
     mylist: List[Point]

p = Point(10, 20)
c = C([p])

def fact(o):
    print(o)
    return dict(o)

print(asdict(c))
print(asdict(c, dict_factory=fact))