import random
import json
import glob
import math
from termcolor import colored
import argparse
import sys
global army1
global army2
global SoldierType_Library
SoldierType_Library = {}


global game_log
game_log = []
global new_turn

# the game log is a list of dictionaries. The dictionaries have the following keys:
# messages : messages from commands and such
# battle_log : logs from the battle
# "army.name" : list of losses
# a new dictionary is created each time after combat.

def log_push_message(message):
    global game_log
    game_log[-1]["messages"].append(message)
def log_push_battle_message(message, losses):
    battle_log = {"message" : message, "losses" : losses}
    game_log[-1]["battle_log"].append(battle_log)
def log_add_losses(army_name, losses):
    game_log[-1][army_name].append(losses)
def log_new_turn():
    global game_log
    game_log.append({"messages" : [], "battle_log" : [], army1.name : [], army2.name : []})
    global new_turn
    new_turn = True





# much faster than urandom, good for integer randomness
def random_bytes(n):
    return random.getrandbits(8 * n).to_bytes(n, 'big')

def random_roll(min_roll = 1, max_roll = 3, byte_count = 1):
    if min_roll == max_roll:
        return min_roll
    elif max_roll == 0:
        return 0
    else:
        return (int.from_bytes(random_bytes(byte_count), "big") % max_roll) + min_roll

def random_roll_f_dice(f, max_roll = 3, min_roll = 1):
    total_roll = 0
    if f == 0:
        return 0
    int_val = int(f)
    if int_val == 0:
        return 0
    f_val = f % int_val
    for i in range(int_val):
        total_roll += random_roll(min_roll = min_roll, max_roll = max_roll)
    if f_val > 0:
        total_roll += random_roll(min_roll = min_roll, max_roll = max_roll) * f_val
    return total_roll


class SoldierType:
    def __init__(self, name="soldier", character="S", maxhp=3, attack_ph=1, attack_m=0, defense_ph=1, defense_m=0, attacks=1, penetration=0, aoe=0, morale_save=1, morale_pool_contribution=2, size=1, melee=True, ranged=False, healer=False, marked=False, color = 'light_grey'):
        self.name = name.lower()
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
        self.color = color

class Soldier:

    # alternative constructor that takes a SoldierType object
    def __init__(self, soldiertype):
        self.name = soldiertype.name
        self.character = soldiertype.character
        self.maxhp = soldiertype.maxhp
        self.hitpoints = soldiertype.maxhp
        self.attack_ph = soldiertype.attack_ph
        self.attack_m = soldiertype.attack_m
        self.defense_ph = soldiertype.defense_ph
        self.defense_m = soldiertype.defense_m
        self.attacks = soldiertype.attacks
        self.attacks_left = soldiertype.attacks
        self.penetration = soldiertype.penetration
        self.aoe = soldiertype.aoe
        self.morale_save = soldiertype.morale_save
        self.morale_pool_contribution = soldiertype.morale_pool_contribution
        self.size = soldiertype.size

        self.melee = soldiertype.melee
        self.ranged = soldiertype.ranged
        self.healer = soldiertype.healer
        self.marked = soldiertype.marked
        self.color = soldiertype.color

    # returns true if the morale save is successful
    def roll_morale_save(self, ignore_death = False):
        if not ignore_death and self.hitpoints <= 0:
            return True

        roll = int(random_roll(min_roll = 0, max_roll = self.morale_save))
        if roll > 0:
            return True
        else:
            return False

    def heal_for(self, dice):
        healed_for = 0
        old_hp = self.hitpoints
        self.hitpoints += random_roll_f_dice(dice, max_roll = 2, min_roll = 0)
        if self.hitpoints > self.maxhp:
            self.hitpoints = self.maxhp
        healed_for = self.hitpoints - old_hp
        if self.marked:
            log_push_battle_message(self.name + " heals for " + str(healed_for) + "!", None)
        return healed_for
        

class Regiment:
    #num_ranks = 1
    #rank = [] # all ranks
    #soldiers = [] # all soldiers
    def __init__(self, name, soldiers, num_ranks):
        self.name = name.lower()
        self.num_ranks = num_ranks
        self.soldiers = soldiers
        self.rank = []
        self.sort_soldiers()
        self.calculate_morale_pool()
        self.range_toggle = True

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

    def purge_empty_ranks(self):
        purge_list = []
        for r in self.rank:
            if len(r) == 0:
                purge_list.append(r)
        for p in purge_list:
            self.rank.remove(p)

    def size_from_index(self,r, index):
        size_counter = 0
        for i in range(index+1):
            try :
                size_counter += self.rank[r][i].size
            except IndexError as e:
                raise(e)
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

    def add_soldiers(self, type, number):
        for i in range(number):
            self.soldiers.append(Soldier(type))
            self.morale_pool += type.morale_pool_contribution
            self.max_morale += type.morale_pool_contribution
        
        self.sort_soldiers()

    def get_troop_types(self):
        troops = []
        def check_redundant(name):
            for t in troops:
                if t[0] == name:
                    return True
            return False
        def incr_troop_count(name):
            for t in troops:
                if t[0] == name:
                    t[1] += 1
                    return
        
        for soldier in self.soldiers:
            if check_redundant(soldier.name):
                incr_troop_count(soldier.name)
            else:
                troops.append([soldier.name, 1, soldier.character])

        return troops

