import colorfight

g = colorfight.Game()
direction = [(0,1), (0,-1), (1, 0), (-1,0)] 
circleRadius2 = [(0,2), (1,1), (2,0), (1,-1), (0,-2), (-1,-1), (-2,0), (-1,1)]
diagonal = [(1,1), (1,-1), (-1,1), (-1,-1)]
desiredRatio = 1.5
targetID = 0

def isOnBoundary(x, y, owner='me'):
    b = g.GetCell(x, y)
    if owner == 'me' and b.owner == g.uid or owner == 'enemy' and b.owner != 0 and b.owner != g.uid:
        for c in adjacentCells(b):
            if c.owner != b.owner:
                return True
    return False

def isAttackable(x, y, attacker='me'):
    target = g.GetCell(x, y)
    if not target.isTaking:
        if attacker == 'me':
            if target.owner != g.uid and isAroundMyCell(target):
                return True
        else:
            if target.owner == g.uid:
                for c in adjacentCells(target):
                    if c.owner != 0 and c.owner != g.uid or c.isTaking and c.attacker != g.uid:
                        return True
    return False

def isMultiAttackable(x, y):   
    target = g.GetCell(x, y)
    # if len(adjacentCells(target, 'me')) != 0:
    #     return False
    count = 0
    for c in adjacentCells(target):
        if isAttackable(c.x, c.y):
            count += 1
    return count >= 2

def isEnemyApproaching(target):
    if not target.isTaking and target.owner == g.uid:
        for c in adjacentCells(target):
            if c.isTaking and c.attacker != g.uid:
                return True
    return False

def takeTime(target, boost=False, attackerID=g.uid):
    count = 0
    for c in adjacentCells(target, 'me'):
        count += 1
    if count > 0: 
        count -= 1
    t = target.takeTime
    if boost: 
        t = t * 0.25 if t * 0.25 > 1 else 1
    return t * (1 - count * 0.25) / (1 + g.energy/200.0)

