import pygame
from pygame import Surface

from CSClasses import *
from CSMap import *

pc = CSCharacter( sprite_file='sprite-base.png',sprite_number=0,direction=3)

class CSSprite:
    def __init__( self ):
        pass


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
                  map_file='map-00.csv',
                  start_coords=None,
                  portal_id=0
                ):
        self.next = self
        #TODO: set starting point for map, initial configuration
        # A scene has a map, an event mask, and characters.
        global pc
        self.map = CSMap( id=0,source=map_file )
        #print( start_coords )
        if start_coords is not None:
            start_coords = np.array( start_coords )
        else:
            start_coords = self.map.portal_coords[ portal_id ]
            #coord_offset = { 0:np.array( (  0.5*SPRITE_SIZE_X,0 ) ,dtype=np.int64),
                             #1:np.array( ( -0.5*SPRITE_SIZE_X,0 ),dtype=np.int64 ),
                             #2:np.array( ( 0, 0.5*SPRITE_SIZE_Y ),dtype=np.int64 ),
                             #3:np.array( ( 0,-0.5*SPRITE_SIZE_Y ),dtype=np.int64 )
                           #}
            #print( start_coords.dtype,coord_offset[pc.direction].dtype )
            #start_coords += coord_offset[ pc.direction ]
        #self.pc = pc
        pc.position = start_coords
        self.screen = pygame.display.set_mode( self.map.surface.get_size() )
        self.target_motion = np.array( ( 0,0 ) )
        self.time = 0
        self.ui = 'gameplay'

        self.font = pygame.font.Font( 'LinBiolinum_RB.otf',32 )
        self.bigfont = pygame.font.Font( 'LinBiolinum_RB.otf',72 )

    def processInput( self,events,pressed_keys ):
        for event in events:
            if self.ui == 'gameplay':
                if pressed_keys[ pygame.K_m ]:
                    # Load a menu.
                    self.ui = 'menu'
                if pressed_keys[ pygame.K_SPACE ]:
                    # Pause the game.
                    self.ui = 'paused'

            elif self.ui == 'menu':
                if pressed_keys[ pygame.K_UP ]:
                    self.target_motion += STEP_UP
                if pressed_keys[ pygame.K_DOWN ]:
                    self.target_motion += STEP_DOWN
                if pressed_keys[ pygame.K_RETURN ]:
                    self.menu_surface.set_alpha( 0 )
                    self.ui = 'gameplay'
                if pressed_keys[ pygame.K_m ]:
                    self.menu_surface.set_alpha( 0 )
                    self.ui = 'gameplay'
                    #XXX should this initiate a separate scene?

            elif self.ui == 'paused':
                if pressed_keys[ pygame.K_SPACE ]:
                    self.menu_surface.set_alpha( 0 )
                    self.ui = 'gameplay'

        if self.ui == 'gameplay':
            if pressed_keys[ pygame.K_LEFT ]:
                self.target_motion += STEP_LEFT
                pc.direction = pc.facing[ STEP_LEFT_TUPLE ]
                pc.moved = True
            if pressed_keys[ pygame.K_RIGHT ]:
                self.target_motion += STEP_RIGHT
                pc.direction = pc.facing[ STEP_RIGHT_TUPLE ]
                pc.moved = True
            if pressed_keys[ pygame.K_UP ]:
                self.target_motion += STEP_UP
                pc.direction = pc.facing[ STEP_UP_TUPLE ]
                pc.moved = True
            if pressed_keys[ pygame.K_DOWN ]:
                self.target_motion += STEP_DOWN
                pc.direction = pc.facing[ STEP_DOWN_TUPLE ]
                pc.moved = True

    def update( self ):
        self.map.renderScene()  #TODO:camera view

        if self.ui == 'gameplay':
            # Check for collisions with the mask.
            if pc.moved:
                target = pc.position + self.target_motion
                # is the tile passable?
                target_index_x = int( ( target[ 0 ] + SPRITE_SIZE_X*0.5 ) / SPRITE_SIZE_X )
                target_index_y = int( ( target[ 1 ] + SPRITE_SIZE_Y*0.5 ) / SPRITE_SIZE_Y )
                if not self.map.tiles[ target_index_x,target_index_y ].passable:
                    target = pc.position
                # is the tile occupied by another character? TODO
                # does the tile have an associated portal action?
                if self.map.tiles[ int( ( target[ 0 ] + SPRITE_SIZE_X*0.5 ) / SPRITE_SIZE_X ),int( ( target[ 1 ] + SPRITE_SIZE_Y*0.5 ) / SPRITE_SIZE_Y ) ].active:
                    p = self.map.tiles[ int( ( target[ 0 ] + SPRITE_SIZE_X*0.5 ) / SPRITE_SIZE_X ),int( ( target[ 1 ] + SPRITE_SIZE_Y*0.5 ) / SPRITE_SIZE_Y ) ].portal

                    next_scene = CSScene( map_file='map-%02i.csv'%p[ 'target_map' ],portal_id=p[ 'target_portal' ],start_coords=p[ 'target_portal_coords' ] )
                    target = p[ 'target_portal_coords' ]

                    self.next = next_scene
                # does the tile have a chance of a random encounter? TODO
                pc.position = target

            char_x = pc.position[ 0 ]
            char_y = pc.position[ 1 ]
            pc.update()
            self.map.surface.blit( pc.sprite,( char_x,char_y ) )

            pc.moved = False
            self.target_motion = np.array( ( 0,0 ) )

        elif self.ui == 'menu':
            # draw the menu based on its current state
            self.menu_surface = pygame.Surface( ( 512,512 ), pygame.SRCALPHA, 32 )
            self.menu_surface.convert_alpha()
            self.menu_surface.set_alpha( 128 )
            pygame.draw.rect( self.menu_surface,pygame.color.Color( 128,128,128,192 ),( 272,16,224,480 ) )

            label = self.font.render( "inventory",1,( 192,192,255 ) )
            self.menu_surface.blit( label,( 282,24 ) )
            label = self.font.render( "creatures",1,( 192,192,255 ) )
            self.menu_surface.blit( label,( 282,54 ) )
            label = self.font.render( "settings",1,( 192,192,255 ) )
            self.menu_surface.blit( label,( 282,84 ) )

        elif self.ui == 'paused':
            # draw a pause bar over the scene
            self.menu_surface = pygame.Surface( ( 512,512 ), pygame.SRCALPHA, 32 )
            self.menu_surface.convert_alpha()
            self.menu_surface.set_alpha( 128 )
            pygame.draw.rect( self.menu_surface,pygame.color.Color( 128,128,128,192 ),( 16,192,480,128 ) )

            label = self.bigfont.render( "game paused",1,( 192,192,255 ) )
            self.menu_surface.blit( label,( 46,212 ) )

    def render( self ):
        self.screen.fill( ( 0,0,0 ) )
        self.screen.blit( self.map.surface,( 0,0 ) )
        if not self.ui == 'gameplay':
            self.screen.blit( self.menu_surface,( 0,0 ) )

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
                elif event.key == pygame.K_q:
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
    pygame.init()
    base_scene = CSScene( start_coords=( 100,100 ) )
    game_loop( base_scene )
    pygame.quit()

if __name__ == '__main__':
    main()
