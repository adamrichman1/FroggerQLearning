import pygame
from pygame.constants import K_w,K_d,K_s,K_a,K_F15
from constants import *
import os,sys,time,random
from sys import stderr as err

class BonusRandom():
    def __init__(self, rate, minDelay):
        self.rate = rate
        self.minDelay = minDelay
        self.prev = 0.0

    def get_chance(self, clk):
        if not self.minDelay == 0:
            now=time.time()
            if now-self.prev < self.minDelay:
                return False

        b = random.random()<0.001*clk/self.rate
        if not self.minDelay==0 and b:
            self.previous = now

        return b        

class Home(pygame.sprite.Sprite):
    def __init__(self, init_pos, image_assets):
        pygame.sprite.Sprite.__init__(self)

        self.image_assets = image_assets
        self.init(init_pos)

    def init(self, init_pos):
        self.image = self.image_assets["blank"]
        self.rect = self.image.get_rect()
        self._x = init_pos[0]
        self._y = init_pos[1]
        self.rect.left = self._x+kXOffset
        self.rect.top = self._y
        self.frogged = False
        
        self.flied = False
        self.croced = False
        self.duration = 0

    def get_rect(self):
        return self.rect.move(-kXOffset,0)
    
    def homeFrog(self):
        self.frogged = True
        self.flied = False
        self.croced = False
        self.image = self.image_assets["frog"]

    def setCroc(self):
        if self.frogged or self.flied or self.croced:
            # can't put a croc here, return
            return

        # can put a croc here, place image
        self.croced = True
        self.image = self.image_assets["croc"]
        self.duration = 0
        # update will take care of getting rid of croc

    def setFly(self):
        if self.frogged or self.flied or self.croced:
            return # can't put fly here, leave

        self.flied = True
        self.image = self.image_assets["fly"]
        self.duration = 0

    def update(self, dt):
        if self.croced or self.flied:
            # need to actually do some work
            self.duration += dt
            if self.duration > kHomeBonusDuration:
                # time to remove the bonus item
                self.croced = False
                self.flied = False # doesn't matter, both are gone
                # set image to blank
                self.image = self.image_assets["blank"]

    def draw(self, screen):
        screen.blit(self.image, (self.rect.left,self.rect.top))

class BaseSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=None
        self.rect=pygame.Rect(0,0,0,0)
        self._x=0.0
        self._y=0.0
        self.speed=(0.0,0.0)

    def set_image(self, image):
        self.image=image
        self.rect=image.get_rect()
        self.rect.left=int(self._x+kXOffset+0.5)
        self.rect.top=int(self._y+0.5)

    def set_pos(self, pos):
        self._x=pos[0]
        self._y=pos[1]
        self.rect.left=int(self._x+kXOffset+0.5)
        self.rect.top=int(self._y+0.5)

    def get_pos(self):
        return (self._x,self._y)

    def get_rect(self):
        return self.rect.move(-kXOffset,0)

    def set_speed(self, spd):
        self.speed=spd

    def get_speed(self):
        return self.speed

    def update(self):
        raise NotImplementedError("Override update method")

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class ScrollingSprite(BaseSprite):
    def __init__(self, init_pos, init_speed, image):
        BaseSprite.__init__(self)
        self.set_pos(init_pos)
        self.set_image(image)
        self.set_speed(init_speed)

    def update(self,dt):
        self._x += float(self.speed[0]*dt)
        self._y += float(self.speed[1]*dt)
        self.rect.left=int(self._x+kXOffset+0.5)
        self.rect.top=int(self._y+0.5)

        if self.speed[0] < 0 and self._x+self.rect.width < 0.0:
            self._x = self._x+kPlayWidth+self.rect.width
            self.rect.left=int(self._x+kXOffset+0.5)
            self.rect.top=int(self._y+0.5)

        if self.speed[0] > 0 and self._x > kPlayWidth:
            self._x = self._x-kPlayWidth-self.rect.width
            self.rect.left=int(self._x+kXOffset+0.5)
            self.rect.top=int(self._y+0.5)

