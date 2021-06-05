# Collision Detection application
# CLASS Project: https://class-project.eu/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Created on 17 Jun 2020
# @author: Jorge Montero - ATOS
#

import numpy as np
import math

from shapely.geometry import MultiLineString, LineString, Point, Polygon
from shapely.affinity import rotate
from shapely.ops import split, nearest_points

import warnings
warnings.simplefilter('ignore', np.RankWarning)

# CD_TYPE = method to be executed to get collision detections
# 1 -> intersections_no_linear_interpolation (lineal trajectories)
# 2 -> intersections_shapely (linear trajectories with shapely)
# 3 -> intersections_shapely_polygons (with sorrounded area)
CD_TYPE = 3

COLLISION_THRESHOLD = 1 # max distance in seconds to alert a collision
SHAPELY_DISTANCE = 0.00001 # distance to get sorrounded area from vehicles for each side (0.00001 = 1.5 meters)
SHAPELY_ANGLE = 25 # angle to get sorrounded area for pedestrians

def transformObjectFromFile(input_object):
    v_id = input_object["v_id"]
    x = input_object["x"]
    y = input_object["y"]
    t = input_object["t"]
    v_type = input_object["v_type"]
    # ['trajectory_px', 'trajectory_py', 'trajectory_pt', 'geohash', 'obj_id', 'type']
    return (x,y,t,"geohash",v_id,v_type)

def get_fxy_fxt(x,y,t):
    fxy = np.polyfit(x, y, 2) # The 2 signifies a polynomial of degree 2
    fxt = np.polyfit(x, t, 2) # The 2 signifies a polynomial of degree 2
    return fxy,fxt


def get_vehicle_functions(input_object):
    # ['trajectory_px', 'trajectory_py', 'trajectory_pt', 'geohash', 'obj_id', 'type']
    v_id = input_object[4]
    x = input_object[0]
    y = input_object[1]
    t = input_object[2]
    v_type = input_object[5]
    cd_object = (v_id,x,y,t,v_type)
    vehicle,vehicle_t = get_fxy_fxt(x, y, t)
    return (v_id,vehicle,vehicle_t,cd_object)


def generate_common_x(x1):
    x = np.arange(x1[0],x1[-1]+0.000001,0.000001)    
    return x


def get_f(x,a,b,c):
    return a * x ** 2 + b * x + c


def intersections_no_linear_interpolation(x,f,g,main_object,other_object,th_collision):

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

        # check if timestamp is after first object timestamp
        if (tv1 >= main_object[3][3][0]):
            if (tdiff < th_collision):
            #    print("    WARNING!!!!!!!!!!!! trayectories crossed in the same time (less than 2 seconds of diference)")
                collisions.append((x[int(sol)],f[int(sol)],tv1))
            #else:
            #    print("    trayectories do not crossed in the same time")
        
    return collisions


def intersections_shapely(x,f,g,main_object,other_object,th_collision):

    collisions = []

    tp1 = []
    tp2 = []
    for i in range(0,len(main_object[3][1])):
        tp1.append((main_object[3][1][i],main_object[3][2][i]))
        tp2.append((other_object[3][1][i],other_object[3][2][i]))
                
    line1 = LineString(tp1)
    line2 = LineString(tp2)
            
    if line1.intersects(line2):

        intersection = line1.intersection(line2)
        coorX = ""
        coorY = ""
        if isinstance(intersection, Point) or isinstance(intersection, LineString):
            coorX = list(intersection.coords)[0][0]
            coorY = list(intersection.coords)[0][1]
        elif isinstance(intersection, MultiLineString):
            coorX = list((list(intersection.geoms)[0]).coords)[0][0]
            coorY = list((list(intersection.geoms)[0]).coords)[0][1]
        else:
            print("Intersection undefined")
                    
        if coorX != "" and coorY != "":
            tv1 = get_f(coorX,main_object[2][0],main_object[2][1],main_object[2][2])
            tv2 = get_f(coorX,other_object[2][0],other_object[2][1],other_object[2][2])
            tdiff = abs(tv1/1000 - tv2/1000)
            # check if timestamp is after first object timestamp
            if (tv1 >= main_object[3][3][0]) and (tv1 <= main_object[3][3][-1]): 
                if (tdiff < th_collision):
                #    print("    WARNING!!!!!!!!!!!! trayectories crossed in the same time (less than 2 seconds of diference)")
                    collisions.append((coorX,coorY,tv1))
                #else:
                #    print("    trayectories do not crossed in the same time")
                   
    return collisions



