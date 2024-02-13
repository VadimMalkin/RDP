import os
import discord
import responses
import roleRoller
import game
from db import db
from random import randint, shuffle
from discord.ui import View, Button
from asyncio import sleep
from dotenv import load_dotenv

precius = game.Game()

class MyView(View):
  async def disable_all_items(self):
    for item in self.children:
      item.disabled = True
    await self.message.edit(view=self)
    self.stop()

  async def disable_item(self, custom_id):
      for item in self.children:
        if item.custom_id == custom_id:
          item.disabled = True
      await self.message.edit(view=self)

  async def on_timeout(self) -> None:
    await self.disable_all_items()
    await self.message.edit(view=self)

    buttonChoosed:str = None 
  

class CheifPick(MyView): 
  def __init__(self, cheif):
    super().__init__()
    self.chief = cheif
    

  async def interaction_check(self, interaction) -> bool:
    if interaction.user != self.cheif:
      await interaction.response.send_message(db["fcheifPick"], ephemeral=True)
      return False
    else:
      return True
  
  @discord.ui.button(label="Вампир", style=discord.ButtonStyle.primary)
  async def vampire(self, interaction: discord.Interaction, button: Button):
    self.buttonChoosed = 'vampire'
    await self.disable_all_items()
    
    
  @discord.ui.button(label="Чернокнижник", style=discord.ButtonStyle.primary)
  async def warlock(self, interaction: discord.Interaction, button: Button):
    self.buttonChoosed = 'warlock'
    await self.disable_all_items()

class UseAbility(MyView):

  @discord.ui.button(label='Использовать', style=discord.ButtonStyle.primary)
  async def useButton(self, interaction: discord.Interaction, button: Button):
    await interaction.response.send_message(db["UseAbilityUsed"]) 
    self.buttonChoosed = 'buttonUsed'
    await self.disable_all_items()
    
  @discord.ui.button(label='Не использавать', style=discord.ButtonStyle.danger)
  async def cancelButton(self, interaction: discord.Interaction, button: Button):
    await interaction.response.send_message(db["UseAbilityNoUsed"]) 
    self.buttonChoosed = None
    await self.disable_all_items()

class ChooseAbilityWarlock(MyView):
  
  @discord.ui.button(label='Покушение', style=discord.ButtonStyle.primary)
  async def useButton(self, interaction: discord.Interaction, button: Button):
    await interaction.response.send_message(db["warlockChooseStrike"]) 
    self.buttonChoosed = 'strike'
    await self.disable_all_items()
    
  @discord.ui.button(label='Просмотр роли', style=discord.ButtonStyle.primary)
  async def cancelButton(self, interaction: discord.Interaction, button: Button):
    await interaction.response.send_message(db["warlockChooseView"]) 
    self.buttonChoosed = 'viewRole'
    await self.disable_all_items()


class ChooseAbilityVampire(MyView):

  @discord.ui.button(label='Покушение', style=discord.ButtonStyle.primary)
  async def useButton(self, interaction: discord.Interaction, button: Button):
    await interaction.response.send_message(db["warlockChooseStrike"]) 
    self.buttonChoosed = 'strike'
    await self.disable_all_items()
    
  @discord.ui.button(label='Подделка ролей', style=discord.ButtonStyle.primary)
  async def cancelButton(self, interaction: discord.Interaction, button: Button):
    await interaction.response.send_message(db["vampireChooseFake"]) 
    self.buttonChoosed = 'fakeRole'
    await self.disable_all_items()

class JoinLeave(MyView):
  def __init__(self, timeout, joinList, muteRoleID):
    super().__init__(timeout = timeout)
    self.joinList = joinList
    self.muteRoleID = muteRoleID
    self.quickStartList = list()
    
  @discord.ui.button(label='Играть', style=discord.ButtonStyle.primary, custom_id='j')
  async def joinButton(self, interaction: discord.Interaction, button: Button):
    joinList = self.joinList
    muteRoleID = self.muteRoleID
    user = interaction.user
    quickStartList = self.quickStartList
    if user not in joinList and user.get_role(muteRoleID) == None:
      stateC = precius.get_state()
      if len(joinList) == 25 and stateC == 'joining':
        joinList.append(user)
        await interaction.response.send_message(f"{user.display_name} "+db["joinLimit"])
        await self.disable_all_items()
        precius.set_state('quickStart')
      else:
        joinList.append(user)
        await interaction.response.send_message(f"{user.display_name} "+db["join"]+f' {len(joinList)}')
        if len(joinList) >= 5 and len(quickStartList) >= len(joinList)*2//3 and stateC == 'joining':
          await self.disable_item('l')
          precius.set_state('quickStart')
    else:
      await interaction.response.send_message(db["fjoin"], ephemeral = True)

  @discord.ui.button(label='Выйти из игры', style=discord.ButtonStyle.danger, custom_id='l')
  async def leaveButton(self, interaction: discord.Interaction, button: Button):
    joinList = self.joinList
    muteRoleID = self.muteRoleID
    user = interaction.user
    quickStartList = self.quickStartList
    if user in joinList and user.get_role(muteRoleID) == None:
      joinList.remove(user)
      if user.id in quickStartList:
        quickStartList.remove(user.id)
      await interaction.response.send_message(f"{user.display_name} "+db["leave"]+f' {len(joinList)}')
    else: 
      await interaction.response.send_message(db["fleave"], ephemeral = True)

  @discord.ui.button(label='Не ждать', style=discord.ButtonStyle.success, custom_id='f')
  async def quickButton(self, interaction: discord.Interaction, button: Button):
    joinList = self.joinList
    user = interaction.user
    quickStartList = self.quickStartList
    stateC = precius.get_state()
    if user not in joinList:
      await interaction.response.send_message(db["fleave"], ephemeral = True)
    elif user.id in quickStartList:
      await interaction.response.send_message(db["fqstart"], ephemeral = True)
    else:
      quickStartList.append(user.id)
      await interaction.response.send_message(db["qstart"], ephemeral = True)
      if len(joinList) >= 5 and len(quickStartList) >= len(joinList)*2//3 and stateC == 'joining':
        await self.disable_item('l')
        precius.set_state('quickStart')


class StopView(MyView):
  def __init__(self, timeout, liveList, stopList, amountToStop):
    super().__init__(timeout = timeout)
    self.liveList = liveList
    self.stopList = stopList
    self.amountToStop = amountToStop
    
  @discord.ui.button(label='Stop', style=discord.ButtonStyle.danger)
  async def stopButton(self, interaction: discord.Interaction, button: Button):
    liveList = self.liveList
    user = interaction.user
    if user.id in liveList:
      stopList = self.stopList
      if user.id not in stopList:
        await interaction.response.send_message(f"{user.display_name} "+db["stops"])
        stopList.append(user.id)
        if len(stopList) == self.amountToStop:
          await self.disable_all_items()
      else:
        await interaction.response.send_message(db["fstops"], ephemeral = True)
    else:
      await interaction.response.send_message(db["flstops"], ephemeral = True)
        

class VoteView(MyView):
  def __init__(self, timeout, voted, votes, liveListLen):
    super().__init__(timeout = timeout)
    self.voted = voted
    self.votes = votes
    self.liveListLen = liveListLen


class MercyView(VoteView):
  @discord.ui.button(label='Убить', style=discord.ButtonStyle.primary)
  async def killBack(self, interaction: discord.Interaction, button: Button):
    state = precius.get_state()
    if state == 'stopping':
      self.disable_all_items()
    livePlayersIDs = getIDs(getLive())
    if interaction.user.id in livePlayersIDs:
      if interaction.user.id not in self.voted:
        self.voted.append(interaction.user.id)
        self.votes.append(1)
        await interaction.response.send_message(f'{interaction.user.display_name} '+db["vote"]+' Убить')
      else:
        await interaction.response.send_message(db["fvote"], ephemeral = True)
      if len(self.voted) == self.liveListLen:
        await self.disable_all_items()
    else:
      await interaction.response.send_message(db["dvote"], ephemeral = True)

  @discord.ui.button(label='Пощадить', style=discord.ButtonStyle.primary)
  async def mercyBack(self, interaction: discord.Interaction, button: Button):
    state = precius.get_state()
    if state == 'stopping':
      self.disable_all_items()
    livePlayersIDs = getIDs(getLive())
    if interaction.user.id in livePlayersIDs:
      if interaction.user.id not in self.voted:
        self.voted.append(interaction.user.id)
        self.votes.append(2)
        await interaction.response.send_message(f'{interaction.user.display_name} '+db["vote"]+' Пощадить')
      else:
        await interaction.response.send_message(db["fvote"], ephemeral = True)
      if len(self.voted) == self.liveListLen:
        await self.disable_all_items()
    else:
      await interaction.response.send_message(db["dvote"], ephemeral = True)
      

