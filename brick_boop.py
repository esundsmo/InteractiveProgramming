import pygame
from pygame.locals import QUIT, KEYDOWN, KEYUP, MOUSEMOTION
import time
from random import choice

#set up the game view
class Player_View(object):
    """brings up the game in a pygame window"""
    def __init__(self, model, size):
        """initialized the view with specific model and screen dimensions"""
        self.model= model
        self.screen= pygame.display.set_mode(size)
    def draw(self):
        """draws the game on the screen"""
        #background color
        self.screen.fill(pygame.Color('black'))
        #draws the walls
        for wall in self.model.wall:
            w=pygame.Rect(wall.left_side_x, wall.top_side_y, wall.width, wall.height)
            pygame.draw.rect(self.screen, pygame.Color('grey'),w)
        for bricks in self.model.brick:
            #creates instance of a brick
            b= pygame.Rect(bricks.left_side_x, 
                            bricks.top_side_y,
                            bricks.width,
                            bricks.height)
            #draws a brick
            pygame.draw.rect(self.screen, pygame.Color('red'), b) 
        #draws a ball
        pygame.draw.circle(self.screen, 
                            pygame.Color('white'),
                            (self.model.ball.left_side_x+int(.5*self.model.ball.width),
                             self.model.ball.top_side_y+int(.5*self.model.ball.height)),
                            int(.5*self.model.ball.width))
        #creates a paddle
        p= pygame.Rect(self.model.paddle.left_side_x, 
                        self.model.paddle.top_side_y,
                        self.model.paddle.width,
                        self.model.paddle.height)
        #draws a paddle
        pygame.draw.rect(self.screen, pygame.Color('white'), p) 
################################
        #destroying all in balls path
        ball_r= pygame.Rect(self.model.ball.left_side_x, self.model.ball.top_side_y,
                        self.model.ball.width, self.model.ball.height)
        for brick in self.model.brick:
            brick_r= pygame.Rect(brick.left_side_x, brick.top_side_y,
                                brick.width, brick.height)
            if ball_r.colliderect(brick_r):
                del(brick)   
###########################
        #refreshes the screen
        pygame.display.update()  

#create the elements of the game
class Rectangle(object):
    """base class for Brick and Paddle"""
    def __init__(self, left_side_x, top_side_y, width, height):
        self.left_side_x= left_side_x
        self.top_side_y= top_side_y
        self.width= width
        self.height= height
class Brick(Rectangle):
    """represents a brick"""
class Wall(Rectangle): 
    """represents a wall boundary"""     
# class Paddle(Rectangle.__init__(left_side_x, top_side_y)):
#     """represent a paddle"""
class Paddle(object):
    """represent a paddle"""
    def __init__(self, left_side_x, top_side_y):
        self.left_side_x= left_side_x
        self.top_side_y= top_side_y
        self.width= 60
        self.height= 10
class Ball(object):
    """represents the ball, which moves wrt time"""
    #also make pygame.Rect
    #the ball will actually be a rectangle for the sake of collisions 
    #(which will be enabled in the model), but only the circle will be 
    #drawn so it will still appear as a ball.
    def __init__(self, left_side_x, top_side_y, width, height):
        """initializing ball as rectangle to enable collisions"""
        self.left_side_x= left_side_x
        self.top_side_y= top_side_y
        self.width= width
        self.height= height
        self.velocity_x = 1         # pixels / frame
        self.velocity_y = -1        # pixels / frame
    def update(self):
        """update the location of the ball"""
        self.left_side_x+= self.velocity_x
        self.top_side_y+= self.velocity_y     

