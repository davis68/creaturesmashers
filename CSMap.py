import pygame
from pygame import Surface

from CSClasses import *

import numpy as np

class CSTile:
    '''
    Tiles need to contain a fair amount of information, and they need to be
    accessible quickly.  We're okay using "singletons" for many elements as a
    result of this (e.g., for bushes).
    '''
    def __init__( self,
                  dtype=0,
                  passable=True,
                  active=False,
                  portal=None
                ):
        self.dtype = dtype
        self.sprite = pygame.image.load( 'tile-%i.png'%self.dtype )
        self.passable = passable
        self.active = active
        self.portal = portal

class CSMap:
    def __init__( self,
                  id=-1,
                  source='',
                  status=''
                ):
        self.id = id            # the map ID number, int
        self.source = source    # the source file for the map, str
        self.status = status    # the map status modifiers file, str

        self.loadMap()
        self.initSurface()

    def loadMap( self ):
        '''
        All maps are square, and stored as a map (of tiles) and a mask (of actions).
        '''
        self.matrix = np.loadtxt( open( self.source, 'r' ),delimiter=',',dtype=np.float64 ).T
        self.parseMap()

    def parseMap( self ):
        '''
        Convert the matrix to a map.
        '''
        x,y = self.matrix.shape[ 0 ],self.matrix.shape[ 0 ]  #XXX map is square!
        map = self.matrix[ :x,:y ].astype( np.int32 ).copy()
        mask = self.matrix[ :x,y:2*y ].copy()

        self.tiles = np.empty( ( x,y ),dtype=np.object_ )
        for i in range( map.shape[ 0 ] ):
            for j in range( map.shape[ 1 ] ):
                self.tiles[ i,j ] = CSTile( dtype=map[ i,j ],passable=( False if mask[ i,j ] == -1 else True ),active=( True if mask[ i,j ] >= 2.0 else False ) )

                '''
                Convert the map values to a mask, used to determine where the PC can go.

                Map masks are a bit strange.  They encode several types of information:
                    -   impassable areas, as -1
                    -   chances of random encounters, in [0.0,1.0]
                    -   actions, in [2,3)
                Actions are perhaps the oddest of these.  The fractional part of the action corresponds to the location on another map to which the character would be transported.  (This is the poor man's tuple.)   This is interpreted as follows:
                    2.XXYYZZZWWW
                where X is the target map (two digits), Y is the target portal on that map (two digits), and Z,W are the exit coordinates on the target map.  For instance,
                    2.0203384352
                points to map 02, door 03.  (The direction the character is facing should be preserved automatically.)
                '''

                if mask[ i,j ] >= 2.0:
                    self.tiles[ i,j ].portal = {}
                    p = mask[ i,j ] - 2.0
                    p *= 100
                    target_map_id = int( p )
                    p -= int( p ); p *= 100
                    target_portal_id = int( p )
                    p -= int( p ); p *= 1000
                    tx = int( p )
                    p -= int( p ); p *= 1000
                    ty = int( p )

                    self.tiles[ i,j ].portal[ 'target_map' ] = target_map_id
                    self.tiles[ i,j ].portal[ 'target_portal' ] = target_portal_id
                    self.tiles[ i,j ].portal[ 'target_portal_coords' ] = np.array( ( tx,ty ) )

    def initSurface( self ):
        xdim,ydim   = self.tiles.shape              # overall map size, in tiles
        xsize,ysize = SPRITE_SIZE_X,SPRITE_SIZE_Y   # tile size, in pixels
        self.surface = Surface( ( xdim*xsize,ydim*ysize ) )

        self.renderScene()

    def renderScene( self ):
        for i in range( self.tiles.shape[ 0 ] ):
            for j in range( self.tiles.shape[ 1 ] ):
                offset_x = i*SPRITE_SIZE_X
                offset_y = j*SPRITE_SIZE_Y
                self.surface.blit( self.tiles[ i,j ].sprite,( offset_x,offset_y ) )