def optimizeAttack(attackable, multiAttackable, goldOrEnergyChoice, enemyBaseChoice):    #detect aggressive AI                                                       
    boost = False       
    if g.energy >= 85:
            boost = True
    if g.energyCellNum >= 4 and g.goldCellNum >= 2:
        for i in range(len(enemyBaseChoice)):
            if not enemyBaseChoice[i][0].isBuilding and g.energy >= 40:
                if len(adjacentCells(enemyBaseChoice[i][0], 'others')) == len(adjacentCells(enemyBaseChoice[i][0])) - 2:
                    if len(adjacentCells(enemyBaseChoice[i][0])) == 4 and isColinear(adjacentCells(enemyBaseChoice[i][0], 'others')[0], adjacentCells(enemyBaseChoice[i][0], 'others')[1]) or len(adjacentCells(enemyBaseChoice[i][0])) == 3 and isColinear(adjacentCells(enemyBaseChoice[i][0], 'others')[0], adjacentCells(enemyBaseChoice[i][0], 'none')[0]):
                        dx1 = enemyBaseChoice[i][0].x - adjacentCells(enemyBaseChoice[i][0], 'self')[0].x 
                        dy1 = enemyBaseChoice[i][0].y - adjacentCells(enemyBaseChoice[i][0], 'self')[0].y 
                        dx2 = enemyBaseChoice[i][0].x - adjacentCells(enemyBaseChoice[i][0], 'self')[1].x 
                        dy2 = enemyBaseChoice[i][0].y - adjacentCells(enemyBaseChoice[i][0], 'self')[1].y
                        for j in range(1, 4):
                            c1 = g.GetCell(enemyBaseChoice[i][0].x + j*dx1, enemyBaseChoice[i][0].y + j*dy1)
                            c2 = g.GetCell(enemyBaseChoice[i][0].x + j*dx2, enemyBaseChoice[i][0].y + j*dy2)
                            if c1 != None and c1.owner == g.uid:
                                if dx1 == 0:
                                    return (c1, False, False, 'vertical')
                                else:
                                    return (c1, False, False, 'horizontal')
                            if c2 != None and c2.owner == g.uid:
                                if dx2 == 0:
                                    return (c2, False, False, 'vertical')
                                else:
                                    return (c2, False, False, 'horizontal')
                if len(adjacentCells(enemyBaseChoice[i][0], 'others')) == len(adjacentCells(enemyBaseChoice[i][0])) - 1:
                    if len(adjacentCells(enemyBaseChoice[i][0])) == 2: 
                        if isColinear(adjacentCells(enemyBaseChoice[i][0], 'others')[0], adjacentCells(enemyBaseChoice[i], 'none')[0]):
                            dx = enemyBaseChoice[i][0].x - adjacentCells(enemyBaseChoice[i][0], 'none')[1].x 
                            dy = enemyBaseChoice[i][0].y - adjacentCells(enemyBaseChoice[i][0], 'none')[1].y 
                        if isColinear(adjacentCells(enemyBaseChoice[i], 'others')[0], adjacentCells(enemyBaseChoice[i][0], 'none')[1]):
                            dx = enemyBaseChoice[i][0].x - adjacentCells(enemyBaseChoice[i][0], 'none')[0].x 
                            dy = enemyBaseChoice[i][0].y - adjacentCells(enemyBaseChoice[i][0], 'none')[0].y 
                    else:
                        dx = enemyBaseChoice[i][0].x - adjacentCells(enemyBaseChoice[i][0], 'self')[0].x 
                        dy = enemyBaseChoice[i][0].y - adjacentCells(enemyBaseChoice[i][0], 'self')[0].y 
                    for j in range(1, 4):
                        c = g.GetCell(enemyBaseChoice[i][0].x + j*dx, enemyBaseChoice[i][0].y + j*dy)
                        if c != None and c.owner == g.uid:
                            if dx == 0:
                                return (c, False, False, 'vertical')
                            else:
                                return (c, False, False, 'horizontal')
    values1 = []    
    values2 = []                                     
    boosted = [boost]*len(attackable)
    if multiAttackable and g.gold >= (3 - g.baseNum) * 60 + 40:   
        for i in range(len(multiAttackable)):
            enemyCells = [c for c in adjacentCells(multiAttackable[i]) if isAttackable(c.x, c.y)]
            myCells = adjacentCells(multiAttackable[i], 'me')
            multiTargets = enemyCells + myCells
            values1 += [33 - max(takeTime(t) for t in multiTargets) + len(enemyCells)/4.0]
            for t in multiTargets:
                if g.energyCellNum >= 4 and g.goldCellNum >= 2:
                    if t.owner != g.uid:
                        for j in range(len(enemyBaseChoice)):
                            if isCloserToDestination(t, enemyBaseChoice[j]):
                                if j == 0: 
                                    values1[i] += 2.5
                                elif j == 1:
                                    values1[i] += 1.5
                                elif j == 2:
                                    values1[i] += 1.25
                    if isAroundEnemyBase(t):
                        values1[i] += 2.75
                if t.isBase:
                    values1[i] = float('-inf')
                else:
                    if t.owner != g.uid:
                        for j in range(len(goldOrEnergyChoice)):
                            if isCloserToDestination(t, goldOrEnergyChoice[j]):
                                if j == 0: 
                                    values1[i] += 1.3
                                elif j == 1:
                                    values1[i] += 0.75
                                elif j == 2:
                                    values1[i] += 0.5
                                elif j == 3:
                                    values1[i] += 0.25
                    if isAroundMyCell(t, 'gold'):   
                        values1[i] += 1.5 if t.owner != g.uid else 0.2
                    if isAroundMyCell(t, 'energy'):
                        values1[i] += 1.5 if t.owner != g.uid else 0.2
                    if isAroundMyCell(t, 'base'):
                        values1[i] += 3 if t.owner != g.uid else 0.4
                    if isAroundMyCell(t, 'gold', 2):
                        values1[i] += 0.6 if t.owner != g.uid else 0.08
                    if isAroundMyCell(t, 'energy', 2):
                        values1[i] += 0.6 if t.owner != g.uid else 0.08
                    if isAroundMyCell(t, 'base', 2):
                        values1[i] += 0.75 if t.owner != g.uid else 0.1
                    if t.owner == g.users[0].id:
                        values1[i] += 1
                    if len(g.users) > 1 and g.users[0].id == g.uid and (isOwnedByCompetitors(t, 50) or t.owner == g.users[1].id):
                        values1[i] += 1
    for i in range(len(attackable)):
        values2 += [33 - takeTime(attackable[i], boost)]
        if g.energyCellNum >= 4 and g.goldCellNum >= 2:
            for j in range(len(enemyBaseChoice)):
                if isCloserToDestination(attackable[i], enemyBaseChoice[j]):
                    if j == 0: 
                        if takeTime(attackable[i]) > 2.5 and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                            values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                            boosted[i] = True
                        values2[i] += 2.5
                    elif j == 1:
                        values2[i] += 1.5
                    elif j == 2:
                        values2[i] += 1.25
            if isAroundEnemyBase(attackable[i]):
                if takeTime(attackable[i]) > 2.5 and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                    values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                    boosted[i] = True
                values2[i] += 2.75 
            if isAroundEnemyBase(attackable[i], True):
                if takeTime(attackable[i]) > 2.5 and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                    values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                    boosted[i] = True
                values2[i] += 2.6
        if attackable[i].isBase and len(adjacentCells(attackable[i], 'others')) == len(adjacentCells(attackable[i])):
            if takeTime(attackable[i]) > 2.5 and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                boosted[i] = True
            values2[i] += 10
        if attackable[i].isBuilding:
            buildingTime = 30 - (g.currTime - attackable[i].buildTime)
            print "building time:", buildingTime
            if (buildingTime <= takeTime(attackable[i]) and buildingTime > takeTime(attackable[i], True) or takeTime(attackable[i]) > 2.5) and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                boosted[i] = True
            if buildingTime > takeTime(attackable[i], boosted[i]):
                values2[i] += 10
        if not attackable[i].isBase:
            for j in range(len(goldOrEnergyChoice)):
                    if isCloserToDestination(attackable[i], goldOrEnergyChoice[j]):
                        if j == 0: 
                            if takeTime(attackable[i]) > 2.5 and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                                values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                                boosted[i] = True
                            values2[i] += 1.3
                        elif j == 1:
                            values2[i] += 0.75
                        elif j == 2:
                            values2[i] += 0.5
                        elif j == 3:
                            values2[i] += 0.25
            if isAroundMyCell(attackable[i], 'gold'): 
                if takeTime(attackable[i]) > 2.5 and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                    values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)     
                    boosted[i] = True 
                values2[i] += 1.5
            if isAroundMyCell(attackable[i], 'gold', 2):
                values2[i] += 0.6   
            if isAroundMyCell(attackable[i], 'energy'):
                if takeTime(attackable[i]) > 2.5 and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                    values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                    boosted[i] = True 
                values2[i] += 1.5
            if isAroundMyCell(attackable[i], 'energy', 2):
                if takeTime(attackable[i]) > 2.5 and g.energy >= 45 + g.energy*0.05 and not boosted[i]:
                    values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                    boosted[i] = True 
                values2[i] += 0.6
            if isAroundMyCell(attackable[i], 'base'):
                if takeTime(attackable[i]) > 2.5 and g.energy >= 15 * g.baseNum + g.energy*0.05 and not boosted[i]:
                    values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                    boosted[i] = True
                values2[i] += 4 if attackable[i].owner == 0 or attackable[i].owner != 0 and get_user(attackable[i].owner).energy >= 30 else 3
            if isAroundMyCell(attackable[i], 'base', 2):
                if takeTime(attackable[i]) > 2.5 and g.energy >= 15 * g.baseNum + g.energy*0.05 and not boosted[i]:
                    values2[i] += takeTime(attackable[i]) - takeTime(attackable[i], True)
                    boosted[i] = True
                values2[i] += 0.75 if attackable[i].owner == 0 else 0.6  
            if attackable[i].owner == g.users[0].id:
                values2[i] += 1
            if len(g.users) > 1 and g.users[0].id == g.uid and (isOwnedByCompetitors(attackable[i], 50) or attackable[i].owner == g.users[1].id):
                values2[i] += 1   
    values = values1 + values2
    ind = values.index(max(values))
    if ind < len(values1):
        return (multiAttackable[ind], False, True, '')
    return (attackable[ind - len(values1)], boosted[ind - len(values1)], False, '')