#create the gameplay models
class Classic_Model(object):
    """stores the game state for the classic brick breaker game"""
    def __init__(self, width, height):
        """arranges the elements on the screen"""
        #set up screen
        self.width= width
        self.height= height
        #created dicitonaty to track key states for use in paddle control
        self.key_states= {'left': False, 'right':False}
        #set constants
        self.BRICK_WIDTH= 40
        self.BRICK_HEIGHT= 20
        self.MARGIN= 5
        self.IMPEDING_LINE_OF_DOOM= height/2
        self.BALL_RADIUS= 10
        #creates the walls [left, ceiling, right, floor]
        self.wall= [Wall(0,0,self.MARGIN-1,height), Wall(self.MARGIN,0, 
                        width-(2*self.MARGIN), self.MARGIN-1),
                    Wall(width-self.MARGIN+1, 0, self.MARGIN-1, height), 
                    Wall(self.MARGIN,height-self.MARGIN+1, 
                        width-(2*self.MARGIN), self.MARGIN-1)]
        #create grid of bricks
        self.brick=[]
        for left_side_x in range(self.MARGIN,
                                self.width - self.MARGIN - self.BRICK_WIDTH,
                                self.MARGIN + self.BRICK_WIDTH):
            for top_side_y in range(self.MARGIN, self.IMPEDING_LINE_OF_DOOM, 
                                    self.MARGIN + self.BRICK_HEIGHT):
                self.brick.append(Brick(left_side_x, top_side_y, 
                                self.BRICK_WIDTH, self.BRICK_HEIGHT))
        #set initial location of the ball and paddle
        self.ball = Ball(width/2-self.BALL_RADIUS, height - 40-self.BALL_RADIUS, 
                        self.BALL_RADIUS*2,self.BALL_RADIUS*2)
        self.paddle = Paddle(width/2, height - 15)
    def update(self):
        """ Update the model state """
        #for ball colliding with walls
        if self.ball.left_side_x<= self.MARGIN:
            self.ball.left_side_x = self.MARGIN+1
            self.ball.velocity_x= -self.ball.velocity_x
        if self.ball.left_side_x>= self.width-self.MARGIN-self.ball.width:
            self.ball.left_side_x = self.width-self.MARGIN-self.ball.width-1
            self.ball.velocity_x= -self.ball.velocity_x
        if self.ball.top_side_y<= self.MARGIN:
            self.ball.top_side_y = self.MARGIN+1
            self.ball.velocity_y= -self.ball.velocity_y
        if self.ball.top_side_y>= self.height-self.MARGIN-self.ball.height:
            self.ball.top_side_y = self.height-self.MARGIN-self.ball.height-1
            self.ball.velocity_y= -self.ball.velocity_y

        #for the movement of the ball
        self.ball.update()
        #for the movement of the paddle
        if self.key_states['left']:
            self.paddle.left_side_x -= 1
        if self.key_states['right']:
            self.paddle.left_side_x += 1 
        #for paddle collision with wall
        if self.paddle.left_side_x<= self.MARGIN:
            self.paddle.left_side_x = self.MARGIN+1
        if self.paddle.left_side_x>= self.width-self.MARGIN-self.paddle.width:
            self.paddle.left_side_x = self.width-self.MARGIN-self.paddle.width-1
        

# class Magic_Balls(object):
#   """multiple balls in play, each has differernt effect"""
#   pass
# class Moving_Wall(object):
#   """the wall moves close to the paddle with time.  If any of the bricks 
#   pass over the line of the paddle, the game is over."""
#   pass
# class Limitless(object):
#   """Unlimited time.  A new row of bricks is generated at the top of the 
#   screen every 30 seconds."""
#     pass  

#set up control method
class Controller(object):
    """established control with a (mouse, keyboard, etc.)"""
    def __init__(self, model):
        """"looks for () movements and responds"""
        self.model=model
    def handle_event(self, event):
        """uses input from left and right arrow keys to move paddle laterally"""
        #set up for recognition of multiple keydown events
        pygame.key.set_repeat(1,10)
        #updates the dictionary from the model each time a key is pressed
        if event.type == KEYDOWN:
            if event.key== pygame.K_LEFT:
                self.model.key_states['left']= True
            elif event.key== pygame.K_RIGHT:
                self.model.key_states['right']= True
        elif event.type == KEYUP:
            if event.key== pygame.K_LEFT:
                self.model.key_states['left']= False
            elif event.key== pygame.K_RIGHT:
                self.model.key_states['right']= False
        else:
            return

if __name__=='__main__':
    """NEEDS WORK"""
    pygame.init()
    size= (640,480)

    model= Classic_Model(size[0], size[1])
    view= Player_View(model, size)
    controller= Controller(model)
    running= True
    #when a key is pressed, changes key_states dictionary, PlayerView updates
    while running:
        for event in pygame.event.get():
            if event.type== QUIT:
                running= False
            else:
                controller.handle_event(event)
        model.update()
        view.draw()
        time.sleep(.001)            