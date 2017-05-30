import pygame

from numpy.random import uniform
import numpy as np

SPRITE_SIZE_X = 32
SPRITE_SIZE_Y = 32

STEP_SIZE  = 8
STEP_LEFT  = np.array( ( -1, 0 ) ) * STEP_SIZE
STEP_RIGHT = np.array( ( +1, 0 ) ) * STEP_SIZE
STEP_UP    = np.array( (  0,-1 ) ) * STEP_SIZE
STEP_DOWN  = np.array( (  0,+1 ) ) * STEP_SIZE
STEP_LEFT_TUPLE  = tuple( STEP_LEFT.tolist() )
STEP_RIGHT_TUPLE = tuple( STEP_RIGHT.tolist() )
STEP_UP_TUPLE    = tuple( STEP_UP.tolist() )
STEP_DOWN_TUPLE  = tuple( STEP_DOWN.tolist() )

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
        datastr = configFile.read().strip()
        data = eval( datastr )
    #XXX yes, this needs to be parsed and secured, maybe pickled and hashed
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
                  kind=[],
                  elements=[],
                  evolution=None,
                  statistics=None,
                  abilities={}
                ):
        self.kind = kind            # creature's kind, str
        self.elements = elements    # creature's associated elements, list
        self.evolution = evolution  # creature's evolution characteristics, dict
        self.statistics = statistics# creature's statistics, dict
        self.abilities = abilities  # creature's abilities, dict

    def __repr__( self ):
        outstr = "CSCreature( kind=%s,elements=%s,evolution=%s,statistics=%s,abilities=%s )"%( self.kind,self.elements,self.evolution,self.statistics,self.abilities )
        return outstr

    def increaseExp( self,xp ):
        '''
        Increase the accumulated XP for this creature, including checking
        for leveling-up and evolution.
        '''
        self.statistics[ 'exp' ] += xp
        self.checkLevelUp()
        self.checkEvolution()

    def checkLevelUp( self ):
        '''
        Check for leveling up, if the accumulated XP are high enough.
        '''
        xps = [ 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040, 1346269, 2178309, 3524578, 5702887, 9227465, 14930352, 24157817, 39088169, 63245986, 102334155 ]
        from numpy import cumsum
        xps_cum = cumsum( xps )
        levels = {}
        for level in range( len( xps ) ):
            levels[ level ] = xps_cum[ level ]

        if self.statistics[ 'exp' ] >= levels[ self.statistics[ 'level' ]+1 ]:
            # possibly multiple level-ups if a solid battle, esp. early on
            # XXX: it is possible to level up twice and skip a possible
            # evolution if the evolution tree is poorly designed!
            lvl = self.statistics[ 'level' ] + 1
            while self.statistics[ 'exp' ] >= levels[ lvl ]:
                lvl += 1
            self.levelUp( lvl )

    def levelUp( self,targetLevel ):
        '''
        Increase the creature's level.
        '''
        self.statistics[ 'level' ] = targetLevel

        # Update statistics.
        self.statistics[ 'maxHealth' ] += 5  #XXX
        self.statistics[ 'maxPower' ] += 5   #XXX
        self.statistics[ 'realHealth' ] = self.statistics[ 'maxHealth' ]
        self.statistics[ 'realPower' ] = self.statistics[ 'maxPower' ]

    def checkEvolution( self ):
        '''
        Check for evolution.
        '''
        # Check for evolution.
        if self.statistics[ 'level' ] in self.evolution:
            # Short-circuit test:
            if self.evolution[ self.statistics[ 'level' ] ][ 0 ][ 0 ] >= 1.0:
                self.evolve( self.evolution[ self.statistics[ 'level' ] ][ 0 ][ -1 ] )

            # Regular test:
            for path in self.evolution[ self.statistics[ 'level' ] ]:
                prob = uniform()
                if prob < path[ 0 ]:
                    self.evolve( path[ -1 ] )

    def evolve( self,target ):
        '''
        Change the creature's kind to the target evolution.

        Leveling up is a separate process, which would typically be handled
        beforehand.
        '''
        try:
            targetEvolvedCreature = findEvolution( target )
        except:
            pass
            #XXX should handle this case more elegantly, TargetNotFoundException
            # or at least a warning

        self.kind = targetEvolvedCreature.kind
        self.elements = targetEvolvedCreature.elements
        self.evolution = targetEvolvedCreature.evolution
        #self.statistics = self.statistics
        self.abilities = targetEvolvedCreature.abilities
        #XXX do abilities inherit? abilitiesUnion?

