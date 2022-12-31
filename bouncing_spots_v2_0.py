

# Bouncing Spots v2.0 11/11/2022

# Func kit
def sin(theta):    
    return math.sin(theta/180 * math.pi)
def cos(theta):    
    return math.cos(theta/180 * math.pi)
def Int(val):    
    return int(round(val,0))
def angle(theta): 
    return (theta+180)%360-180
def newton(a,b,c,d,x=0.001,e=1e-6):
    '''To solve the cubic equation in velocity level calculation'''
    x_p = x - ((a * x ** 3 + b * x ** 2 + c * x + d) / 
                (3 * a * x ** 2 + 2 * b * x + c))
    while abs(x_p - x) > e:
        x = x_p
        x_p = x - ((a * x ** 3 + b * x ** 2 + c * x + d) / 
                    (3 * a * x ** 2 + 2 * b * x + c))
    return x_p

class Spot:
    H_w = 10    # Damage got when hitting the wall
    H_s = 15    # Damage got when hitting other spots
    H_m = 0.01  # Damage got when moving
    health = 512
    Ls_health = H_w

    velocity_max=1
    velocity_min=0.1

    velocity_level1 = 0.4641588834    # v_min + d_1 + d_2 = 0.1 + 0.115443469 + 0.2487154144
    velocity_level2 = 0.215443469    # v_min + d_1 = 0.1 + 0.115443469
    velocity_level3 = 0.1    # v_min = 0.1

    def __init__(self,Ls=False,name=None,pos=None,theta=None,velocity=None,color=None):
        global pattern_gl,index_gl,point_gl,frame_gl
        
        if Ls:  # Generating a Little spot
            self.color = "\033[1;33m⭐\033[0m"
            self.name,self.velocity,self.survivor = "Ls",Spot.velocity_max,False
            self.pos,self.theta,self.health = pos,theta,Spot.Ls_health
            if type(name) == str:
                self.name = name
            if type(velocity) in (float,int):
                self.velocity = velocity
            if type(color) == str:
                self.color = color
        
        else:   # Generating a regular spot
            index_gl+=1
            self.name = name
            self.index = index_gl
            self.health = Spot.health
            self.survivor = False

            if pos == None:
                # Randomly choose a generating pattern that will be used to define the new spot's pos.
                pos = random.choice(pattern_gl["Gen_count"])
                if pos == "Gen_Ran":
                    self.pos = [random.randint(1,frame_gl[0]),random.randint(1,frame_gl[1])]
                elif pos == "Gen_P":
                    self.pos = list(copy.deepcopy(point_gl[random.randint(0,len(point_gl)-1)]))
                elif pos == "Gen_L":
                    self.pos = [1,random.randint(1,frame_gl[1])]
                elif pos == "Gen_R":
                    self.pos = [frame_gl[0],random.randint(1,frame_gl[1])]
                elif pos == "Gen_T":
                    self.pos = [random.randint(1,frame_gl[0]),1]
                elif pos == "Gen_B":
                    self.pos = [random.randint(1,frame_gl[0]),frame_gl[1]]
            else:    
                self.pos = pos

            if theta == None:
                if pattern_gl["Gen_t"] == None:
                    self.theta = random.uniform(-180,180)
                elif pattern_gl["Gen_t"] == "L&R":
                    self.theta = 0 if self.pos[0] == 1 else 180
                elif pattern_gl["Gen_t"] == "T&B":
                    self.theta = -90 if self.pos[1] == 1 else 90
                else:    
                    self.theta = float(pattern_gl["Gen_t"])
            else:    
                self.theta = (theta+180)%360-180

            if velocity == None:
                if pattern_gl["Gen_V"] == None:
                    self.velocity = random.uniform(self.velocity_min,self.velocity_max)
                else:    
                    self.velocity = pattern_gl["Gen_V"]
            else: 
                self.velocity = velocity

            if color == None:
                if pattern_gl["Gen_C"] == None:
                    self.color = f"\033[{random.randint(0,2)};{random.randint(30,37)}m██\033[0m"
                else:
                    self.color = pattern_gl["Gen_C"]
            else:
                self.color = color

            if pattern_gl["C-V"]:    Spot.c_v(self)

    def c_v(self):
        '''Change the brightness of a spot's color according to its velocity'''
        if self.velocity >= Spot.velocity_level1:
            self.color = f"\033[1{self.color[3:]}"
        elif self.velocity >= Spot.velocity_level2:
            self.color = f"\033[0{self.color[3:]}"
        elif self.velocity >= Spot.velocity_level3:
            self.color = f"\033[2{self.color[3:]}"

    def v_lvl(v1,v0):
        '''
        Set the velocity standard for c_v.
        Spots with same health and different velocity have different life time.
        So if assign the color in a simple way, dark spots whose velocities are slow 
        will be much more than the bright ones whose velocities are fast in number.
        To make the numbers of spots with various brightness equal, the possibility
        of being assigned a particular brightness and the average velocity of the
        required velocity range should be in direct ratio.

        - (d1/(v1-v0)) : (d2/(v1-v0)) : (d3/(v1-v0)) = (v0+d1/2) : (v0+d1+d2/2) : (v0+d1+d2+d3/2)
        - v0 + d1 + d2 + d3 = v1
        =>  d1 : ((d1)^3)/(v0)+3(d1)^2+3(v0)d+(v0)^2-(v1)(v0) = 0
            d2 = ((d1)^2)/(v0)+(d1)
        =>  velocity_level1 = v_min + d_1 + d_2
            velocity_level2 = v_min + d_1
            velocity_level3 = v_min
        '''
        Spot.velocity_level3 = v0
        d1 = newton(a=1/v0,b=3,c=3*v0,d=v0**2-v1*v0)
        Spot.velocity_level2 = v0 + d1
        d2 = d1**2 / v0 + d1
        Spot.velocity_level1 = v0 + d1 + d2

    def move(self):
        if pattern_gl["Mov_T"] == True:
            self.theta += random.randint(-5,5)
        if pattern_gl["Mov_H"] == True:
            self.health -= Spot.H_m
        self.pos[0] += cos(self.theta)*self.velocity
        self.pos[1] -= sin(self.theta)*self.velocity    # Due to the coordinate system's y aixs, it's subtraction.
        
    def die(self,type):
        '''Survivor won't die'''
        if self.health <= 0 and pattern_gl["D"] == True and not self.survivor: 
            if type == "spot":
                spots_gl.remove(self)
            elif type == "Ls":
                Ls_spots_gl.remove(self)

    def wall(self,is_Ls):
        '''Detect whether the spot is hitting the wall. If so, change it attribute according to the pattern_gl'''
        wall = False    # Initially False and will be changed into vertical or horizontal if hitting the wall
        # Collision Detect
        if Int(self.pos[0]) <= 0:
            self.theta = angle(180 - self.theta)
            self.pos[0] = 1
            wall = "vertical"
            if pattern_gl["Walls_H"] == True:
                self.health -= Spot.H_w
        elif Int(self.pos[0]) >= frame_gl[0]+2:
            self.theta = angle(180 - self.theta)
            self.pos[0] = frame_gl[0]+1
            wall = "vertical"
            if pattern_gl["Walls_H"] == True:
                self.health -= Spot.H_w
        if Int(self.pos[1]) <= 0:
            self.theta = angle(- self.theta)
            self.pos[1] = 1
            wall = "horizontal"
            if pattern_gl["Walls_H"] == True:
                self.health -= Spot.H_w
        elif Int(self.pos[1]) >= frame_gl[1]+2:
            self.theta = angle(- self.theta)
            self.pos[1] = frame_gl[1]+1
            wall = "horizontal"
            if pattern_gl["Walls_H"] == True:
                self.health -= Spot.H_w
        
        # If hitting the wall
        if wall != False and not is_Ls:
            if pattern_gl["Walls_V"] != False:
                if pattern_gl["Walls_V"] == "+":
                    self.velocity += random.uniform(0,Spot.velocity_max-self.velocity)
                elif pattern_gl["Walls_V"] == "-":
                    self.velocity -= random.uniform(0,Spot.velocity_max-self.velocity)
                elif type(pattern_gl["Walls_V"]) in (int,float):
                    self.velocity += pattern_gl["Walls_V"]
                elif pattern_gl["Walls_V"] == True:
                    self.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
            
            if pattern_gl["Walls_C"] == True:
                self.color = f"\033[{random.randint(0,2)};{random.randint(30,37)}{self.color[6:]}"

            if pattern_gl["C-V"] == True:
                Spot.c_v(self)

            if pattern_gl["Walls_Ls"] == True:
                if wall == "vertical":
                    Ls_spots_gl.append(Spot(Ls=True,theta=0+random.randint(-30,30),pos=copy.deepcopy(self.pos)))
                    Ls_spots_gl.append(Spot(Ls=True,theta=0+random.randint(-30,30),pos=copy.deepcopy(self.pos)))
                elif wall == "horizontal":
                    Ls_spots_gl.append(Spot(Ls=True,theta=90+random.randint(-30,30),pos=copy.deepcopy(self.pos)))
                    Ls_spots_gl.append(Spot(Ls=True,theta=90+random.randint(-30,30),pos=copy.deepcopy(self.pos)))
            
