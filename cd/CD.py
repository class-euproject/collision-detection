# -*- coding: utf-8 -*-

# /*
#  * Copyright (C) 2019  Atos Spain SA. All rights reserved.
#  *
#  * This file is part of pCEP.
#  *
#  * pCEP is free software: you can redistribute it and/or modify it under the
#  * terms of the Apache License, Version 2.0 (the License);
#  *
#  * http://www.apache.org/licenses/LICENSE-2.0
#  *
#  * The software is provided "AS IS", without any warranty of any kind, express or implied,
#  * including but not limited to the warranties of merchantability, fitness for a particular
#  * purpose and noninfringement, in no event shall the authors or copyright holders be
#  * liable for any claim, damages or other liability, whether in action of contract, tort or
#  * otherwise, arising from, out of or in connection with the software or the use or other
#  * dealings in the software.
#  *
#  * See README file for the full disclaimer information and LICENSE file for full license
#  * information in the project root.
#  *
#  * Authors:  Atos Research and Innovation, Atos SPAIN SA
#  */

import numpy as np

import warnings
warnings.simplefilter('ignore', np.RankWarning)


COLLISION_THRESHOLD = 2 # max distance in seconds to alert a collision


def transformObjectFromFile(input_object):
    v_id = input_object["v_id"]
    x = input_object["x"]
    y = input_object["y"]
    t = input_object["t"]
    return (v_id,x,y,t)

def get_fxy_fxt(x,y,t):
    fxy = np.polyfit(x, y, 2) # The 2 signifies a polynomial of degree 2
    fxt = np.polyfit(x, t, 2) # The 2 signifies a polynomial of degree 2
    return fxy,fxt


def get_vehicle_functions(input_object):
    v_id = input_object[0]
    x = input_object[1]
    y = input_object[2]
    t = input_object[3]
    vehicle,vehicle_t = get_fxy_fxt(x, y, t)
    return (v_id,vehicle,vehicle_t)


def generate_common_x(x1):
    x = np.arange(x1[0],x1[-1]+0.000001,0.000001)    
    return x


def get_f(x,a,b,c):
    return a * x ** 2 + b * x + c


def intersections_no_linear_interpolation(x,f,g,main_object,other_object):

    collisions = []
    
    idx = np.argwhere(np.diff(np.sign(np.array(f) - np.array(g)))).flatten()
    #if len(idx) == 0:
        #print("no intersection")
    for sol in idx:
        #print("Collision:")
        #print("  X: "+str(x[int(sol)]))
        #print("  Y: "+str(f[int(sol)]))
        tv1 = get_f(x[int(sol)],main_object[2][0],main_object[2][1],main_object[2][2])
        tv2 = get_f(x[int(sol)],other_object[2][0],other_object[2][1],other_object[2][2])
        #print("  tv1: "+str(tv1))
        #print("  tv2: "+str(tv2))
        tdiff = abs(tv1/1000 - tv2/1000)
        #print("    tdiff (seconds): "+str(tdiff))
        if (tdiff < COLLISION_THRESHOLD):
        #    print("    WARNING!!!!!!!!!!!! trayectories crossed in the same time (less than 2 seconds of diference)")
            collisions.append((x[int(sol)],f[int(sol)],tv1))
        #else:
        #    print("    trayectories do not crossed in the same time")
        
        return collisions



def interpolated_intercepts(x, y1, y2):
        """Find the intercepts of two curves, given by the same x data"""

        def intercept(point1, point2, point3, point4):
            """find the intersection between two lines
            the first line is defined by the line between point1 and point2
            the first line is defined by the line between point3 and point4
            each point is an (x,y) tuple.

            So, for example, you can find the intersection between
            intercept((0,0), (1,1), (0,1), (1,0)) = (0.5, 0.5)

            Returns: the intercept, in (x,y) format
            """    

            def line(p1, p2):
                A = (p1[1] - p2[1])
                B = (p2[0] - p1[0])
                C = (p1[0]*p2[1] - p2[0]*p1[1])
                return A, B, -C

            def intersection(L1, L2):
                D  = L1[0] * L2[1] - L1[1] * L2[0]
                Dx = L1[2] * L2[1] - L1[1] * L2[2]
                Dy = L1[0] * L2[2] - L1[2] * L2[0]

                x = Dx / D
                y = Dy / D
                return x,y

            L1 = line([point1[0],point1[1]], [point2[0],point2[1]])
            L2 = line([point3[0],point3[1]], [point4[0],point4[1]])

            R = intersection(L1, L2)

            return R

        idxs = np.argwhere(np.diff(np.sign(np.array(y1) - np.array(y2))) != 0)

        xcs = []
        ycs = []

        for idx in idxs:
            xc, yc = intercept((x[int(idx)], y1[int(idx)]),((x[int(idx)+1], y1[int(idx)+1])), ((x[int(idx)], y2[int(idx)])), ((x[int(idx)+1], y2[int(idx)+1])))
            xcs.append(xc)
            ycs.append(yc)
        return np.array(xcs), np.array(ycs)

    
def intersections_linear_interpolation(x,f,g,main_object,other_object):

    collisions = []
    
    # new method!
    xcs, ycs = interpolated_intercepts(x,f,g)
    #if len(xcs) == 0:
        #print("no intersection")
    for xc, yc in zip(xcs, ycs):
        #print("Collision, with linear interpolation:")
        #print("  X: "+str(xc))
        #print("  Y: "+str(yc))
        tv1 = get_f(x[int(xc)],main_object[2][0],main_object[2][1],main_object[2][2])
        tv2 = get_f(x[int(xc)],other_object[2][0],other_object[2][1],other_object[2][2])
        #print("  tv1: "+str(tv1))
        #print("  tv2: "+str(tv2))
        tdiff = abs(tv1/1000 - tv2/1000)
        #print("    tdiff (seconds): "+str(tdiff))
        if (tdiff < COLLISION_THRESHOLD):
        #    print("    WARNING!!!!!!!!!!!! trayectories crossed in the same time (less than 2 seconds of diference)")
            collisions.append((x[int(xc)],f[int(xc)],tv1))
        #else:
        #    print("    trayectories do not crossed in the same time")
        
        return collisions



def collision_detection(main_obj, other_obj):
    
    main_object = get_vehicle_functions(main_obj)
    other_object = get_vehicle_functions(other_obj)
    
    #print("Calculating collisions for "+main_object[0] +" and "+other_object[0])

    x = generate_common_x(main_obj[1])

    f = []
    for xx in x: 
        f.append(get_f(xx,main_object[1][0],main_object[1][1],main_object[1][2]))

    g = []
    for xx in x: 
        g.append(get_f(xx,other_object[1][0],other_object[1][1],other_object[1][2]))


    collisions = intersections_no_linear_interpolation(x,f,g,main_object,other_object)
    #collisions = intersections_linear_interpolation(x,f,g,main_object,other_object)

    return collisions

