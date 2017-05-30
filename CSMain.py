import pygame
from pygame import Surface

from CSClasses import *

SPRITE_SIZE_X = 32
SPRITE_SIZE_Y = 32

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
        self.matrix = np.loadtxt( open( self.source, 'r' ),delimiter=',',dtype=np.int32 )
        self.mask   = self.parseMapToMask()

    def parseMapToMask( self ):
        pass
        # negative values are impassable, and have to look up active sites
        #TODO

    def initSurface( self ):
        xdim,ydim   = self.matrix.shape             # overall map size, in tiles
        xsize,ysize = SPRITE_SIZE_X,SPRITE_SIZE_Y   # tile size, in pixels
        self.surface = Surface( ( xdim*xsize,ydim*ysize ) )

        for i in range( self.matrix.shape[ 0 ] ):
            for j in range( self.matrix.shape[ 0 ] ):
                offset_x = i*SPRITE_SIZE_X
                offset_y = j*SPRITE_SIZE_Y
                self.surface.blit( self.tiles[ np.abs( self.matrix[ i,j ] ) ],( offset_x,offset_y ) )

    def initTiles( self ):
        self.tiles = []
        for i in range( np.max( np.abs( self.matrix ) ) + 1 ):
            self.tiles.append( pygame.image.load( 'tile-%i.png'%i ) )

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
    def __init__( self ):
        self.next = self
        #TODO: set starting point for map, initial configuration
        # A scene has a map, an event mask, and characters.
        self.pc = CSCharacter( sprite_file='character.png',position=( 100,100 ) )
        self.map = CSMap( id=0,source='map-0.csv' )
        self.screen = pygame.display.set_mode( self.map.surface.get_size() )
        self.time = 0

    def processInput( self,events,pressed_keys ):
        for event in events:
            if pressed_keys[ pygame.K_LEFT ]:
                self.pc.position[ 0 ] -= 1
            if pressed_keys[ pygame.K_RIGHT ]:
                self.pc.position[ 0 ] += 1
            if pressed_keys[ pygame.K_UP ]:
                self.pc.position[ 1 ] -= 1
            if pressed_keys[ pygame.K_DOWN ]:
                self.pc.position[ 1 ] += 1

    def update( self ):
        char_x = self.pc.position[ 0 ] #+32*np.cos( self.time ) + 300
        char_y = self.pc.position[ 1 ] #+32*np.sin( self.time ) + 300
        self.time += np.pi/180
        self.map.surface.blit( self.pc.sprite,( char_x,char_y ) )

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
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
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
    base_scene = CSScene()
    pygame.init()
    game_loop( base_scene )
    pygame.quit()

if __name__ == '__main__':
    main()