def spots_hit():
    '''It'll check through the spots_gl and look for if there're any spots bouncing at each other'''
    # In this way, it can check less spots to get the same effect as the most obvious approach
    # It can improve the performance to n!/n^(n) (n = len(spots_gl))
    for index1,spot1 in enumerate(spots_gl[:-1]):
        for spot2 in spots_gl[index1+1:]:
            # Check if spot 1 and 2 are close enough to bouncing at each other. int() matters.
            if int(spot1.pos[0]) == int(spot2.pos[0]) and int(spot1.pos[1]) == int(spot2.pos[1]):
                # Change their coordinates a little bit to make less bug I guess?
                spot1.pos[0],spot1.pos[1] = Int(spot1.pos[0]),Int(spot1.pos[1])
                spot2.pos = copy.deepcopy(spot1.pos)
                # Change their theta as the bouncing can change their track
                if int(angle(spot1.theta)) == int(angle(spot2.theta)):  # Sepically, one is chasing another
                    if spot1.velocity > spot2.velocity:
                        spot1.theta = -spot1.theta
                    else:
                        spot2.theta = -spot2.theta
                else:
                    spot1.theta,spot2.theta = spot2.theta,spot1.theta   # Normally, just swap their thetas

                if pattern_gl["Spots_H"] == True: 
                    spot1.health -= Spot.H_s
                    spot2.health -= Spot.H_s
                
                if pattern_gl["Spots_V"] != False:
                    if pattern_gl["Spots_V"] == "+":
                        spot1.velocity += random.uniform(0,Spot.velocity_max-spot1.velocity)
                        spot2.velocity += random.uniform(0,Spot.velocity_max-spot2.velocity)
                    elif pattern_gl["Spots_V"] == "-":
                        spot1.velocity -= random.uniform(0,Spot.velocity_max-spot1.velocity)
                        spot2.velocity -= random.uniform(0,Spot.velocity_max-spot2.velocity)
                    elif type(pattern_gl["Spots_V"]) in (int,float):
                        spot1.velocity += pattern_gl["Spots_V"]
                        spot2.velocity += pattern_gl["Spots_V"]
                    elif pattern_gl["Spots_V"] == True:
                        spot1.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
                        spot2.velocity = random.uniform(Spot.velocity_min,Spot.velocity_max)
            
                if pattern_gl["Spots_C"] == True:
                    spot1.color = f"\033[{random.randint(0,2)};{random.randint(30,37)}{spot1.color[6:]}"
                    spot2.color = f"\033[{random.randint(0,2)};{random.randint(30,37)}{spot1.color[6:]}"

                if pattern_gl["C-V"]:    
                    Spot.c_v(spot1)
                    Spot.c_v(spot2)

                if pattern_gl["Spots_Ls"]:
                    theta = angle((spot1.theta+spot2.theta)/2)+random.randint(-10,10)
                    Ls_spots_gl.append(Spot(Ls=True,theta=theta,pos=copy.deepcopy(spot1.pos)))
                    Ls_spots_gl.append(Spot(Ls=True,theta=theta+180,pos=copy.deepcopy(spot2.pos)))

                while int(spot1.pos[0]) == int(spot2.pos[0]) and int(spot1.pos[1]) == int(spot2.pos[1]):
                    # Split them to make they'll not produce more than 2 Ls in one hit
                    Spot.move(spot1)
                    Spot.move(spot2)

def coordinate_init():
    '''Initiate the coordinate dict. With out it, the spots' track will be left instead of being wiped'''
    global frame_gl
    coordinate = {}
    for y in range(0,frame_gl[1]+2):
        coordinate[y] = {}
    for x in range(0,frame_gl[0]+2):    # The top and bottom line of the frame
        coordinate[0][x],coordinate[frame_gl[1]+1][x] = frame_gl[2],frame_gl[2]
    for y in range(1,frame_gl[1]+1):    # The left and right line of the frame
        coordinate[y][0],coordinate[y][frame_gl[0]+1] = frame_gl[2],frame_gl[2]
    return coordinate

def spot_to_coordinate(spot,is_Ls):
    global coordinate_gl,spots_gl,Errors_gl
    if Int(spot.pos[0]) in range(frame_gl[0]+2) and Int(spot.pos[1]) in range(frame_gl[1]+2):
        coordinate_gl[Int(spot.pos[1])][Int(spot.pos[0])] = spot.color
    else:    # The spot is out of the frame range
        try:
            if is_Ls == True:
                Ls_spots_gl.remove(spot)
            elif is_Ls == False:
                spots_gl.remove(spot)
        except ValueError:    # sometimes it just occurs, don't know why
            # The spot that should be delete but is not in its list will be collected
            Errors_gl.append(vars(spot))    # Can be accessed by "E"