def isCloserToDestination(target, dest):  #pathfinding to get around obstacles or more alternatives
    if dest[0] != None:
        dist = distance(dest[0], target)
        if dist < 1*dest[1]:
            for c in adjacentCells(target, 'me'):
                if distance(dest[0], c) > dist:
                    return True
    return False

def isAroundEnemyBase(target, isDiagonal=False):
    if isDiagonal:
        for d in diagonal:
            c = g.GetCell(target.x+d[0], target.y+d[1])
            if c != None and c.owner != g.uid and c.isBase:
                return True
    else:
        for c in adjacentCells(target, 'enemy'):
            if c.isBase:
                return True
    return False

def isAroundMyCell(target, type='all', dist=1):
    if dist == 1:
        for c in adjacentCells(target, 'me'):
            if type == 'all' or type == 'base' and c.isBase or c.cellType == type:
                return True
    if dist == 2:
        for d in circleRadius2:
            c = g.GetCell(target.x+d[0], target.y+d[1])
            if c != None and c.owner == g.uid and (type == 'all' or type == 'base' and c.isBase or c.cellType == type):
                return True
    return False

def isOwnedByCompetitors(target, diff):
    for user in g.users:
        if target.owner == user.id and abs(g.cellNum - user.cellNum) < diff:
            return True