class Army:
    #regiments = []
    def __init__(self, name, regiments):
        self.regiments = regiments
        self.name = name.lower()
        self.ranged_enabled = True
        self.temporary_combat_advantage = 1.0
        self.oldtroops = 0
        #print("army init:")
        #print(regiments)
        #print(regiments[0].rank)
        #print()

    # add option to invert the display
    # center the army lines
    def print_army(self, reverse = False, count = False, space_size = -1):
        if space_size == -1:
            max_line = 0
            for regiment in self.regiments:
                for rank in regiment.rank:
                    if len(rank) > max_line:
                        max_line = len(rank)
        else:
            max_line = space_size

        reg_print = []
        for regiment in self.regiments:
            rank_print = []
            for rank in regiment.rank:
                spaces = max_line - len(rank)
                front = math.floor(spaces / 2) * " "
                back = math.ceil(spaces / 2) * " "# remainder goes on the back
                line = ""
                for soldier in rank:
                    line += colored(soldier.character, soldier.color)
                if count : 
                    count_barrier = " || "
                else : 
                    count_barrier = ""
                rank_print.append(front + line + back + count_barrier)
            if reverse:
                rank_print.reverse()

            # display troop counts
            if count:
                troops = regiment.get_troop_types()
                rank_print[0] += colored(" Morale : " + str(regiment.morale_pool), "green") + ""
                i = 1
                if len(rank_print) < 2:
                    i = 0
                rank_print[i] += colored( " Rangle Toggled : " + str(regiment.range_toggle), "red") + " /"

                for i in range(len(troops)):

                    stat_string = " " + str(troops[i][1]) + " " + troops[i][0] + "s (" + colored(troops[i][2], SoldierType_Library[troops[i][0]].color) + ")"
                    if (i+2) / len(rank_print) > 1:
                        stat_string = " /" + stat_string
                    
                    # divide the number stats across the ranks, for better formatting!
                    rank_print[(i+1)%len(rank_print)] += stat_string

            reg_print.append(rank_print)
        if reverse:
            reg_print.reverse()

        print()
        for rp in reg_print:
            for r in rp:
                print(r)
            print()
        print()

    def get_size_of_largest_rank(self):
        max = 0
        for reg in self.regiments:
            for rank in reg.rank:
                size = len(rank)
                if size > max:
                    max = size
        
        return max

    def count_troops(self):
        troop_count = 0
        for reg in self.regiments:
            troop_count += len(reg.soldiers)
        return troop_count

    def prepare_loss_count(self):
        self.oldtroops = self.count_troops()

    def loss_count(self):
        troops = self.count_troops()
        diff = self.oldtroops - troops
        return diff


    def purge_empty_ranks(self):
        for reg in self.regiments:
            reg.purge_empty_ranks()

    def purge_empty_regiments(self):
        purgelist = []
        for reg in self.regiments:
            if len(reg.soldiers)==0:
                purgelist.append(reg)
        for p in purgelist:
            self.regiments.remove(p)

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

        try:
            ranksize = len(self.regiments[selected_regiment_index].rank) -1
        except IndexError:
            print(self.regiments)
            print(selected_regiment_index)
            raise Exception("Trying to shoot at nothing")
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
        purge_reg = []
        for reg in self.regiments:
            losses += purge_dead(reg)
            for rank in reg.rank:
                if len(rank) == 0:
                    reg.rank.remove(rank)
            if len(reg.soldiers) <= 0:
                purge_reg.append(reg)
        for reg in purge_reg:
            self.regiments.remove(reg)

        return losses

    def refresh_attacks(self):
        for reg in self.regiments:
            reg.refresh_attacks()

    def activate_healers(self, reg):
        total_heal = 0
        for soldier in reg.soldiers:
            if soldier.healer:
                wounded = []
                for regiment in self.regiments:
                    for candidate in regiment.soldiers:
                        if candidate.hitpoints < candidate.maxhp:
                            wounded.append(candidate)
                try:
                    total_heal += wounded[random_roll(0, len(wounded) -1)].heal_for(soldier.attack_m)
                except IndexError:
                    pass
        return total_heal

    def activate_all_healers(self):
        total_heal = 0
        for reg in self.regiments:
            total_heal += self.activate_healers(reg)
        return total_heal

    def kill_random_soldiers(self, kills, reg, line, name=''):
        if reg > len(self.regiments)-1:
            reg = len(self.regiments) -1
        if reg > -1:
            if line > len(self.regiments[reg].rank) -1:
                line = len(self.regiments[reg].rank) -1
        if kills == -1:
            count = 0
            for r in self.regiments:
                for soldier in r.soldiers:
                    if soldier.name == name or name == '':
                        soldier.hitpoints = -1
                        count +=1
            if count == 0:
                return -1
            else : return 0

        # build a pool of soldiers to kill
        killpool = []
        if reg <= -1:
            for r in self.regiments:
                for s in r.soldiers:
                    if s.name == name or name == '':
                        killpool.append(s)
        else:
            if reg > len(self.regiments) : reg = len(self.regiments)
            if line == -1:
                for s in self.regiments[reg].soldiers:
                    if s.name == name or name == '':
                        killpool.append(s)
            else:
                if line > len(self.regiments[reg].rank) :
                    line = len(self.regiments[reg].rank)
                for s in self.regiments[reg].rank[line-1]:
                    if s.name == name or name == '':
                        killpool.append(s)
        if len(killpool) <= 0:
            return -1

        kill_count = 0
        for i in range(kills):
            if len(killpool) <= 0:
                break
            roll = random_roll(min_roll=0, max_roll=len(killpool)-1, byte_count=4)
            killpool[roll].hitpoints = -1
            killpool.pop(roll)
            kill_count += 1

        return kill_count

    def get_regiment_position(self, reg):
        for i in range(len(self.regiments) - 1):
            if regiments[i] == reg:
                return i
        return -1

    def get_troop_types(self):
        troops = []
        def check_redundant(name):
            for t in troops:
                if t[0] == name:
                    return True
            return False
        def incr_troop_count(name):
            for t in troops:
                if t[0] == name:
                    t[1] += 1
                    return
        for reg in self.regiments:
            for soldier in reg.soldiers:
                if check_redundant(soldier.name):
                    incr_troop_count(soldier.name)
                else:
                    troops.append([soldier.name, 1])

        return troops


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

    if smalllength == 0:
        raise Exception("Small size is zero!")
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
        return len(l) -1

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

    #midsize = int(len(smallsizematch)-1/2) -1
    midsize = int((len(smallsizematch))/2) -1
    midflip = 0
    #print(smallsizematch)
    #print("sizextra : " + str(sizeextra))
    while sizeextra > 0:
        midflip *= -1
        if midflip >= 0:
            midflip +=1
        #print(smallsizematch)
        #print(midsize)
        #print(len(smallsizematch))
        #print(midflip)
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
            message = "\t" + attacker.name + " attacks " + defender.name + ", rolling " + str(attack_roll) + " vs " + str(defense_roll) + " - " + str(attacker.penetration) + ". " + defender.name + " takes " + str(max(delta_hp, 0)) + " damage, left with " + str(defender.hitpoints) + " HP."
            log_push_battle_message(message, None)
        
        return max(delta_hp,0)
    else:
        return 0

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
            val = 0.8 - (0.3 * (reg.morale_pool / neghalf))
            if val < 0:
                val = 0
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

    bigreg_total_damage = 0
    smallreg_total_damage = 0
    for fight in fights:
        bigreg_total_damage += melee_attack(fight[0], fight[1], bigmod, smallmod)
        smallreg_total_damage += melee_attack(fight[1], fight[0], smallmod, bigmod)

    reg1_soldiers_count = len(reg1.soldiers)
    reg2_soldiers_count = len(reg2.soldiers)

    # now we must remove dead soldiers, and apply morale damage
    losses = []
    if dead_purging:
        losses = [purge_dead(reg1), purge_dead(reg2)]

    log_push_battle_message("As the front lines clash, " + bigreg.name + " does " + str(bigreg_total_damage) + " damage to " + smallreg.name + ", who does " + str(smallreg_total_damage) + " damage in return.", losses)

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
            if soldier.marked:
                message = colored(soldier.name + " has been slain!", "red")
                log_push_message(message)
                log_push_battle_message(message, None)
    purge = []
    for soldier in reg.soldiers:
        if soldier.hitpoints <= 0:
            losses.append(soldier)
            purge.append(soldier)
    for soldier in purge:
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



    def defend_against_attack(attack, pen, defender, aoe=False):
        defense_power = 0
        if attack_type == 'm':
            defense_power = defender.defense_m
        else:
            defense_power = defender.defense_ph

        defense_roll = random_roll_f_dice(defense_power) - attacker.penetration
        defender.hitpoints -= max(attack - defense_roll, 0)
        if attacker.marked or defender.marked:
            if not aoe:
                damage_message = "\t" + attacker.name + " shoots at " + defender.name + " for " + str(max(attack - defense_roll, 0)) + " damage!"
            else:
                damage_message = "\t" + defender.name + " is caught in the blast of " + attacker.name + "\'s attack " + " for " + str(max(attack - defense_roll, 0)) + " damage!"
            log_push_battle_message(damage_message, None)
        return max(attack - defense_roll, 0)

    if attacker.aoe < 1:
        attack_roll = random_roll_f_dice(attack_power)
        try:
            return defend_against_attack(attack_roll, attacker.penetration, defender_regiment.rank[defender_rank][defender_index])
        except IndexError:
            return 0
    elif attacker.aoe >= 1:
        adjacent_defenders = defender_regiment.get_adjacent(defender_rank, defender_index, attacker.aoe)
        dam = 0
        for defender in adjacent_defenders:
            dam += defend_against_attack(random_roll_f_dice(attack_power), attacker.penetration, defender, aoe=True)
        return dam