class Car(ScrollingSprite):
    def __init__(self, init_pos, init_speed, image):
        ScrollingSprite.__init__(self,init_pos,init_speed,image)

class Log(ScrollingSprite):
    def __init__(self,init_pos, init_speed, image):
        ScrollingSprite.__init__(self,init_pos,init_speed,image)

class Turtle(ScrollingSprite):
    def __init__(self,init_pos,init_speed,image,image_assets,canDive=False,animRate=500):
        ScrollingSprite.__init__(self,init_pos,init_speed,image)
        self.image_assets = image_assets
        self.dive_seq=0
        self.canDive=canDive
        self.animateIndex=0
        self.lastAnim=0
        self.animRate=animRate
        self.image_maps = {0:"A",1:"B",2:"C",3:"D",4:"E",5:"D",6:"C",7:"B",8:"A"}
        self.disappeared = False

    def update(self, dt):
        ScrollingSprite.update(self,dt)
        if self.canDive:
            self.lastAnim += dt
            if self.lastAnim >= self.animRate:
                # update image to display
                self.animateIndex = (self.animateIndex+1) % 8
                self.set_image(self.image_assets[self.image_maps[self.animateIndex]])
                
                # check if frog should die
                if self.animateIndex == 4:
                    # no frog, frog needs to check this
                    self.disappeared = True
                else:
                    self.disappeared = False
                # reset lastAnim
                self.lastAnim -= self.animRate
                
                

class Frog(BaseSprite):
    def __init__(self, init_pos, image):
        BaseSprite.__init__(self)
        self.set_pos(init_pos)
        self.set_image(image)

        self.orig_image = image
        
        self.init()

    def init(self):
        self.toMove=False
        self.moveV = (0.0,0.0)
        self.direction=0
        self.attached = False
        self.attachedObj = None

    def set_move(self, vector):
        self.toMove = True
        self.moveV = vector

        # if frog wants to go off the screen, don't allow move
        if self._x+(self.rect.width/2)+(kPlayCellSize[0]*self.moveV[0])<0.0 or self._x+(self.rect.width/2)+(kPlayCellSize[0]*self.moveV[0])>kPlayWidth:
            self.toMove = False
            self.moveV = (0.0,0.0)

        if self._y+(self.rect.height/2)+(kPlayCellSize[1]*self.moveV[1])<0.0 or self._y+(self.rect.height/2)+(kPlayCellSize[1]*self.moveV[1])>kPlayHeight:
            self.toMove = False
            self.moveV = (0.0,0.0)

        # check if frog goes from attached to not attached
        if self._y+(kPlayCellSize[1]*self.moveV[1]) > kPlayYRiverLimit and self.attached:
            self.attached = False
            self.attachedObj = None

    def update(self, dt):
        self.game_tick = 1
        
        if self.toMove:
            self.set_pos((self._x+(kPlayCellSize[0]*self.moveV[0]),self._y+(kPlayCellSize[1]*self.moveV[1])))
            self.toMove = False
            if self.moveV[1] > 0.0: self.direction = 180
            else: self.direction = 0
            if self.moveV[0] < 0.0: self.direction = 90
            if self.moveV[0] > 0.0: self.direction = 270
            self.update_image()

        if self.attached and self.attachedObj != None:
            self._x += float(self.attachedObj.speed[0]*dt)
            self._y += float(self.attachedObj.speed[1]*dt)
            self.rect.left=int(self._x+kXOffset+0.5)
            self.rect.top=int(self._y+0.5)

    def attachDisappeared(self):
        (x,y)=self.get_pos()
        dx=0.5*self.rect.width
        return self.attached and ((x < -dx) or (x+self.rect.width > kPlayWidth+dx))

    def update_image(self):
        self.image = pygame.transform.rotate(self.orig_image, self.direction)

    def attachTo(self, obj):
        if obj != None:
            self.attached = True
            self.attachedObj = obj
        
            
            
