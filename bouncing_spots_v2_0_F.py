

#Bouncing Spots v2.0.F 10/23/2022, 10/27/2022, 11/4/2022 - 11/5/2022

# 一些点 出现 移动 碰撞 消失
# 边框 大小 是否显示
# 点 速度 颜色 方向 生命
# 出现：
#       随机任意位置出现
#       随机边框任意位置出现
#       固定点出现
# 移动：
#       速度
#       方向
#       生命减少
#       变角度
# 碰撞：
#       相撞穿过
#       相撞反弹
#       相撞分裂
#       碰壁减速
# 消失：
#       随即消失
#       相撞消失
#       生命尽头
#       碰壁消失

# Pattern (str)
# 随机
# 单侧深浅
# 双侧深浅
# 4侧深浅
# 固定点生成
# pattern lst
# 第一位 生成
#       R 随机位置
#       G 固定点 generator_pos_gl
#       lrtb LRTB
#       gc 颜色和速度有关
# 第二位 遇到边
#       B 反弹
#       C 变色
#       V 速度随机
#       V+ 速度加
#       V- 速度减
#       gc 颜色和速度有关
#       LS 小光点
#       h 生命减少
#       D 消失
# 第三位 移动过程中
#       h 生命减少
#       d 生命小于等于0时死亡
# 第四位 互相撞
#       B 反弹
#       C 变色
#       V 速度随机
#       V+ 速度加
#       V- 速度减
#       gc 颜色和速度有关
#       LS 小光点
#       h 生命减少

from itertools import count
import math,random,os,time,threading,copy
def Int(val):   return int(round(val,0))
def sin(theta):   return math.sin(theta/180*math.pi)
def cos(theta):   return math.cos(theta/180*math.pi)