def draw(i_gl,y_axis = False):
    '''Put all these on display'''
    global coordinate_gl,space_gl
    print("\033[F"*(frame_gl[1]+10),end='')
    img = []
    for y in range(0,frame_gl[1]+2):
        if y_axis:
            img.append(f"{y}\t")
        for x in range(0,frame_gl[0]+2):
            img.append(f"{coordinate_gl[y][x] if x in coordinate_gl[y].keys() else space_gl}")
        img.append("\n")
    frame = "".join(img) + i_gl
    print(frame,end='\n')
    return frame

def xward(frames_gl,fbward):
    '''Replay the previous frames frame by frame, also support frames later'''
    global command_gl,frame_gl
    def k_i():  # key input
        while True:
            key = msvcrt.getwch()
            if key == ',':
                key = "backward"
                return key
            elif key == '.':
                key = "forward"
                return key
            elif key == ' ':
                key = "continue"
                return key

    def d(frames_gl):   # draw
        print("\033[F"*(frame_gl[1]+10),end='')
        print(frames_gl[frames_gl[0]])

    while True:
        # Previous frames
        if fbward == "forward" and (frames_gl[0]+1) in range(-len(frames_gl)+1,0):
            frames_gl[0] += 1
            d(frames_gl)
            fbward = k_i()
        elif fbward == "backward" and (frames_gl[0]-1) in range(-len(frames_gl)+1,0):
            frames_gl[0] -= 1
            d(frames_gl)
            fbward = k_i()
        # Display the frame one by one
        elif fbward == "forward":
            frames_gl[0] = -1
            command_gl = "standby"
            break
        # Cycle
        elif fbward == "backward":
            frames_gl[0] = -1
            d(frames_gl)
            fbward = k_i()

        elif fbward == "continue":
            frames_gl[0] = -1
            command_gl = None
            break
        elif fbward == "standby":
            fbward = k_i()

def key_input():
    '''A func in a sub-thread. Listening to the keyboard.'''
    global command_gl,pattern_gl,spots_gl,Ls_spots_gl,coordinate_gl,lines_gl,twist_gl
    spot_additon_count = 0
    lines_gl = False
    command_gl = None
    while True:       
        while command_gl != None:
            pass

        key = msvcrt.getwch()
        
        if key == '/':
            command_gl = "command"
        elif key == 'L':
            command_gl = "list"
        elif key == 'Q':
            command_gl = "quit"
            break
        elif key == ' ':
            command_gl = "pause"

        elif key == ',':
            command_gl = 'backward'
        elif key == '.':
            command_gl = 'forward'

        elif key == 'r':
            twist_gl = 0
            os.system('cls')
        
        elif key == 'E':
            command_gl = "errors"
        
        elif key == 'l':
            lines_gl = not lines_gl
        elif key == 'b':
            pattern_gl["Walls_B"] = not pattern_gl["Walls_B"]
        elif key == 's':
            pattern_gl["Walls_Ls"] = not pattern_gl["Walls_Ls"]
        elif key == 'B':
            pattern_gl["Spots_B"] = not pattern_gl["Spots_B"]
        elif key == 'S':
            pattern_gl["Spots_Ls"] = not pattern_gl["Spots_Ls"]
        
        elif key == 't':
            pattern_gl["Mov_T"] = not pattern_gl["Mov_T"]

        elif key == '4':
            pattern_gl["Gen_L"] = not pattern_gl["Gen_L"]
            pattern_gl["Gen_count"] = [key for key in ("Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P") if pattern_gl[key]]
        elif key == '6':
            pattern_gl["Gen_R"] = not pattern_gl["Gen_R"]
            pattern_gl["Gen_count"] = [key for key in ("Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P") if pattern_gl[key]]
        elif key == '8':
            pattern_gl["Gen_T"] = not pattern_gl["Gen_T"]
            pattern_gl["Gen_count"] = [key for key in ("Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P") if pattern_gl[key]]
        elif key == '2':
            pattern_gl["Gen_B"] = not pattern_gl["Gen_B"]
            pattern_gl["Gen_count"] = [key for key in ("Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P") if pattern_gl[key]]
        elif key == '5':
            command_gl = "Gen_chance"
        
        elif key == '7':
            pattern_gl["Gen_Ran"] = not pattern_gl["Gen_Ran"]
            pattern_gl["Gen_count"] = [key for key in ("Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P") if pattern_gl[key]]
        elif key == '9':
            pattern_gl["Gen_P"] = not pattern_gl["Gen_P"]
            pattern_gl["Gen_count"] = [key for key in ("Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P") if pattern_gl[key]]
        
        elif key == '+':
            spot_additon_count+=1
            spots_gl.append(Spot(name=f"Manual Added Spot No.{spot_additon_count}"))
        elif key == '-':
            tributes = []
            for spot in spots_gl:
                if not spot.survivor:
                    tributes.append(spot)
            if len(tributes) > 0:
                spots_gl.remove(tributes[random.randint(0,len(tributes)-1)])

def I():
    '''The information bar below the frame'''
    global i_gl,frames_count_gl,timegap_gl,fps_gl,twist_gl,Errors_gl
    indicator = (
                "\033[0;31m██\033[0m",
                "\033[1;31m██\033[0m",
                "\033[1;33m██\033[0m",
                "\033[2;32m██\033[0m",
                "\033[1;32m██\033[0m",
                )
    while True:
        framerate = frames_count_gl/timegap_gl
        df = abs(framerate-fps_gl)
        dt = 1/fps_gl-1/framerate
        if df > 1 and abs(twist_gl) <= 0.05:
            twist_gl += dt/2
        twist_gl = max(-0.05,twist_gl)
        twist_gl = min(0.05,twist_gl)

        i_gl = f"{framerate:.0f}fps {1/framerate:.3f}s    \
{indicator[min(4,int(framerate/fps_gl//0.2))]}\
{100*(framerate/fps_gl):.3f}%    \
Spots:{len(spots_gl)}  Ls:{len(Ls_spots_gl)}  \
Errors:{len(Errors_gl)}    \
All:{len(spots_gl)+len(Ls_spots_gl)}        {twist_gl:.3f}s   {df:.3f}fps   {dt:.3f}s         "
        frames_count_gl = 0.0001
        
        time.sleep(timegap_gl)

