#Author: https://github.com/yt-koike/
#Title: Mine Sweeper 10000

import sys
import copy
import random
from pygame_lib import PygameBasicTools

SPACE = 0
LANDMINE = 1
FLAG = 2
CLOSED = 3

class Map:
    def __init__(self,width,height):
        self.w = width
        self.h = height
        self.floormap=[[0 for j in range(width)] for i in range(height)]

    def get_size(self):
        return (self.w,self.h)

    def get_block(self,i,j):
        return self.floormap[i][j]

    def get_list(self):
        return self.floormap

    def put_block(self,i,j,block_type):
        self.floormap[i][j] = block_type

    def fill_block(self,block_type):
        self.floormap=[[block_type for j in range(self.w)]
                       for i in range(self.h)]

    def is_valid(self,i,j):
        return 0<=i<self.h and 0<=j<self.w

    def neighbors(self,i,j):
        x = [(i-1, j-1), (i, j-1), (i+1, j-1),
             (i-1, j  ),           (i+1, j  ),
             (i-1, j+1), (i, j+1), (i+1, j+1)]
        return [v for v in x if self.is_valid(v[0],v[1])]


class View2D:
    def __init__(self,pbt,game):
        self.pbt = pbt
        self.game = game
        self.origin_x=100
        self.origin_y=100
        self.block_w=30
        self.block_h=30

    def draw(self):
        self.pbt.clear()
        origin_x = self.origin_x
        origin_y = self.origin_y
        block_w = self.block_w
        block_h = self.block_h
        sc_w, sc_h = self.pbt.get_screen_size()
        map_w,map_h = self.game.floormap.get_size()
        for i in range(map_h):
            for j in range(map_w):
                x=block_w*j+origin_x
                y=block_h*i+origin_y
                if (x < -block_w or x > sc_w+block_w
                    or y < -block_h or y > sc_h+block_h):
                    continue
                block = self.game.floormap.get_block(i,j)
                cs={SPACE:"white", LANDMINE:"red", FLAG:"blue",CLOSED:"grey"}
                self.pbt.draw_rect(x,y,
                                   x+self.block_w,y+self.block_h,
                                   cs[block])
                if block == SPACE:
                    self.pbt.draw_text(x+self.block_w/2,y+self.block_h/2,
                                       str(self.game.countmap.get_block(i,j)),
                                       anchor="CENTER")
        self.pbt.update()

    def get_index_by_xy(self,x,y):
        x -= self.origin_x
        y -= self.origin_y
        idx = (y//self.block_h,x//self.block_w)
        if self.game.floormap.is_valid(idx[0],idx[1]):
            return idx
        else:
            return (-1,-1)

    def move_camera(self,di,dj):
        self.origin_x -= dj*self.block_w
        self.origin_y -= di*self.block_h

class Game:
    def __init__(self,pbt):
        self.pbt = pbt
        self.pbt.set_title("sub")
        mapsizes = {"10x10":(10,10),"20x20":(20,20),"30x30":(30,30),"50x50":(50,50),"100x100":(100,100)}
        mapsize = self.user_select("Mapsize = ",list(mapsizes.keys()))
        width,height = mapsizes[mapsize]
        self.floormap = Map(width,height)
        self.floormap.fill_block(CLOSED)
        self.minemap = Map(width,height)
        self.countmap = Map(width,height)
        levels = {"easy":0.05,"normal":0.08,"hard":0.12,"veryhard":0.2}
        level = self.user_select("Level = ",list(levels.keys()))
        self.mine_num = int(width * height * levels[level])
        self.put_mines(self.mine_num)
        self.unopened = width * height
        for i in range(height):
            for j in range(width):
                self.countmap.put_block(i,j,self.count_mines(i,j))
        self.view2d = View2D(pbt,self)
        self.view2d.draw()
        self.show_info()
        self.mainloop()

    def show_info(self):
        self.pbt.draw_rect(0,0,250,50,"white")
        self.pbt.draw_text(10,5,
                           f"Mine = {self.mine_num}/{self.unopened}",
                           "black")
        self.pbt.draw_text(10,25,
                           f"q=Quit",
                           "black")
        self.pbt.update()

    def draw(self):
        self.view2d.draw()
        self.show_info()

    def mainloop(self):
        while True:
            keys,mouse_buttons = self.pbt.keys_and_mouse()
            if "q" in keys:
                break
            if "up" in keys:
                self.view2d.move_camera(-1,0)
                self.draw()
            elif "down" in keys:
                self.view2d.move_camera(1,0)
                self.draw()
            elif "left" in keys:
                self.view2d.move_camera(0,-1)
                self.draw()
            elif "right" in keys:
                self.view2d.move_camera(0,1)
                self.draw()
            if 1 in mouse_buttons: #left click
                x,y = self.pbt.mouse_pos()
                i,j = self.view2d.get_index_by_xy(x,y)
                if i==-1:
                    #print("invalid click point")
                    continue
                self.open(i,j)
                self.draw()
                self.check_goal()
            elif 3 in mouse_buttons: #right click
                x,y = self.pbt.mouse_pos()
                i,j = self.view2d.get_index_by_xy(x,y)
                if i==-1:
                    #print("invalid click point")
                    continue
                if self.floormap.get_block(i,j) == CLOSED:
                    self.floormap.put_block(i,j,FLAG)
                    self.draw()
                elif self.floormap.get_block(i,j) == FLAG:
                    self.floormap.put_block(i,j,CLOSED)
                    self.draw()
            self.pbt.sleep(50)
        self.pbt.end()   

    def put_mines(self,n):
        while n > 0:
            w,h = self.minemap.get_size()
            i = random.randint(0,h-1)
            j = random.randint(0,w-1)
            if self.minemap.get_block(i,j) != LANDMINE:
                self.minemap.put_block(i,j,LANDMINE)
                n-=1

    def count_mines(self,i,j):
        m = self.minemap
        return len([0 for v in m.neighbors(i,j)
                    if m.get_block(v[0],v[1]) == LANDMINE])

    def open(self,i,j):
        if self.floormap.get_block(i,j)==FLAG:
            return
        elif self.minemap.get_block(i,j)==LANDMINE:
            self.floormap.put_block(i,j,LANDMINE)
            self.end("Gameover")
        elif self.floormap.get_block(i,j)==CLOSED:
            self.floormap.put_block(i,j,SPACE)
            self.unopened -= 1
            to_open = self.countmap.neighbors(i,j)
            while len(to_open) > 0:
                i,j = to_open.pop()
                if self.floormap.get_block(i,j) != CLOSED:
                    continue
                if self.minemap.get_block(i,j) == LANDMINE:
                    continue
                self.floormap.put_block(i,j,SPACE)
                self.unopened -= 1
                if self.countmap.get_block(i,j) == 0:
                    for v in self.countmap.neighbors(i,j):
                        if self.floormap.get_block(v[0],v[1])==CLOSED:
                            to_open.append(v)

    def check_goal(self):
        if self.unopened == self.mine_num:
            self.end("Cleared!")

    def end(self,message):
        self.floormap=self.minemap
        self.view2d.draw()
        self.pbt.draw_rect(0,0,250,50,"white")
        self.pbt.draw_text(0,0,message,"black")
        self.pbt.draw_text(0,20,"Press q to exit","black")
        self.pbt.update()
        while True:
            keys = self.pbt.pushed_keys()
            if "q" in keys:
                 break
            elif "up" in keys:
                self.view2d.move_camera(-1,0)
                self.view2d.draw()
            elif "down" in keys:
                self.view2d.move_camera(1,0)
                self.view2d.draw()
            elif "left" in keys:
                self.view2d.move_camera(0,-1)
                self.view2d.draw()
            elif "right" in keys:
                self.view2d.move_camera(0,1)
                self.view2d.draw()
            if len(keys)>0:
                self.pbt.draw_rect(0,0,250,50,"white")
                self.pbt.draw_text(0,0,message,"black")
                self.pbt.draw_text(0,20,"Press q to exit","black")
                self.pbt.update()
        self.pbt.end()
        sys.exit(0)

    def user_select(self,prompt,options):
        i = 0
        sc_w,sc_h = self.pbt.get_screen_size()       
        while True:
            keys = self.pbt.pushed_keys()
            if "up" in keys:
                if i>0:
                    i-=1
            elif "down" in keys:
                if i<len(options)-1:
                    i+=1
            elif "return" in keys:
                return options[i]
            self.pbt.draw_rect(sc_w/2-100,100,sc_w/2+100,120,"white")
            self.pbt.draw_text(sc_w/2,110,
                               f"{prompt}{options[i]} ({str(i+1)}/{len(options)})",
                               anchor="CENTER")
            self.pbt.update()
            self.pbt.sleep(10)


pbt = PygameBasicTools(600,400)
pbt.set_font("arias",25)
game = Game(pbt)