# ========= Spot =========
class Spot:

    velocity_min = 0.1
    velocity_max = 1
    velocity_level = (velocity_max-velocity_min)/3

    health = 1000
    health_hurt = 1
    wall_hurt = 10
    spot_hurt = 5

    def __init__(self,pattern=None,name=None,color=None,theta=None,pos=None,health=None,velocity=None):
        global pattern_gl
        self.name=name
        if pattern==None:    self.pattern=pattern_gl
        else:    self.pattern = pattern
        if health == None:    self.health = Spot.health
        else:    self.health = health

        if type(self.pattern) == str:
            if self.pattern == 'Random':
                self.pos = Spot.spot_generate_pos(self,'R')
                self.theta = random.randint(-180,180)
                self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                pattern_gl = ['Rgc','BCVh','hd','BhCV']
                Spot.spot_color(self,True)
            elif self.pattern == 'Left':
                self.pos = Spot.spot_generate_pos(self,'l')
                self.theta = 0
                self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                pattern_gl = ['lgc','D','','']
                Spot.spot_color(self,True)
            elif self.pattern == 'Right':
                self.pos = Spot.spot_generate_pos(self,'r')
                self.theta = 180
                self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                pattern_gl = ['rgc','D','','']
                Spot.spot_color(self,True)
            elif self.pattern == 'Top':
                self.pos = Spot.spot_generate_pos(self,'t')
                self.theta = -90
                self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                pattern_gl = ['tgc','D','','']
                Spot.spot_color(self,True)
            elif self.pattern == 'Bottom':
                self.pas = Spot.spot_generate_pos(self,'b')
                self.theta = 90
                self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                pattern_gl = ['bgc','D','','']
                Spot.spot_color(self,True)
            elif self.pattern == 'L&R':
                self.pos = [random.choice((1,frame_gl[0])), random.randint(1,frame_gl[1])]
                self.theta = 0
                self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                pattern_gl = ['lrgc','D','','']
                Spot.spot_color(self,True)
            elif self.pattern == 'T&B':
                self.pos = [random.randint(1,frame_gl[0]), random.choice((1,frame_gl[1]))]
                self.theta = 90
                self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                pattern_gl = ['tbgc','D','','']
                Spot.spot_color(self,True)
            elif pattern == 'LS':    
                self.pattern = [0,'Bh','hd']
                self.name = 'little spot'
                self.velocity = 1
                self.color = '\033[1;33m⭐\033[0m'   # ◗◖
                self.health = Spot.health / 8
                if theta==None:    self.theta = LS_B_gl
                else:    self.theta = theta
                self.pos = copy.deepcopy(pos)

        elif type(self.pattern) == list and self.pattern[1:4]!=['D','','']:
            if pos == None:    self.pos = Spot.spot_generate_pos(self,random.choice(self.pattern[0]))
            else:    self.pos = pos
            if theta == None:    self.theta = random.randint(-180,180)
            else:    self.theta = theta
            if velocity == None:    self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
            else:    self.velocity = velocity
            if color == None:    Spot.spot_color(self,'gc' in self.pattern[0])
            else:    self.color = color

    def spot_generate_pos(self,pos_mode):
        if pos_mode == 'R':
            return [random.randint(1,frame_gl[0]), random.randint(1,frame_gl[1])]
        elif pos_mode == 'l':
            return [1, random.randint(1,frame_gl[1])]
        elif pos_mode == 'r':
            return [frame_gl[0], random.randint(1,frame_gl[1])]
        elif pos_mode == 't':
            return [random.randint(1,frame_gl[0]), frame_gl[1]]
        elif pos_mode == 'b':
            return [random.randint(1,frame_gl[0]), 1]
        elif pos_mode == 'G':
            return generator_pos_gl
        elif pos_mode == 'g' or pos_mode == 'c':
            return Spot.spot_generate_pos(self,random.choice(self.pattern[0]))

    def spot_color(self,preset=False):
        if preset:
            if self.velocity <= Spot.velocity_level+Spot.velocity_min:
                self.color = f'\033[2;{random.randint(31,37)}m██\033[0m'
            elif self.velocity <= Spot.velocity_level*2+Spot.velocity_min:
                self.color = f'\033[0;{random.randint(31,37)}m██\033[0m'
            elif self.velocity <= Spot.velocity_level*3+Spot.velocity_min:
                self.color = f'\033[1;{random.randint(30,37)}m██\033[0m'
        else: self.color = f'\033[{random.randint(0,2)};{random.randint(31,37)}m██\033[0m'


    def moving(self):
        self.pos[0] += cos(self.theta)*self.velocity
        self.pos[1] += sin(self.theta)*self.velocity
        if 'h' in self.pattern[2]:
            self.health -= self.health_hurt*0.5
        if 'd' in self.pattern[2]:
            if self.health <= 0:
                del all_spots_gl[all_spots_gl.index(self)]

    def bouncing_on_walls(self):
        global LS_B_gl
        hit = False
        if 'B' in self.pattern[1] or 'D' in self.pattern[1]:
            if 'B' in self.pattern[1]:
                for t in range(2):
                    # LR
                    if Int(self.pos[0]) <= 0:
                        hit = True
                        self.theta = 180-self.theta
                        self.pos[0] = 1
                        if 'LS' in self.pattern[1]:
                            LS_B_gl = self.theta/2
                    elif Int(self.pos[0]) >= frame_gl[0]+1:
                        hit = True
                        self.theta = 180-self.theta
                        self.pos[0] = frame_gl[0]
                        if 'LS' in self.pattern[1]:
                            LS_B_gl = self.theta/2
                    # TB
                    elif Int(self.pos[1]) <= 0:
                        hit = True
                        self.theta = -self.theta
                        self.pos[1] = 1
                        if 'LS' in self.pattern[1]:
                            LS_B_gl = self.theta/2
                    elif Int(self.pos[1]) >= frame_gl[1]+1:
                        hit = True
                        self.theta = -self.theta
                        self.pos[1] = frame_gl[1]
                        if 'LS' in self.pattern[1]:
                            LS_B_gl = self.theta/2
            
            else:
                if Int(self.pos[0])<=0 or Int(self.pos[0])>=frame_gl[0]+1:
                    hit = True
                elif Int(self.pos[1])<=0 or Int(self.pos[1]) >= frame_gl[1]+1:
                    hit = True

            if hit:
                if 'V+' in self.pattern[1]:
                    self.velocity += random.uniform(0,Spot.velocity_max-self.velocity)
                elif 'V-' in self.pattern[1]:
                    self.velocity -= random.uniform(0,self.velocity-Spot.velocity_min)
                elif 'V' in self.pattern[1]:
                    self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                
                if 'C' in self.pattern[1]:
                    Spot.spot_color(self)       
                if 'gc' in self.pattern[1] and 'C' in self.pattern[1]:
                    Spot.spot_color(self,True)
                if 'gc' in self.pattern[1] and 'V' in self.pattern[1]:
                    if self.velocity <= Spot.velocity_level+Spot.velocity_min:
                        self.color = f'\033[2;{self.color[4:6]}m██\033[0m'
                    elif self.velocity <= Spot.velocity_level*2+Spot.velocity_min:
                        self.color = f'\033[0;{self.color[4:6]}m██\033[0m'
                    elif self.velocity <= Spot.velocity_level*3+Spot.velocity_min:
                        self.color = f'\033[1;{self.color[4:6]}m██\033[0m'

                if 'h' in self.pattern[1]:
                    self.health -= Spot.wall_hurt
                if 'D' in self.pattern[1]:
                    del all_spots_gl[all_spots_gl.index(self)]
# ========= Class =========


