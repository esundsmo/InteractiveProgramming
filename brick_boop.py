"""
Brick Break style game using pygame library.  Game window opens and game begins when script is ran.  
The player uses the left and right arrow keys to move the paddle and bounce the ball.  
When the ball hits a brick, that brick disappears and the velocity of the ball changes 
approptiately.  If the ball touches the bottom of the screen, the game is over.  
During gameplay, the player's score is shown in the bottom left  corner.  When the 
game is over, the player's rank (based on their score) is displayed.


@Authors: Rebecca Patterson, Elizabeth Sundsmo   3/9/2016
"""


import pygame
import pygame.mixer
from pygame.locals import QUIT, KEYDOWN, KEYUP, MOUSEMOTION
import time
from random import choice
import math

#set up the game view
class Player_View(object):
    """brings up the game in a pygame window"""
    def __init__(self, model, size):
        """initialize the view with specific model and screen dimensions"""
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
        #creates an instane of a brick rect. and draws it for all bricks
        for bricks in self.model.brick:
            b= pygame.Rect(bricks.left_side_x, 
                            bricks.top_side_y,
                            bricks.width,
                            bricks.height)
            pygame.draw.rect(self.screen, pygame.Color('red'), b) 
        #draws the ball-- note the the ball is actually a rect, only being drawn as
        #a circle
        pygame.draw.circle(self.screen, 
                            pygame.Color('white'),
                            (int(self.model.ball.left_side_x+.5*self.model.ball.width),
                             int(self.model.ball.top_side_y+.5*self.model.ball.height)),
                            int(.5*self.model.ball.width))
        #creates and draws the paddle rect.
        p= pygame.Rect(self.model.paddle.left_side_x, 
                        self.model.paddle.top_side_y,
                        self.model.paddle.width,
                        self.model.paddle.height)
        pygame.draw.rect(self.screen, pygame.Color('white'), p) 

        #set up the score and end-game displays
        #font sizes
        font_size_small= 20
        font_size_big= 30
        #update score counter
        score_counter = pygame.font.SysFont("monospace", font_size_small)
        score_str = score_counter.render("SCORE: {}".format(self.model.score), 1, pygame.Color('white'))
        self.screen.blit(score_str, (self.model.MARGIN+5, self.model.height-self.model.MARGIN-self.model.BALL_RADIUS*2- font_size_small))  
        #say rank
        player_rank= pygame.font.SysFont("monospace", font_size_big)
        rank_str= player_rank.render(str(self.model.rank), 1, pygame.Color('white'))
        self.screen.blit(rank_str, (self.model.MARGIN+5, 360))
        #say when game is over
        game_status= pygame.font.SysFont("monospace", font_size_big)
        status_str= game_status.render("{}".format(self.model.status), 1, pygame.Color('white'))
        self.screen.blit(status_str, (self.model.MARGIN+5, 300))
        
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

class Paddle(object):
    """represent a paddle"""
    def __init__(self, left_side_x, top_side_y):
        self.left_side_x= left_side_x
        self.top_side_y= top_side_y
        self.width= 150
        self.height= 9

class Ball(object):
    """represents the ball, which moves wrt time"""
    #the ball will actually be a rectangle for the sake of collisions 
    #(which will be enabled in the model), but only a circle will be 
    #drawn in PlayerView, so it will still appear as a ball.
    def __init__(self, left_side_x, top_side_y, width, height):
        """initializing ball as rectangle to enable collisions"""
        self.left_side_x= left_side_x
        self.top_side_y= top_side_y
        self.width= width
        self.height= height
        self.velocity_x = 0         # pixels / frame
        self.velocity_y = 1         # pixels / frame
    def update(self):
        """update the location of the ball based on the current x and y velocity"""
        self.left_side_x+= self.velocity_x
        self.top_side_y+= self.velocity_y     

#set up control method
class Controller(object):
    """established control with a keyboard"""
    def __init__(self, model):
        """sets the model that the controller will be used for"""
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