class TestView(MyView):
  @discord.ui.button(label='he', style=discord.ButtonStyle.primary, custom_id='t')
  async def testButton(self, interaction: discord.Interaction, button: Button):
    await self.disable_item('t')
    await interaction.response.send_message("hehe", ephemeral = True)


class VoteButton(Button):  
  async def callback(self,interaction):
    state = precius.get_state()
    if state == 'stopping':
      self.view.disable_all_items()
    livePlayersIDs = getIDs(getLive())
    if interaction.user.id in livePlayersIDs:
      if interaction.user.id not in self.view.voted:
        self.view.voted.append(interaction.user.id)
        self.view.votes.append(self.custom_id)
        await interaction.response.send_message(f'{interaction.user.display_name} '+db["vote"]+f' {self.label}')
      else:
        await interaction.response.send_message(db["fvote"], ephemeral = True)
      if len(self.view.voted) == self.view.liveListLen:
        await self.view.disable_all_items()
    else:
      await interaction.response.send_message(db["dvote"], ephemeral = True)
      

class AbilityButton(Button):
  async def callback(self,interaction):
      self.view.buttonChoosed = self.custom_id
      await interaction.response.send_message('ок', ephemeral = True)
      await self.view.disable_all_items()


def wait_seconds(x):
  sleep(x)


def saveGame(precius):
  playersL = precius.get_playersL()
  deadPlayers = precius.get_deadList()
  playerDict = precius.get_playersD()
  actionDict = precius.get_actionDict()
  electionDict = precius.get_electionDict()
  state = precius.get_state()
  guildID = precius.get_guildID()
  gameOn = precius.get_gameOn()
  playerDictIDs = list(playerDict.keys())
  playerClasses = list(playerDict.values())
  actionUsers = list(actionDict.keys())
  actionTargets = list(actionDict.values())
  
  
  db_playersL = []
  db_deadPlayers = []
  db_playerData = []
  db_actions = []

  for user in playersL:
    db_playersL.append(user.id)
  for user in deadPlayers:
    db_deadPlayers.append(user.id)
  for i in range(len(playerDictIDs)):
    db_playerData.append([playerDictIDs[i], playerClasses[i].get_role(), playerClasses[i].get_lives(), playerClasses[i].get_usedAbility(), playerClasses[i].get_cooldown()])
  for i in range(len(actionUsers)):
    db_actions.append([actionUsers[i], actionTargets[i]])
  

  db['GO_'+guildID] = gameOn
  db['PL_'+guildID] = db_playersL
  db['PDL_'+guildID] = db_deadPlayers
  db['PD_'+guildID] = db_playerData
  db['S_'+guildID] = state
  db['ED_'+guildID] = electionDict
  db['AD_'+guildID] = actionDict


def continueGame(precius, client, guildID):
  playersL = []
  deadPlayers = []
  playerDict = {}
  actionDict = {}

  for id in db['PL_'+guildID]:
    playersL.append(client.get_guild(int(guildID)).get_member(id))
  for id in db['PDL_'+guildID]:
    deadPlayers.append(client.get_guild(int(guildID)).get_member(id))
  for playerData in db['PD_'+guildID]:
    playerDict[playerData[0]] = roleRoller.Player(role=playerData[1], lives=playerData[2], usedAbility=playerData[3], cooldown=playerData[4])
  for action in db['AD_'+guildID]:
    if len(action) == 2:
      actionDict[action[0]] = action[1]

  precius.set_gameOn(True)
  precius.set_playersL(playersL)
  precius.set_deadList(deadPlayers)
  precius.set_playersD(playerDict)
  precius.set_actionDict(actionDict)
  precius.set_state(db['S_'+guildID])
  precius.set_electionDict(db['ED_'+guildID])
  precius.set_guildID(guildID)


def clearGame(guildID):
  del db['GO_'+guildID]
  del db['PL_'+guildID]
  del db['PDL_'+guildID]
  del db['PD_'+guildID]
  del db['S_'+guildID]
  del db['ED_'+guildID]
  del db['AD_'+guildID]
    

def getValuesFromDB(key):
  dbIDs = db[key]
  listOfIDs = dbIDs.split()
  return listOfIDs
      

def getUsersFromIDs(client, listOfIDs):
  listOfUsers = []

  for id in listOfIDs:
    listOfUsers.append(client.get_user(int(id)))
  
  return listOfUsers


def getbullies(client):
  listOfIDs = getValuesFromDB('cyberbullies')
  listOfUsers = getUsersFromIDs(client, listOfIDs)
  return listOfUsers


def getbullied(client):
  listOfIDs = getValuesFromDB('cyberbullied')
  listOfUsers = getUsersFromIDs(client, listOfIDs)
  return listOfUsers

def getghostpingprankersIDs():
  listOfIDs = getValuesFromDB('ghostpingprankers')
  return listOfIDs


def unique(list:list):
  uniqueList = []
  for x in list:
    if x not in uniqueList:
      uniqueList.append(x)
      
  return uniqueList

def strList(list:list):
  listStr = []  
  for x in list:
    x = str(x)
    listStr.append(x)
  return listStr

def findIDEnd(messageString):
  for i in range(len(messageString)):
    if messageString[i] == '>':
      return i
      
def findIDStart(messageString):
  for i in range(len(messageString)):
    if messageString[i] == '@':
      return i+1

def getElected(client) -> list:
  elecDict = precius.get_electionDict()
  electedIDs = elecDict.values()
  electedIDs = unique(electedIDs)
  electedPlayers = []
  for id in electedIDs:
    player = client.get_guild(int(precius.get_guildID())).get_member(id)
    electedPlayers.append(player)
  
  return electedPlayers

def getLive():
  playerList = precius.get_playersL()
  deadList = precius.get_deadList()
  liveList = [x for x in playerList if x not in deadList]
  return liveList

def getGreen():
  liveList = getLive()
  playersD = precius.get_playersD()
  redRoles = ['vampire','dead','warlock','werewolf']
  greenList = []
  for player in liveList:
    role = playersD[str(player.id)].get_role()
    if role not in redRoles:
      greenList.append(player)
  return greenList
  
def getRed():
  liveList = getLive()
  playersD = precius.get_playersD()
  redRoles = ['vampire','dead','warlock','werewolf']
  redList = []
  for player in liveList:
    role = playersD[str(player.id)].get_role()
    if role in redRoles:
      redList.append(player)
  return redList

def getIDs(listOfUsers):
  listOfIDs = []
  for user in listOfUsers:
    listOfIDs.append(user.id)
  return listOfIDs

def getAbilityUsers():
  liveList = getLive()
  playersD = precius.get_playersD()
  abilDict = {}
  for player in liveList:
    user = playersD[str(player.id)]
    role = user.get_role()
    if role != 'warrior':
      lives = user.get_lives()
      if lives > 0:
        onCooldown = user.get_usedAbility()
        if onCooldown == False:
          playerID = player.id
          abilDict[playerID] = role
  return abilDict

def roleTranslator(role):
  engRoles = ['warrior','ranger','mage','necromancer','werewolf','warlock','dead','vampire','hunter', 'berserk']
  ruRoles = ['воин','лучник','маг','некромант','оборотень','чернокнижник','мертвец','вампир','охотник','берсерк']
  
  for i in range(len(engRoles)):
    if role == engRoles[i]:
      return ruRoles[i]

  