class CSCharacter:
    """
    The base CSCharacter type.  CSCreature is _not_ derived from this class.
    """

    def __init__( self,
                  name='',
                  inventory=[],
                  creatures=[],
                  position=np.array( ( 0.,0. ) ),
                  direction=0,
                  behavior=None,
                  statistics=None,
                  dialogue=None,
                  sprite_file='',
                  sprite_number=0
                ):
        self.name = name            # character's name, if any, str
        self.inventory = inventory  # character's inventory, list
        self.creatures = creatures  # character's creatures, list
        self.position = np.array( position )    # character's position, array
        self.direction = 3          # character's direction, int in [0,4)
        self.behavior = behavior    # character's behavior, class CSBehaviorPattern
        self.statistics = statistics# character's statistics, dict
        self.dialogue = dialogue    # character's dialogue tree, class CSDialogue

        self.sprite_file = sprite_file  # character's sprite file, str
        self.sprites = []
        self.facing = { STEP_LEFT_TUPLE  : 2,  # left
                        STEP_RIGHT_TUPLE : 3,  # right
                        STEP_UP_TUPLE    : 0,  # backwards
                        STEP_DOWN_TUPLE  : 1   # forwards
                      }
        self.loadSprites( sprite_file,sprite_number )

        self.sprite = None
        self.sprite_frame = 0       # current sprite frame
        self.sprite_next  = 0       # next sprite frame (if nothing changes)
        self.update()

    def loadSprites( self,sprite_file,sprite_number ):
        img = pygame.image.load( sprite_file )
        offset_x = sprite_number * SPRITE_SIZE_X * 3
        offset_y = 0
        self.sprites = []
        # should be 4 directional sprites, 4 frames (if flipped)
        for direction in ( 3,0,1,2 ):
            dir_sprites = []
            for stage in range( 4 ):
                xmin = stage * SPRITE_SIZE_X + offset_x
                ymin = direction * SPRITE_SIZE_Y + offset_y

                if stage == 3:
                    stage_sprite = dir_sprites[ 1 ]
                else:
                    rect = pygame.Rect( xmin,ymin,SPRITE_SIZE_X,SPRITE_SIZE_Y )
                    stage_sprite = img.subsurface( ( rect ) )
                dir_sprites.append( stage_sprite )
            self.sprites.append( dir_sprites )

    def update( self ):
        self.sprite = self.sprites[ self.direction ][ self.sprite_frame ]

        self.sprite_frame = self.sprite_next
        self.sprite_next = ( self.sprite_next + 1 ) % 4

def main( ):
    """
    Test instantiations.
    """

    """
        Evolution is stored as a dictionary of levels mapped to tuples containing the likelihood and target.

        The dictionary may be generated ahead of time or modified on-the-fly.
        Note that evolution happens when leveling up.  In other words, if you
        instantiate a creature at a higher level than it usually would be, it
        will not automatically level up but will continue with its current
        form.  If you do not desire this behavior, you should start the
        creature as its evolved form at the appropriate level.

        For a creature that has a single evolutionary result with likelihood 100% at level 8:
            { 8: ( ( 1.0,'gryphon' ) ) }

        For a creature with a gradually increasing likelihood of evolution along a single evolutionary line:
            { 1: ( ( 0.1,'sylph' ) ), 2:( ( 0.2,'sylph' ) ), 3:( ( 0.3,'sylph' ) ) }
            # etc.

        For a creature with two possible paths at a certain stage:
            { 5: ( ( 0.25,'air golem' ),( 1.0,'earth golem' ) ) }

        Note that the probabilities should not sum to more than 100%.
        Also note that the probabilities should be _cumulative_---that is,
        the probability range should be increasing.  The following represents
        a 1/3 likelihood of evolving to each of three types:
            { 5: ( ( 0.33,'death kite' ),( 0.67,'turkey vulture' ),( 1.0,'peregrine falcon' ) ) }
    """
    print( findEvolution( 'liger' ) )
    print( findEvolution( 'gryphon' ) )
    print( findEvolution( 'lamia' ) )

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

    empty_statistics = { 'name': '',
                         'exp': 0,
                         'level': 0,
                         'realHealth':0,
                         'maxHealth':0,
                         'realPower':0,
                         'maxPower':0,
                         'status':None,
                         'attack':0,
                         'defence':0,
                         'modifiers':{},
                         'effects':{}
                       }

    skeleton_statistics = { 'name': 'Skelly',
                            'exp': 0,
                            'level': 0,
                            'realHealth':10,
                            'maxHealth':10,
                            'realPower':5,
                            'maxPower':5,
                            'status':None,
                            'attack':2,
                            'defence':1,
                            'modifiers':{},
                            'effects':{}
                          }
    skeleton = CSCreature( kind=['skeleton'],elements=['bone'],evolution={ 1:( ( 0.5,'skeleton knight' ), ),2:( ( 1.0,'skeleton knight' ), ) },statistics=skeleton_statistics,abilities={} )
    print( skeleton )

    skeleton.increaseExp( 1 )
    print( skeleton )

if __name__ == '__main__':
    main()