def regiment_make_ranged_attacks(regiment, army2):
    total_damage = 0
    if regiment.range_toggle:
        for line in regiment.rank:
            for soldier in line:
                if soldier.ranged == True:
                    while soldier.attacks_left > 0:
                        defender = army2.get_weighed_random_soldier()
                        total_damage += ranged_attack(soldier, defender[0], defender[1], army2.regiments[defender[2]])
                        soldier.attacks_left -= 1
    if total_damage > 0:
        message = regiment.name + " fires volleys at " + army2.name + ", doing a total of " + str(total_damage) + "."
        log_push_battle_message(message, None)
    return total_damage

def army_make_ranged_attacks(army1, army2):
    army1.purge_empty_ranks()
    army2.purge_empty_ranks()
    total_damage = 0
    if len(army2.regiments )> 0 and army1.ranged_enabled:
        for reg in army1.regiments:
            total_damage += regiment_make_ranged_attacks(reg, army2)
    if total_damage > 0:
        message = army1.name + "'s ranged attacks against " + army2.name + " do a total of " + str(total_damage) + "."
        log_push_battle_message(message, None)
    army1.purge_empty_ranks()
    army2.purge_empty_ranks()

def army_fight(army1, army2, reporting = True):
    army1.refresh_attacks()
    army2.refresh_attacks()
    for s in army1.regiments[0].soldiers:
        if s.hitpoints <= 0:
            raise Exception("Dead soldiers fighting")

    army1.prepare_loss_count()
    army2.prepare_loss_count()

    fights = match_soldeirs(army1.regiments[0].rank[0], army2.regiments[0].rank[0])
    losses = calculate_melee_fights(army1.regiments[0], army2.regiments[0], fights, reporting = True, reg1mod = army1.temporary_combat_advantage, reg2mod = army2.temporary_combat_advantage)

    def breakthrough_loop(a1, a2):
        # loop for multiple breakthroughs
        while True:
            if len(a1.regiments) == 0 or len(a2.regiments) == 0:
                break
            breakthrough = 0
            if len(a1.regiments[0].rank[0]) == 0:
                a1.regiments[0].rank.pop(0)
                if len (a1.regiments[0].rank) == 0 :
                    a1.regiments.pop(0)
                    break
                breakthrough += 1
            if len(a2.regiments[0].rank[0]) == 0:
                a2.regiments[0].rank.pop(0)
                if len (a2.regiments[0].rank) == 0 : 
                    a2.regiments.pop(0)
                    break
                breakthrough += 2

            if len(a1.regiments[0].soldiers) == 0:
                a1.regiments.pop(0)
                break
            if len(a2.regiments[0].soldiers) == 0:
                a2.regiments.pop(0)
                break
            r1 = a1.regiments[0]
            r2 = a2.regiments[0]
            if breakthrough > 0:
                if breakthrough == 1:
                    log_push_battle_message(r2.name + " Breaks through " + r1.name + "'s Front line, and continues forward.", None)
                elif breakthrough == 2:
                        log_push_battle_message(r1.name + " Breaks through " + r2.name + "'s Front line, and continues forward.", None)
                elif breakthrough == 3:
                        log_push_battle_message(r1.name + "'s and " + r2.name + "'s frontlines both dissolve, and the fresh second lines charge forward.", None)




                fights = match_soldeirs(a1.regiments[0].rank[0], a2.regiments[0].rank[0])
                l = calculate_melee_fights(a1.regiments[0], a2.regiments[0], fights, reporting = reporting, attacks_refreshment = False, reg1mod = army1.temporary_combat_advantage, reg2mod = army2.temporary_combat_advantage)
                losses[0] += l[0]
                losses[1] += l[1]

            else:
                break

    army1_oldrank = len(army1.regiments[0].rank)
    army2_oldrank = len(army2.regiments[0].rank)
    reg1 = army1.regiments[0]
    reg2 = army2.regiments[0]

    army1.purge_empty_ranks()
    army1.purge_empty_regiments()
    army2.purge_empty_ranks()
    army2.purge_empty_regiments()
    breakthrough_loop(army1, army2)

    army1.purge_empty_ranks()
    army1.purge_empty_regiments()
    army2.purge_empty_ranks()
    army2.purge_empty_regiments()

    losses[0] += army1.purge_dead()
    losses[1] += army2.purge_dead()

    if not reg1 in army1.regiments:
        army1_rankdiff = army1_oldrank
    else:
        army1_rankdiff = army1_oldrank - len(reg1.rank)
    if not reg2 in army2.regiments:
        army2_rankdiff = army2_oldrank
    else:
        army2_rankdiff = army2_oldrank - len(reg2.rank)

    melee_message = "In the melee, " + army1.name + " loses " + str(army1.loss_count()) + " and " + str(army1_rankdiff) + " ranks have fallen. " + army2.name + " loses " + str(army2.loss_count())+ " and " + str(army2_rankdiff) + " ranks have fallen.\n"
    log_push_battle_message(melee_message, losses)
    log_push_message(melee_message)

    if not reg1 in army1.regiments:
        doom_message = reg1.name + " in " + army1.name + " has fallen!"
        log_push_battle_message(doom_message, None)
        log_push_message(doom_message)
    if not reg2 in army2.regiments:
        doom_message = reg2.name + " in " + army2.name + " has fallen!"
        log_push_battle_message(doom_message, None)
        log_push_message(doom_message)

    army1.prepare_loss_count()
    army2.prepare_loss_count()
    # ranged attacks
    army_make_ranged_attacks(army1, army2)
    army_make_ranged_attacks(army2, army1)

    ranged_losses = [army1.purge_dead(), army2.purge_dead()]

    ranged_losses = [army1.purge_dead(), army2.purge_dead()]
    ranged_damage_message = "During the ranged attacks, " + army1.name + " loses " + str(army1.loss_count()) + " and " + army2.name + " loses " + str(army2.loss_count()) + "\n"
    log_push_battle_message(ranged_damage_message, ranged_losses)
    log_push_message(ranged_damage_message)


    # here is where the healing goes
    army1heal = army1.activate_all_healers()
    army2heal = army2.activate_all_healers()
    healing_message = army1.name + "\'s healers heal for a total of " + str(army1heal) + " damage, and " + army2.name + " heals for " + str(army2heal) + " damage."
    log_push_battle_message(healing_message, None)
    log_push_message(healing_message)



