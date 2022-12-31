#Bouncing spots v1.0 10/13/2022

#Functions
import math,time,threading,msvcrt,random,os

def draw_c(coordinate,spot='██',space='  ',y_axis = True,x_limit = False,int_color = True):
    '''支持24色彩色输出 坐标格式为coordinate={y:{x:color}}
    color应为3或4位integer 前两位表示颜色 第三位为 暗/默认/高亮 第四位可选为闪烁
         或为如 '\033[1;36;5m██\033[0m' 的格式
    
    spot 为表示点的字符 默认为██
    space 为表示空的字符 默认为  (两个空格)
    y_axis 默认为False 不显示纵坐标 0或False为不显示 1或True为显示
    x_limit 默认为True 不限制
    int_color 默认为True 把int颜色改为包含 颜色 点(默认██) 空(默认  ) 的字符串   建议保持默认
    
    前景色   30 黑色   31 红色   32 绿色    33 黄色   34 蓝色   35 红紫   36 蓝绿   37 白色
    背景色   40 黑色   41 红色   42 绿色    43 黄色   44 蓝色   45 红紫   46 蓝绿   47 白色
    '''
    def xline(start_value):
        '''用来把单行的颜色/空添加到列表coor里面用的'''
        for x in range(start_value,max(coordinate[y].keys())+1):
            if x in coordinate[y].keys():   
                coor.append(coordinate[y][x])
            else:   
                coor.append(space)
        coor.append('\n')
        return coor

    if int_color:   #把int颜色改为包含 颜色 点(默认██) 空(默认  ) 的字符串   建议保持默认开启
        for y in coordinate.keys():
            for x in coordinate[y].keys():
                if str(coordinate[y][x]) == coordinate[y][x]:
                    continue
                color = str(coordinate[y][x])   # str 颜色
                if len(color) == 4:
                    coordinate[y][x] = f'\033[{color[2]};{color[:2]};{color[3]}m{spot}\033[0m'
                else:
                    coordinate[y][x] = f'\033[{color[2]};{color[:2]}m{spot}\033[0m'

    if not x_limit:   #如果没有限制 x ≥ 0 那么找到x最小值
        x_min = 0
        for y in coordinate.keys():
            if x_min > min(coordinate[y].keys()):
                x_min = min(coordinate[y].keys())

    coor = []   #字典coordinate 转为 列表coor
    for y in range(max(coordinate.keys()),min(coordinate.keys())-1,-1):
        if y_axis:   #显示纵坐标
            coor.append(f'{y}\t')
        
        if y in coordinate.keys():   #改行有点
            if x_limit:    
                coor = xline(0)
            else:    
                coor = xline(x_min)
        elif y not in coordinate.keys():    
            coor.append('\n')
        
    print(''.join(coor))   #把列表coor变为一个很长的字符即最终图像并输出

def sin(theta):    return math.sin(theta*math.pi/180)
def cos(theta):    return math.cos(theta*math.pi/180)
def Int(val):    return int(round(val,0))
def posi(val):
    if val >= 0:
        return val
    else: return 0
def angle(theta,max=180,min=-180):
    '''To ensure that the theta is in the right range.'''
    while theta > max:
        theta -= 360
    while theta < min:
        theta += 360
    return theta

def coordinate_init():
    coordinate = {}    # {y:{x:color}}
    coordinate[frame[1]+2] = {x:370 for x in range(0,frame[0]+3)}
    coordinate[0] = coordinate[frame[1]+2]
    for y in range(frame[1]+1,0,-1):
        coordinate[y] = {0:370, frame[0]+2:370}
    return coordinate

def control():
    global space_gl,tp_gl,v_gl,p_gl,l_gl
    p_gl,l_gl = False,False
    while True:
        c = msvcrt.getwch()
        if c == 'b':
            space_gl = '\033[40;2m  '
        elif c == 'w':
            space_gl = '\033[47;1m  '
        elif c == 'd':
            space_gl = '  '
        elif c == 't':
            tp_gl = True
        elif c == 'p':
            tp_gl = False
        elif c == 'Q':
            v_gl = 0
        elif c == 'n':
            v_gl = -1
        elif c == 'y':
            v_gl = 1
        elif c == 'P':
            p_gl = not p_gl
        elif c == '+':
            v_gl = 3
        elif c == '-':
            v_gl = -2
        elif c == 'l':
            l_gl = not l_gl

