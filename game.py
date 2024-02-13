class Game:

  def __init__(self, gameOn=False, state='noGame', playersL=[], playersD={}, guildID = None, deadList=[], electionDict={}, actionDict={}):
    self.gameOn = gameOn
    self.state = state
    self.playersL = playersL
    self.playersD = playersD
    self.guildID = guildID
    self.deadList = deadList
    self.electionDict = electionDict
    self.actionDict = actionDict

  def get_gameOn(self):
    return self.gameOn

  def get_state(self):
    return self.state

  def get_playersL(self):
    return self.playersL

  def get_playersD(self):
    return self.playersD

  def get_guildID(self):
    return self.guildID

  def get_deadList(self):
    return self.deadList

  def get_electionDict(self):
    return self.electionDict

  def get_actionDict(self):
    return self.actionDict
    
  
  def set_gameOn(self, x):
    self.gameOn = x

  def set_state(self, x):
    self.state = x

  def set_playersL(self, x):
    self.playersL = x

  def set_playersD(self, x):
    self.playersD = x

  def set_guildID(self, x):
    self.guildID = x

  def set_deadList(self, x):
    self.deadListc = x

  def set_electionDict(self, x):
    self.electionDict = x

  def set_actionDict(self, x):
    self.actionDict = x

  def clear(self):
    self.gameOn = False
    self.state = 'noGame'
    self.playersL = []
    self.playersD = {}
    self.guildID = None
    self.deadList = []
    self.electionDict = {}
    self.actionDict = {}