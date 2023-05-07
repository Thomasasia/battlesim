
class Soldier:
    #name = "default"
    #character = "d"
    #maxhp = 1
    #hitpoints = 1
    #attack_ph = 1
    #attack_m = 0
    #defense_ph = 1
    #defense_m = 0
    #attacks = 1
    #penetration = 0
    #aoe = 0
    #morale = 1
    #moralepool = 1
    #size = 1

    #melee = True
    #ranged = False
    #healer = False
    #marked = False # determines if the console will output messages from this soldier especially. ie for player characters.


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
    #num_ranks = 1
    #rank = [] # all ranks
    #soldiers = [] # all soldiers
    def __init__(self, soldiers, num_ranks):
        self.num_ranks = num_ranks
        self.soldiers = soldiers
        self.rank = []
        self.sort_soldiers()

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







class Army:
    #regiments = []
    def __init__(self, regiments):
        self.regiments = regiments
        #print("army init:")
        #print(regiments)
        #print(regiments[0].rank)
        #print()
    def print_army(self):
        for regiment in self.regiments:
            print()
            for rank in regiment.rank:
                for soldier in rank:
                    print(soldier.character, end='')
                print()

def match_soldeirs(line1, line2, n=3):
    bigline = []
    smallline = []
    if len(line1) >= len(line2):
        bigline = line1
        smallline = line2
    else:
        bigline = line2
        smallline = line1
    biglength = 0
    smalllength = 0
    for soldier in bigline:
        biglength += soldier.size
    for soldier in smallline:
        smalllength += soldier.size
    length_ratio = biglength / smalllength
    
    # i should probably make a more efficient method. Probably a hash table. Def a hash table!!
    def size_index_to_soldier(l, s):
        if 0 > s:
            raise Exception("Size cannot be negative")
        sc = 0
        for i in range(len(l)):
            sc += l[i].size
            if sc >= s:
                #print("size: " + str(s) + " position/index: " + str(i))
                return i
        print("Size indexer failed~~")
        print(l)
        print(sc)
        print(s)
        print()
        raise Exception("Size indexer failure")

    # trim excess
    if length_ratio > n:
        diff = biglength - (smalllength * n)
        purgei1 = size_index_to_soldier(bigline, int(diff/2))
        purgei2 = size_index_to_soldier(bigline, biglength - int(diff/2) - (diff%2))
        #print("diff " + str(diff))
        #print(purgei1)
        #print(purgei2)


        bigline = bigline[purgei1:purgei2]
        biglength = 0
        for soldier in bigline:
            biglength += soldier.size
        length_ratio = n
    
    # calculate sizematch
    smallsizematch = []
    sizeeach = int(biglength/smalllength)
    sizeextra = int(biglength) % int(smalllength)
    for i in range(smalllength): # initialization, with size each default
        smallsizematch.append(sizeeach)
    
    mindex = 0
    midsize = int(len(smallsizematch)-1/2) -1
    midflip = 0
    #print("sizextra : " + str(sizeextra))
    while sizeextra > 0:
        midflip *= -1
        if midflip >= 0:
            midflip +=1
        smallsizematch[midsize + midflip] +=1
        sizeextra -= 1

    #print("Small size match: ")
    #print(smallsizematch)
    #print("Size each: ")
    #print(sizeeach)
    #print("Size extra: ")
    #print(sizeextra)
    #print("Big length: ")
    #print(biglength)
    #print("small length: ")
    #print(smalllength)
    #print()

    # map sizes to sizes, to create a list of pairings.
    # start with right
    fights = []
    bigrightindex = 0
    bigmid = int(biglength/2)
    smallmid = int(smalllength/2)
    for i in range(smallmid, len(smallsizematch)):
        #print(" I VALUE : " + str(i), " midsize" + str(smallmid))
        for n in range(smallsizematch[i]):
            
            big_index = size_index_to_soldier(bigline, bigmid + bigrightindex)
            #print("bigmid :" + str(bigmid) + " bigrightindex : " + str(bigrightindex) + " big_index = " + str(big_index))
            small_index = size_index_to_soldier(smallline, i +1)
            fight = [bigline[big_index], smallline[small_index], big_index, small_index]
            bigrightindex += 1
            # no redundant fights
            if len(fights) == 0:
                fights.append(fight)
            elif fight[0] != fights[-1][0] or fight[1] != fights[-1][1]:
                fights.append(fight)
    bigleftindex = -1
    for i in range(smallmid-1, -1, -1):
        #print(" I VALUE : " + str(i))
        for n in range(smallsizematch[i]):
            
            big_index = size_index_to_soldier(bigline, bigmid + bigleftindex)
            #print("bigmid :" + str(bigmid) + " bigleftindex : " + str(bigleftindex)  + " big_index = " + str(big_index))
            small_index = size_index_to_soldier(smallline, i +1)
            fight = [bigline[big_index], smallline[small_index], big_index, small_index]
            bigleftindex -= 1
            # no redundant fights
            if len(fights) == 0:
                fights.append(fight)
            elif fight[0] != fights[-1][0] or fight[1] != fights[-1][1]:
                fights.append(fight)
    return fights

def print_fights(fights):
    for fight in fights:
        text = fight[0].name + " at position " + str(fight[2]) + " vs " + fight[1].name + " at position " + str(fight[3])
        print(text) 

    

soldiers1 = []
for i in range(3):
    soldiers1.append(Soldier("Outnumbered Dude", 'A', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, True, False, False, False))

soldiers2 = []
for i in range(10):
    soldiers2.append(Soldier("Confident Dude", 'A', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, True, False, False, False))


reg1 = Regiment(soldiers1, 1)
reg2 = Regiment(soldiers2, 1)


army1 = Army([reg1])
army2 = Army([reg2])

army1.print_army()
army2.print_army()

fights = match_soldeirs(army1.regiments[0].rank[0], army2.regiments[0].rank[0])

print_fights(fights)