def command():  
    '''
    The function is meant to be powerful.
    Block the function itself to block main and make a dead loop to block the Input.

    Going well, end after changes have been made
    Unexisted command, block main and show all supported command, press any key to continue
    False syntax, block main and show the correct formation of the command
    '''
    global command_gl,frame_gl,fps_gl,pattern_gl,point_gl,color_dict_gl,space_gl
    exception = False
    command = input('/')
    command = command.split() if len(command.split())!=0 else [None,None]

    if command[0] == "frame":
        global coordinate_gl
        if len(command) == 4:
            frame_gl[2] = command[3]
        if len(command) == 3 and command[1].isdigit() and command[2].isdigit():
            frame_gl[0],frame_gl[1] = int(command[1]),int(command[2])
            coordinate_gl = coordinate_init()
        else:
            exception = True
            print("\033[33;1m",end='')
            print("frame -width -height -(color)")
            print("\033[0;33m",end='')
            print("\t-width and -height should be positive integers;")
            print("\t-(color) is optional and should be in form of \"\\033[{num connected with ;}m{str}\\033[0m\".")
            print("\033[0m",end='')

    elif command[0] == "fps":
        try: 
            fps_gl = float(command[1])
        except (IndexError,ValueError): 
            exception = True
            print("\033[33;1m",end='')
            print("/fps -frames_gl_per_second")
            print("\033[0;33m",end='')
            print("\t-frames_gl_per_second should be a positive float.")
            print("\033[0m",end='')

    elif command[0] == "pattern":
        if len(command) == 3:
            try:
                pattern_key = command[1].split(",")
                pattern_val = command[2].split(",")
                if len(pattern_key) != len(pattern_val):
                    raise Exception
                for index,key in enumerate(pattern_key):
                    try:    
                        if pattern_val in (["y"],["Y"],["T"],["True"],["t"]):
                            pattern_gl[key] = True
                        elif pattern_val in (["n"],["N"],["F"],["False"],["f"]):
                            pattern_gl[key] = False
                        else:
                            pattern_gl[key] = float(pattern_val[index])
                    except ValueError:
                        pattern_gl[key] = pattern_val[index]
                pattern_gl["Gen_count"] = [key for key in ("Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P") if pattern_gl[key]]
            except (Exception,KeyError):
                exception = True
                
        elif len(command) == 2 and command[1] in ("lst","l","list"):
            exception = True
            for key in pattern_gl.keys():
                print(key,"    \t",pattern_gl[key])
        elif len(command) == 2:
            preset_pattern(command[1])
        else:    exception = True
        if exception:
            print("\033[33;1m",end='')
            print("/pattern -keys -values")
            print("\033[0;33m",end='')
            print("\t-keys should be one or a few keys in pattern_gl, connected with \",\";")
            print("\t-values should be the values to the keys above, connected with \",\", in the same order.")
            print("\033[0m",end='')

    elif command[0] == "point":
        try:
            if len(command) == 2:
                point_gl.pop(int(command[1]))
                if len(point_gl) == 0:
                    point_gl.append((-1,-1))
            elif len(command) == 3:
                point_gl = [(float(command[1]),float(command[2]))]
            elif len(command) == 4 and command[1] in ("a","A","add","Add"):
                point_gl.append((float(command[2]),float(command[3])))
            elif len(command) == 4 and command[1] in ("r","R","remove","Remove"):
                removal = (float(command[2]),float(command[3]))
                point_gl.remove(removal)
                if len(point_gl) == 0:
                    point_gl.append((-1,-1))
            elif len(command) == 4:
                point_gl[int(command[1])] = (float(command[1]),float(command[2]))
            elif len(command) == 5:
                index = point_gl.index((float(command[1]),float(command[2])))
                point_gl[index] = (float(command[3]),float(command[4]))
        except (ValueError,TypeError):    
            exception = True
            print("\033[33;1m",end='')
            print("/point -index")
            print("\033[0;33m",end='')
            print("\t-index is the index of the point that will be removed;\n")
            print("\033[33;1m",end='')
            print("/point -coordinate_x -coordinate_y")
            print("\033[0;33m",end='')
            print("\t-coordinate_x&y should be positive float number.\n")
            print("\033[33;1m",end='')
            print("/point -type -coordinate_x -coordinate_y")
            print("\033[0;33m",end='')
            print("\t-type should be whether in:")
            print("\t\t(\"a\",\"A\",\"add\",\"Add\") or (\"r\",\"R\",\"remove\",\"Remove\";")
            print("\t\tThe first one will add a new point while the latter one will remove one;")
            print("\t-coordinate_x&y should be positive float number.\n")
            print("\033[33;1m",end='')
            print("/point -index -coordinate_x -coordinate_y")
            print("\033[0;33m",end='')
            print("\t-index is the index of the point that will be modified;")
            print("\t-coordinate_x&y should be positive float number.\n")
            print("\033[33;1m",end='')
            print("/point -modified_coordinate_x -modified_coordinate_y -coordinate_x -coordinate_y")
            print("\033[0;33m",end='')
            print("\t--modified_coordinate_x&y is the coordinate that will be modified;")
            print("\t-coordinate_x&y should be positive float number.\n")
            print("\033[0m",end='')

    elif command[0] == "list":
        if len(command) == 1:
            info(spot=False,Ls=False)
        elif len(command) == 2 and command[1] in ("L","l","Ls","Little spots","little spots","ls"):
            info(spot=False,Ls=True)
        elif len(command) == 2 and command[1] in ("S","s","Spots","spots","Spot","spot"):
            info(spot=True,Ls=False)
        elif len(command) == 2 and command[1] in ("A","a","All","all"):
            info(spot=True,Ls=True)

        else:
            exception = True
            print("\033[33;1m",end='')
            print("/list -(L/l)")
            print("\033[0;33m",end='')
            print("\t-(L/l) is optional and with \"L\" or \"l\", it'll show Little spots.")
            print("\033[0m",end='')

    elif command[0] == "attribute":
        try:
            if command[1] == "health":
                Spot.health = float(command[2])
            elif command[1] == "Ls_health":    
                Spot.Ls_health = float(command[2])
            elif command[1] == "H_w":
                Spot.H_w = float(command[2])
            elif command[1] == "H_s":
                Spot.H_s = float(command[2])
            elif command[1] == "H_m":
                Spot.H_m = float(command[2])
            elif command[1] == "velocity_max":
                Spot.velocity_max = float(command[2])
                Spot.v_lvl(v1=Spot.velocity_max,v0=Spot.velocity_min)
            elif command[1] == "velocity_min":
                Spot.velocity_min = float(command[2])
                Spot.v_lvl(v1=Spot.velocity_max,v0=Spot.velocity_min)
            else:
                exception = True
        except (ValueError,IndexError):
            exception = True
        if exception == True:
            print("\033[33;1m",end='')
            print("/attribute -spot.attribute -val")
            print("\033[0;33m",end='')
            print("\t-spot.attribute should be in health,Ls_health,H_w,H_s,H_m,velocity_max,velocity_min;")
            print("\t-val should be a float.")
            print("\033[0m",end='')
            
    elif command[0] == "spot":
        if len(command) >= 4:    
            found = False
            if command[1] == "i_gl" or command[1] == "I" or command[1] == "index":
                for spot in spots_gl:
                    if str(spot.index) == command[2]:    
                        found = True
                        break
            elif command[1] == "n" or command[1] == "N" or command[1] == "name":
                for spot in spots_gl:
                    if str(spot.name) == command[2]:   
                        found = True
                        break
            else:
                exception = True
            
            if found:
                if command[3] in ("n","N","name"):
                    spot.name = command[4]
                
                elif command[3] in ("c","C","color"):
                    cmd_clr = command[4].split("_",2)
                    if len(cmd_clr) == 1 and command[4] in color_dict_gl.keys():
                        spot.color = color_dict_gl[command[4]]
                    
                    elif len(cmd_clr) == 2 and cmd_clr[1] in color_dict_gl.keys():
                        spot.color = color_dict_gl[cmd_clr[1]]
                        if cmd_clr[0] == "dark":
                            spot.color = f"{spot.color[:2]}2{spot.color[3:]}"
                        elif cmd_clr[0] == "bright":
                            spot.color = f"{spot.color[:2]}1{spot.color[3:]}"
                    
                    elif len(cmd_clr) == 2 and cmd_clr[0] in color_dict_gl.keys():
                        spot.color = color_dict_gl[(cmd_clr)[0]]
                        spot.color = f"{spot.color[:2]}{repr(cmd_clr[1])}{spot.color[3:]}"

                    elif len(cmd_clr) == 3 and cmd_clr[1] in color_dict_gl.keys():
                        spot.color = color_dict_gl[(cmd_clr)[1]]
                        if cmd_clr[0] == "dark":
                            spot.color = f"{spot.color[:2]}2{spot.color[3:]}"
                        elif cmd_clr[0] == "bright":
                            spot.color = f"{spot.color[:2]}1{spot.color[3:]}"
                        spot.color = f"{spot.color[:7]}{cmd_clr[2]}{spot.color[-4:]}"

                    else:    spot.color = command[4]

                elif command[3] in ("v","V","velocity"):
                    try:
                        spot.velocity = float(command[4])
                    except ValueError:
                        print("\n\033[1;33mVelocity should be a float number.\033[0m")
                        exception = True
                
                elif command[3] in ("t","T","theta"):
                    try:
                        spot.theta = float(command[4])
                    except ValueError:
                        print("\n\033[1;33mTheta should be a float number.\033[0m")
                        exception = True
                        
                elif command[3] in ("h","H","health"):
                    try:
                        spot.health = float(command[4])
                    except ValueError:
                        print("\n\033[1;33mHealth should be a float number.\033[0m")
                        exception = True

                elif command[3] in ("p","P","position","pos"):
                    try:
                        spot.pos[0] = float(command[4]) if float(command[4]) in range(0,frame_gl[0]+2) else int("")
                        spot.pos[1] = float(command[5]) if float(command[5]) in range(0,frame_gl[1]+2) else int("")
                    except ValueError:
                        print("\n\033[1;33mPositon should be float and ranging in the frame.\033[0m")
                        exception = True

                elif command[3] in ("s","S","survivor"):
                    if len(command) == 4:
                        spot.survivor = not spot.survivor
                    else:
                        spot.survivor = command[4]

                elif command[3] in ("k","K","kill"):
                    if spot in spots_gl:
                        spots_gl.remove(spot)
                    elif spot in Ls_spots_gl:
                        Ls_spots_gl.remove(spot)

                else: 
                    exception = True                    
            elif not found:
                print("\n\033[1;33mSpot Unfound\033[0m",end="\n\n")
                exception = True
        
        else:
            exception = True

        if exception:
            print("\033[33;1m",end='')
            print("/spot -searching_type -index_or_name -attribute -value")
            print("\033[0;33m",end='')
            print("\t-searching_type should be either by index or name,")
            print("\t\t\"i_gl\" or \"I\" or \"index\" for index,")
            print("\t\t\"n\" or \"N\" or \"name\" for name;")
            print("\t-index_or_name should be the index or name of the spot that will be modified,")
            print("\t\t index should be an integer;")
            print("\t--attribute should be one of the spots attribute,")
            print("\t\tincluding name, color, velocity, theta, pos, health, survivor")
            print("\t\t\"n\" or \"N\" or \"name\" for name,")
            print("\t\t\"c\" or \"C\" or \"color\" for color,")
            print("\t\t\"v\" or \"V\" or \"velocity\" for velocity,")
            print("\t\t\"t\" or \"T\" or \"theta\" for theta,")
            print("\t\t\"p\" or \"P\" or \"position\" for position,")
            print("\t\t\"h\" or \"H\" or \"health\" for health,")
            print("\t\t\"s\" or \"S\" or \"survivor\" for survivor,")
            print("\t\t\"k\" or \"K\" or \"kill\" to kill the spot,")
            print("\t-value should be the value that will replace the former one,")
            print("\t\tname, as a string, can be anything;")
            print("\t\tcolor includes color and the character(s) to represent the spot and has 5 formations,")
            print("\t\t\t1 black/red/green/yellow/blue/magenta/cyan/white" ,)
            print("\t\t\t2 dark/bright/(normal) + \"_\" + black/red/green/yellow/blue/magenta/cyan/white ,")
            print("\t\t\t3 black/red/green/yellow/blue/magenta/cyan/white + \"_\" + the character(s) to represent the spot ,")
            print("\t\t\t4 dark/bright/(normal) + \"_\" + black/red/green/yellow/blue/magenta/cyan/white+ \"_\" + the character(s) to represent the spot ,")
            print("\t\t\t5 In the formation like \\033[1;36m**\\033[0m ;")
            print("\t\tVelocity, theta and health all should be a float or an integer.")
            print("\033[0m",end='')

    elif command[0] == "new":
        if len(command) == 1:
            try:
                print("Type in the attributes of the spot you're going to create.")
                print("Press Enter to skip and generated automatically")
                name = str(input("Name (String):"))
                if name == "": name = "Generated by Command"

                clr = input("Color (String):")
                if clr == "": 
                    color = None
                else:
                    clr = clr.split("_",2)
                    if len(clr) == 1 and str(clr[0]) in color_dict_gl.keys():
                        color = color_dict_gl[str(clr[0])]
                    elif len(clr) == 2 and clr[1] in color_dict_gl.keys():
                        color = color_dict_gl[clr[1]]
                        if clr[0] == "dark":
                            color = f"{color[:2]}2{color[3:]}"
                        elif clr[0] == "bright":
                            color = f"{color[:2]}1{color[3:]}"                
                    elif len(clr) == 2 and clr[0] in color_dict_gl.keys():
                        color = color_dict_gl[(clr)[0]]
                        color = f"{color[:2]}{repr(clr[1])}{color[3:]}"
                    elif len(clr) == 3 and clr[1] in color_dict_gl.keys():
                        color = color_dict_gl[(clr)[1]]
                        if clr[0] == "dark":
                            color = f"{color[:2]}2{color[3:]}"
                        elif clr[0] == "bright":
                            color = f"{color[:2]}1{color[3:]}"
                        color = f"{color[:7]}{clr[2]}{color[-4:]}"
                    else: color = clr

                velocity = input("Velocity (Float or Int):")
                if velocity == "": velocity = None
                else: velocity = float(velocity)

                theta = input("Theta (Float or Int):")
                if theta == "": theta = None
                else: theta = float(theta)
                
                pos = input("Position (2 Ints or Floats connected by space or _):")
                if pos == "": 
                    pos = None
                else:
                    if len(pos.split()) == 2:
                        pos = pos.split()
                    elif len(pos.split(",")) == 2:
                        pos = pos.split(",")
                    elif pos != "": 
                        raise Exception
                    pos[0] = float(pos[0])
                    pos[1] = float(pos[1])

                Ls = input("Is Little spot (Bool):")
                if Ls in ("True","true","Yes","yes","Y","y"): Ls = True
                else: Ls = False
                survivor = input("Is Survivor (Bool):")
                if survivor in ("True","true","Yes","yes","Y","y"): survivor = True
                else: survivor = False

                if Ls:
                    if velocity == None: velocity = Spot.velocity_max
                    if pos == None:
                        pos = random.choice(pattern_gl["Gen_count"])
                        if pos == "Gen_Ran":
                            pos = [random.randint(1,frame_gl[0]),random.randint(1,frame_gl[1])]
                        elif pos == "Gen_P":
                            pos = list(copy.deepcopy(point_gl[random.randint(0,len(point_gl)-1)]))
                        elif pos == "Gen_L":
                            pos = [1,random.randint(1,frame_gl[1])]
                        elif pos == "Gen_R":
                            pos = [frame_gl[0],random.randint(1,frame_gl[1])]
                        elif pos == "Gen_T":
                            pos = [random.randint(1,frame_gl[0]),frame_gl[1]]
                        elif pos == "Gen_B":
                            pos = [random.randint(1,frame_gl[0]),1]
                    Ls_spots_gl.append(Spot(True,name,pos,theta,velocity,color))
                    if survivor == True: Ls_spots_gl[-1].survivor = True
                else:
                    spots_gl.append(Spot(False,name,pos,theta,velocity,color))
                    if survivor == True: spots_gl[-1].survivor = True
            except:
                exception = True
        elif len(command) == 2 and command[1].isnumeric() and int(command[1]) > 0:
            for _ in range(int(command[1])):
                spots_gl.append(Spot())
        else:
            exception = True
        if exception == True:
            print("\033[33;1m",end='')
            print("/new")
            print("\033[0;33m",end='')
            print("\tJust follow the instruction popped up when typing in the command;\n")
            print("\033[33;1m",end='')
            print("/new -number")
            print("\033[0;33m",end='')
            print("\t-number should be positive, which represents how many spots will be generated.")
            print("\033[0m",end='')

    elif command[0] == "space":
        space = input("Space (-color_)-space:")
        if len(space.split("_",1))==2 and space.split("_",1)[0] in color_dict_gl.keys():
            space = space.split("_",1) 
            space1 = color_dict_gl[space[0]]
            space = f"\033[4{space1[5]}m{space[1]}\033[0m"
        else:
            if space in color_dict_gl.keys():
                space = color_dict_gl[space]
                space = f"\033[4{space[5]}m{space_gl[5:]}"
            else: space = f"{space_gl[:5]}{space}\033[0m"
        space_gl = space

    elif command[0] == "clear":
        if len(command) == 1:
            spots_gl.clear()
            Ls_spots_gl.clear()
        elif len(command) == 2:
            if command[1] in ("l","L","Ls","LS","ls",
                            "Little_spot","little_spot","LITTLE_SPOT","Little_spots","little_spots","LITTLE_SPOTs"):
                Ls_spots_gl.clear()
            elif command[1] in ("s","S","spot","Spot","spots","Spots","SPOT","SPOTS"):
                spots_gl.clear()
        
    elif command[0] == "buffer":
        global frames_gl
        if len(command) == 1:
            print(f"{len(frames_gl)-1}")
            print("------Press Any Key to Continue------")
            msvcrt.getwch()
            os.system('cls')
        elif len(command) == 2 and command[1].isnumeric() and int(command[1]) > 0:
            command = int(command[1])

            if command > len(frames_gl)-1:
                for _ in range(command-len(frames_gl)+1):
                    frames_gl.insert(1,"")

            elif command < len(frames_gl)-1:
                for _ in range(len(frames_gl)-1-command):
                    frames_gl.pop(1)
        else:
            exception = True
            print("\033[33;1m",end='')
            print("/buffer -(number)")
            print("\033[0;33m",end='')
            print("\t/buffer will show the current buffer;")
            print("\t-(number) is the frames buffer number you're going to set.")
            print("\033[0m",end='')

    elif command[0] in ("indi","indicator"):
        global timegap_gl
        if len(command) == 1:
            print(timegap_gl)
            print("------Press Any Key to Continue------")
            msvcrt.getwch()
            os.system('cls')
        elif len(command) == 2:
            try:
                command = float(command[1])
                if command <= 0:
                    raise TypeError
                else:
                    timegap_gl = command
            except TypeError:
                exception = True
        else:
            exception = True
        if exception == True:
            print("\033[33;1m",end='')
            print("/indi(cator) -(number)")
            print("\033[0;33m",end='')
            print("\t/indi or /indicator will show the current indicator updating time gap;")
            print("\t-(number) is the time gap you're going to set for the indicator to update.")
            print("\033[0m",end='')

    elif command[0] == "default":
        if len(command) == 1:
            default(init=False)
        elif len(command) == 2 and command[1] in ("all","All","a","A","d","D","i_gl","I","init","Init"):
            default(init=True)
        else:
            exception = True
            print("\033[33;1m",end='')
            print("/default -(init)")
            print("\033[0;33m",end='')
            print("\t/default will initiate some of the variables;")
            print("\t-(init) will initiate all the variables if it's in the following list.")
            print("\t\t\"all\",\"All\",\"a\",\"A\",\"d\",\"D\",\"i_gl\",\"I\",\"init\",\"Init\"")
            print("\033[0m",end='')

    else:    # Show all supported commands
        exception = True
        print("Supported command:")
        print("/frame -width -height -(color)")
        print("/fps -frames_gl_per_second")
        print("/pattern -keys -values")
        print("/pattern -values")
        print("/point -*")
        print("/list -*")
        print("/attribute -spot.attribute -val")
        print("/spot -searching_type -index_or_name -attribute -value")
        print("/new")
        print("/space -color_code_of_space")
        print("/clear -(spots_or_Little_spots)")
        print("/buffer -(number)")
        print("/indi(cator) -(number)")
    
    if exception:    # Pop up when any error occurs
        print("\n------Press Any Key to Continue------",end='',flush=True)
        msvcrt.getwch()
        os.system('cls')
    
    os.system("cls")
    command_gl = None