#create the gameplay model
class Classic_Model(object):
    """stores the game state for the classic brick breaker game"""
    def __init__(self, width, height):
        """arranges the elements on the screen"""
        #set up screen
        self.width= width
        self.height= height
        #starting score count at 0
        self.score= 0
        self.win_flag = 0
        #sets status and rank to be blank.  will update when ball stops moving
        self.rank= ""
        self.status= ""
        #created dicitonaty to track key states for use in paddle control
        self.key_states= {'left': False, 'right':False}

        #set constants
        self.BRICK_WIDTH= 40
        self.BRICK_HEIGHT= 20
        self.MARGIN= 5
        self.IMPEDING_LINE_OF_DOOM= height/2
        self.BALL_RADIUS= 10

        #creates the walls [left, ceiling, right, floor]
        self.wall= [Wall(0,0,self.MARGIN,height), Wall(self.MARGIN,0, 
                        width-(2*self.MARGIN), self.MARGIN),
                    Wall(width-self.MARGIN, 0, self.MARGIN, height), 
                    Wall(self.MARGIN,height-self.MARGIN, 
                        width-(2*self.MARGIN), self.MARGIN)]
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
        self.ball = Ball(width/2-self.BALL_RADIUS, height - 160-self.BALL_RADIUS, 
                        self.BALL_RADIUS*2,self.BALL_RADIUS*2)
        self.paddle = Paddle(width/2, height - 15) 

    def update(self):
        """ Update the model state """
        #make ball and paddle a rectangle object for collisions
        ball_r= pygame.Rect(self.ball.left_side_x, self.ball.top_side_y,
                            self.ball.width, self.ball.height)
        paddle_r= pygame.Rect(self.paddle.left_side_x, self.paddle.top_side_y,
                            self.paddle.width, self.paddle.height)
        
        #for ball colliding with walls
        #left side
        if self.ball.left_side_x<= self.MARGIN:
            wall_sound.play()
            self.ball.left_side_x = self.MARGIN+1
            self.ball.velocity_x= -self.ball.velocity_x
        #right side    
        if self.ball.left_side_x>= self.width-self.MARGIN-self.ball.width:
            wall_sound.play()
            self.ball.left_side_x = self.width-self.MARGIN-self.ball.width-1
            self.ball.velocity_x= -self.ball.velocity_x
        #top
        if self.ball.top_side_y<= self.MARGIN:
            wall_sound.play()
            self.ball.top_side_y = self.MARGIN+1
            self.ball.velocity_y= -self.ball.velocity_y
        #bottom-- stops ball movement and ends the game.
        if self.ball.top_side_y>= self.height-self.MARGIN-self.ball.height:
            end_sound.play()
            self.ball.top_side_y = self.height-self.MARGIN-self.ball.height-1
            self.ball.velocity_x=0
            self.ball.velocity_y=0

        #for ball collision with paddle---  when the ball rect. collides with the
        #paddle rect., the ball will bounce off and an angle.  The angle depends on
        #which of the 6 "segments" of the paddle that it hits.
        if ball_r.colliderect(paddle_r):
            paddle_sound.play()
            #segment 1
            if self.paddle.left_side_x<= self.ball.left_side_x+.5*self.ball.width<= self.paddle.left_side_x+ (1/6.0)*self.paddle.width:
                self.ball.top_side_y= self.ball.top_side_y-1
                theta=(30.0)*(math.pi/180)
                new_vel_x= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.sin(theta)
                new_vel_y= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.cos(theta)
                self.ball.velocity_x= -(new_vel_x)
                self.ball.velocity_y= -(new_vel_y)
            #segment 2
            elif self.paddle.left_side_x+ (1/6.0)*self.paddle.width< self.ball.left_side_x+.5*self.ball.width<= self.paddle.left_side_x+ (2/6.0)*self.paddle.width:
                self.ball.top_side_y= self.ball.top_side_y-1
                theta=(45.0)*(math.pi/180)
                new_vel_x= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.sin(theta)
                new_vel_y= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.cos(theta)
                self.ball.velocity_x= -(new_vel_x)
                self.ball.velocity_y= -(new_vel_y) 
            #segment 3
            elif self.paddle.left_side_x+ (2/6.0)*self.paddle.width< self.ball.left_side_x+.5*self.ball.width<= self.paddle.left_side_x+ (3/6.0)*self.paddle.width:
                self.ball.top_side_y= self.ball.top_side_y-1
                theta=(60.0)*(math.pi/180)
                new_vel_x= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.sin(theta)
                new_vel_y= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.cos(theta)
                self.ball.velocity_x= -(new_vel_x)
                self.ball.velocity_y= -(new_vel_y)      
            #segment 4
            elif self.paddle.left_side_x+ (3/6.0)*self.paddle.width< self.ball.left_side_x+.5*self.ball.width<= self.paddle.left_side_x+ (4/6.0)*self.paddle.width:
                self.ball.top_side_y= self.ball.top_side_y-1
                theta=(60.0)*(math.pi/180)
                new_vel_x= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.sin(theta)
                new_vel_y= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.cos(theta)
                self.ball.velocity_x= (new_vel_x)
                self.ball.velocity_y= -(new_vel_y) 
            #segment 5
            elif self.paddle.left_side_x+ (4/6.0)*self.paddle.width< self.ball.left_side_x+.5*self.ball.width<= self.paddle.left_side_x+ (5/6.0)*self.paddle.width:
                self.ball.top_side_y= self.ball.top_side_y-1
                theta=(45.0)*(math.pi/180)
                new_vel_x= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.sin(theta)
                new_vel_y= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.cos(theta)
                self.ball.velocity_x= (new_vel_x)
                self.ball.velocity_y= -(new_vel_y)  
            #segment 6
            elif self.paddle.left_side_x+ (5/6.0)*self.paddle.width< self.ball.left_side_x+.5*self.ball.width<= self.paddle.left_side_x+ self.paddle.width:
                self.ball.top_side_y= self.ball.top_side_y-1
                theta=(30.0)*(math.pi/180)
                new_vel_x= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.sin(theta)
                new_vel_y= math.sqrt(self.ball.velocity_y**2 + self.ball.velocity_x**2)*math.cos(theta)
                self.ball.velocity_x= (new_vel_x)
                self.ball.velocity_y= -(new_vel_y)
        
        #for "destroying" the bricks in the ball's path. checks for collision with 
        #each brick rect. object.  if they have collided, the ball's velocity will
        #change accordingly and the brick will be relocated off the screen
        for brick in self.brick:
            brick_r= pygame.Rect(brick.left_side_x, brick.top_side_y,
                                brick.width, brick.height)
            if ball_r.colliderect(brick_r):
                brick_sound.play()
                #increase score for each brick hit
                self.score+=1
                #find center of ball
                ball_x= self.ball.left_side_x+ .5*self.ball.width
                ball_y= self.ball.top_side_y+ .5*self.ball.height
                #find sides of brick
                brick_left= brick.left_side_x
                brick_right= brick.left_side_x+ brick.width
                brick_top= brick.top_side_y
                brick_bottom= brick.top_side_y+ brick.height
                #for vertical collisions
                if brick_left<= ball_x<= brick_right:
                        self.ball.velocity_y= -self.ball.velocity_y
                #for horizontal collisions        
                elif brick_top<= ball_y<= brick_bottom:
                        self.ball.velocity_x= -self.ball.velocity_x     
                #move broken brick off screen        
                brick.left_side_x=0-self.BRICK_WIDTH
                brick.top_side_y= 0-self.BRICK_HEIGHT

        #for the movement of the ball
        self.ball.update()

        #for the movement of the paddle
        if self.key_states['left']:
            self.paddle.left_side_x -= 1
        if self.key_states['right']:
            self.paddle.left_side_x += 1
        #for paddle collision with wall--- paddle should "stop" moving when it hits wall
        if self.paddle.left_side_x<= self.MARGIN:
            self.paddle.left_side_x = self.MARGIN+1
        if self.paddle.left_side_x>= self.width-self.MARGIN-self.paddle.width:
            self.paddle.left_side_x = self.width-self.MARGIN-self.paddle.width-1

        #if all bricks are hit, ball stops moving, win sound plays
        score_percentage= (float(self.score)/float(len(self.brick)))*100.0
        if score_percentage==100:
            self.win_flag+=1
            if self.win_flag==1:
                win_sound.play()
            self.ball.velocity_x=0
            self.ball.velocity_y=0
        #checks if ball is in play, updates status and sets rank
        if self.ball.velocity_x==0 and self.ball.velocity_y==0:
            self.status= "GAME OVER"
            if self.score== 0:
                self.rank= "RANK: NEWTON'S APPLE"
            elif 0<score_percentage<=20:
                self.rank= "RANK: TWO YEAR OLD TERROR"
            elif 20<score_percentage<=40:
                self.rank= "RANK: KRONK"             
            elif 40<score_percentage<=60:
                self.rank= "RANK: MILEY'S WRECKING BALL"
            elif 60<score_percentage<=80:
                self.rank= "RANK: HULK"
            elif 80<score_percentage<100:
                self.rank= "RANK: JACK-JACK"
            elif score_percentage== 100:
                self.rank="RANK: YE OLDE SMASHER OF BRICKS"    

