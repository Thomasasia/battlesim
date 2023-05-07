import random

# much faster than urandom, good for integer randomness
def random_bytes(n):
    return random.getrandbits(8 * n).to_bytes(n, 'big')

def random_roll(min_roll = 1, max_roll = 3, byte_count = 1):
    if min_roll == max_roll:
        return min_roll
    else:
        return (int.from_bytes(random_bytes(byte_count), "big") % max_roll) + min_roll

def random_roll_f_dice(f, max_roll = 3, min_roll = 1):
    total_roll = 0
    if f == 0:
        return 0
    int_val = int(f)
    f_val = f % int_val
    for i in range(int_val):
        total_roll += random_roll(min_roll = min_roll, max_roll = max_roll)
    if f_val > 0:
        total_roll += random_roll(min_roll = min_roll, max_roll = max_roll) * f_val
    return total_roll

class Soldier:
    def __init__(self, name="soldier", character="S", maxhp=3, attack_ph=1, attack_m=0, defense_ph=1, defense_m=0, attacks=1, penetration=0, aoe=0, morale_save=1, morale_pool_contribution=2, size=1, melee=True, ranged=False, healer=False, marked=False):
        self.name = name
        self.character = character
        self.maxhp = maxhp
        self.hitpoints = maxhp
        self.attack_ph = attack_ph
        self.attack_m = attack_m
        self.defense_ph = defense_ph
        self.defense_m = defense_m
        self.attacks = attacks
        self.attacks_left = attacks
        self.penetration = penetration
        self.aoe = aoe
        self.morale_save = morale_save
        self.morale_pool_contribution = morale_pool_contribution
        self.size = size

        self.melee = melee
        self.ranged = ranged
        self.healer = healer
        self.marked = marked

    # returns true if the morale save is successful
    def roll_morale_save(self, ignore_death = False):
        if not ignore_death and self.hitpoints <= 0:
            return True
        
        roll = random_roll_f_dice(self.morale_save, max_roll = 3)
        if roll > 0:
            return True
        else:
            return False

class Regiment:
    #num_ranks = 1
    #rank = [] # all ranks
    #soldiers = [] # all soldiers
    def __init__(self, name, soldiers, num_ranks):
        self.name = name
        self.num_ranks = num_ranks
        self.soldiers = soldiers
        self.rank = []
        self.sort_soldiers()
        self.calculate_morale_pool()
    
    def calculate_morale_pool(self):
        self.max_morale = 0
        self.morale_pool = 0
        for soldier in self.soldiers:
            self.max_morale += soldier.morale_pool_contribution
        self.morale_pool = self.max_morale

    def refresh_attacks(self):
        for line in self.rank:
            for soldier in line:
                soldier.attacks_left = soldier.attacks

    def swap_ranks(self, pos1, pos2):
        temp = self.rank[pos1]
        self.rank[pos1] = self.rank[pos2]
        self.rank[pos2] = temp

    def index_from_size(self,r, size):
        sizecounter = 0
        for i in range(len(self.rank[r])):
            sizecounter += self.rank[r][i].size
            if sizecounter >= size:
                return i
    def size_from_index(self,r, index):
        size_counter = 0
        for i in range(index+1):
            size_counter += self.rank[r][i].size
        return size_counter

    def get_adjacent(self, rank_index, index, distance):
        sizemap = []
        for r in self.rank:
            maxsize = 0
            for soldier in r:
                maxsize += soldier.size
            sizemap.append(maxsize)
        # we need to calculate midsize for the size, counting from the middle instead of the edges
        def size_to_midsize(size, maxsize):
            return size - (maxsize / 2)
        def midsize_to_size(size, maxsize):
            return size + (maxsize / 2)
        
        center = size_to_midsize(self.size_from_index(rank_index, index), sizemap[rank_index])
        min_rank_search = max(0, rank_index - distance)
        max_rank_search = min(len(self.rank)-1, rank_index + distance)

        adjacent_soldiers = []
        for i in range(min_rank_search, max_rank_search + 1, 1):
            
            for s in range(int(center - distance), int(center + distance + 1), 1):
                soldier = self.index_from_size(i, midsize_to_size(s, sizemap[i]))
                if soldier == None:
                    continue
                soldier = self.rank[i][soldier]
                if len(adjacent_soldiers)==0:
                    adjacent_soldiers.append(soldier)
                elif adjacent_soldiers[-1] != soldier:
                    adjacent_soldiers.append(soldier)
        return adjacent_soldiers





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
    def __init__(self, name, regiments):
        self.regiments = regiments
        self.name = name
        #print("army init:")
        #print(regiments)
        #print(regiments[0].rank)
        #print()

    # add option to invert the display
    # center the army lines
    def print_army(self):
        for regiment in self.regiments:
            print()
            for rank in regiment.rank:
                for soldier in rank:
                    print(soldier.character, end='')
                print()
    
    # random soldier, using size instead of index inside of a line
    def get_weighed_random_soldier(self):
        regroll = []
        for i in range(len(self.regiments)):
            # closer regiments to the front are much more likely to be hit
            roll = random_roll_f_dice( len(self.regiments) - i   )
            regroll.append(roll)
        
        selected_regiment_index = 0
        selected_regiment_index_roll = 0
        for i in range(len(regroll)):
            if selected_regiment_index_roll < regroll[i]:
                selected_regiment_index_roll = regroll[i]
                selected_regiment_index = i
        
        ranksize = len(self.regiments[selected_regiment_index].rank) -1
        rank_index = random_roll(min_roll = 0, max_roll = ranksize, byte_count = ranksize + 1)
        rank = self.regiments[selected_regiment_index].rank[rank_index]

        maxsize = 0
        for soldier in rank:
            maxsize += soldier.size
        
        size_selection = random_roll(min_roll = 1, max_roll = maxsize, byte_count = 8)

        soldier_index = 0
        size_counter = 0
        for i in range(len(rank)):
            size_counter += rank[i].size
            if size_counter >= size_selection:
                soldier_index = i
                break

        return [soldier_index, rank_index, selected_regiment_index]

    def check_empty(self):
        for reg in self.regiments:
            for soldier in reg.soldiers:
                return False
        return True

    def purge_dead(self):
        losses = []
        for reg in self.regiments:
            losses += purge_dead(reg)
        return losses
    def refresh_attacks(self):
        for reg in self.regiments:
            reg.refresh_attacks()


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