def info(spot=True,Ls=False):
    global spots_gl
    print(f'''
{"--"*frame_gl[0]}
Active Thread(s): {threading.enumerate()}
Frame Size: {frame_gl[0]}x{frame_gl[1]}    \tFrame Color: {frame_gl[2]}  {repr(frame_gl[2])}   FPS: {fps_gl}
Generating Point: {point_gl}\tSpace: {space_gl}\033[0m  {repr(space_gl)}
Health: {Spot.health} \t\tLs Health: {Spot.Ls_health}
H_m: {Spot.H_m}    \t\tH_w: {Spot.H_w}    \t\tH_s: {Spot.H_s}
velocity_max: {Spot.velocity_max}   \tvelocity_min: {Spot.velocity_min}
velocity_level1: {Spot.velocity_level1}   \tvelocity_level2: {Spot.velocity_level2}   \t\
velocity_level3: {Spot.velocity_level3}
{'--'*frame_gl[0]}

Pattern:
Gen_count: {pattern_gl['Gen_count']}
Gen_Ran: {pattern_gl['Gen_Ran']}    \tGen_P: {pattern_gl['Gen_P']}
Gen_L: {pattern_gl['Gen_L']}     \tGen_R: {pattern_gl['Gen_R']}
Gen_T: {pattern_gl['Gen_T']}     \tGen_B: {pattern_gl['Gen_B']}
Gen_chance: {pattern_gl['Gen_chance']*100:.3f}%
Gen_t: {pattern_gl['Gen_t']}%

Mov_H: {pattern_gl['Mov_H']}     \tD: {pattern_gl['D']}
Mov_T: {pattern_gl['Mov_T']}

C-V: {pattern_gl['C-V']}

Walls_B: {pattern_gl['Walls_B']}    \tWalls_Ls: {pattern_gl['Walls_B']}
Walls_V: {pattern_gl['Walls_V']}    \tWalls_C: {pattern_gl['Walls_C']}
Walls_H: {pattern_gl['Walls_H']}

Spots_B: {pattern_gl['Spots_B']}    \tSpots_Ls: {pattern_gl['Spots_Ls']}
Spots_C: {pattern_gl['Spots_C']}    \tSpots_V: {pattern_gl['Spots_V']}
Spots_H: {pattern_gl['Spots_H']}
{'--'*frame_gl[0]}''')

    if spot == True:
        spots_list = []
        for spot in spots_gl:
            spots_list.append(f'''
Name: {spot.name}     \t Index: {spot.index}     \tSurvivor: {spot.survivor} 
Color: {spot.color}     \t{repr(spot.color)}
Velocity: {spot.velocity:.3}          \t\tTheta: {((spot.theta+180)%360-180):.3f}({spot.theta})
Position: ({spot.pos[0]:.3f}, {spot.pos[1]:.3f})     \tHealth: {spot.health}
''')
        print(f"All Spots:                Num:{len(spots_gl)}\n","".join(spots_list))
    
    if Ls == True:
        global Ls_spots_gl
        print('--'*frame_gl[0],"Little spots:                Num:",len(Ls_spots_gl))
        print(f"Name: Ls    Color: \033[1;33m⭐\033[0m \\033[1;33m⭐\\033[0m    velocity: {Spot.velocity_max}")
        Ls_list = []
        for spot in Ls_spots_gl:
            Ls_list.append(f'''
\nHealth: {spot.health:.3}
Position: ({spot.pos[0]:.3f},{spot.pos[1]:.3f})     \tTheta: {((spot.theta+180)%360-180):.3f}({spot.theta})
'''   )
        print("".join(Ls_list),"--"*frame_gl[0])

    print("------Press Any Key to Continue------")
    msvcrt.getwch()
    os.system('cls')

