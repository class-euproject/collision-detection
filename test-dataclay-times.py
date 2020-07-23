from cd.CD import collision_detection
from cd.dataclayObjectManager import DataclayObjectManager

import random
import time 

if __name__ == '__main__':
    
    dm = DataclayObjectManager(alias="DKB") # alias for DKB objects

    while True: # infinite loop

        collision_time = []
        collision_detection_time = []
        collision_count = 0
        collision_empty = 0
    
        print("\n\nStarting collision detection\n\n")

        start_time = time.time()
        
        input_objects = dm.getObjects()

        dataclay_end_time = time.time()
        
#        ###### 1 Vs All ######
#        main_object = input_objects[0]
#        other_objects = input_objects[1:]
#
#        for other_object in other_objects:
#            collisions = collision_detection(main_object,other_object)
#
#            #if not collisions:
#            #    print("No collisions detected")
#            if collisions:
#                for collision in collisions:
#                    dm.alertCollision(main_object[0], other_object[0], collision)


        ###### All Vs All ######
        random_list = random.sample(range(len(input_objects)), len(input_objects))
        for i in random_list:

            start_collision_time = time.time()

            actual_objects = input_objects

            main_object = actual_objects[i]
            
            other_objects = actual_objects.copy()
            other_objects.pop(i)

            for other_object in other_objects:

                if main_object[1] and other_object[1]:

                    collision_count = collision_count + 1
                    start_collision_detection_time = time.time()

                    collisions = collision_detection(main_object,other_object)

                    #if not collisions:
                    #    print("No collisions detected")
                    if collisions:
                        for collision in collisions:
                            dm.alertCollision(main_object[0], other_object[0], collision)

                    end_collision_detection_time = time.time()
                    collision_detection_time.append(end_collision_detection_time - start_collision_detection_time)

                else:
                    collision_empty = collision_empty + 1
                    
            end_collision_time = time.time()
            
            collision_time.append(end_collision_time - start_collision_time)

        end_time = time.time()

        print("\n\nEnded collision detection\n\n")

        print("\n\nStarting time reporting\n\n")
        print("Global time (loop): " + str(end_time - start_time))
        print("dataclay time (getObjects): " + str(dataclay_end_time - start_time))
        print("Collision detection global time (all objects): " + str(end_collision_time - start_collision_time))
        print("Total collisions detections analyzed: " + str(collision_count + collision_empty))
        print("Total collisions detections analyzed (without empty trajectories): " + str(collision_count))
        if len(collision_detection_time)>0:
            print("Collision detection average time (per match): " + str(sum(collision_detection_time)/len(collision_detection_time)))
        print("\n\nEnded time reporting\n\n")

        print("-----------------------------------------------------")

        time.sleep(10) #make function to sleep for 10 seconds