if __name__=='__main__':
    """When the code is ran, the game sets up as specified"""
    # setup mixer to avoid sound lag
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=4096)
    #initialize pygame
    pygame.init()
    #select screen size
    size= (640,480) 
    #loads sounds.  includes a warning if soundfiles cannot be located
    try:
        wall_sound = pygame.mixer.Sound("Blop.wav")
        paddle_sound = pygame.mixer.Sound("Blop.wav")
        brick_sound = pygame.mixer.Sound("Pop_Cork.wav")
        end_sound = pygame.mixer.Sound("Sad_Trombone.wav")
        win_sound = pygame.mixer.Sound("TaDa.wav")
    except:
        raise UserWarning, "Could not load or play soundfiles in specified folder. Check naming convention and folder location!"
 
    model= Classic_Model(size[0], size[1])
    view= Player_View(model, size)
    controller= Controller(model)
    running= True
    #checks for user input.  if the window is not closed by the user, it will check for arrow keys being pressed.
    #when a key is pressed, changes key_states dictionary, PlayerView updates paddle location accordingly.
    #the model is updated, and the view is redrawn with the specified pause time in between.
    while running:
        for event in pygame.event.get():
            if event.type== QUIT:
                running= False 
            else:
                controller.handle_event(event)
        model.update()
        view.draw()
        time.sleep(.001)            