def preset_pattern(pattern_name):
    global pattern_gl
    if pattern_name == "Random":
        pattern_gl = {
        "Gen_Ran":  True, 
        "Gen_L":    True,
        "Gen_R":    True,
        "Gen_T":    True,
        "Gen_B":    True,
        "Gen_P":    True,
        "Gen_count":["Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P"],
        "Gen_chance":0.01,
        "Gen_t":    None, 
        "Gen_V":    None, 
        "Gen_C":    None, 

        "Mov_H":    True, 
        "D":    True, 
        "Mov_T":    True,

        "C-V":      True, 

        "Walls_B":  True, 
        "Walls_Ls": False,
        "Walls_C":  True, 
        "Walls_V":  True, 
        "Walls_H":  True, 

        "Spots_B":  True, 
        "Spots_Ls": True, 
        "Spots_C":  True,
        "Spots_V":  False, 
        "Spots_H":  True, 
    }
    elif pattern_name in ("Left","Right","Top","Bottom","L&R","T&B","L","R","T","B","LR","TB","P"):
        pattern_gl = {
        "Gen_Ran":  False, 
        "Gen_L":    False,
        "Gen_R":    False,
        "Gen_T":    False,
        "Gen_B":    False,
        "Gen_P":    False,
        "Gen_chance":0.5,
        "Gen_t":    None,
        "Gen_V":    None, 
        "Gen_C":    None, 

        "Mov_H":    False, 
        "D":    True, 
        "Mov_T":    False, 

        "C-V":      True,  

        "Walls_B":  False, 
        "Walls_Ls": False, 
        "Walls_C":  False, 
        "Walls_V":  False, 
        "Walls_H":  True, 

        "Spots_B":  False, 
        "Spots_Ls": False, 
        "Spots_C":  False, 
        "Spots_V":  False, 
        "Spots_H":  False, 

    }
        if pattern_name in ("Left","L"):
            pattern_gl["Gen_t"] = 0
            pattern_gl["Gen_L"] = True
            pattern_gl["Gen_count"] = ["Gen_L"]
        elif pattern_name in ("Right","R"):
            pattern_gl["Gen_t"] = 180
            pattern_gl["Gen_R"] = True
            pattern_gl["Gen_count"] = ["Gen_R"]
        elif pattern_name in ("L&R","LR"):
            pattern_gl["Gen_t"] = "L&R"
            pattern_gl["Gen_L"],pattern_gl["Gen_R"] = True,True
            pattern_gl["Gen_count"] = ["Gen_L","Gen_R"]
        elif pattern_name in ("Top","T"):
            pattern_gl["Gen_t"] = -90
            pattern_gl["Gen_T"] = True
            pattern_gl["Gen_count"] = ["Gen_T"]
        elif pattern_name in ("Bottom","B"):
            pattern_gl["Gen_t"] = 90
            pattern_gl["Gen_B"] = True
            pattern_gl["Gen_count"] = ["Gen_B"] 
        elif pattern_name in ("T&B","TB"):
            pattern_gl["Gen_t"] = "T&B"
            pattern_gl["Gen_T"],pattern_gl["Gen_B"] = True,True
            pattern_gl["Gen_count"] = ["Gen_T","Gen_B"]
    elif pattern_name in ("Point","P"):
        pattern_gl = {
        "Gen_Ran":  False,   
        "Gen_L":    False,  
        "Gen_R":    False,  
        "Gen_T":    False,  
        "Gen_B":    False,  
        "Gen_P":    True,  
        "Gen_count":["Gen_P"],
        "Gen_chance":0.02,
        "Gen_t":    None,   
        "Gen_V":    None,   
        "Gen_C":    None,   

        "Mov_H":    True,   
        "D":    True,   
        "Mov_T":    True,  

        "C-V":      True,   

        "Walls_B":  True,   
        "Walls_Ls": False,  
        "Walls_C":  True,   
        "Walls_V":  True,   
        "Walls_H":  True,   

        "Spots_B":  True,   
        "Spots_Ls": True,   
        "Spots_C":  True,  
        "Spots_V":  False,   
        "Spots_H":  True,   

    }

