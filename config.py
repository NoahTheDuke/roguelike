import yaml

mons = None
with open("monsters.yaml", 'r') as mon:
    mons = [x for x in yaml.load_all(mon)]

print(mons)
print(type(mons))
for x in mons:
    print(x)