def populate_troop_library():
    global SoldierType_Library
    # gets all json files in troops, recursively
    files = glob.glob('troops/**/*.json', recursive = True)
    for file in files:
        with open(file, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)
            for s in data:
                if not s["name"] in SoldierType_Library.keys():
                    SoldierType_Library[s["name"]] = SoldierType(name=s["name"], character=s["character"], maxhp=s["maxhp"], attack_ph=s["attack_ph"], attack_m=s["attack_m"], defense_ph=s["defense_ph"], defense_m=s["defense_m"], attacks=s["attacks"], penetration=s["penetration"], aoe=s["aoe"], morale_save=s["morale_save"], morale_pool_contribution=s["morale_pool_contribution"], size=s["size"], melee=s["melee"], ranged=s["ranged"], healer=s["healer"], marked=s["marked"], color=s["color"])

global army_library
army_library = {}
def populate_army_library():
    files = glob.glob('armies/**/*.json', recursive = True)
    for file in files:
        with open(file, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)
            army_library[data["name"]] = data




def get_type_count_from_losses(losses):
    typecount = {}
    for soldier in losses:
        if soldier.name in typecount.keys():
            typecount[soldier.name] += 1
        else:
            typecount[soldier.name] = 1
    return typecount


from help import help as command_help

def print_use(command = ""):
    if command is None : return
    if command == "":
        print()
        for key in command_help.keys():
            print(command_help[key])
            print()
    elif not command in command_help.keys():
        return 0
    else:
        print()
        print(command_help[command])
        print()
    return 1