def nearbyGoldOrEnergy(unclaimedGold, unclaimedEnergy, myBoundary):
    unclaimed = unclaimedGold + unclaimedEnergy
    choices = [] 
    if unclaimed:
        unclaimed.sort(key=lambda c: minDistance(c, myBoundary))
        energyGoldRatio = g.energyCellNum/(float(g.goldCellNum) if g.goldCellNum != 0 else 0.01) 
        if abs(energyGoldRatio - desiredRatio) > 0.5:
            insert_ind = 0
            for i in range(len(unclaimed)):
                if unclaimed[i].cellType == ('gold' if energyGoldRatio > desiredRatio else 'energy'):
                    tmp = unclaimed[i]
                    unclaimed.remove(unclaimed[i])
                    unclaimed.insert(insert_ind, tmp)  
                    insert_ind += 1
                if insert_ind == (3 if abs(energyGoldRatio - desiredRatio) > 1.25 else 2):
                    break
        for c in unclaimed:
            choices += [(c, minDistance(c, myBoundary))]
    return choices

def nearbyEnemyBases(enemyBases, myBoundary):
    global targetID
    choices = [] 
    if enemyBases and g.energyCellNum >= 4 and g.goldCellNum >= 2:
        baseTargets = []
        if targetID not in (base.owner for base in enemyBases): 
            targetID = 0
        if targetID == 0:
            groupedBases = []
            avgDist = []
            for user in g.users:
                if user.id != g.uid:
                    userBases = []
                    for base in enemyBases:
                        if base.owner == user.id:
                            userBases += [base]
                    if userBases:
                        groupedBases += [userBases]
                        avgDist += [sum(minDistance(base, myBoundary) for base in userBases)/float(len(userBases))]
            baseTargets = sorted(groupedBases[avgDist.index(min(avgDist))], key=lambda c: minDistance(c, myBoundary) if c.isBuilding else (minDistance(c, myBoundary) + 10))
            targetID = baseTargets[0].owner
        else:
            userBases = []
            for base in enemyBases:
                if base.owner == targetID:
                    userBases += [base]
            baseTargets = sorted(userBases, key=lambda c: minDistance(c, myBoundary) if c.isBuilding else (minDistance(c, myBoundary) + 10))   #change targetID if cant kill
        for c in baseTargets:
            choices += [(c, minDistance(c, myBoundary) - 1)]
    else:
        targetID = 0
    return choices

def adjacentCells(cell, owner='all'):
    adjacent = []
    for d in direction:
        x = cell.x+d[0]
        y = cell.y+d[1]
        c = g.GetCell(x, y)
        if owner == 'none' and c == None:
            adjacent += [(x, y)] 
        if c != None and (owner == 'all' or owner == 'me' and c.owner == g.uid or owner == 'enemy' and c.owner != g.uid and c.owner != 0 or owner == 'self' and c.owner == cell.owner and not (c.isTaking and c.attacker == g.uid) or owner == 'others' and (c.owner != cell.owner or c.isTaking and c.attacker == g.uid)):
            adjacent += [c]                             #consider take time and count enemy's taking cells as his or hers 
    return adjacent

def minDistance(cell, cellList):
    dist = []
    for c in cellList:
        dist += [distance(cell, c)]
    return min(dist)

def distance(c1, c2):
    return abs(c1.x-c2.x) + abs(c1.y-c2.y)

