#!/usr/bin/env python3
#by Daniel Hyland,7.2.2021
from time import sleep
import pygame
import sys
import os
import random
import json

'''
colours
'''
BLUE  = (25,25,200)
BLACK = (0,0,0 )
WHITE = (254,254,254)
ALPHA =(0,0,0)
NAVY = (0,0,153)
CYAN = (0,204,204)
'''
global variables
'''
worldx=1000
worldy=300

gap=275
oby=25
obx=25
tx=64
ty=64
fps=20
ani=4

'''
objects
'''

class Platform(pygame.sprite.Sprite):    
    def __init__(self,xloc,yloc,imgw,imgh,img,copy=False,ptype='plat'):
        self.ptype=ptype
        pygame.sprite.Sprite.__init__(self)
        self.imgfile=img
        self.image = pygame.image.load(os.path.join('images',img)).convert()
        self.image= pygame.transform.scale(self.image,(imgw,imgh))
#        self.image.convert_alpha()
#        self.image.set_colorkey(ALPHA)
        self.rect = self.image.get_rect()
        self.rect.y = yloc
        self.rect.x = xloc
        self.imgw=imgw
        self.imgh=imgh
 
 
class Obstacle(pygame.sprite.Sprite):
 
    '''
    Spawn an obstacle
    '''

    def __init__(self,x,y,obtype='spike',speed=10):
        pygame.sprite.Sprite.__init__(self)
#        self.movex = 0
#        self.movey = 0
        self.img=1
        
        self.speed=speed

        directory='Tiles'
        filenames={'spike':('spikes.png',obx,oby),'lowfence':('lowfence.png',obx,oby),'bigspike':('spikes.png',int(obx*1.1),int(oby*1.3))}
     
        self.imgname=filenames[obtype][0]
        self.px=filenames[obtype][1]
        self.py=filenames[obtype][2]
        
     
        img = pygame.image.load(os.path.join('images',directory,self.imgname))
        img = pygame.transform.scale(img,(self.px,self.py))
        img.convert_alpha()     # optimise alpha
        img.set_colorkey(ALPHA) # set alpha
        self.image = img
        self.rect  = self.image.get_rect()
        self.rect.x=x
        self.rect.y=y-self.py
        
    def update(self):
        self.rect.x-=self.speed
        if self.rect.x<0:
            self.rect.x=worldx+gap+random.randint(int(gap/2),gap)
 
class Player(pygame.sprite.Sprite):
    
    '''
    Spawn a player
    '''
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0
        self.health=1
#        self.score=0
        self.collide_delta = 0
        self.jump_delta = 6
        self.img=1
        self.px=64
        self.py=55
        self.ducking=False

        directory='5x'
        filenames=['run_0.png','run_1.png','run_2.png','run_3.png','run_4.png','run_5.png','jump_1.png','jump_2.png','jump_3.png','jump_0.png','jump_3.png','jump_2.png']
        self.images = []
        for f in filenames:
            img = pygame.image.load(os.path.join('images',directory,f))
            img = pygame.transform.scale(img,(self.px,self.py))
            #img.convert_alpha()     # optimise alpha
            #img.set_colorkey(ALPHA) # set alpha
            self.images.append(img)
            
        
        self.image = self.images[self.img]
        self.rect  = self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
     
  #  def control(self,x,y):
   #     self.movex += x
    #    self.movey += y
     
    def update(self,game_components):
        

#        self.rect  = self.image.get_rect()

#update position by current movement
        self.rect.x +=self.movex
        self.rect.y +=self.movey
        
        obstacle_hit_list=pygame.sprite.spritecollide(self, game_components['obstacles'],False)
        for ob in obstacle_hit_list:
            self.health-=1
        
        ground_list=game_components['ground']
        ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False)
        for g in ground_hit_list:
            self.movey = 0
            self.rect.y =worldy-ty-self.py+10
            if self.collide_delta>0:
                self.img=0
            self.collide_delta = 0 # stop jumping
            
        #change image
        self.img+=1
        if self.img==6:
            self.img=0
        if self.img==12:
            self.img=7 
        self.image = self.images[self.img]
        if self.ducking:
            self.image=pygame.transform.scale(self.image,(self.px,30))
            self.rect.y+=25
            

        
        