def use_error(e, cmd):
    print(e)
    print_use(cmd)

def bool_logic(code, cmd):
    if code.lower() == 'true':
        return True
    if code.lower() == 'false':
        return False
    if code.isdecimal():
        if int(code) == 0:
            return False
        if int(code) == 1:
            return True
    use_error("Incorrect boolean value " + code, cmd)
    return None

def army_logic(code, cmd):
    if code.isnumeric():
        if int(code) == 1:
            army = army1
        elif int(code) == 2:
            army = army2
        else:
            use_error("Invalid army value " + code, cmd)
            return None
    else:
        if army1.name == code:
            army = army1
        elif army2.name == code:
            army = army2
        else:
            use_error("Invalid army value " + code, cmd)
            return None
    return army

def regiment_logic(code, army, cmd):
    if army is None:
        return None
    regiment = -1

    if not code.isnumeric():
        for i in range(len(army.regiments)):
            if army.regiments[i].name == code:
                regiment = i
        if regiment == -1:
            use_error("Invalid regiment value", cmd)
            return
    else:
        regiment = int(code) -1
    return regiment

def cmd_pass_turns(cmd):
    turns = 1
    if len(command) > 1:
        if command[1].isnumeric():
            turns = int(command[1])
            if turns <= 0:
                turns = 1
        else:
            use_error("Invalid turns value", 'turn')
            return
    for i in range(turns):
        army_fight(army1,army2)
        global round
        round += 1
        if army1.check_empty() or army2.check_empty():
            return

def cmd_kill_soldiers(cmd):
    command_name = "kill"
    if len(cmd) < 3:
        use_error("Not enough arguments", 'kill')
        return


    global army1
    global army2
    try:
        kills = cmd[1]
    except ValueError:
        use_error("Invalid kills value", 'kill')
        return
    
    army = army_logic(cmd[2], command_name)
    if army is None : return
    regiment = -1
    if len(cmd) > 3:
        regiment = regiment_logic(cmd[3],army,  command_name)
    if regiment is None : return

    line = -1
    if len(cmd) > 4:
        if not cmd[4].isnumeric():
            use_error("Invalid line value", 'kill')
            return
        else:
            line = int(cmd[4])
            if line < -1 :
                line = -1

    ret = army.kill_random_soldiers(int(cmd[1]), regiment, line)

    message = "{} loses {} random soldiers".format(army.name, str(ret))
    if regiment == -1:
        message += " distributed randomly across the entire army"
    elif regiment != -1 and line == -1:
        message += " distributed randomaly across " + army.regiments[regiment].name
    else:
        message += " at rank " + str(line) + " of " + army.regiments[regiment].name
    message += ".\n Deaths:"

    losses = army.purge_dead()

    typecount = get_type_count_from_losses(losses)

    for key in typecount.keys():
        addstr = str(key) + "s : " + str(typecount[key]) + "\n"
    
        message += addstr
    log_push_message(message)

def cmd_range_toggle(cmd):
    global army1
    global army2
    newval = True

    # no arguments, then it flips both
    if len(cmd) == 1:
        army1.ranged_enabled = not army1.ranged_enabled
        army2.ranged_enabled = not army2.ranged_enabled
        log_push_message("Both armies have toggled their ranged. {}:{} {}:{}".format(army1.name, army1.ranged_enabled, army2.name, army2.ranged_enabled))
        return

    if len(cmd) >=2:
        if not cmd[1].isnumeric():
            use_error("Incorrect range toggle value " + cmd[1], 'range_toggle')
            return
        if int(cmd[1]) == 1:
            newval = True
        elif int(cmd[1]) == 0:
            newval = False
        else:
            use_error("Incorrect range toggle value " + cmd[1], 'range_toggle')
            return

    if len(cmd) == 2:
        army1.ranged_enabled = newval
        army2.ranged_enabled = newval
        log_push_message("Both armies have changed their ranged toggle. {}:{} {}:{}".format(army1.name, army1.ranged_enabled, army2.name, army2.ranged_enabled))

        return
    if len(cmd) >= 3:
        army=army_logic(cmd[2], "range_toggle")
        if army is None : return
    reg = -1
    if len(cmd) >=4:
        reg = regiment_logic(cmd[3], army, "range_toggle")
        if reg is None : return

    if reg == -1:
        army.ranged_enabled = newval
        log_push_message("{} has changed their ranged toggle to : {}".format(army.name, army.ranged_enabled))
    else:
        army.regiments[reg].range_toggle = newval
        log_push_message("{} in {} has changed their ranged toggle to : {}".format(army.regiments[reg].name, army.name, army.regiments[reg].range_toggle))

def cmd_morale_change(command):
    if len(command) < 4:
        use_error("Not enough arguments", 'morale_change')
        return
    army = army_logic(command[1], 'morale_change')
    regiment = regiment_logic(command[2], army, 'morale_change')
    if army is None or regiment is None:
        return

    try:
        army.regiments[regiment].morale_pool += int(command[3])
        message = "{} in {} morale has changed by {} to a total of {}.".format(army.regiments[regiment].name, army.name, int(command[3]), str(army.regiments[regiment].morale_pool))
        log_push_message(message)
    except ValueError:
        use_error("Morale change is not numeric", 'morale_change')
        return