def melee_attack(attacker, defender, attacker_mod = 1.0, defender_mod = 1.0):
    if attacker.attacks_left > 0 and defender.hitpoints > 0:
        attacker.attacks_left -= 1
        attacker_attack_score = 0
        defender_defense_score = 0
        # if physical attack is more effective, or if the attacker cannot use magic attacks, attack will be physical
        # in other words, they will use the most effective attack availible to them
        if (attacker.attack_ph - defender.defense_ph) > (attacker.attack_m - defender.defense_m) or attacker.attack_m == 0:
            attacker_attack_score = attacker.attack_ph
            defender_defense_score = defender.defense_ph
        else:
            attacker_attack_score = attacker.attack_m
            defender_defense_score = defender.defense_m
        
        # modifications to score
        def melee_penalty(battle_score, fighter):
            new_battle_score = battle_score
            if fighter.melee == False:
                new_battle_score = new_battle_score / 2
            return new_battle_score

        attacker_attack_score = melee_penalty(attacker_attack_score, attacker) * attacker_mod
        defender_defense_score = melee_penalty(defender_defense_score, defender) * defender_mod

        attack_roll = random_roll_f_dice(attacker_attack_score, max_roll = 3)
        defense_roll = random_roll_f_dice(attacker_attack_score, max_roll = 3, min_roll = 0)

        delta_hp = attack_roll - max( defense_roll - attacker.penetration ,0)
        defender.hitpoints -= max(delta_hp, 0)
        if defender.marked or attacker.marked:
            print(attacker.name + " attackes " + defender.name + "!!")
            print("\t" + attacker.name + " attack strength : " + str(attacker_attack_score))
            print("\t" + attacker.name + " attack roll     : " + str(attack_roll))
            print("\t" + defender.name + " defense strength : " + str(defender_defense_score))
            print("\t" + defender.name + " defense roll     : " + str(defense_roll))
            print("\tAttacker penetration : " + str(attacker.penetration))
            mortal = ""
            if defender.hitpoints <= 0:
                mortal = "MORTAL WOUND!"
            print("\t" + defender.name + " takes " + str(max(delta_hp, 0)) + " damage! " + mortal)

