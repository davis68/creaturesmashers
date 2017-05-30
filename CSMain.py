import pygame
from pygame import Surface

from CSClasses import *

class CSSprite:
    def __init__( self ):
        pass

import numpy as np
class CSMap:
    def __init__( self,
                  id=-1,
                  source='',
                  status='',
                  matrix=None
                ):
        self.id = id            # the map ID number, int
        self.source = source    # the source file for the map, str
        self.status = status    # the map status modifiers file, str
        self.matrix = matrix

        if source and not matrix:
            self.loadMap()

        self.initTiles()
        self.initSurface()

    def loadMap( self ):
        self.matrix = np.loadtxt( open( self.source, 'r' ),delimiter=',',dtype=np.int32 ).T
        self.parseMapToMask()

    def parseMapToMask( self ):
        '''
        Convert the map values to a mask, used to determine where the PC can go.

        From the map, negative values are impassable, and active sites are
        indicated by the tile type.

        On the mask, 1 is passable, 0 is impassable, 2 is active.
        '''
        self.mask = np.ones_like( self.matrix )

        for i in range( self.matrix.shape[ 0 ] ):
            for j in range( self.matrix.shape[ 1 ] ):
                if self.matrix[ i,j ] < 0:
                    self.mask[ i,j ] = 0
                if self.matrix[ i,j ] == 0:  # a door XXX change this to lookup
                    self.mask[ i,j ] = 2

    def initSurface( self ):
        xdim,ydim   = self.matrix.shape             # overall map size, in tiles
        xsize,ysize = SPRITE_SIZE_X,SPRITE_SIZE_Y   # tile size, in pixels
        self.surface = Surface( ( xdim*xsize,ydim*ysize ) )

        for i in range( self.matrix.shape[ 0 ] ):
            for j in range( self.matrix.shape[ 1 ] ):
                offset_x = i*SPRITE_SIZE_X
                offset_y = j*SPRITE_SIZE_Y
                self.surface.blit( self.tiles[ np.abs( self.matrix[ i,j ] ) ],( offset_x,offset_y ) )

    def initTiles( self ):
        self.tiles = []
        for i in range( np.max( np.abs( self.matrix ) ) + 1 ):
            self.tiles.append( pygame.image.load( 'tile-%i.png'%i ) )

    def renderScene( self ):
        for i in range( self.matrix.shape[ 0 ] ):
            for j in range( self.matrix.shape[ 0 ] ):
                offset_x = i*SPRITE_SIZE_X
                offset_y = j*SPRITE_SIZE_Y
                self.surface.blit( self.tiles[ np.abs( self.matrix[ i,j ] ) ],( offset_x,offset_y ) )


class SceneBase:
    '''
    Basic scene class, from http://www.nerdparadise.com/programming/pygame/part7
    '''
    def __init__( self ):
        self.next = self

    def processInput( self,events,pressed_keys ):
        print("uh-oh, you didn't override this in the child class")

    def update( self ):
        print("uh-oh, you didn't override this in the child class")

    def render( self,screen ):
        print("uh-oh, you didn't override this in the child class")

    def switchToScene( self,next_scene ):
        self.next = next_scene

    def terminate(self):
        self.switchToScene( None )

class CSScene( SceneBase ):
    def __init__( self,
                  map_file='map-0.csv',
                  start_coords=( 224,448 )
                ):
        self.next = self
        #TODO: set starting point for map, initial configuration
        # A scene has a map, an event mask, and characters.
        self.pc = CSCharacter( sprite_file='sprite-base.png',sprite_number=7,position=start_coords )
        self.map = CSMap( id=0,source=map_file )
        self.screen = pygame.display.set_mode( self.map.surface.get_size() )
        self.target_motion = np.array( ( 0,0 ) )
        self.time = 0

    def processInput( self,events,pressed_keys ):
        for event in events:
            if pressed_keys[ pygame.K_LEFT ]:
                self.target_motion += STEP_LEFT
                self.pc.direction = self.pc.facing[ STEP_LEFT_TUPLE ]
            if pressed_keys[ pygame.K_RIGHT ]:
                self.target_motion += STEP_RIGHT
                self.pc.direction = self.pc.facing[ STEP_RIGHT_TUPLE ]
            if pressed_keys[ pygame.K_UP ]:
                self.target_motion += STEP_UP
                self.pc.direction = self.pc.facing[ STEP_UP_TUPLE ]
            if pressed_keys[ pygame.K_DOWN ]:
                self.target_motion += STEP_DOWN
                self.pc.direction = self.pc.facing[ STEP_DOWN_TUPLE ]

    def update( self ):
        self.map.renderScene()  #TODO:camera view

        # Check for collisions with the mask.
        target = self.pc.position + self.target_motion
        if self.map.mask[ int( ( target[ 0 ] + SPRITE_SIZE_X*0.5 ) / SPRITE_SIZE_X ),int( ( target[ 1 ] + SPRITE_SIZE_Y*0.5 ) / SPRITE_SIZE_Y ) ] == 0:
            target = self.pc.position
        if self.map.mask[ int( ( target[ 0 ] + SPRITE_SIZE_X*0.5 ) / SPRITE_SIZE_X ),int( ( target[ 1 ] + SPRITE_SIZE_Y*0.5 ) / SPRITE_SIZE_Y ) ] == 2:
            next_scene = CSScene( map_file='map-1.csv' )
            self.next = next_scene
        self.pc.position = target
        self.pc.update()

        char_x = self.pc.position[ 0 ]
        char_y = self.pc.position[ 1 ]
        self.time += np.pi/180
        self.map.surface.blit( self.pc.sprite,( char_x,char_y ) )

        self.target_motion = np.array( ( 0,0 ) )

    def render( self ):
        self.screen.fill( ( 0,0,0 ) )
        self.screen.blit( self.map.surface,( 0,0 ) )

def game_loop( starting_scene ):
    clock = pygame.time.Clock()
    fps = 25

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()

        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[ pygame.K_LALT ] or \
                              pressed_keys[ pygame.K_RALT ]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.terminate()
            else:
                filtered_events.append( event )

        active_scene.processInput( filtered_events,pressed_keys )
        active_scene.update()
        active_scene.render()

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick( fps )


def main():
    base_scene = CSScene( start_coords=( 100,100 ) )
    pygame.init()
    game_loop( base_scene )
    pygame.quit()

if __name__ == '__main__':
    main()
