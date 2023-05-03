
class soldier:
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

    def __init__(self, name, character, maxhp, attack_ph, attack_m, defense_ph, defense_m, attacks, penetration, aoe, morale, moralepool, size, melee, ranged, healer):
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

class regiment:
    num_ranks = 1
    rank = [] # all ranks
    soldiers = [] # all soldiers
    def __init__(self, soldiers, num_ranks):
        self.num_ranks = num_ranks
        self.soliders = soldiers
        sort_soldiers()
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
        for key in types.keys:
            if len(t) == 0:
                t.append(name)
            else:
                slen = len(t)
                for n in range(t):
                    if len(types[key]) >= len(types[t[n]]):
                        t.insert(n, key)
                        break
                is slen == len(t):
                    t.append(key)
        # add each type into the middle
        # this will surround the commanders by their soldiers
        for key in t:
            num_solders = len(key)
            per_rank = num_soldiers / self.num_ranks
            soldier_index = 0
            for r in self.rank:
                for i in range(per_rank):
                    r.insert(len(r)/2, key[soldier_index])
                    soldier_index+=1
            # put extras into the first rank
            while soldier_index < num_soldiers:
                self.rank[0]..insert(len(r)/2, key[soldier_index])
                soldier_index+=1




class army:
    regiments = []
    def __init__(self, regiments):
        self.regiments = regiments