def default(init=False):
    global pattern_gl,spots_gl,Ls_spots_gl,frame_gl,fps_gl,point_gl,index_gl,command_gl,coordinate_gl
    global color_dict_gl,space_gl,lines_gl,frames_gl,timegap_gl,twist_gl,Errors_gl
    pattern_gl = {
        "Gen_Ran":  True,       # Random
        "Gen_L":    False,      # Left
        "Gen_R":    False,      # Right
        "Gen_T":    False,       # Top
        "Gen_B":    False,      # Bottom
        "Gen_P":    False,      # Positions
        "Gen_count":["Gen_Ran"],# [key for key in ("Gen_Ran","Gen_L","Gen_R","Gen_T","Gen_B","Gen_P") if pattern_gl[key]]
        "Gen_chance":0,
        "Gen_t":    None,       # Theta    Random if None
        "Gen_V":    None,       # Velocity    Random if None
        "Gen_C":    None,       # Color    Random if None

        "Mov_H":    True,       # Hurt
        "D":        True,       # Die when health is 0 or below
        "Mov_T":    False,      # Random theta

        "C-V":      False,       # Color associated with velocity

        "Walls_B":  True,       # Bouncing
        "Walls_Ls": False,      # Little spots
        "Walls_C":  False,      # Random Color
        "Walls_V":  False,      # Velocity Change   float or int if accurate val  "+"  "-"
        "Walls_H":  True,       # Hurt

        "Spots_B":  True,       # Bouncing
        "Spots_Ls": True,       # Little spots
        "Spots_C":  False,      # Random Color
        "Spots_V":  False,      # Velocity Change   float or int if accurate val  "+"  "-"
        "Spots_H":  True,       # Hurt              

    }
    fps_gl = 144
    twist_gl = 0
    timegap_gl = 0.5
    frame_gl = [72,36,'\033[47m  \033[0m']
    point_gl = [(1,1)]
    Errors_gl = []
    if init:
        lines_gl = False
        space_gl = '\033[40m  \033[0m'
        os.system('cls')
        spots_gl = []
        Ls_spots_gl = []
        coordinate_gl = coordinate_init()
        frames_gl = [-1,]
        for _ in range(48):
            frames_gl.append("")
        index_gl = 0
        color_dict_gl = {
        "black":"\033[0;30m██\033[0m",
        "red":"\033[0;31m██\033[0m",
        "green":"\033[0;32m██\033[0m",
        "yellow":"\033[0;33m██\033[0m",
        "blue":"\033[0;34m██\033[0m",
        "magenta":"\033[0;35m██\033[0m",
        "cyan":"\033[0;36m██\033[0m",
        "white":"\033[0;37m██\033[0m",
        }
        command_gl = None