def cmd_change_ranks(command):
    if len(command) < 4:
        use_error("Not enough arguments", 'change_ranks')
        return
    army = army_logic(command[1], 'change_ranks')
    regiment = regiment_logic(command[2], army, 'change_ranks')
    if army is None or regiment is None:
        return

    if not command[3].isnumeric():
        use_error("rank depth is not numeric " + command[3], 'change_ranks')
        return
    elif int(command[3]) <= 0:
        use_error("rank depth cannot be 0", 'change_ranks')
        return
    else:
        new_ranks = int(command[3])
        reg = army.regiments[regiment]
        old_ranks = len(reg.rank)
        if new_ranks > len(reg.soldiers):
            new_ranks = len(reg.soldiers)
        reg.num_ranks = new_ranks
        reg.sort_soldiers()
        message = "{} in {} has changed the number of ranks from {} to {}".format(reg.name, army.name, old_ranks, new_ranks)
        log_push_message(message)

def cmd_kss(command):
    if len(command) < 4:
        use_error("Missing arguments ", 'kss')
        return
    soldier_name = command[1]
    try:
        kills = int(command[2])
    except ValueError:
        use_error("Non numeric kill count", 'kss')
        return
    army = army_logic(command[3], 'kss')
    if army is None : return
    regiment = -1
    if len(command) >= 5:
        regiment = regiment_logic(command[4], army, 'kss')
        if regiment is None : return
    line = -1
    if len(command) >= 6:
        try:
            line = int(command[5])
        except ValueError:
            use_error("Non numeric rank chosen", 'kss')
            return
    ret = army.kill_random_soldiers(kills, regiment, line, name=soldier_name)
    if ret == -1:
        use_error("No soldier with name " + command[1] + " found!", None)
        return

    message = "{} loses {} {}s".format(army.name, str(ret), soldier_name)
    if regiment == -1:
        message += " distributed randomly across the entire army."
    elif regiment != -1 and line == -1:
        message += " distributed randomaly across " + army.regiments[regiment].name
    else:
        message += " at rank " + str(line + 1) + " of " + army.regiments[regiment].name

    army.purge_dead()

    #log_push_message(message)

def cmd_add(command):
    command_name = 'add'
    if len(command) < 5:
        use_error("Not enough arguments ", command_name)
        return
    try:
        number = int(command[1])
        if number < 1:
            number = 1
    except ValueError:
        use_error("Non numeric value given for soldier count " + command[1], command_name)
        return
    soldier_name = command[2].lower()
    if not soldier_name in SoldierType_Library.keys():
        use_error("Invalid soldier name " + soldier_name, command_name)
        return
    soldier_type = SoldierType_Library[soldier_name]
    army = army_logic(command[3], command_name)
    if army is None : return
    reg = regiment_logic(command[4], army, command_name)
    if reg is None : return

    army.regiments[reg].add_soldiers(soldier_type, number)

    message = "{} adds {} {}s to {}".format(army.name, str(number), soldier_type.name, army.regiments[reg].name)

def cmd_advantage(command):
    command_name = 'advantage'
    if len(command) < 3:
        use_error("Not enough arguments" , command_name)
        return
    army = army_logic(command[1], command_name)
    if army is None : return
    try:
        adv = float(command[2])
        if adv < 0.0:
            adv = 0.0
    except ValueError:
        use_error("Float needed for advantage " + command[2], command_name)
        return

    army.temporary_combat_advantage = adv
    log_push_message(army.name + " is given a temporary battle advantage of " + str(adv))

def cmd_swap_regiments(command):
    if len(command) < 4:
        use_error("Not enough arguments", 'swap')
        return
    army = army_logic(command[1], 'swap')
    reg1 = regiment_logic(command[2], army, 'swap')
    reg2 = regiment_logic(command[3], army, 'swap')
    if army is None:
        use_error("Invalid army name " + command[1], 'swap')
        return
    if reg1 is None:
        use_error("Invalid reg1 name " + command[2], 'swap')
        return
    if reg2 is None:
        use_error("Invalid reg2 name " + command[3], 'swap')
        return


    message = "In {} {} at position {} swaps places with {} at position {}".format(army.name, army.regiments[reg1].name, str(reg1 +1), army.regiments[reg2].name, str(reg2 + 1))
    log_push_message(message)

    temp = army.regiments[reg1]
    army.regiments[reg1] = army.regiments[reg2]
    army.regiments[reg2] = temp