async def switch_state(x, state, gameChat):
  if x//60 > 0:
    seconds = x%60
    for i in range(x//60-1, 0, -1):
      await sleep(60)
      stateC = precius.get_state()
      if stateC == 'stopping' or stateC == 'joining':
        return
      await gameChat.send(f'{i} '+db["minutesLeft"])
    await sleep(60+seconds)
  else:
    await sleep(x)
  stateC = precius.get_state()
  if stateC != 'stopping' and stateC != 'joining' : 
    precius.set_state(state)

async def first_switch_state(x, state, joinChat, joinTime, view):
  if x//60 > 0:
    seconds = x%60
    for i in range(x//60-1, 0, -1): #with x=600 starts at 9 and goes to 0
      stateC = precius.get_state()
      if stateC == 'stopping':
        return
      elif stateC == 'quickStart':
        precius.set_state(state)
        await joinChat.send(db["quickStart"])
        return
      await sleep(60)
      stateC = precius.get_state()
      if stateC == 'stopping':
        return
      elif stateC == 'quickStart':
        precius.set_state(state)
        await joinChat.send(db["quickStart"])
        return
      await view.message.delete()
      oMessage = await joinChat.send(db["start1"]+f' {i} '+db["start2"],view=view)
      view.message = oMessage
    await sleep(60+seconds)
  else:
    await sleep(x)
  stateC = precius.get_state()
  if stateC != 'stopping': 
    precius.set_state(state)


async def redRolePicker(redList:list, playerDict:dict, evilChat):
  cheifRed = redList[0]
  view = CheifPick(timeout=120, cheif=cheifRed)
  
  oMessage = await evilChat.send(db["cheifPick"], view=view) 
  view.message = oMessage
  
  await view.wait()
  await view.disable_all_items()
  cheifRole = view.buttonChoosed
  if cheifRole is None:
    num = randint(1,2)
    if num == 1:
      cheifRole = 'warlock'
    else:
      cheifRole = 'vampire'
    await evilChat.send(db["chiefPickTimeOut"]+f' {cheifRole}')
  else:    
    await evilChat.send(db["cheifPick"]+f' {cheifRole}!')
  
  if cheifRole == 'warlock':
    redRole = 'werewolf'
  else:
    redRole = 'dead'

  playerDict[str(cheifRole.id)].set_role(cheifRole) 
  for red in redList[1:]:
    playerDict[str(red.id)].set_role(redRole)

  for red in redList:
    role = playerDict[str(red.id)].get_role()
    file = discord.File(fp=f'/imgs_ru/{role}.png')
    await red.send(db["yourRole"], file=file)

  return
  
  
async def roleInformer(playerList:list, playerDict:dict):
  for player in playerList:
    role = playerDict[str(player.id)].get_role()
    file = discord.File(fp=f'imgs_ru/{role}.png')
    await player.send(db["yourRole"] + db[f"{role}"], file=file)


async def monkey():
  haha = []
  await voter(haha,haha,haha,haha)


async def voter(electedList, gameChat, client, playerDict, revoteTime):
  voted = []
  votes = []
  names = []
  globalName = False
  liveListLen = len(getLive())
  view = VoteView(votes=votes, timeout=60, voted=voted, liveListLen=liveListLen)
  for elec in electedList:
    names.append(elec.display_name)
    if names.count(elec.display_name) > 1:
      globalName = True
      break
  for elec in electedList:
    if globalName == True:
      label = elec.name
    else:
      label = elec.display_name
    elec = VoteButton(label=label, style=discord.ButtonStyle.primary, custom_id=str(elec.id))
    view.add_item(elec)
        
  oMessage = await gameChat.send(db["voter"],view=view)
  view.message = oMessage
      
  await view.wait()
  
  uniqueVotes = unique(view.votes)
  biggestCount = 0
  elecWinnerList = []
  for vote in uniqueVotes:
    count = view.votes.count(vote)
    if biggestCount < count:
      biggestCount = count
      elecWinnerList = []
      elecWinnerList.append(vote)
    elif biggestCount == count:
      elecWinnerList.append(vote)
  if len(elecWinnerList) == 1:
    playerToDieID = int(elecWinnerList[0])
    playerToDie = client.get_guild(int(precius.get_guildID())).get_member(playerToDieID)
    playerToDieName = playerToDie.display_name
    await gameChat.send(f"{playerToDieName} " + db["voterDeath"])
    player = playerDict[elecWinnerList[0]]
    player.set_lives(0)
    deadList = precius.get_deadList()
    deadList.append(playerToDie)
    precius.set_deadList(deadList)
  else:
    await gameChat.send(db["revotes1"]+f' {revoteTime//60} '+db["revotes2"])
    await switch_state(1, 'dayRV',gameChat)
    await switch_state(revoteTime, 'voting', gameChat)
    elecWinnerListU = []
    for id in elecWinnerList:
      elecWinnerListU.append(client.get_guild(int(precius.get_guildID())).get_member(int(id)))
    await voter(elecWinnerListU, gameChat, client, playerDict, revoteTime)

async def mercer(electedList, gameChat, client, playerDict, playerID):
  voted = []
  votes = []
  playerToDie = client.get_guild(int(precius.get_guildID())).get_member(playerID)
  liveListLen = len(getLive())
  view = MercyView(timeout=60, votes=votes, voted=voted, liveListLen=liveListLen)
  oMessage = await gameChat.send(f'{playerToDie.display_name} '+db["mercy"],view=view)
  view.message = oMessage
  
  await view.wait()
  
  uniqueVotes = unique(view.votes)
  biggestCount = 0
  elecWinnerList = []
  for vote in uniqueVotes:
    count = view.votes.count(vote)
    if biggestCount < count:
      biggestCount = count
      elecWinnerList = []
      elecWinnerList.append(vote)
    elif biggestCount == count:
      elecWinnerList.append(vote)
  if len(elecWinnerList) == 1:
    if elecWinnerList[0] == 1:
      await gameChat.send(f"{playerToDie.display_name} " + db["voterDeath"])
      player = playerDict[str(playerID)]
      player.set_lives(0)
      deadList = precius.get_deadList()
      deadList.append(playerToDie)
      precius.set_deadList(deadList)
    else:
      await gameChat.send(f"{playerToDie.display_name} " + db["voterMercy"])
  else:
    await gameChat.send(f"{playerToDie.display_name} " + db["voterDeath"])
    player = playerDict[str(playerID)]
    player.set_lives(0)
    deadList = precius.get_deadList()
    deadList.append(playerToDie)
    precius.set_deadList(deadList)
  

    
async def roleViewer(listOfTargets:list, playersDict, necro:bool, client, user):
  view = MyView(timeout=120)
  for target in listOfTargets:
    target = AbilityButton(label=target.display_name, style=discord.ButtonStyle.primary, custom_id=str(target.id))
    view.add_item(target)

  oMessage = await user.send(db["roleViewer"],view=view)
  view.message = oMessage
  
  await view.wait()
  await view.disable_all_items()
  targetID = view.buttonChoosed
  if targetID != None:
    await user.send(db["viewroleSuc1"]+f' {client.get_guild(int(precius.get_guildID())).get_member(int(targetID)).display_name} '+db["viewroleSuc2"])
    userID = str(user.id)
    actionDict = precius.get_actionDict()
    actionDict['v'+userID] = targetID 
    precius.set_actionDict(actionDict)



async def striker(listOfTargets:list, client, user):
  view = MyView(timeout=120)
  for target in listOfTargets:
    target = AbilityButton(label=target.display_name, style=discord.ButtonStyle.primary, custom_id=str(target.id))
    view.add_item(target)

  oMessage = await user.send(db["striker"],view=view)
  view.message = oMessage
  
  await view.wait()
  await view.disable_all_items()
  targetID = view.buttonChoosed
  if targetID != None:
    await user.send(db["strikerSuc"]+' '+client.get_guild(int(precius.get_guildID())).get_member(int(targetID)).display_name)
    userID = str(user.id)
    actionDict = precius.get_actionDict()
    actionDict['s'+userID] = targetID
    precius.set_actionDict(actionDict)
    

  return


async def stalker(listOfTargets:list, playersDict, client, user):
  view = MyView(timeout=120)
  for target in listOfTargets:
    target = AbilityButton(label=target.display_name, style=discord.ButtonStyle.primary, custom_id=str(target.id))
    view.add_item(target)

  oMessage = await user.send(db["stalker"],view=view) #change to "stalker"
  view.message = oMessage
  await view.wait()
  await view.disable_all_items()
  targetID = view.buttonChoosed
  if targetID != None:
    await user.send(db["stalkerSuc1"]+f' {client.get_guild(int(precius.get_guildID())).get_member(int(targetID)).display_name} '+db["stalkerSuc2"])
    userID = str(user.id)
    actionDict = precius.get_actionDict()
    actionDict['t'+userID] = targetID
    precius.set_actionDict(actionDict)
  


async def abilityUser(user, playersDict):
  view = UseAbility(timeout=120)

  oMessage = await user.send(db["UseAbility"],view=view)
  view.message = oMessage
  
  await view.wait()
  await view.disable_all_items()
  used = view.buttonChoosed
  state = precius.get_state()
  if used != None and state == 'night':
    player = playersDict[str(user.id)]
    player.set_usedAbility(True)
  

  return


async def warlockChoose(listOfTargets, playersDict, client, user):
  view = ChooseAbilityWarlock(timeout=120)
  
  oMessage = await user.send(db["warlockChoose"], view=view)
  view.message = oMessage
  
  await view.wait()
  await view.disable_all_items()
  choose = view.buttonChoosed
  if choose == 'strike':
    await striker(listOfTargets, client, user)
  elif choose == 'viewRole':
    await roleViewer(listOfTargets, playersDict, False, client, user)
  else:
    await user.send(db["fwarlockChoose"])

  return


async def vampireChoose(listOfTargets, playersDict, client, user):
  view = ChooseAbilityVampire(timeout=120)
  #change to vampire
  oMessage = await user.send(db["warlockChoose"], view=view)
  view.message = oMessage
  
  await view.wait()
  await view.disable_all_items()
  choose = view.buttonChoosed
  if choose == 'strike':
    await striker(listOfTargets, client, user)
  elif choose == 'fakeRole':
    await roleChanger(listOfTargets, playersDict, client, user)
  else:
    await user.send(db["fwarlockChoose"])

  return


async def roleChanger(listOfTargets:list, playersDict, client, user):
  roleList = ['warrior','ranger','mage','necromancer','hunter','berserk','werewolf','warlock','dead','vampire']
  for i in range (1,2):
    targetView = MyView(timeout=120)
    fakeRoleView = MyView(timeout=120)
    
    
    for role in roleList[:6]:
      role = AbilityButton(label=roleTranslator(role), style=discord.ButtonStyle.primary, custom_id=role)
      fakeRoleView.add_item(role)
    for role in roleList[6:]:
      role = AbilityButton(label=roleTranslator(role), style=discord.ButtonStyle.danger, custom_id=role)
      fakeRoleView.add_item(role)
    for target in listOfTargets:
      target = AbilityButton(label=target.display_name, style=discord.ButtonStyle.primary, custom_id=str(target.id))
      targetView.add_item(target)
  
    oMessage = await user.send(db[f"roleChanger{i}"],view=targetView)
    targetView.message = oMessage
    
    await targetView.wait()
    await targetView.disable_all_items()
  
    oMessage = await user.send(db[f"roleChanger{i}fr"],view=fakeRoleView)
    fakeRoleView.message = oMessage
    
    await fakeRoleView.wait()
    await fakeRoleView.disable_all_items()
  
    targetID = targetView.buttonChoosed
    fakeRole = fakeRoleView.buttonChoosed
    if targetID != None and fakeRole != None:
      target = client.get_guild(int(precius.get_guildID())).get_member(int(targetID))
      name = target.display_name
      target = playersDict[targetID]
      target.set_fakeRole(fakeRole)
      precius.set_playersD(playersDict)
      fakeRole = roleTranslator(fakeRole)
      await user.send(f"Ты подменил роль {name} на {fakeRole}")

  return


def actionProcessor(playersDict, actionDict, client):
  strikeDict = {}
  viewDict = {}
  stalkerDict = {}
  users = list(actionDict.keys())
  targets = list(actionDict.values())
  i = 0
  
  for user in users:
    if user[0] == 's':
      strikeDict[user[1:]] = targets[i]
    elif user[0] == 'v':
      viewDict[user[1:]] = targets[i]
    elif user[0] == 't':
      stalkerDict[user[1:]] = targets[i]
    i+=1

  return strikeDict, viewDict, stalkerDict

async def viewerProcessor(playersDict, viewDict, client):
  viewers = list(viewDict.keys())
  targets = viewDict.values()
  i = 0
  
  for targetID in targets:
    userViewer = client.get_user(int(viewers[i]))
    necro = 'necromancer' == playersDict[viewers[i]].get_role()
    targetUser = client.get_guild(int(precius.get_guildID())).get_member(int(targetID))
    name = targetUser.display_name
    target = playersDict[targetID]
    role = target.get_role()
    if necro == False:
      fakeRole = target.get_fakeRole()
      if fakeRole != None:
        role = fakeRole
    role = roleTranslator(role)
    await userViewer.send(f"Ролью {name} является {role}")
    i += 1


async def stalkeProcessor(playersDict, stalkerDict, client):
  stalkers = list(stalkerDict.keys())
  targets = stalkerDict.values()
  i = 0
  walkingRoles = ['mage', 'hunter', 'necromancer', 'berserk', 'vampire', 'warlock', 'werewolf']
  
  for targetID in targets:
    userStalker = client.get_guild(int(precius.get_guildID())).get_member(int(stalkers[i]))
    targetUser = client.get_guild(int(precius.get_guildID())).get_member(int(targetID))
    name = targetUser.display_name
    target = playersDict[targetID]
    targetRole = target.get_role()
    walker = False
    
    if targetRole in walkingRoles:
      usedAbility = target.get_usedAbility()
      cooldown = target.get_cooldown()
      if usedAbility == True and cooldown == 2:
        walker = True

    if walker == True:
      await userStalker.send(name+' '+db["stalkerTrue"])
    else:
      await userStalker.send(name+' '+db["stalkerFalse"])
    i += 1


def berserkRage(playersDict, strikeDict):
  targets = strikeDict.values()
  rageBerserksList = []
  for target in targets:
    player = playersDict[target]
    targetRole = player.get_role()
    if targetRole == 'berserk':
      rageBerserksList.append(target)
      
  return rageBerserksList


async def berserkRageInformer(rageBerserksList, client):
  for berserk in rageBerserksList:
    user = client.get_guild(int(precius.get_guildID())).get_member(int(berserk))
    await user.send(db["berRage"])


def berserkRageStart(playersDict, rageBerserksList):
  for berserk in rageBerserksList:
    player = playersDict[berserk]
    player.set_usedAbility(False)

  return playersDict


def berserkRageEnd(playersDict, rageBerserksList):
  for berserk in rageBerserksList:
    player = playersDict[berserk]
    player.set_usedAbility(True)

  return playersDict


def strikeProcessor(playersDict, strikeDict, client):
  strikers = list(strikeDict.keys())
  targets = strikeDict.values()
  i = 0
  rangerSucLists = []
  for target in targets:
    player = playersDict[target]
    targetRole = player.get_role()
    if targetRole == 'ranger':
      usedAbility = player.get_usedAbility()
      cooldown = player.get_cooldown()
      if usedAbility == True and cooldown == 2:
        userTarget = client.get_guild(int(precius.get_guildID())).get_member(int(target))
        userID = userTarget.id
        userStriker = client.get_guild(int(precius.get_guildID())).get_member(int(strikers[i]))
        strikerName = userStriker.display_name
        rangerSucLists.append([userID, strikerName])
      else: 
        targetLives = player.get_lives()
        targetLives -= 1
        player.set_lives(targetLives)
    else:
      targetLives = player.get_lives()
      targetLives -= 1
      player.set_lives(targetLives)

    i += 1

  return rangerSucLists


def berserkProccesor(livePlayers, strikeDict, rageBerserksList):
  strikers = list(strikeDict.keys())
  for rageBerserk in rageBerserksList:
    if rageBerserk not in strikers:
      i = randint(0, len(livePlayers) - 1)
      strikeDict[rageBerserk] = str(livePlayers[i].id)
  return strikeDict


def nightProccesor(playersDict, strikeDict, client):
  targets = strikeDict.values()
  players = playersDict.values()
  playerIDs = list(playersDict.keys())
  nightChronic = {}
  i = 0
  for player in players:
    role = player.get_role()
    if role == 'dead':
      usedAbility = player.get_usedAbility()
      if usedAbility == True:
        zombie = client.get_guild(int(precius.get_guildID())).get_member(int(playerIDs[i]))
        zombieName = zombie.display_name
        nightChronic[zombieName] = 'attacked'
    i += 1

  for target in targets:
    targetPlayer = playersDict[target]
    targetLives = targetPlayer.get_lives()
    targetUser = client.get_guild(int(precius.get_guildID())).get_member(int(target))
    #targetID = str(targetUser.id)
    targetName = targetUser.display_name
    if targetLives <= 0:
      nightChronic[targetName] = 'died'
      deadList = precius.get_deadList()
      deadList.append(targetUser)
      precius.set_deadList(deadList)
    else:
      nightChronic[targetName] = 'attacked'
      
  return nightChronic

def allowLastWords(playersDict):
  players = playersDict.values()
  for player in players:
    role = player.get_role()
    if role == 'necromancer':
      lives = player.get_lives()
      if lives > 0:
        return True
  return False

def cooldown(playersDict):
  players = playersDict.values()
  for player in players:
    if player.get_usedAbility() == True:
      role = player.get_role()
      if role == "ranger":
        cd = player.get_cooldown()
        cd -= 1
        if cd == 0:
          player.set_usedAbility(False)
          cd = 2
        player.set_cooldown(cd)
      elif role != 'berserk':
        player.set_usedAbility(False)
      
  
def healer(playersDict):
  players = playersDict.values()
  mageAlive = False
  warListToHeal = []
  for player in players:
    lives = player.get_lives()
    role = player.get_role()
    if role == 'mage':
      if lives == 1:
        mageAlive = True
    elif role == 'warrior' or role == 'berserk':
      if lives == 1:
        warListToHeal.append(player)
  if mageAlive == True:
    for warrior in warListToHeal:
      warrior.set_lives(2)


def fakeRoleClearer(playersDict):
  players = playersDict.values()
  for player in players:
    player.set_fakeRole(None)
  return playersDict

def checkForWin():
  redList = getRed()
  redListLen = len(redList)
  if redListLen == 0:
    return True
  else:
    greenList = getGreen()
    greenListLen = len(greenList)
    if greenListLen <= redListLen:
      return False
    else:
      return None


def makePrettyList(playerList):
  message = ""
  for i in range(len(playerList)):
    message += str(i+1)+". "+playerList[i]+'\n'
    
  return message
  

def getRoles(playersDict, client):
  nameRoleList = []
  ids = playersDict.keys()
  deadPlayers = precius.get_deadList()

  for id in ids:
    user = client.get_guild(int(precius.get_guildID())).get_member(int(id))
    player = playersDict[id]

    name = user.display_name
    role = player.role
    role = roleTranslator(role)

    if user in deadPlayers:
      role = role + ' :skull:'
    
    nameRoleList.append([name, role])
  
  return nameRoleList


async def resulter(gameChat, joinChat, playersDict, client):
  winCheck = checkForWin()
  if winCheck != None:
    if winCheck == True:
      await gameChat.send(db["greenWon"])
      await joinChat.send(db["greenWon"])
    else:
      await gameChat.send(db["redWon"])
      await joinChat.send(db["redWon"])
      
    nameRole = getRoles(playersDict, client)
    nameRoleMessage = ""
    
    for nr in nameRole:
      nameRoleMessage = nameRoleMessage+nr[0]+' - '+nr[1]+'\n'

    await gameChat.send(nameRoleMessage)
    await joinChat.send(nameRoleMessage)
    
    await switch_state(1, 'dayf', gameChat)
    await switch_state(29, 'dayf', gameChat)
    guildID = precius.get_guildID()
    guild = client.get_guild(int(guildID))
    playerRoleID = db[guildID+'_PR']
    playerRole = guild.get_role(playerRoleID)
    await gameChat.set_permissions(playerRole, read_messages=True)
    precius.set_gameOn(False)

async def startContinuer(client, gameChat, joinChat):
  state = precius.get_state()
  guildID = precius.get_guildID()
  playerRoleID = db[guildID+'_PR']
  playerList = precius.get_playersL()
  evilChatID = db[guildID+'_EC']
  evilChat = client.get_channel(evilChatID)
  firstNightTime = 240
  firstDayTime = 120

  redList = getRed()
  if state == 'dayf':
    redAmount, greenAmount, mageAmount, warriorAmount, necroArcherPool, randomGreen, necroLimit, bersLimit = roleRoller.rolesAmount(len(playerList))
    playersAmountMessage = f'{db["greenPlayers"]} {greenAmount}, {db["redPlayers"]}  {redAmount}\n'
    rolesAmountMessage = f'({db["magEmoji"]} {mageAmount} маг, {db["warEmoji"]} {warriorAmount} воинов, возможны: {db["arcEmoji"]} лучник, {db["necEmoji"]} некромант'
    if greenAmount >= 8 and randomGreen != 0:
      rolesAmountMessage += f', {db["hunEmoji"]} охотник'
    if greenAmount >= 9 and randomGreen != 0:
      rolesAmountMessage += f', {db["warEmoji"]} воин'
    if greenAmount >= 9:
      rolesAmountMessage += f' и {db["berEmoji"]} берсерк' 
    rolesAmountMessage += ')'
    if len(playerList) == 5:
      await gameChat.send(f"<@&{playerRoleID}> "+db["gameStartedDay0Fast"]+playersAmountMessage+rolesAmountMessage)
      precius.set_state('day')
    else:
      await gameChat.send(f"<@&{playerRoleID}> "+db["gameStartedDay0Message1"]+f' {firstDayTime//60} '+db["gameStartedDay0Message2"]+playersAmountMessage+rolesAmountMessage)
      await switch_state(firstDayTime, 'nightf', gameChat)
      saveGame(precius)
    await gameChat.send(db["firstNightGameMessage1"]+f' {firstNightTime//60} '+db["firstNightGameMessage2"]+db["noMessages"])
    for redPlayer in redList:
      await evilChat.set_permissions(redPlayer, read_messages=True)
    await evilChat.send(f"<@&{playerRoleID}> "+db["firstNightMessage1"]+f' {firstNightTime//60} ' +db["firstNightMessage2"])
    saveGame(precius)
    await switch_state(firstNightTime, 'day', gameChat)
    for redPlayer in redList:
      await evilChat.set_permissions(redPlayer, overwrite=None)
      
  await cycle(client, gameChat, joinChat, 0)
  

async def starter(client, mode):
  state = precius.get_state()
  guildID = precius.get_guildID()
  gameChatID = db[guildID+'_GC']
  evilChatID = db[guildID+'_EC']
  joinChatID = db[guildID+'_JC']
  playerRoleID = db[guildID+'_PR']
  muteRoleID = db[guildID+'_MR']
  guild = client.get_guild(int(guildID))
  gameChat = client.get_channel(gameChatID)
  evilChat = client.get_channel(evilChatID)
  joinChat = client.get_channel(joinChatID)
  playerRole = guild.get_role(playerRoleID)
  

  if mode == 1:
    joinTime = 300
    firstDayTime = 120
    firstNightTime = 180
  elif mode == 2:
    joinTime = 120
    firstDayTime = 120
    firstNightTime = 240
    mode == 0
  else:
    joinTime = 600
    firstDayTime = 120
    firstNightTime = 240
  
  playerList = precius.get_playersL()   
  view = JoinLeave(timeout=None, joinList=playerList, muteRoleID=muteRoleID)
  oMessage = await joinChat.send(db["start1"]+f' {joinTime//60} '+db["start2"],view=view)
  view.message = oMessage
  await first_switch_state(joinTime, 'dayf', joinChat, joinTime, view)
  await view.disable_all_items()
  playerList = view.joinList
  if len(playerList) >= 5:
    if len(playerList) == 5:
      firstNightTime = 10
      
    playerDict = roleRoller.playerCreator(playerList)
    roleRoller.roleAssigner(playerList, playerDict)
    precius.set_playersL(playerList)
    precius.set_playersD(playerDict)
    await roleInformer(playerList, playerDict)
    await gameChat.set_permissions(playerRole, read_messages=True, send_messages=True)
  else:
    precius.clear()
    await joinChat.send(db["gameDidNotStarted"])
    return 

  redAmount, greenAmount, mageAmount, warriorAmount, necroArcherPool, randomGreen, necroLimit, bersLimit = roleRoller.rolesAmount(len(playerList))
  redList = getRed()
  playersAmountMessage = f'{db["greenPlayers"]} {greenAmount}, {db["redPlayers"]}  {redAmount}\n'
  rolesAmountMessage = f'({db["magEmoji"]} {mageAmount} маг, {db["warEmoji"]} {warriorAmount} воинов, возможны: {db["arcEmoji"]} лучник, {db["necEmoji"]} некромант'
  if greenAmount >= 8 and randomGreen != 0:
    rolesAmountMessage += f', {db["hunEmoji"]} охотник'
  if greenAmount >= 9 and randomGreen != 0:
    rolesAmountMessage += f', {db["warEmoji"]} воин'
  if greenAmount >= 9:
    rolesAmountMessage += f' и {db["berEmoji"]} берсерк' 
  rolesAmountMessage += ')'
  saveGame(precius)
  if len(playerList) == 5:
    await gameChat.send(f"<@&{playerRoleID}> "+db["gameStartedDay0Fast"]+playersAmountMessage+rolesAmountMessage)
    precius.set_state('day')
  else:
    await gameChat.send(f"<@&{playerRoleID}> "+db["gameStartedDay0Message1"]+f' {firstDayTime//60} '+db["gameStartedDay0Message2"]+playersAmountMessage+rolesAmountMessage)
    await switch_state(firstDayTime, 'nightf', gameChat)
    await gameChat.send(db["firstNightGameMessage1"]+f' {firstNightTime//60} '+db["firstNightGameMessage2"]+db["noMessages"])
    for redPlayer in redList:
      await evilChat.set_permissions(redPlayer, read_messages=True)
    await evilChat.send(f"<@&{playerRoleID}> "+db["firstNightMessage1"]+f' {firstNightTime//60} ' +db["firstNightMessage2"])
    saveGame(precius)
    await switch_state(firstNightTime, 'day', gameChat)
    for redPlayer in redList:
      await evilChat.set_permissions(redPlayer, overwrite=None)


  await cycle(client, gameChat, joinChat, mode)
    
async def cycle(client, gameChat, joinChat, mode):
  day = 1
  rageBerserksList = []
  if mode == 1:
    dayTime = 240
    revoteTime = 180
    nightTime = 120
    lastWordsTime = 120
  else:
    dayTime = 360
    revoteTime = 240
    nightTime = 120
    lastWordsTime = 120
    
  while precius.get_gameOn() == True:
    state = precius.get_state()
    playersDict = precius.get_playersD()
    actionDict = precius.get_actionDict()
    saveGame(precius)
    
    if state == 'day':
      precius.set_electionDict({})
      
      await gameChat.send(db["dayMessage1"]+f' {dayTime//60} '+db["dayMessage2"]) 
      await switch_state(dayTime, 'voting', gameChat)
    elif state == 'voting':
      electedList = getElected(client)
      electedLen = len(electedList)
      if electedLen == 0:
        await gameChat.send(db["votingMessagePac"])
      elif electedLen == 1:
        await mercer(electedList, gameChat, client, playersDict, electedList[0].id)
      else:
        await voter(electedList, gameChat, client, playersDict, revoteTime)
      await switch_state(5, 'night', gameChat)
      await resulter(gameChat, joinChat, playersDict, client)
  
          
    elif state == 'night':
      playersDict = fakeRoleClearer(playersDict)
      playersDict = berserkRageStart(playersDict, rageBerserksList)
      precius.set_playersD(playersDict)
      await gameChat.send(db["nightMessage1"]+f' {nightTime//60} '+db["nightMessage2"]+db["noMessages"])
      precius.set_actionDict({})
      
      await berserkRageInformer(rageBerserksList, client)
      await switch_state(nightTime, 'lastWords', gameChat)
        
    elif state == 'lastWords':
      strikeDict, viewDict, stalkerDict = actionProcessor(playersDict, actionDict, client)
      await viewerProcessor(playersDict, viewDict, client)
      await stalkeProcessor(playersDict, stalkerDict, client)

      
      livePlayers = getLive()     
      strikeDict = berserkProccesor(livePlayers, strikeDict, rageBerserksList)
      rangersLists = strikeProcessor(playersDict, strikeDict, client)
      lenRL = len(rangersLists)
      
      if lenRL > 0:
        for case in rangersLists:
          ranger = client.get_user(case[0])
          await ranger.send(db["rangerSuc"]+f" {case[1]}")
      
      nightChronic = nightProccesor(playersDict, strikeDict, client)
      nightChronicKeys = list(nightChronic.keys())
      nightChronicValues = nightChronic.values()
      i = 0
      attackedNames = []
      deadNames = []
      healer(playersDict)
      cooldown(playersDict)
      playersDict = berserkRageEnd(playersDict, rageBerserksList)
      precius.set_playersD(playersDict)
      rageBerserksList = berserkRage(playersDict, strikeDict)
      
      for value in nightChronicValues:
        key = nightChronicKeys[i]
        if value == 'attacked':
          attackedNames.append(key)
        else:
          deadNames.append(key)
        i += 1
        
      if len(attackedNames) > 0 and len(deadNames) > 0:
        attackedNames = str(attackedNames)
        attackedNames = attackedNames[1:-1]
        deadNames = str(deadNames)
        deadNames = deadNames[1:-1]
      
        await gameChat.send(f"Сегодня ночью были покушения, их пережили: {attackedNames}, погибли: {deadNames}")
          
      elif len(attackedNames) > 0:
        attackedNames = str(attackedNames)
        attackedNames = attackedNames[1:-1]
      
        await gameChat.send(f"Сегодня ночью были покушения, их пережили: {attackedNames}")
        
      elif len(deadNames) > 0:
        deadNames = str(deadNames)
        deadNames = deadNames[1:-1]
      
        await gameChat.send(f"Сегодня ночью были покушения, погибли: {deadNames}")
        
      else: 
        await gameChat.send("Сегодня ночью было тихо")
  
      if len(deadNames) > 0:
        necroIsAlive = allowLastWords(playersDict)
        if necroIsAlive == True:              
          await gameChat.send(db["lastWord1"]+f' {lastWordsTime//60} '+db["lastWord2"])
          await switch_state(lastWordsTime, 'day', gameChat) 
            
        else:
          await gameChat.send(db["flastWord"])
          await switch_state(1, 'day', gameChat)
          
      await resulter(gameChat, joinChat, playersDict, client)
      
      await switch_state(1, 'day', gameChat) 
  
      day += 1
      
    

  clearGame(precius.get_guildID())
  precius.clear()
        
        
  return


def spaceFinder(string, curSpace):
  for i in range(len(string[curSpace:])):
    i += curSpace
    if string[i] == ' ':
      return i
  return 0

async def send_message(message, user_message, is_private):
  try:
    response = responses.handle_response(user_message)

    if len(response) == 2: 
      if is_private == True:
        await message.author.send(response[0])
        await message.author.send(response[1])
      else:
        await message.channel.send(response[0])
        await message.channel.send(response[1])
    else:
      if is_private == True:
        await message.author.send(response)
      else:
        await message.channel.send(response)

  except Exception as e:
    print(e)


def run_discord_bot():
  load_dotenv()
  TOKEN = os.environ['TOKEN']
  intents = discord.Intents.all()
  intents.message_content = True
  client = discord.Client(intents=intents)

  @client.event
  async def on_ready():
    print(f'{client.user} is now running')
    keysList = list(db.keys())
    matches = []
    for key in keysList:
      if key[0:3] == "GO_":
        matches.append(key)
    #matches = db.prefix("GO_")
    for match in matches:
      continueGame(precius, client, str(match[3:]))
      guildID = precius.get_guildID()
      gameChatID = db[guildID+'_GC']
      joinChatID = db[guildID+'_JC']
      gameChat = client.get_channel(gameChatID)
      joinChat = client.get_channel(joinChatID)
      state = precius.get_state()
      playerRoleID = db[guildID+'_PR']
      guild = client.get_guild(int(guildID))
      playerRole = guild.get_role(playerRoleID)
      await gameChat.set_permissions(playerRole, read_messages=True, send_messages=True)
      if state == 'dayf' or state == 'nightf':
        await startContinuer(client, gameChat, joinChat)
      else:
        await cycle(client, gameChat, joinChat, 0)
      
    
  @client.event
  async def on_guild_join(guild):
    categoryName = 'Rogues Dark Pocket'
    gameChatName = 'RDP-game-chat'
    evilChatName = 'RDP-evil-chat'
    joinChatName = 'RDP-join-and-discuss'
    role = guild.self_role
    
    
    category = await guild.create_category(categoryName)
    gameChat = await guild.create_text_channel(gameChatName, topic = db["gameChatTopic"], category = category)
    evilChat = await guild.create_text_channel(evilChatName, topic = db["redChatTopic"], category = category)
    joinChat = await guild.create_text_channel(joinChatName, topic = db["joinChatTopic"], category = category)
    playerRole = await guild.create_role('RDP', mentionable=True)
    
    await category.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True)
    await category.set_permissions(guild.default_role, read_messages=False)
    await gameChat.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True)
    await gameChat.set_permissions(guild.default_role, read_messages=False)
    await gameChat.set_permissions(playerRole, read_messages=True)
    await evilChat.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True)
    await evilChat.set_permissions(guild.default_role, read_messages=False)
    await joinChat.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True)
    await joinChat.set_permissions(playerRole, read_messages=True)
    await joinChat.set_permissions(guild.default_role, read_messages=False)
    
    db[str(guild.id)+'_C'] = gameChat.category_id
    db[str(guild.id)+'_GC'] = gameChat.id
    db[str(guild.id)+'_EC'] = evilChat.id
    db[str(guild.id)+'_JC'] = joinChat.id
    db[str(guild.id)+'_PR'] = playerRole.id
    
  
  @client.event
  async def on_message(message):
    
    if message.author.bot == True:
      return

    user_message = str(message.content)
    guild = (message.guild)
    state = precius.get_state()
    if guild != None:
      guildID = str(guild.id)
      gameChatID = db[guildID+'_GC']
      gameChat = client.get_channel(gameChatID)
    
      if message.channel == gameChat:
        livePlayers = getLive()
        deadPlayers = precius.get_deadList()
        author = message.author
        dontDelete = False
        if author in livePlayers:
          days = ['day','dayRV','dayf']
          if state in days:
            dontDelete = True 
        elif author in deadPlayers:
          if state == 'lastWords':
            actionDict = precius.get_actionDict()
            targetIDs = actionDict.values()
            for targetID in targetIDs:
              target = client.get_user(int(targetID))
              if author == target:
                dontDelete = True
                break
        if dontDelete == False:
          await message.delete()
          return 
    
    
    if len(user_message) == 0:
      return
    if user_message[0] != '.':
      return
    user_message = user_message[1:]
    
    enWords = ['rules','help','state','show','live','dead','use','start','startq','play','warrior','ranger','mage','necromancer','werewolf','warlock','died','vampire','hunter','berserk']
    ruWords = ['правила','помощь','состояние','показать','живые','мёртвые','использовать','старт','стартб','играть','воин','лучник','маг','некромант','оборотень','чернокнижник','мертвец','вампир','охотник','берсерк']
    
    if user_message in ruWords:
      for i in range(len(ruWords)):
        if user_message == ruWords[i]:
          user_message = enWords[i]
          break;
    

    username = str(message.author)
    channel = str(message.channel)
    gameChat = None
    if precius.get_guildID() != None:
      gameChatID = db[precius.get_guildID()+'_GC']
      gameChat = client.get_channel(gameChatID)
      
    if user_message[:5] == 'start' or user_message[:4] == 'play':
      if isinstance(message.channel, discord.DMChannel):
        await message.channel.send(db["dmstart"])
      else:
        if precius.get_gameOn() == False:
          precius.set_gameOn(True)
          precius.set_state('joining')
          precius.set_guildID(guildID)
          playersL = precius.get_playersL()
          playersL.append(message.author)
          precius.set_playersL(playersL)
          state = precius.get_state()
          if len(user_message) > 5:
            if user_message[5] == 'q':
              await starter(client, 1)
            elif user_message[5] == 's':
              await starter(client, 2)
            else:
              await starter(client, 0)
          else: 
            await starter(client, 0)
        else:
          await message.channel.send(db["fstart"])
    elif user_message == 'restart':
      if message.author.id == 633589923018178570:
        precius.set_gameOn(True)
        precius.set_state('night')
        precius.set_guildID(guildID)
        listOfPLayers = []
        listOfIDs = [756587908219273217,624916078501298199,454031068144599041,897557357733773332]
        for i in range(len(listOfIDs)):
          listOfPLayers.append(client.get_user(listOfIDs[i]))
        playerDict = {}
        playerDict[str(listOfIDs[0])] = roleRoller.Player(role="dead")
        playerDict[str(listOfIDs[1])] = roleRoller.Player(role="warrior", lives =2)
        playerDict[str(listOfIDs[2])] = roleRoller.Player(role="mage")
        playerDict[str(listOfIDs[3])] = roleRoller.Player(role="warrior", lives =2)
        precius.set_playersL(listOfPLayers)
        precius.set_playersD(playerDict)
        guildID = precius.get_guildID()
        gameChatID = db[guildID+'_GC']
        joinChatID = db[guildID+'_JC']
        guild = client.get_guild(int(guildID))
        gameChat = client.get_channel(gameChatID)
        joinChat = client.get_channel(joinChatID)
        await cycle(client, gameChat, joinChat, 0)
      else:
        await message.channel.send("no")
        
    elif user_message[:5] == 'state':
      await message.channel.send(f'{state}')
      
    elif user_message[:4] == 'show':
      if precius.get_gameOn() == True:
        noShowList = precius.get_playersL()
        showList = []
        for inGameUser in noShowList:
          showList.append(inGameUser.display_name)
        prettyListMessage = makePrettyList(showList)
        
        await message.channel.send(prettyListMessage)
        
      else:
        await message.channel.send(db["fshow"])
        
    elif user_message == 'testdbu':
      db[str(message.author.id)] = message.author.id
      await message.channel.send(client.get_user(db[str(message.author.id)]))
    elif user_message == 'testview':
      view = TestView()
      oMessage = await message.author.send("here is your view", view=view)
      view.message = oMessage
    
    elif user_message[:4] == 'live':
      if precius.get_gameOn() == True:
        noShowList = getLive()
        showList = []
        for inGameUser in noShowList:
          showList.append(inGameUser.display_name)
        prettyListMessage = makePrettyList(showList)
        
        await message.channel.send(prettyListMessage)

    elif user_message[:4] == 'died':
      if precius.get_gameOn() == True:
        noShowList = precius.get_deadList()
        showList = []
        for inGameUser in noShowList:
          showList.append(inGameUser.display_name)
        prettyListMessage = makePrettyList(showList)

        if len(prettyListMessage) == 0:
          prettyListMessage = db['noDeadYet']
        await message.channel.send(prettyListMessage)
  
    elif user_message[:3] == 'use':
      if isinstance(message.channel, discord.DMChannel):
        if precius.get_state() == 'night':
          abilityUsers = getAbilityUsers()
          aUIDs = abilityUsers.keys()
          user = message.author
          uID = user.id

          if uID in aUIDs:
            livePlayers = getLive()
            playersDict = precius.get_playersD()
            role = abilityUsers[uID]
            player = playersDict[str(uID)]
            
            if role == 'mage':
              player.set_usedAbility(True)
              await roleViewer(livePlayers, playersDict, False, client, user)
            elif role == 'necromancer':
              deadList = precius.get_deadList()
              player.set_usedAbility(True)
              if len(deadList) != 0:
                await roleViewer(deadList, playersDict, True, client, user)
              else:
                await message.channel.send(db["necroRest"])
            elif role == 'ranger':
              await abilityUser(user, playersDict)
            elif role == 'werewolf':
              player.set_usedAbility(True)
              await striker(livePlayers, client, user)
            elif role == 'dead':
              await abilityUser(user, playersDict)
            elif role == 'warlock':
              player.set_usedAbility(True)
              await warlockChoose(livePlayers, playersDict, client, user)
            elif role == 'vampire':
              player.set_usedAbility(True)
              await vampireChoose(livePlayers, playersDict, client, user)
            elif role == 'hunter':
              player.set_usedAbility(True)
              await stalker(livePlayers, playersDict, client, user)
            elif role == 'berserk':
              player.set_usedAbility(True)
              await striker(livePlayers, client, user)
          else:
            await message.author.send(db["useD"])
        else:
          await message.author.send(db["useT"])
      else:
        await message.channel.send(db["useF"])
    
    elif user_message[:5] == 'elect' or user_message[:9] == 'выдвинуть':
      if gameChat != None:
        if message.channel == gameChat:
          playersIDs = getIDs(getLive())
          if message.author.id in playersIDs:
            if state == 'day':    
              elecDict = precius.get_electionDict()
              elector = message.author
              elected = int(user_message[findIDStart(user_message):findIDEnd(user_message)])
              if elected in playersIDs:
                elecDict[str(elector.id)] = elected
                precius.set_electionDict(elecDict) 
                await message.channel.send(f'{elector.display_name} '+db["election"]+f' {user_message[findIDStart(user_message)-2:findIDEnd(user_message)+1]}')
                electedPlayers = elecDict.values()
                electedPlayers = unique(electedPlayers)
                for i in range(len(electedPlayers)):
                  user = message.guild.get_member(electedPlayers[i])
                  electedPlayers[i] = user.display_name
                prettyListMessage = makePrettyList(electedPlayers)
                await message.channel.send(db["electionList"]+prettyListMessage)
              else:
                await message.channel.send(f'<@{elected}> '+db["felection"])
            else:
              await message.channel.send(db["electfd"])
        else:
          await message.channel.send(db["electfc"])
      
      
    elif user_message[:4] == 'stop':
      if gameChat != None:
        if precius.get_gameOn():
          livePlayersIDs = getIDs(getLive())
          user = message.author
          if user.id in livePlayersIDs:
            lenToStop = 2 #len(livePlayers) //3 + 1
            stopList = []
            stopList.append(user.id)
            view = StopView(timeout=60, liveList = livePlayersIDs, stopList = stopList, amountToStop = lenToStop)
            oMessage = await gameChat.send(db["stop"], view = view)
            view.message = oMessage
            await view.wait()
            await view.disable_all_items()
            
            stopList = view.stopList
            if len(stopList) >= lenToStop:
              guildID = precius.get_guildID()
              joinChatID = db[guildID+'_JC']
              joinChat = client.get_channel(joinChatID)
              
              stopMessage = db["stopped"] + f" {message.guild.get_member(stopList[0]).display_name} и {message.guild.get_member(stopList[1]).display_name}"
              await gameChat.send(stopMessage)
              await joinChat.send(stopMessage)

              playersDict = precius.get_playersD()
              nameRole = getRoles(playersDict, client)
              nameRoleMessage = ""
    
              for nr in nameRole:
                nameRoleMessage = nameRoleMessage+nr[0]+' - '+nr[1]+'\n'

              await gameChat.send(nameRoleMessage)
              await joinChat.send(nameRoleMessage)

              guildID = precius.get_guildID()
              guild = client.get_guild(int(guildID))
              playerRoleID = db[guildID+'_PR']
              playerRole = guild.get_role(playerRoleID)
              await gameChat.set_permissions(playerRole, read_messages=True)
              
              precius.set_gameOn(False)
              precius.set_state("stopping")
              
            else:
              await gameChat.send(db["fstopped"])

        
    elif user_message[:11] == 'randomthing':
      randomNumber = randint(0,9)
      roleList = ['warrior','ranger','mage','necromancer','werewolf','warlock','dead','vampire','hunter','berserk']
      file = discord.File(fp=f'imgs_ru/{roleList[randomNumber]}.png')
      await message.channel.send(file=file)

    elif user_message[:9] == 'roleroles':
      numberOfRoles = int(user_message[10:])
      if numberOfRoles > 0:
        roleList = roleRoller.roleGenerator(numberOfRoles)
        shuffle(roleList)
        roleMessage = ''
        for i in  range(len(roleList)):
          roleMessage = roleMessage+f'{i+1}. {roleTranslator(roleList[i])}\n'
  
        await message.channel.send(roleMessage)
      else:
        await message.channel.send(f".roleroles {numberOfRoles*-1}")
        
    
    elif user_message in ['rules','help','warrior','ranger','mage','necromancer','werewolf','warlock','dead','vampire','hunter','berserk']:
      if gameChat != None:
        if message.channel == gameChat:
          await send_message(message, user_message, is_private=True)
        else: 
          await send_message(message, user_message, is_private=False)
      else:
        await send_message(message, user_message, is_private=False)


    elif user_message[:8] == 'dbchange':
      if message.author.id == 633589923018178570:
        firstSpace = spaceFinder(user_message, 0)
        secondSpace = spaceFinder(user_message, firstSpace+1)
        if secondSpace != 0:
          db[user_message[firstSpace+1:secondSpace]] = user_message[secondSpace+1:]
          await message.channel.send(f"changed {user_message[firstSpace+1:secondSpace]} to {user_message[secondSpace+1:]}")
        else:
          await message.channel.send("spaces?")
      else:
        await message.channel.send("no")

    elif user_message[:6] == 'dbsend':
      if message.author.id == 633589923018178570:
        firstSpace = spaceFinder(user_message, 0)
        if firstSpace != 0:
          await message.channel.send(db[user_message[firstSpace+1:]])
        else:
          await message.channel.send("spaces?")
      else:
        await message.channel.send("no")

    elif user_message[:3] == 'fix':
      if message.author.id == 633589923018178570:
        #guildID = precius.get_guildID()
        guildID = str(709349607322157096)
        evilChatID = db[guildID+'_EC']
        evilChat = client.get_channel(evilChatID)
        stuckIDs = [519552595103186983, 633589923018178570]
        for evilStuckID in stuckIDs:
          evilStuck = client.get_user(evilStuckID)
          await evilChat.set_permissions(evilStuck, overwrite=None)


    elif user_message[:8] == 'testname':
      test_id = int(user_message[9:])
      if message.guild == None:
        test_user = client.get_user(test_id)
      else:
        test_user = message.guild.get_member(test_id)
      await message.channel.send(f'name: {test_user.name}\nglobal_name: {test_user.global_name}\ndisplay_name: {test_user.display_name}')


    elif user_message[:16] == 'bullymessagesoff':
      bullies = getbullies(client)
      if message.author in bullies:
        db['cyberbublingmessages'] = 'False'


    elif user_message[:15] == 'bullymessageson':
      bullies = getbullies(client)
      if message.author in bullies:
        db['cyberbublingmessages'] = 'True'


    elif user_message[:10] == 'addbullied':
      bullies = getbullies(client)
      if message.author in bullies:
        db['cyberbullied'] += ' ' + str(user_message[11:])


    elif user_message[:13] == 'removebullied':
      bullies = getbullies(client)
      if message.author in bullies:
        bulliedIDs = getValuesFromDB('cyberbullied')
        bulliedIDs.remove(user_message[14:])
        db['cyberbullied'] = ' '.join(bulliedIDs)


    elif user_message[:10] == 'addbullies':
      if message.author.id == 633589923018178570:
        db['cyberbullies'] += ' ' + str(user_message[11:])

    
    elif user_message[:13] == 'removebullies':
      if message.author.id == 633589923018178570:
        bulliesIDs = getValuesFromDB('cyberbullies')
        bulliesIDs.remove(user_message[14:])
        db['cyberbullies'] = ' '.join(bulliesIDs)


    elif user_message[:17] == 'bullyreactionsoff':
      bullies = getbullies(client)
      if message.author in bullies:
        db['cyberbublingreactions'] = 'False'


    elif user_message[:16] == 'bullyreactionson':
      bullies = getbullies(client)
      if message.author in bullies:
        db['cyberbublingreactions'] = 'True'


    elif user_message[:20] == 'clearBadReactionsoff':
      bullies = getbullies(client)
      if message.author in bullies:
        db['clearBadReactions'] = 'False'


    elif user_message[:19] == 'clearBadReactionson':
      bullies = getbullies(client)
      if message.author in bullies:
        db['clearBadReactions'] = 'True'
        

    elif user_message[:15] == 'addbadreactions':
      bullies = getbullies(client)
      if message.author in bullies:
        db['badreactions'] += ' ' + str(user_message[16:])


    elif user_message[:18] == 'removebadreactions':
      bullies = getbullies(client)
      if message.author in bullies:
        bulliedIDs = getValuesFromDB('badreactions')
        bulliedIDs.remove(user_message[19:])
        db['badreactions'] = ' '.join(bulliedIDs)


    elif user_message[:19] == 'lazyaddbadreactions':
      bullies = getbullies(client)
      if message.author in bullies:
        db['badreactions'] += ' ' + str(user_message[21:-1])


    elif user_message[:22] == 'lazyremovebadreactions':
      bullies = getbullies(client)
      if message.author in bullies:
        bulliedIDs = getValuesFromDB('badreactions')
        bulliedIDs.remove(user_message[24:-1])
        db['badreactions'] = ' '.join(bulliedIDs)

    elif user_message[:12] == 'deletethread':
      if message.author.id == 633589923018178570:
        await message.channel.delete()    
    

    if db['cyberbublingmessages'] == 'True':
      bulliedUsers = getbullied(client)
      if message.author in bulliedUsers:
        await message.delete()
    

      
    '''
    if user_message[0] == '?':
      user_message = user_message[1:]
      await send_message(message, user_message, is_private=True)
    else:
      await send_message(message, user_message, is_private=False)
      '''

  
  '''@client.event
  async def on_reaction_add(reaction, user):
    if db['cyberbublingreactions'] == 'True':
      bulliedUsers = getbullied(client)
      if user in bulliedUsers:
        await reaction.remove(user)
        
    if db['clearBadReactions'] != 'True':
      return
    if reaction.message.channel.id != int(db['marketID']):
      return
    bad_reactions = getValuesFromDB('badreactions')
    if reaction.emoji.name.lower() in bad_reactions:
      await reaction.remove(user)'''


  '''@client.event 
  async def on_thread_create(thread):
    if db['ghostpingthreadsdelete'] != 'True':
      return
    if str(thread.owner_id) not in getghostpingprankersIDs():
      return
    await sleep(1)
    await thread.delete()'''
      
  
  client.run(TOKEN)
