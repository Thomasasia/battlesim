
class Soldier:
    name = "default"
    character = "d"
    maxhp = 1
    hitpoints = 1
    attack_ph = 1
    attack_m = 0
    defense_ph = 1
    defense_m = 0
    attacks = 1
    penetration = 0
    aoe = 0
    morale = 1
    moralepool = 1
    size = 1

    melee = True
    ranged = False
    healer = False
    marked = False # determines if the console will output messages from this soldier especially. ie for player characters.


    def __init__(self, name, character, maxhp, attack_ph, attack_m, defense_ph, defense_m, attacks, penetration, aoe, morale, moralepool, size, melee, ranged, healer, marked):
        self.name = name
        self.character = character
        self.maxhp = maxhp
        self.hitpoints = maxhp
        self.attack_ph = attack_ph
        self.attack_m = attack_m
        self.defense_ph = defense_ph
        self.defense_m = defense_m
        self.attacks = attacks
        self.penetration = penetration
        self.aoe = aoe
        self.morale = morale
        self.moralepool = moralepool
        self.size = size

        self.melee = melee
        self.ranged = ranged
        self.healer = healer
        self.marked = marked

class Regiment:
    num_ranks = 1
    rank = [] # all ranks
    soldiers = [] # all soldiers

    def swap_ranks(self, pos1, pos2):
        temp = self.rank[pos1]
        self.rank[pos1] = self.rank[pos2]
        self.rank[pos2] = temp

    def sort_soldiers(self):
        self.rank.clear()
        for i in range(self.num_ranks):
            self.rank.append([])
        types = {}
        for soldier in self.soldiers:
            if not soldier.character in types.keys():
                types[soldier.character] = []                
            types[soldier.character].append(soldier)
        # sort types by count
        t = []
        for key in types.keys():
            if len(t) == 0:
                t.append(key)
            else:
                slen = len(t)
                for n in range(len(t)):
                    if len(types[key]) >= len(types[t[n]]):
                        t.insert(n, key)
                        break
                if slen == len(t):
                    t.append(key)
        # add each type into the middle
        # this will surround the commanders by their soldiers
        for key in t:
            num_soldiers = len(types[key])
            per_rank = int(num_soldiers / self.num_ranks)
            soldier_index = 0
            for r in self.rank:
                for i in range(per_rank):
                    r.insert(int(len(r)/2), types[key][soldier_index])
                    soldier_index+=1
            # put extras into the first rank
            while soldier_index < num_soldiers:
                self.rank[0].insert(int(len(r)/2), types[key][soldier_index])
                soldier_index+=1
            
            # the front will have the most variety, so we move that to the back so commanders dont die immediately.
            if self.num_ranks > 1:
                self.swap_ranks(0, len(self.rank)-1)

    def __init__(self, soldiers, num_ranks):
        self.num_ranks = num_ranks
        self.soldiers = soldiers
        self.sort_soldiers()





class Army:
    regiments = []
    def __init__(self, regiments):
        self.regiments = regiments
    def print_army(self):
        for regiment in self.regiments:
            print()
            for rank in regiment.rank:
                for soldier in rank:
                    print(soldier.character, end='')
                print()



soldiers = []
for i in range(100):
    soldiers.append(Soldier("Dude", 'A', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, True, False, False, False))
for i in range(30):
    soldiers.append(Soldier("Dude", 'B', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, True, False, False, False))
for i in range(1):
    soldiers.append(Soldier("Dude", 'C', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, True, False, False, False))

reg = Regiment(soldiers, 3)
army = Army([reg])
army.print_army()
