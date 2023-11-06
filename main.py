# coding=utf-8
#the cool stuff is happening in engine...
#teaching myself factory methods
from __future__ import division
from bearlibterminal import terminal as blt
import numpy as np
l1 = ["a"]*10
ll = [l1]*10
nparr = np.arange(0,40).reshape(2,20)

st_nparr = np.array(nparr,dtype = [('code','i4')])

def MakeBoxBorder(h,w,brd = "║═╔╗╚╝",fgcolor = "red",bgcolor ="black"):
    """

    :param x: x position
    :param y: y position
    :param w: width in cells
    :param h: height in cells
    :param brd: characters for vertical, horizonta, upper left, upper right, lower left, lowre right corners
    :return: structured numpy array ready to be drawn
    """
    st_array = np.zeros((h,w),dtype = [("ch",np.uint32),("fg",np.uint32),("bg",np.uint32)])
    st_array[:] = (ord(" "),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    st_array[0,:] = (ord(brd[0]),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    st_array[-1,:] = (ord(brd[0]),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    st_array[:,0] = (ord(brd[1]),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    st_array[:,-1] = (ord(brd[1]),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    st_array[0,0] = (ord(brd[2]),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    st_array[0,-1] = (ord(brd[4]),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    st_array[-1,0] = (ord(brd[3]),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    st_array[-1,-1] = (ord(brd[5]),blt.color_from_name(fgcolor),blt.color_from_name(bgcolor))
    return st_array

def DrawBoxBorder(x,y,st_array):
    blt.put_np_array(x,y,st_array,
                     tile_code=st_array.dtype.names[0],
                     tile_color=st_array.dtype.names[1],
                     tile_back_color=st_array.dtype.names[2])

class Menu:
    def __init__(self,item_list = [],parent_menu = None,size = (1,1),position = (1,1),title = "",name=""):
        self.item_list = item_list
        self.size = size
        self.title = title
        self.position = position
        self.selected = 0
        self.name = name
        self.parent_menu = parent_menu
        self.index = 0
    def __call__(self,*args,**kwargs):
        return self

    def as_parent(self,item_list = [],title = "",name = ""):
        return Menu(parent_menu = self,
                        size = self.size,
                        position = self.position,
                        item_list = item_list,
                        title = title,
                        name = name)


    @property
    def index(self):
        return self._index
    @index.setter
    def index(self,value):
        if len(self.item_list) != 0:
            self._index = value % len(self.item_list)
        else:
            self._index = 0
        
    def activate(self,goback = False,*args,**kwargs):
        if goback:
            if self.parent_menu:
                return self.parent_menu
            else:
                return self
        else:
            if len(self.item_list) > 0:
                return self.item_list[self.index]()
            else:
                return 0

class MenuManager:
    def __init__(self,active_menu = None,root_menu = None):
        self.active_menu = active_menu
        self.root_menu = root_menu

    def draw_active_menu(self):
        border = MakeBoxBorder(*self.active_menu.size)
        DrawBoxBorder(*self.active_menu.position,border)
        blt.puts(self.active_menu.position[0],
                    self.active_menu.position[1],
                    self.active_menu.title,
                    self.active_menu.size[0],
                    self.active_menu.size[1]-1,
                    blt.TK_ALIGN_CENTER)
    def draw_active_menu_items(self):
        for ii,it in enumerate(self.active_menu.item_list):
            blt.puts(self.active_menu.position[0],
                     self.active_menu.position[1]+2+ii,
                     it.name,
                     self.active_menu.size[0],
                     self.active_menu.size[1]-1,
                     blt.TK_ALIGN_CENTER)

        blt.put(self.active_menu.position[0]+2,
                self.active_menu.position[1]+2+self.active_menu.index,">")

    def control(self):
        while True:

            if blt.has_input():
                print(blt.read())
                key = blt.read()
                if key == blt.TK_UP:
                    self.active_menu.index -= 1
                if key == blt.TK_DOWN:
                    self.active_menu.index += 1
                if key == blt.TK_RETURN:
                    if isinstance(self.active_menu.activate(),Menu):
                        self.active_menu = (self.active_menu.activate())
                if key == blt.TK_ESCAPE:
                    self.active_menu = self.active_menu.activate(goback=True)

                if key == blt.TK_Q:
                    blt.close()
                    return 0
                blt.clear()
                self.draw_active_menu()
                self.draw_active_menu_items()
                blt.refresh()

    def __call__(self, *args, **kwargs):
        self.draw_active_menu()
        self.draw_active_menu_items()
        blt.refresh()
        self.control()


# coding=utf-8
if __name__ == "__main__":
    blt.open()
    blt.set("window: cellsize=12x12, title='Omni: menu', fullscreen=true; font: default")
    blt.set("window.title='Rouge Rogue Rage'")
    blt.color("white")
    blt.clear()
    print(blt.color_from_name("black"),blt.color_from_name("red"))
    #blt.puts(4,5,"bla")
    #key = "a"
    #blt.put_np_array(1, 0, st_nparr, tile_code="code")
    root_menu = Menu(parent_menu=None, size=(21, 14), position=(3, 3), title="Main Menu")
    itemlist1 = [Menu(size=(21,14),parent_menu=root_menu,position=(3,3),title="{} SubMenu".format(ii),name="{} SubMenu".format(ii)) for ii in range(3)]
    itemlist10 = [[Menu(size=(21, 14),
                        parent_menu=it,
                        position=(3, 3),
                        title="{} {} SubMenu".format(ii,jj),
                        name="{} {} SubMenu".format(ii,jj))
                   for ii in range(5)]
                  for jj,it in enumerate(itemlist1)]
    for it,it10 in zip(itemlist1,itemlist10):
        it.item_list = it10
    print(itemlist1[0])

    print(itemlist1[0].item_list[0].parent_menu)
    print(type(itemlist1[0]))
    if isinstance(itemlist1[0],Menu):
        print("YES")
    root_menu.item_list = itemlist1
    main_menu = MenuManager(active_menu=root_menu,root_menu=root_menu)
    main_menu()
    blt.close()

