def isColinear(c1, c2):
    c1x = 0
    c1y = 0
    c2x = 0
    c2y = 0
    if isinstance(c1, colorfight.Cell):
        c1x = c1.x
        c1y = c1.y
    else:
        c1x = c1[0]
        c1y = c1[1]
    if isinstance(c2, colorfight.Cell):
        c2x = c2.x
        c2y = c2.y
    else:
        c2x = c2[0]
        c2y = c2[1]
    return c1x - c2x == 0 or c1y - c2y == 0

def isDuplicateAttack(target, last):
    if last[2]:
        if target[2]:
            return target[0] == last[0]
        else:
            return target[0] in adjacentCells(last[0])
    elif target[2]:
        return last[0] in adjacentCells(target[0])
    return target[0] == last[0]

def get_user(ID):
    for user in g.users:
        if user.id == ID:
            return user
    return None

def optimizeDefence(myGold, myEnergy, myBases):
    boost = False
    if g.energy >= 85:
        boost = True
    for base in myBases: 
        if base.isBuilding:
            if isAttackable(base.x, base.y, 'enemy'):       
                if takeTime(base) < 2.5:
                    return (base, boost, False, '')
                else:
                    for c in adjacentCells(base, 'me'):                
                        if takeTime(c) < 2 and isEnemyApproaching(c):
                            return (c, boost, False, '')
            elif not base.isTaking:    
                for c in adjacentCells(base, 'me'):
                    if takeTime(c) < 2 and isEnemyApproaching(c):
                        return (c, boost, False, '')              
        elif len([c for c in adjacentCells(base) if c.owner != g.uid and c.owner != 0 or c.isTaking and c.attacker != g.uid]) >= (2 if len(adjacentCells(base)) == 4 else 1):
            if g.energy >= 30:
                return (base, boost, False, 'square')     
            else:
                for c in adjacentCells(base, 'me'):    
                    if not c.isTaking and takeTime(c) < 2.5:
                        return (c, boost, False, '')
        # elif len(adjacentCells(base, 'me')) <= 2 and max(takeTime(c) for c in adjacentCells(base)) < 2.5 and g.gold >= (3 - g.baseNum) * 60 + 40:
        #     return (base, False, True, '')
    target = [None]*2
    boosted = [boost]*2
    multiAttack = [False]*2
    for gold in myGold:
        if gold.isTaking:
            if gold.attacker != g.uid:
                if max(takeTime(c) for c in adjacentCells(gold)) < 2.5 and g.gold >= (3 - g.baseNum) * 60 + 40:
                    target[0] = gold
                    multiAttack[0] = True   
                elif adjacentCells(gold, 'enemy'):  
                    target[0] = min(adjacentCells(gold, 'enemy'), key=lambda c: takeTime(c))  
                    if takeTime(target[0]) >= 2:
                        if g.energy >= 45 + g.energy*0.05: 
                            boosted[0] = True
                        else:
                            target[0] = None    #not stopping bug
        elif isAttackable(gold.x, gold.y, 'enemy'):       
            if max(takeTime(c) for c in adjacentCells(gold)) < 2.5 and g.gold >= (3 - g.baseNum) * 60 + 40:
                target[0] = gold
                multiAttack[0] = True
            elif takeTime(gold) < 2.5:
                if not (len(adjacentCells(gold, 'enemy')) == 1 and takeTime(adjacentCells(gold, 'enemy')[0]) < 2.5):
                    target[0] = gold
            else:
                for c in adjacentCells(gold, 'me'):
                    if takeTime(c) < 2 and isEnemyApproaching(c):
                        target[0] = c
                        break
        else:    
            for c in adjacentCells(gold, 'me'):
                if takeTime(c) < 2 and isEnemyApproaching(c):
                    target[0] = c
                    break
        if target[0] != None:
            break
    for energy in myEnergy:
        if energy.isTaking:
            if energy.attacker != g.uid:
                if max(takeTime(c) for c in adjacentCells(energy)) < 2.5 and g.gold >= (3 - g.baseNum) * 60 + 40:
                    target[1] = energy
                    multiAttack[1] = True
                elif adjacentCells(energy, 'enemy'):
                    target[1] = min(adjacentCells(energy, 'enemy'), key=lambda c: takeTime(c))
                    if takeTime(target[1]) >= 2:
                        if g.energy >= 45 + g.energy*0.05: 
                            boosted[1] = True
                        else:
                            target[1] = None
        elif isAttackable(energy.x, energy.y, 'enemy'):
            if max(takeTime(c) for c in adjacentCells(energy)) < 2.5 and g.gold >= (3 - g.baseNum) * 60 + 40:
                target[1] = energy
                multiAttack[1] = True
            elif takeTime(energy) < 2.5:
                if not (len(adjacentCells(energy, 'enemy')) == 1 and takeTime(adjacentCells(energy, 'enemy')[0]) < 2.5):
                    target[1] = energy
            else:
                for c in adjacentCells(energy, 'me'):
                    if takeTime(c) < 2 and isEnemyApproaching(c):
                        target[0] = c
                        break
        else:
            for c in adjacentCells(energy, 'me'):
                if takeTime(c) < 2 and isEnemyApproaching(c):
                    target[1] = c;
                    break
        if target[1] != None:
            break
    if target[0] != None and target[1] != None:
        if g.energyCellNum/(float(g.goldCellNum) if g.goldCellNum != 0 else 0.01) > desiredRatio:
            return (target[0], boosted[0], multiAttack[0], '')
        else:
            return (target[1], boosted[1], multiAttack[1], '')
    elif target[0] != None:
        return (target[0], boosted[0], multiAttack[0], '')
    elif target[1] != None:
        return (target[1], boosted[1], multiAttack[1], '')
    return (None, False, False, '')