def calculate_melee_fights(reg1, reg2, fights, reg1mod=1.0, reg2mod=1.0, dead_purging = True, reporting = False, attacks_refreshment = True):
    bigreg = []
    smallreg = []
    bigmod = 1.0
    smallmod = 1.0
    if len(reg1.rank[0]) >= len(reg2.rank[0]):
        bigreg = reg1
        bigmod = reg1mod
        smallreg = reg2
        smallmod = reg2mod
    else:
        bigreg = reg2
        bigmod = reg2mod
        smallreg = reg1
        smallmod = reg1mod

    def calculate_morale_mod(reg):
        if isinstance(reg,float):
            raise Exception("invalid regiment, got a number")
        if reg.morale_pool >= 0:
            return 1.0
        else:
            neghalf = reg.max_morale / (-2)
            val = 0.8 - (0.3 (reg.morale_pool / neghalf))
            return val

    bigmod *= calculate_morale_mod(bigreg)
    smallmod *= calculate_morale_mod(smallreg)
    # each soldier must be granted their attacks:
    def reset_attacks(reg):
        for soldier in reg.rank[0]:
            soldier.attacks_left = soldier.attacks

    if attacks_refreshment:
        reset_attacks(reg1)
        reset_attacks(reg2)

    for fight in fights:
        melee_attack(fight[0], fight[1], bigmod, smallmod)
        melee_attack(fight[1], fight[0], bigmod, smallmod)
    
    reg1_soldiers_count = len(reg1.soldiers)
    reg2_soldiers_count = len(reg2.soldiers)

    # now we must remove dead soldiers, and apply morale damage
    losses = []
    if dead_purging:
        losses = [purge_dead(reg1), purge_dead(reg2)]

    #if reporting:
    #    print(reg1.name + " lost " + str(reg1_soldiers_count - len(reg1.soldiers)) + " soldiers")
    #    print(reg2.name + " lost " + str(reg2_soldiers_count - len(reg2.soldiers)) + " soldiers")
    return losses

def purge_dead(reg, morale_damage = True):
    losses = []
    for rank in reg.rank:
        purges = []
        for i in range(len(rank)):
            if rank[i].hitpoints <= 0:
                # reduce the morale pool by their share.
                reg.morale_pool -=  (rank[0].morale_pool_contribution / reg.max_morale) * reg.morale_pool
                purges.append(rank[i])
                # adjacent soldiers must make a morale save, else the morale pool is decreased
                if i-1 >= 0:
                    if not rank[i-1].roll_morale_save():
                        reg.morale_pool -=1
                if i+1 < len(rank):
                    if not rank[i+1].roll_morale_save():
                        reg.morale_pool -=1
        for soldier in purges:
            # remove dead soldiers
            rank.remove(soldier)
    for soldier in reg.soldiers:
        if soldier.hitpoints <= 0:
            if soldier.marked:
                #print(soldier.name + " Dies!")
                pass
            losses.append(soldier)
            reg.soldiers.remove(soldier)
    return losses

def ranged_attack(attacker, defender_index, defender_rank, defender_regiment):
    attack_power = 0
    attack_type = ''
    if attacker.attack_m >= attacker.attack_ph:
        attack_type = 'm'
        attack_power = attacker.attack_m
    else:
        attack_type = 'p'
        attack_power = attacker.attack_ph
    
    

    def defend_against_attack(attack, pen, defender):
        defense_power = 0
        if attack_type == 'm':
            defense_power = defender.defense_m
        else:
            defense_power = defender.defense_ph
        
        defense_roll = random_roll_f_dice(defense_power) - attacker.penetration
        defender.hitpoints -= max(attack - defense_roll, 0)
        if attacker.marked or defender.marked:
            print(attacker.name + " shoots at " + defender.name + " for " + str(max(attack - defense_roll, 0)) + " damage!")
    
    if attacker.aoe < 1:
        attack_roll = random_roll_f_dice(attack_power)
        defend_against_attack(attack_roll, attacker.penetration, defender_regiment.rank[defender_rank][defender_index])
    elif attacker.aoe >= 1:
        adjacent_defenders = defender_regiment.get_adjacent(defender_rank, defender_index, attacker.aoe)

        for defender in adjacent_defenders:
            defend_against_attack(random_roll_f_dice(attack_power), attacker.penetration, defender)
    
def regiment_make_ranged_attacks(regiment, army2):
    for line in regiment.rank:
        for soldier in line:
            if soldier.ranged == True:
                while soldier.attacks_left > 0:
                    defender = army2.get_weighed_random_soldier()
                    ranged_attack(soldier, defender[0], defender[1], army2.regiments[defender[2]])
                    soldier.attacks_left -= 1