def bouncing_on_spot():
    for index,spot1 in enumerate(all_spots_gl,start=1):
        if index == len(all_spots_gl):break
        if spot1.name=='little spot':continue
        for spot2 in all_spots_gl[index:]:
            if spot2.name=='little spot':continue
            if Int(spot1.pos[1]) == Int(spot2.pos[1]) and Int(spot1.pos[0]) == Int(spot2.pos[0]):
                if 'B' in spot1.pattern[3]:
                    spot1.theta += 180
                    spot2.theta +=180
                if 'C' in spot1.pattern[3]:
                    Spot.spot_color(spot1)
                    Spot.spot_color(spot2)
                if 'h' in spot1.pattern[3]:
                    spot1.health -= Spot.spot_hurt
                    spot2.health -= Spot.spot_hurt
                
                if 'V+' in spot1.pattern[3]:
                    spot1.velocity += random.uniform(0,Spot.velocity_max-spot1.velocity)
                    spot2.velocity += random.uniform(0,Spot.velocity_max-spot2.velocity)
                # Slowing down the spots will get them too slow to separate resulting in 
                # continuously being slowed and sticked to each other, which may be a bug
                elif 'V-' in spot1.pattern[3]:
                    spot1.velocity -= random.uniform(0,spot1.velocity-Spot.velocity_min)
                    spot2.velocity -= random.uniform(0,spot2.velocity-Spot.velocity_min)
                elif 'V' in spot1.pattern[3]:
                    spot1.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                    spot2.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                
                if 'gc' in spot1.pattern[3] and 'C' in spot1.pattern[3]:
                    Spot.spot_color(spot1,True)
                    Spot.spot_color(spot1,True)
                if 'gc' in spot1.pattern[3] and 'V' in spot1.pattern[3]:
                    if spot1.velocity <= Spot.velocity_level+Spot.velocity_min:
                        spot1.color = f'\033[2;{spot1.color[4:6]}m██\033[0m'
                        spot2.color = f'\033[2;{spot2.color[4:6]}m██\033[0m'
                    elif spot1.velocity <= Spot.velocity_level*2+Spot.velocity_min:
                        spot1.color = f'\033[0;{spot1.color[4:6]}m██\033[0m'
                        spot2.color = f'\033[0;{spot2.color[4:6]}m██\033[0m'
                    elif spot1.velocity <= Spot.velocity_level*3+Spot.velocity_min:
                        spot1.color = f'\033[1;{spot1.color[4:6]}m██\033[0m'
                        spot2.color = f'\033[1;{spot2.color[4:6]}m██\033[0m'
                
                if 'LS' in spot1.pattern[3]:
                    all_spots_gl.append(Spot(
                    pattern='LS',name='little spot',theta=spot1.theta+90,pos=spot1.pos
                    ))
                    all_spots_gl.append(Spot(
                    pattern='LS',name='little spot',theta=spot2.theta+90,pos=spot2.pos
                    ))


def spots_coordinate(coordinate):
    for spot in all_spots_gl:
        try:
            coordinate[Int(spot.pos[1])][Int(spot.pos[0])] = spot.color
        except KeyError: pass    # To prevent exception occuring when changing the frame size
    return coordinate


def Input():
    from msvcrt import getwch
    global paused_gl,pattern_gl,generator_pos_gl,quit_gl,frame_gl,control_gl
    global line_track_gl,fps_gl
    line_track_gl = False
    while True:
        key = getwch()
        if key == '/':
            paused_gl = True
            command = input("/")
            if command in ("Random","Left","Right","Top","Bottom","L&R","T&B","Sides"):
                pattern_gl = command
                paused_gl = False
            elif command[0] == "(" and command[-1] == ")":
                generator_pos_gl = tuple([int(n) for n in command[1:-1].split()])
                paused_gl = False
            elif command == 'frame':
                frame = input('\t')
                frame = frame.split()
                frame_gl[0] = int(frame[0])
                frame_gl[1] = int(frame[1])
                os.system('cls')
                paused_gl = False
            elif command == 'pattern':
                pattern_index = int(input('\033[F\t'))
                pattern_gl[pattern_index] = input('\033[F\t')
                paused_gl = False
            elif command == 'fps':
                fps_gl = float(input('\033[F\t'))
                paused_gl = False
            elif command == 'theta':
                for spot in all_spots_gl:
                    spot.theta = (spot.theta+180)%360-180
                paused_gl = False
            else:    paused_gl = False
        
        elif key == 'Q':
            break
        elif key == 'C':
            control_gl = 'clear'
        elif key == 'R':
            control_gl = 'refresh'
        elif key == 'D':
            default(keepspots=True)
        elif key == 'L':
            paused_gl = True
            print('\n'*2)
            print(f'Active Threads Count: {threading.active_count()}')
            print('\nSpots:',end='')
            for spot in all_spots_gl:
                if spot.name != 'little spot':
                    print('')
                    print(f'Name: {spot.name} \t\tColor: {spot.color} {repr(spot.color)}')
                    print(f'Pos: [{spot.pos[0]:.3f}, {spot.pos[1]:.3f}]\tPattern:{spot.pattern}')
                    print(f'Velocity: {spot.velocity:.6f}\tHealth: {spot.health}')
                    print(f'Theta: {(spot.theta+180)%360-180}({spot.theta})')
            while True:
                if getwch() == ' ':
                    break
            paused_gl = False
            os.system('cls')
        elif key == 't':
            for spot in all_spots_gl:
                    spot.theta = (spot.theta+180)%360-180
        elif key == ' ':
            paused_gl = not paused_gl
        elif key == '+':
            all_spots_gl.append(Spot())
        elif key == '-':
            while True:
                        random_index = random.randint(0,len(all_spots_gl)-1)
                        if all_spots_gl[random_index].name!='little spot':
                            all_spots_gl.pop(random_index)
                            break
            
                    
        elif key == 'l':
            line_track_gl = not line_track_gl


    quit_gl = True



