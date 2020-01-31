# (2) my resource_gen    = [ 2,  2,  2,  0,  0]
# (3) point resource_gen = [ 2,  1,  0,  0,  1]

# (5) = (3) / [(2) + 1]  = [2/3,1/3, 0,  0,  1]


class Player:
    resource_generation = [2, 2, 2, 0, 0]


class Point:
    resource_generation = [2, 1, 0, 0, 1]


player = Player()
point = Point()

four = [res + 1 for res in player.resource_generation]
print('four')
print(four)

five = [a/b for (a, b) in zip(point.resource_generation, four)]
print('five')
print(five)