class Ball:
    def __init__(self):
        self.speed = -1
        while self.speed < 0 or self.speed > 2:
            self.speed = random.normalvariate(1,0.8)
        self.theta = random.randint(-180,180)
        self.ball = [random.randint(1,frame[0]),random.randint(1,frame[1]),random.randint(31,37)*10+random.randint(0,1)]

    def biu(self):
        #Ball's moving
        self.ball[0] += cos(self.theta)*self.speed
        self.ball[1] += sin(self.theta)*self.speed

        #Bouncing on the walls
        #Left, Right, Top
        for n in (1,2):
            if self.ball[0] < 0:
                self.ball[0] = 0
                self.theta = 180-self.theta
                if random.randint(0,10) <= 3:self.theta,self.ball[2] = random.randint(-180,180),random.randint(31,37)*10+random.randint(0,1)
            elif self.ball[0] > frame[0]:
                self.ball[0] = frame[0]
                self.theta = 180-self.theta
                if random.randint(0,10) <= 3:self.theta,self.ball[2] = random.randint(-180,180),random.randint(31,37)*10+random.randint(0,1)
            elif self.ball[1] > frame[1]:
                self.ball[1] = frame[1]
                self.theta = -self.theta
                if random.randint(0,10) <= 3:self.theta,self.ball[2] = random.randint(-180,180),random.randint(31,37)*10+random.randint(0,1)
            elif self.ball[1] < 0:
                self.ball[1] = 0
                self.theta = -self.theta
                if random.randint(0,10) <= 3:self.theta,self.ball[2] = random.randint(-180,180),random.randint(31,37)*10+random.randint(0,1)

        coordinate[Int(self.ball[1])].update({Int(self.ball[0]):self.ball[2],Int(self.ball[0])+1:self.ball[2]})
        coordinate[Int(self.ball[1]+1)].update({Int(self.ball[0]):self.ball[2],Int(self.ball[0])+1:self.ball[2]})

        if self.theta in (0,180,-180):
            self.theta = abs(angle(self.theta+1))

        return self.theta,self.ball[2],coordinate

    def tp(self):
        if random.randint(0,1_000) <= 5:
            self.ball[0],self.ball[1] = random.randint(1,frame[0]),random.randint(1,frame[1])
            if random.randint(0,1_000) <= 200:
                self.ball[2] = random.randint(31,37)*10+random.randint(0,2)
        return self.ball[0],self.ball[1],self.ball[2]


#Default Arguments
frame = (200,100)
coordinate = coordinate_init()
tp_gl = True
v_gl = 9
space_gl = '  '

balls = []
for n in range(0,25):
    balls.append(Ball())

E = threading.Thread(target=control,daemon=True)
E.start()
while 1:
    st = time.time()
    while p_gl:pass

    if random.randint(1,8) == 1 and len(balls) > 1:
        del balls[random.randint(0,len(balls)-1)]
    if random.randint(1,8) == 1 and len(balls) <= 50 or random.randint(0,2) == 0 and len(balls) in range(1,5):
        balls.append(Ball())
    if random.randint(1,2048) == 1:
        balls.clear()
    elif random.randint(1,2048) == 1:
        for n in range(0,50):
            balls.append(Ball())
    
    if not l_gl:
        coordinate = coordinate_init()
    
    for ball in (balls):
        ball.theta,ball.ball[2],coordinate = ball.biu()
        if tp_gl:
            ball.ball[0],ball.ball[1],ball.ball[2] = ball.tp()

    print('\033[F'*(frame[1]+4),end='')
    draw_c(coordinate,y_axis=False,x_limit=True,space=space_gl)

    if v_gl == 0:
        break
    elif v_gl == -1:
        balls.clear()
        v_gl = 9
    elif v_gl == 1:
        for n in range(0,50-len(balls)+1):
            balls.append(Ball())
        v_gl = 9
    elif v_gl == 3:
        for n in range(0,5):
            balls.append(Ball())
        v_gl = 9
    elif v_gl == -2:
        for n in range(4,-1,-1):
            try:   del balls[n]
            except: pass
        v_gl = 9
            

    time.sleep(posi(1/240-(time.time()-st)))
os.system('cls')