def default(keepspots=False):
    # frame
    os.system('cls')
    global paused_gl,pattern_gl,generator_pos_gl,quit_gl,frame_gl,control_gl
    global line_track_gl,all_spots_gl,LS_B_gl,fps_gl
    LS_B_gl = 0
    fps_gl = 144
    if not keepspots:    all_spots_gl = []
    quit_gl = False
    line_track_gl = False
    control_gl = None
    frame_gl = [72,32,'\033[47m  \033[0m']
    paused_gl = False
    pattern_gl = ['lrtbGgc','Bh','hd','BLSh'] # ---- Temporarily ----
    generator_pos_gl = [Int(frame_gl[0]/2), Int(frame_gl[1]/2), ]
    pass



def coordinate_init():
    coordinate = {}
    for y in range(frame_gl[1]+2):
        coordinate[y] = {}
        for x in (0,frame_gl[0]+1):
            coordinate[y][x] = frame_gl[2]
    for x in range(frame_gl[0]+2):
        coordinate[0][x] = frame_gl[2]
        coordinate[frame_gl[1]+1][x] = frame_gl[2]
    return coordinate




def draw_c(coordinate,y_axis=False):    # ██
    img = []
    for y in range(frame_gl[1]+1,-1,-1):
        img.append('\n')
        if y_axis:   img.append(f'{y}\t')
        for x in range(frame_gl[0]+3):
            if x in coordinate[y].keys():
                img.append(coordinate[y][x])
            else: img.append('\033[0m  \033[0m')
    print('\033[F'*(frame_gl[1]+18))            
    print(''.join(img))


def main():
    default()
    coordinate = coordinate_init()
    KeyboardInput = threading.Thread(target=Input,daemon=True)
    KeyboardInput.start()

    global LS_B_gl,control_gl,pattern_gl

    while True and threading.active_count()==2:
        while paused_gl and not quit_gl: pass    # Pause
        if control_gl == 'clear':
            all_spots_gl.clear()
            control_gl = None
        if control_gl == 'refresh':
            coordinate = coordinate_init()
            os.system('cls')
            control_gl = None

        if pattern_gl[1:4]==['D','','']:
            all_spots_gl.append(Spot(pattern=pattern_gl))
        else:    
            if random.uniform(0,100) <= 2:
                if random.choice((True,False)):
                    all_spots_gl.append(Spot(pattern=pattern_gl))
                # else:
                #     if len(all_spots_gl) > 1 and random.uniform(0,100) <= 60:
                #         while True:
                #                 random_index = random.randint(0,len(all_spots_gl)-1)
                #                 if all_spots_gl[random_index].name!='little spot':
                #                     all_spots_gl.pop(random_index)
                #                     break
        
        bouncing_on_spot()
        for spot in all_spots_gl:
            Spot.moving(spot)
            Spot.bouncing_on_walls(spot)
            if LS_B_gl:
                all_spots_gl.append(Spot(
                    pattern='LS',name='little spot',theta=LS_B_gl,pos=spot.pos
                    ))
                LS_B_gl = 0



        if not line_track_gl: coordinate = coordinate_init()
        coordinate = spots_coordinate(coordinate)
        draw_c(coordinate,)
        

        if quit_gl:
            os.system('cls')
            exit()

        print('  '*frame_gl[0])
        print('\033[F')
        print(f'{len(all_spots_gl):4}',end='\t\t')
        count = 0
        for spot in all_spots_gl:
            if spot.name != 'little spot':
                count += 1
        print(f'{count:4}',end='')

        time.sleep(1/fps_gl)

if __name__ == '__main__':
    main()