def army_make_ranged_attacks(army1, army2):
    for reg in army1.regiments:
        regiment_make_ranged_attacks(reg, army2)

def army_fight(army1, army2, reporting = True):
    army1.refresh_attacks()
    army2.refresh_attacks()
    fights = match_soldeirs(army1.regiments[0].rank[0], army2.regiments[0].rank[0])
    losses = calculate_melee_fights(army1.regiments[0], army2.regiments[0], fights, reporting = True)

    def breakthrough_loop(a1, a2):
        # loop for multiple breakthroughs
        while True:
            losses[0] += army1.purge_dead()
            losses[1] += army2.purge_dead()
            breakthrough = 0
            if len(a1.regiments[0].rank[0]) == 0:
                a1.regiments[0].rank.pop(0)
                breakthrough += 1
            if len(a2.regiments[0].rank[0]) == 0:
                a2.regiments[0].rank.pop(0)
                breakthrough += 2
            
            if len(a1.regiments[0].soldiers) == 0:
                a1.regiments.pop(0)
                break
            if len(a2.regiments[0].soldiers) == 0:
                a2.regiments.pop(0)
                break
            
            if breakthrough > 0:
                armies = [a1, a2]
                if reporting:
                    if breakthrough == 1:
                        print(a2.name + " Breaks through " + a1.name + "'s Front line, and continues forward.")
                    elif breakthrough == 2:
                            print(a1.name + " Breaks through " + a2.name + "'s Front line, and continues forward.")
                    elif breakthrough == 3:
                            print(a1.name + "'s and " + a2.name + "'s frontlines both dissolve, and the fresh second lines charge forward.")

                try:
                    fights = match_soldeirs(a1.regiments[0].rank[0], a2.regiments[0].rank[0])
                    l = calculate_melee_fights(a1.regiments[0], a2.regiments[0], fights, reporting = reporting, attacks_refreshment = False)
                    losses[0] += l[0]
                    losses[1] += l[1]
                except:
                    print(breakthrough)
                    print("t1")
                    print(a1.regiments[0])
                    print("t2")
                    print(a1.regiments[0].rank[0])
                    print("t3")
                    print(a2.regiments[0])
                    print(a2.regiments[0].soldiers[0].hitpoints)
                    print("t4")
                    print(a2.regiments[0].rank[0])

                    

                    raise Exception("fuckshit")
            else:
                break
        
    
    breakthrough_loop(army1, army2)

    print("Melee losses: ")
    print("\t" + army1.name + " loses " + str(len(losses[0])))
    print("\t" + army2.name + " losses " + str(len(losses[1])))
    
    # ranged attacks
    army_make_ranged_attacks(army1, army2)
    army_make_ranged_attacks(army2, army1)

    ranged_losses = [army1.purge_dead(), army2.purge_dead()]

    print("Ranged losses: ")
    print("\t" + army1.name + " loses " + str(len(ranged_losses[0])))
    print("\t" + army2.name + " losses " + str(len(ranged_losses[1])))

    # here is where the healing goes
    
soldiers1 = []
for i in range(100):
    soldiers1.append(Soldier(name="soldier", character="S", maxhp=3, attack_ph=1, attack_m=0, defense_ph=1, defense_m=0, attacks=1, penetration=0, aoe=0, morale_save=1, morale_pool_contribution=2, size=1, melee=True, ranged=False, healer=False, marked=False))

soldiers2 = []
for i in range(10):
    soldiers2.append(Soldier("Defender", 'D', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, True, False, False, False))

artillery = []
for i in range(1):
    artillery.append(Soldier("Artillery Cannon", 'C', 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, True, True, False, False))


reg1 = Regiment("Target Practice", soldiers1, 5)
reg2 = Regiment("Defenders", soldiers2, 1)
artyreg = Regiment("Artillery Regiment", artillery, 1)

army1 = Army("Outnumbered Dude Army",[reg1])
army2 = Army("Confident Dude Army",[reg2,artyreg])

army1.print_army()
army2.print_army()

round = 1
while True:
    print("\n---- ROUND "+str(round)+" ----\n")
    army_fight(army1, army2)

    print("army1")
    army1.print_army()
    print("\narmy2")
    army2.print_army()
    input()
    round += 1
    if army1.check_empty() or army2.check_empty():
        break


# then heal spells.
# then commands