def cmd_assault(command):
    command_name = 'assault'
    if len(command) < 3:
        use_error("Incorrect number of arguments ", command_name)
        return
    global army1
    global army2
    reg1 = army1.regiments[regiment_logic(command[1], army1, command_name)]
    reg2 = army2.regiments[regiment_logic(command[2], army2, command_name)]

    if reg1 is None: return
    if reg2 is None: return

    ranged_enabled = False
    if len(command) > 3:
        range_enabled = bool_logic(command[3])
        if range_enabled is None : return

    reg1.refresh_attacks()
    reg2.refresh_attacks()

    army1.prepare_loss_count()
    army2.prepare_loss_count()

    fights = match_soldeirs(reg1.rank[0], reg2.rank[0])
    losses = calculate_melee_fights(reg1, reg2, fights, reporting = True, reg1mod = army1.temporary_combat_advantage, reg2mod = army2.temporary_combat_advantage)

    def breakthrough_loop(r1, r2):
        # loop for multiple breakthroughs
        while True:
            breakthrough = 0
            if len(r1.rank[0]) == 0:
                r1.rank.pop(0)
                breakthrough += 1
            if len(r2.rank[0]) == 0:
                r2.rank.pop(0)
                breakthrough += 2

            if len(r1.soldiers) == 0:
                army1.regiments.remove(r1)
                break
            if len(r2.soldiers) == 0:
                army2.regiments.remove(r2)
                break

            if breakthrough > 0:
                if breakthrough == 1:
                    log_push_battle_message(r2.name + " Breaks through " + r1.name + "'s Front line, and continues forward.", None)
                elif breakthrough == 2:
                        log_push_battle_message(r1.name + " Breaks through " + r2.name + "'s Front line, and continues forward.", None)
                elif breakthrough == 3:
                        log_push_battle_message(r1.name + "'s and " + r2.name + "'s frontlines both dissolve, and the fresh second lines charge forward.", None)




                fights = match_soldeirs(r1.rank[0], r2.rank[0])
                l = calculate_melee_fights(r1, r2, fights, reporting = reporting, attacks_refreshment = False, reg1mod = army1.temporary_combat_advantage, reg2mod = army2.temporary_combat_advantage)
                losses[0] += l[0]
                losses[1] += l[1]

            else:
                break

    army1_oldrank = len(reg1.rank)
    army2_oldrank = len(reg2.rank)
    breakthrough_loop(reg1, reg2)

    losses[0] += army1.purge_dead()
    losses[1] += army2.purge_dead()

    if not reg1 in army1.regiments:
        army1_rankdiff = army1_oldrank
    else:
        army1_rankdiff = army1_oldrank - len(reg1.rank)
    if not reg2 in army2.regiments:
        army2_rankdiff = army1_oldrank
    else:
        army2_rankdiff = army1_oldrank - len(reg2.rank)

    log_push_message(reg1.name + " from " + army1.name + " assaults " + reg2.name + " from " + army2.name)
    
    melee_message = "In the assault, " + army1.name + " loses " + str(army1.loss_count()) + " and " + str(army1_rankdiff) + " ranks have fallen. " + army2.name + " loses " + str(army2.loss_count()) + " and " + str(army2_rankdiff) + " ranks have fallen."
    log_push_battle_message(melee_message, losses)
    log_push_message(melee_message)

    if not reg1 in army1.regiments:
        doom_message = reg1.name + " in " + army1.name + " has fallen!"
        log_push_battle_message(doom_message, None)
        log_push_message(doom_message)
    if not reg2 in army2.regiments:
        doom_message = reg2.name + " in " + army2.name + " has fallen!"
        log_push_battle_message(doom_message, None)
        log_push_message(doom_message)


    if ranged_enabled:
        army1.prepare_loss_count()
        army2.prepare_loss_count()
        # ranged attacks
        regiment_make_ranged_attacks(reg1, army2)
        regiment_make_ranged_attacks(reg2, army1)

        ranged_losses = [army1.purge_dead(), army2.purge_dead()]
        ranged_damage_message = "In ranged attacks during the assault, " + army1.name + " loses " + str(army1.loss_count()) + " and " + army2.name + " loses " + str(army2.loss_count())
        log_push_battle_message(ranged_damage_message, ranged_losses)
        log_push_message(ranged_damage_message)

    # here is where the healing goes
    army1heal = army1.activate_healers(reg1)
    army2heal = army2.activate_healers(reg2)
    healing_message = army1.name + "\'s healers heal for a total of " + str(army1heal) + " damage, and " + army2.name + " heals for " + str(army2heal) + " damage."
    log_push_battle_message(healing_message, None)
    log_push_message(healing_message)

def print_troop(troop, count = -1):
    print("Name : " + troop.name)
    if count > 0 : print("Count : " + str(count))
    print("\tcharacter   : " + colored(str(troop.character), troop.color))
    print("\tmaxhp       : " + str(troop.maxhp))
    print("\tattack_ph   : " + str(troop.attack_ph))
    print("\tattack_m    : " + str(troop.attack_m))
    print("\tdefense_ph  : " + str(troop.defense_ph))
    print("\tdefense_m   : " + str(troop.defense_m))
    print("\tattacks     : " + str(troop.attacks))
    print("\tpenetration : " + str(troop.penetration))
    print("\taoe         : " + str(troop.aoe))
    print("\tmorale_save : " + str(troop.morale_save))
    print("\tmorle cntrb : " + str(troop.morale_pool_contribution))
    print("\tsize        : " + str(troop.size))
    print("\tmelee       : " + str(troop.melee))
    print("\tranged      : " + str(troop.ranged))
    print("\thealer      : " + str(troop.healer)) 
    print("\tmarked      : " + str(troop.marked))

def cmd_display_troops(command):
    if len(command) == 1:
        for st in SoldierType_Library:
            print_troop(SoldierType_Library[st])
    else:
        army = army_logic(command[1], "display_troops")
        if army is None : return
        troops = army.get_troop_types()
        for t in troops:
            print_troop(SoldierType_Library[t[0]], count = t[1])

def display_both_armies():
    global army1
    global army2
    space_size = max(army1.get_size_of_largest_rank(), army2.get_size_of_largest_rank())

    army1.print_army(reverse = True, space_size=space_size)
    print("-" * space_size)
    print()
    army2.print_army(space_size=space_size)

def cmd_display_army(command):
    if len(command) == 1:
        display_both_armies()
    else:
        army = army_logic(command[1], "display_army")
        if army is None : return
        army.print_army(count=True)