#checking whether to jump
        if self.collide_delta < 6 and self.jump_delta < 6:
            self.jump_delta = 6*2
            self.movey -= 25  # how high to jump
            self.collide_delta += 6
            self.jump_delta    += 6

    def gravity(self):
        self.movey +=3.0
        if self.rect.y > worldy and self.movey >= 0:
            self.movey = 0
            self.rect.y = worldy-2*ty


    def jump(self):
        self.jump_delta = 0
        self.img=7
        
            
        
class PlatformGame():
    
    
    def __init__(self):
        '''
        setup
        '''
        self.clock = pygame.time.Clock()
        pygame.init()
        self.world    = pygame.display.set_mode([worldx,worldy])
        self.backdrop = pygame.image.load(os.path.join('images','sky1.png')).convert()  #uncomment 3 lines for picture background
        self.backdrop = pygame.transform.scale(self.backdrop,(worldx,worldy))
        self.backdropbox = self.world.get_rect()
        self.groundlist=self.ground()
        
        self.player = Player(50,worldy-ty-80)   # spawn player
   
        self.player_list = pygame.sprite.Group()
        self.player_list.add(self.player)
        
        
        self.obstacle_list=pygame.sprite.Group()
            
        spike=Obstacle(worldx-gap,worldy-ty,obtype='spike')
        self.obstacle_list.add(spike)
        spike=Obstacle(worldx,worldy-ty,obtype='lowfence')
        self.obstacle_list.add(spike)
        spike=Obstacle(worldx+gap,worldy-ty,obtype='bigspike',speed=10)
        self.obstacle_list.add(spike)
        spike=Obstacle(worldx+gap+gap,worldy-ty,obtype='bigspike',speed=10)
        self.obstacle_list.add(spike)
        spike=Obstacle(worldx+gap+gap+gap,worldy-ty,obtype='lowfence',speed=10)
        self.obstacle_list.add(spike)
        
        
        self.game_components={'ground':self.groundlist,'player':self.player_list,'obstacles':self.obstacle_list}
     
     
    def ground(self):
        ground_list = pygame.sprite.Group()
        x=0
        y=worldy-ty
        
        while x <worldx:
            ground = Platform(x,y,tx,ty,'Tiles/grass.png')
            ground_list.add(ground)
            x+=tx
            
        

        return ground_list
     
    def main(self):
        
        main = True
   
        '''
        main loop
        '''
        score=0.0
        score_display=''
        dragging = False
        pygame.event.clear()  #clear event queue
        while main == True:
            if self.player.health<1:
                main = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #print ("Game over ")
                    #pygame.quit()
                    #sys.exit()
                    main = False
                if event.type == pygame.KEYDOWN:
                    if event.key == ord('q'):
                        main = False
                    if event.key == pygame.K_UP or event.key == ord('w') or event.key ==  ord(' '):
                        self.player.jump()
                    
                    if event.key == pygame.K_DOWN:
                        self.player.ducking=True
                        
                if event.type==pygame.KEYUP:
                    if event.key ==pygame.K_DOWN:
                        self.player.ducking=False
                        
            self.world.blit(self.backdrop,self.backdropbox) #refresh backdrop
            largeFont=pygame.font.SysFont('comicsans',27)
            text= largeFont.render('Score: ' +score_display,1,WHITE)
            self.world.blit(text,(worldx-100,20))         
            self.groundlist.draw(self.world)
            self.player.update(self.game_components)
            self.player.gravity()
            self.player_list.draw(self.world)
            
            for ob in self.obstacle_list:
                ob.update()
            self.obstacle_list.draw(self.world)
            
            if main == False:
                largerFont=pygame.font.SysFont('comicsans',50)
                text= largerFont.render('GAME OVER!',1,WHITE)
                self.world.blit(text,(worldx/3,worldy/3))
              
            pygame.display.flip()
            self.clock.tick(fps)
            if main == False:
                sleep(3)
            score+=1/fps
            score_display=str(int(round(score,0)))
        return score_display
 
 
mygame=PlatformGame()
score=mygame.main()
print ("Game over ")
print('your score is '+score)
pygame.quit()
sys.exit()
                     
                        