if __name__ == '__main__':
    import time,random,msvcrt,threading,os,math,copy

    global pattern_gl,spots_gl,Ls_spots_gl,frame_gl,fps_gl,lines_gl,frames_gl,i_gl
    global frames_count_gl,twist_gl

    default(True)
    randomly_spot_count,frame_start,i_gl = 0,0,""
    frames_count_gl,twist_gl = fps_gl * timegap_gl,0

    threading.Thread(target=key_input,daemon=True).start()
    threading.Thread(target=I,daemon=True).start()

    while True:
        frames_count_gl+=1
        frame_start = time.time()

        if not lines_gl:
            coordinate_gl = coordinate_init()

        # Update the frame
        for x in range(0,frame_gl[0]+2):
            coordinate_gl[0][x],coordinate_gl[frame_gl[1]+1][x] = frame_gl[2],frame_gl[2]
        for y in range(1,frame_gl[1]+1):
            coordinate_gl[y][0],coordinate_gl[y][frame_gl[0]+1] = frame_gl[2],frame_gl[2]
        

        # Randomly add a new spot
        if len(pattern_gl["Gen_count"])!=0 and random.random()<= pattern_gl["Gen_chance"]:
            randomly_spot_count += 1
            spots_gl.append(Spot(name = f"Randomly Added Spot No.{randomly_spot_count}"))

        for Ls_spot in Ls_spots_gl:
            Spot.die(Ls_spot,"Ls")
            Ls_spot.move()
            if pattern_gl["Walls_B"]:    Spot.wall(Ls_spot, is_Ls=True)
            spot_to_coordinate(Ls_spot,True)
        
        for spot in spots_gl:
            Spot.die(spot,"spot")
            spot.move()
            if pattern_gl["Walls_B"]:    Spot.wall(spot, is_Ls=False)
            spot_to_coordinate(spot,False)

        if pattern_gl["Spots_B"]:    
            spots_hit()

        # frame buffering
        frames_gl.pop(1)
        frames_gl.append(draw(i_gl))

        if command_gl == "command":
            command()
            command_gl = None
            frames_count_gl,twist_gl = fps_gl * timegap_gl,0
        elif command_gl == "quit":
            os.system('cls')
            exit()
        elif command_gl == "list":
            info()
            command_gl = None
            frames_count_gl,twist_gl = fps_gl * timegap_gl,0
        elif command_gl in ("forward","backward","standby"):
            xward(frames_gl, fbward = command_gl)
            frames_count_gl,twist_gl = fps_gl * timegap_gl,0
        elif command_gl == "Gen_chance":
            c = input("Gen_chance: ")
            try:
                c = float(c)
                if c > 1 or c < 0:
                    del c
                    raise TypeError
                else:
                    pattern_gl["Gen_chance"] = c
                    del c
                    os.system('cls')
                    command_gl = None
                    frames_count_gl,twist_gl = fps_gl * timegap_gl,0
            except TypeError:
                print("Gen_chance should be a float number in the range of [0,1], \
which indicate the probability of generating a new spot in a frame.")
                del c
                print("------Press any key to continue------")
                msvcrt.getwch()
                os.system('cls')
                command_gl = None
                frames_count_gl,twist_gl = fps_gl * timegap_gl,0
        elif command_gl == "errors":
            for intel in Errors_gl:
                print(intel)
            print("------Press any key to continue------")
            msvcrt.getwch()
            os.system('cls')
            command_gl = None
            frames_count_gl,twist_gl = fps_gl * timegap_gl,0
        while command_gl == "pause":
            if msvcrt.getwch() == ' ':
                command_gl = None
                frames_count_gl,twist_gl = fps_gl * timegap_gl,0
        
        frame_duration = time.time()-frame_start
        time.sleep(max(0,1/fps_gl-frame_duration + twist_gl))    # keep the framerate