def print_log_messages(start, log_type):
    log = game_log[-start:]
    for l in log:
        if log_type == "battle" or log_type == "b":
            for b in l["battle_log"]:
                print(b["message"])
        if log_type == "message" or log_type == "messages" or log_type == "m":
            for m in l["messages"]:
                print(m)
    print()


def cmd_show_log(command):
    command_name = "log"
    start = 2
    if len(command) == 1:
        print_log_messages(start, "message")
    command_type = ""
    if len(command) > 1:
        if command[1] != "battle" and command[1] != "message" and command[1] != "b" and command[1] != "m":
            use_error("incorrect log type " + command[1], command_name)
            return
        else:
            if command[1] == "battle" or command[1] == "b":
                command_type = "battle"
            elif command[1] == "message" or command[1] == "m":
                command_type = "message"
            else:
                return
    
    if len(command) > 2:
        try:
            start = int(command[2])
        except ValueError:
            use_error("Non numeric log start " + command[2], command_name)
            return
    if start == 0:
        start = 1
    print_log_messages(start, command_type)

def cmd_show_help(command):
    if len(command) > 1:
        if not command[1] in command_help.keys():
            use_error("Unknown function " + command[1], None)
        else:
            print_use(command[1])
    else:
        print_use()

def cmd_verbose(command):
    global verbose
    verbose = not verbose
    log_push_message("Verbose setting set to : " + str(verbose))

def ask_for_army_name(position):
    while True:
        print("Enter " + position + " army name : ", end = "")
        inp = input()
        if inp in army_library.keys():
            return inp
        else:
            print("Incorrect army name.")

def make_soldiers(type, count):
    soldiers = []
    for i in range(count):
        soldiers.append(Soldier(SoldierType_Library[type]))
    return soldiers

def create_army_from_template(army_name):
    data = army_library[army_name]
    regiments = []
    for reg in data["regiments"]:
        soldiers = []
        for soldier in reg["soldiers"]:
            if not soldier["name"] in SoldierType_Library:
                print("ERROR: nonexistant soldier type in {} : {}".format(army_name, soldier["name"]))
            soldiers += make_soldiers(soldier["name"], soldier["count"])
        r = Regiment(reg["name"], soldiers, reg["num_ranks"])
        regiments.append(r)
    return Army(data["name"], regiments)

populate_troop_library()
populate_army_library()


parser = argparse.ArgumentParser(prog='Tabletop Battle Sim', description="This program is a simulation of a battle, with full control through commands. It is intended as an aid for tabletop gaming.")
parser.add_argument('army_names', type=str, help="names of the two armies to load", nargs='*')
args = parser.parse_args()
army1_name = None
army2_name = None
if len(args.army_names) > 0:
    army1_name = args.army_names[0]
if len(args.army_names) > 1:
    army2_name = args.army_names[1]

if not army1_name is None:
    if not army1_name in army_library.keys():
        print("Nonexistant armyname for army 1 : " + army1_name)
        sys.exit()
if not army2_name is None:
    if not army2_name in army_library.keys():
        print("Nonexistant armyname for army 2 : " + army2_name)
        sys.exit()

if army1_name is None:
    army1_name = ask_for_army_name("first")
if army2_name is None:
    army2_name = ask_for_army_name("second")

army1 = create_army_from_template(army1_name)
army2 = create_army_from_template(army2_name)

display_both_armies()

global verbose
verbose = True

global round
round = 1

log_new_turn()
while True:
    try:
        if army1.check_empty() or army2.check_empty():
            print()
            break
        
        if new_turn:
            display_both_armies()
            print_log_messages(2, "messages")
            new_turn = False
        else:
            try:
                print(game_log[-1]["messages"][-1])
            except IndexError:
                pass

        print(colored("<👉😎👈>", "light_red"), end="")
        command = input().lower().strip().split()
        # pass turns
        if len(command) == 0 or command[0] == 't' or command[0] == 'turn':
            cmd_pass_turns(command)
            army1.temporary_combat_advantage = 1.0
            army2.temporary_combat_advantage = 1.0
            log_new_turn()
            continue

        elif command[0] == 'kill' or command[0] == 'k':
            cmd_kill_soldiers(command)
            continue

        elif command[0] == 'range' or command[0] == 'r':
            cmd_range_toggle(command)
            continue

        elif command[0] == 'morale' or command[0] == 'm':
            cmd_morale_change(command)
            continue

        elif command[0] == 'ranks' or command[0] == 'cr':
            cmd_change_ranks(command)
            continue

        elif command[0] == 'kss':
            cmd_kss(command)
            continue

        elif command[0] == 'add':
            cmd_add(command)
            continue

        elif command[0] == 'advantage' or command[0] == 'adv':
            cmd_advantage(command)
            continue

        elif command[0] == 'swap':
            cmd_swap_regiments(command)
            continue

        elif command[0] == 'assault' or command[0] == 'ass':
            cmd_assault(command)
            army1.temporary_combat_advantage = 1.0
            army2.temporary_combat_advantage = 1.0
            log_new_turn()
            continue

        elif command[0] == 'troops':
            cmd_display_troops(command)
            continue

        elif command[0] == 'show':
            cmd_display_army(command)
            continue

        elif command[0] == 'log':
            cmd_show_log(command)
            continue

        elif command[0] == 'help' or command[0] == 'h':
            cmd_show_help(command)
            continue
        elif command[0] == 'v' or command[0] == "verbose":
            cmd_verbose(command)
            continue
        elif command[0] == "exit":
            sys.exit()
        else:
            print("Unknown command entered : " + command[0])
    except Exception as e:
        print(colored("Ran into an error!", "red"))
        print(e)
        raise(e)

# command to show the help function
# make army for session
# test army
# test for a while
