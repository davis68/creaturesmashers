import pygame

from numpy.random import uniform

"""
    Evolution is stored as a dictionary of levels mapped to tuples containing the likelihood and target.

    The dictionary may be generated ahead of time or modified on-the-fly.
    Note that evolution happens when leveling up.  In other words, if you instantiate a creature at a higher level than it usually would be, it will not automatically level up but will continue with its current form.  If you do not desire this behavior, you should start the creature as its evolved form at the appropriate level.
    
    For a creature that has a single evolutionary result with likelihood 100% at level 8:
        { 8: ( ( 1.0,'gryphon' ) ) }

    For a creature with a gradually increasing likelihood of evolution along a single evolutionary line:
        { 1: ( ( 0.1,'sylph' ) ), 2:( ( 0.2,'sylph' ) ), 3:( ( 0.3,'sylph' ) ) }
        # etc.

    For a creature with two possible paths at a certain stage:
        { 5: ( ( 0.25,'air golem' ),( 0.75,'earth golem' ) ) }

    Note that the probabilities should not sum to more than 100%.

    Q: is it better to store by type and likelihood, or by level then likelihood then type?
"""

"""
The psychosomatic statistics of the creature are stored as a dictionary
containing the fields:

    realHealth: int  # current hit points
    maxHealth: int   # maximum hit points (including any modifiers)
    realPower: int   # current power level
    maxPower: int    # maximum power level (including any modifiers)
    status: list     # status modifiers, such as 'enchanted' or 'asleep'
    attack: int      # attack level (including any modifiers)
    defence: int     # defence level (including any modifiers)
    modifiers: dict  # currently active modifiers, listed as a dictionary
                     # mapping statistic name to value
    effects: dict    # currently active effects, listed as a dictionary
                     # mapping effect name to class CSEffect
"""

statistics = { 'realHealth':0,
               'maxHealth':0,
               'realPower':0,
               'maxPower':0,
               'status':None,
               'attack':0,
               'defence':0,
               'modifiers':{},
               'effects':{}
	     }

class CSEffect:
    """
    Stub for CSEffect class.
    """

class CSDialogue:
    """
    Stub for class CSDialogue.
    """

class CSBehaviorPattern:
    """
    Stub for class CSBehaviorPattern.
    """

evolutions = None

def loadEvolution( configFile ):
    '''
    Load the target evolution data structure from disk.

    The evolution data structure is a dictionary mapping strings representing
    creature names to CSCreatures with genericized features (since attributes
    like names will be overwritten by the actual creature later).
    '''
    from os import getcwd
    from os.path import join
    configPath = join( getcwd(),configFile )
    with open( configPath,'r' ) as configFile:
        exec( "data=%s"%configFile.read().strip() )
	#XXX yes, this needs to be parsed and secured
    return data

from copy import deepcopy
def findEvolution( target ):
    '''
    Identify the intended target evolution.
    '''
    # Load the list of evolutions from disk (if not previously loaded).
    global evolutions
    if not evolutions:
        evolutions = loadEvolution( 'evolutions.txt' )

    targetEvolvedCreature = None
    if target in evolutions:
        targetEvolvedCreature = deepcopy( evolutions[ target ] )

    return targetEvolvedCreature


class CSCreature:
    """
    The base CSCreature type.  CSCharacter is _not_ derived from this class.
    """

    def __init__( self,
                  name='',
                  kind=[],
                  elements=[],
                  level=0,
                  exp=0,
                  evolution=None,
                  statistics=None,
                  abilities={}
                ):
        self.name = name            # creature's name, if any, str
        self.kind = kind            # creature's kind, str
        self.elements = elements    # creature's associated elements, list
        self.level = level          # creature's level, int
        self.exp = exp              # creature's accumulated experience, int
        self.evolution = evolution  # creature's evolution characteristics, dict
        self.statistics = statistics        # creature's statistics, dict
        self.abilities = abilities  # creature's abilities, dict

    def __repr__( self ):
        outstr = "CSCreature( name='%s',kind=%s,elements=%s,level=%i,exp=%i,evolution=%s,statistics=%s,abilities=%s )"%( self.name,self.kind,self.elements,self.level,self.exp,self.evolution,self.statistics,self.abilities )
        return outstr

    def levelUp( self ):
        '''
        Increase the creature's level, including checking for evolution.
        
        Returns a tuple indicating whether evolution should occur, and,
        if so, the target kind.
        '''
        self.level += 1
	
	# Update statistics.
	self.statistics[ 'maxHealth' ] += 5  #XXX
	self.statistics[ 'maxPower' ] += 5   #XXX
	self.statistics[ 'realHealth' ] = self.statistics[ 'maxHealth' ]
	self.statistics[ 'realPower' ] = self.statistics[ 'maxPower' ]

        # Check for evolution.
        if self.level in self.evolution:
            # Short-circuit test:
            if self.evolution[ self.level ][ 0 ] >= 1.0:
                return ( True,self.evolution[ self.level ][ -1 ] )

            # Regular test:
            for path in self.evolution[ self.level ]:
                prob = uniform()
                if prob < path[ 0 ]:
                    return ( True,path[ -1 ] )

        return ( False,None )  # no evolution occurs

    def evolve( self,target ):
        '''
        Change the creature's kind to the target evolution.

        Leveling up is a separate process, which would typically be handled first.

        Returns a new CSCreature which should replace the former creature.
        '''
        try:
            targetEvolvedCreature = findEvolution( target )
        except:
            return None
            #XXX should handle this case more elegantly

        targetCreature = CSCreature( name=self.name,
                                     kind=targetEvolvedCreature.kind,
                                     elements=targetEvolvedCreature.element,
                                     level=self.level,
                                     exp=self.exp,
                                     evolution=targetEvolvedCreature.evolution,
                                     statistics=self.statistics,
                                     abilities=targetEvolvedCreature.abilities
                                   )
                                   #XXX do abilities inherit? abilitiesUnion?
        return targetCreature

class CSCharacter:
    """
    The base CSCharacter type.  CSCreature is _not_ derived from this class.
    """

    def __init__( self,
                  name='',
                  inventory=[],
                  creatures=[],
                  position=( 0.,0. ),
                  direction=0,
                  behavior=None,
                  statistics=None,
                  dialogue=None,
                  sprite=''
                ):
        self.name = name            # character's name, if any, str
        self.inventory = inventory  # character's inventory, list
        self.creatures = creatures  # character's creatures, list
        self.position = position    # character's position, tuple of floats
        self.direction = 0          # character's direction, int in [0,4)
        self.behavior = behavior    # character's behavior, class CSBehaviorPattern
        self.statistics = statistics# character's statistics, dict
        self.dialogue = dialogue    # character's dialogue tree, class CSDialogue
        self.sprite = sprite        # character's sprite file, str

def main( ):
    """
    Test instantiations.
    """
    pass

if __name__ == '__main__':
    main()