if __name__ == '__main__':
    if g.JoinGame('YourAI'):
        g.Refresh()
        last = (None, False, False, '')
        while True:
            target = (None, False, False, '')
            unclaimedGold = []
            unclaimedEnergy = []
            attackable = []
            multiAttackable = []
            myCells = []
            myBoundary = []
            enemyBoundary = []
            myBases = []
            enemyBases = []
            myGold = []
            myEnergy = []
            for x in range(g.width):
                for y in range(g.height):
                    c = g.GetCell(x, y)
                    if c.owner == g.uid:
                        myCells += [c]
                    if c.isBase or c.isBuilding:
                        if c.owner == g.uid:
                            myBases += [c]
                        else:
                            enemyBases += [c]
                    if c.cellType == 'gold': 
                        if c.owner == g.uid: 
                            myGold += [c]
                        else:
                            unclaimedGold += [c]
                    if c.cellType == 'energy':
                        if c.owner == g.uid: 
                            myEnergy += [c]
                        else:
                            unclaimedEnergy += [c]
                    if isOnBoundary(x, y):
                        myBoundary += [c]
                    if isOnBoundary(x, y, 'enemy'):
                        enemyBoundary += [c]
                    if isMultiAttackable(x, y):
                        multiAttackable += [c]
                    if isAttackable(x, y): 
                        attackable += [c]
            if myCells and enemyBoundary and g.baseNum < 3 and g.gold >= 60:
                myCells.sort(key=lambda c: minDistance(c, enemyBoundary), reverse=True)  
                i = 0
                while minDistance(myCells[i], myBases) < 3 or myCells[i].isBuilding: i += 1
                print "BuildBase:", g.BuildBase(myCells[i].x, myCells[i].y)
            if myGold or myEnergy or myBases:
                target = optimizeDefence(myGold, myEnergy, myBases)
            if attackable and target[0] == None: 
                target = optimizeAttack(attackable, multiAttackable, nearbyGoldOrEnergy(unclaimedGold, unclaimedEnergy, myBoundary), nearbyEnemyBases(enemyBases, myBoundary))
            flag = (False, 3, None)
            action = ""
            while(target[0] != None and not isDuplicateAttack(target, last) and flag[1] == 3):
                if target[2]:
                    flag = g.MultiAttack(target[0].x, target[0].y)
                    action = "MultiAttack:"
                elif len(target[3]) > 0:
                    flag = g.Blast(target[0].x, target[0].y, target[3])
                    action = "Blast:"
                else:
                    flag = g.AttackCell(target[0].x, target[0].y, target[1])
                    action = "Boosted Attack:" if target[1] else "Attack:"
                print action, flag
            if get_user(targetID) != None and targetID != 0:
                print "Target:", get_user(targetID).name
            #print action, flag
            if flag[0]: last = target
            g.Refresh()
    else:
        print("Failed to join the game!")