def getShapelySectors(v_type,trajectory,shapely_dist,shapely_ang):

    sectors = []
    
    if v_type == "person":
        for i in range(1,len(trajectory.coords)):
            p1 = Point(trajectory.coords[0])
            p1b = Point(trajectory.coords[i-1])
            p2 = Point(trajectory.coords[i])
            dist = p1.distance(p2)
            circle = p1.buffer(dist)
        
            line = LineString([trajectory.coords[0],trajectory.coords[i]])
            left_border = rotate(line, -shapely_ang, origin=p1b)
            right_border = rotate(line, shapely_ang, origin=p1b)
            splitter = LineString([*left_border.coords, line.coords[-1] ,*right_border.coords[::-1]])
            polygon = split(circle, splitter)
            if len(polygon)>1:
                sectors.append(polygon[1])
    else:
        for i in range(1,len(trajectory.coords)):    
            line = LineString([trajectory.coords[i-1],trajectory.coords[i]])
            lineB = line.buffer(shapely_dist, cap_style=1)    
            sectors.append(lineB)

    return sectors            



def intersections_shapely_polygons(x,f,g,main_object,other_object,th_collision,shapely_dist,shapely_ang):

    collisions = []

    tp1 = []
    tp2 = []
    for i in range(0,len(main_object[3][1])):
        tp1.append((main_object[3][1][i],main_object[3][2][i]))
        tp2.append((other_object[3][1][i],other_object[3][2][i]))
                
    line1 = LineString(tp1)
    line2 = LineString(tp2)

    main_object_type = main_object[3][4]
    other_object_type = other_object[3][4]
    
    sectorsA = getShapelySectors(main_object_type,line1,shapely_dist,shapely_ang)
    sectorsB = getShapelySectors(other_object_type,line2,shapely_dist,shapely_ang)

    collision_shapely = False
    for i in range(0,len(sectorsA)):
        for j in range(0,len(sectorsB)):
            if sectorsA[i].intersects(sectorsB[j]):

                intersection = sectorsA[i].intersection(sectorsB[j])
                #print(intersection)
                p0 = intersection.centroid
                #print(p0.xy)
                           
                p1a, p2a = nearest_points(line1, p0)
                p1b, p2b = nearest_points(line2, p0)
                #print(p1a.xy)
                #print(p1b.xy)
                               
                coorXa = p1a.xy[0][0]
                coorYa = p1a.xy[1][0]
                coorXb = p1b.xy[0][0]
                coorYb = p1b.xy[1][0]


                tv1 = get_f(coorXa,main_object[2][0],main_object[2][1],main_object[2][2])
                tv2 = get_f(coorXb,other_object[2][0],other_object[2][1],other_object[2][2])
                tdiff = abs(tv1/1000 - tv2/1000)
                # check if timestamp is after first object timestamp
                if (tv1 >= main_object[3][3][0]) and (tv1 <= main_object[3][3][-1]): 
                    if (tdiff < th_collision):
                    #    print("    WARNING!!!!!!!!!!!! trayectories crossed in the same time (less than 2 seconds of diference)")
                        collision_shapely = True
                        collisions.append((coorXa,coorYa,tv1))
                    #else:
                    #    print("    trayectories do not crossed in the same time")


            if collision_shapely:
                break
        if collision_shapely:
            break

    return collisions



def collision_detection(main_obj, other_obj, th_collision=COLLISION_THRESHOLD, shapely_dist=SHAPELY_DISTANCE, shapely_ang=SHAPELY_ANGLE):

    # check if x, y and t are not empty
    if main_obj[1] and main_obj[2] and main_obj[3] and other_obj[1] and other_obj[2] and other_obj[3]:
        
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

        collisions = []
        if CD_TYPE == 1:
            collisions = intersections_no_linear_interpolation(x,f,g,main_object,other_object,th_collision)
        elif CD_TYPE == 2:
            collisions = intersections_shapely(x,f,g,main_object,other_object,th_collision)
        elif CD_TYPE == 3:
            collisions = intersections_shapely_polygons(x,f,g,main_object,other_object,th_collision,shapely_dist,shapely_ang)
        else:
            collisions = intersections_shapely_polygons(x,f,g,main_object,other_object,th_collision,shapely_dist,shapely_ang)

    else:
        collisions = []
        #print("empty")
        
    return collisions

