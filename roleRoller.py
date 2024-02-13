from random import randint, shuffle 


class Player:
  def __init__(self, role = 'warrior', lives = 1, usedAbility = False, cooldown = 2, fakeRole = None):
    self.role = role
    self.lives = lives
    self.usedAbility = usedAbility
    self.cooldown = cooldown
    self.fakeRole = fakeRole

  def get_role(self):
    return self.role
  def get_lives(self):
    return self.lives
  def get_usedAbility(self):
    return self.usedAbility
  def get_cooldown(self):
    return self.cooldown
  def get_fakeRole(self):
    return self.fakeRole
    
  def set_role(self, x):
    self.role = x
  def set_lives(self, x):
    self.lives = x
  def set_usedAbility(self, x):
    self.usedAbility = x
  def set_cooldown(self, x):
    self.cooldown = x
  def set_fakeRole(self, x):
    self.fakeRole = x


def rolesAmount(playerAmount:int):
  redAmount = playerAmount // 3
  greenAmount = playerAmount - redAmount
  mageAmount = greenAmount // 7
  if mageAmount < 1:
    mageAmount = 1
  warriorAmount = greenAmount * 3 // 5
  necroArcherPool = greenAmount // 5
  randomGreen = greenAmount - mageAmount - warriorAmount - necroArcherPool
  necroLimit = playerAmount//3
  bersLimit = playerAmount//9

  return redAmount, greenAmount, mageAmount, warriorAmount, necroArcherPool, randomGreen, necroLimit, bersLimit


def roleGenerator(playerAmount:int):
  listOfRoles = []
  redAmount, greenAmount, mageAmount, warriorAmount, necroArcherPool, randomGreen, necroLimit, bersLimit = rolesAmount(playerAmount)

  random = randint(1,3)
  if random < 3:
    listOfRoles.append('warlock')
  else: 
    listOfRoles.append('vampire')
  for i in range(redAmount-1):
    random = randint(1,3)
    if playerAmount == 6:
      listOfRoles.append('dead')
    else:
      if random == 1:
        listOfRoles.append('dead')
      else:
        listOfRoles.append('werewolf')
  for i in range(mageAmount):
    listOfRoles.append('mage')
  for i in range(warriorAmount):
    if listOfRoles.count('berserk') < bersLimit:
      random = randint(1,3)
      if random != 1:
        listOfRoles.append('berserk')
      else:
        listOfRoles.append('warrior')
    else:
      listOfRoles.append('warrior')
  for i in range(necroArcherPool):
    if listOfRoles.count('necromancer') >= necroLimit:
      listOfRoles.append('ranger')
    else:
      random = randint(1, 2)
      if random == 1:
        listOfRoles.append('necromancer')
      else:
        listOfRoles.append('ranger')
  for i in range(randomGreen):
    highNumber = 6
    lowNumber = 4
    if listOfRoles.count('necromancer') >= necroLimit:
      highNumber -= 1
    if playerAmount >= 8:
      lowNumber -= 2
    if playerAmount >= 9:
      lowNumber -= 1
    random = randint(lowNumber, highNumber)
    if random == 6:
      listOfRoles.append('necromancer')
    elif random > 3:
      listOfRoles.append('ranger')
    elif random > 1:
      listOfRoles.append('hunter')
    else:
      listOfRoles.append('warrior')
    
  
  return listOfRoles

def playerCreator(listOfPlayers:list):
    loc = {}
    for player in listOfPlayers:
        loc[str(player.id)] = Player()
    return loc


def roleAssigner(listOfPlayers:list, dictOfPlayers:dict):
  listOfRoles = roleGenerator(len(listOfPlayers))
  
  shuffle(listOfRoles)
  shuffle(listOfPlayers)
  
  i = 0
  for player in listOfPlayers:
    role = listOfRoles[i]
    instance = dictOfPlayers[str(player.id)]
    
    if role == 'warrior': 
      instance.set_lives(2)
    elif role == 'berserk':
      instance.set_lives(2)
      instance.set_role(role)
      instance.set_usedAbility(True)
    else:
      instance.set_role(role)

    i += 1