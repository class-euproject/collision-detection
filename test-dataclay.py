from cd.CD import collision_detection
from cd.dataclayObjectManager import DataclayObjectManager

import random
import time 

if __name__ == '__main__':
    
    dm = DataclayObjectManager(alias="DKB") # alias for DKB objects

    while True: # infinite loop

        print("\n\nStarting collision detection\n\n")
        
        input_objects = dm.getObjects()
        
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
            actual_objects = input_objects

            main_object = actual_objects[i]
            
            other_objects = actual_objects.copy()
            other_objects.pop(i)

            for other_object in other_objects:

                if main_object[1] and main_object[2] and main_object[3] and other_object[1] and other_object[2] and other_object[3] and min(main_object[1])>-180 and max(main_object[1])<180 and min(other_object[1])>-180 and max(other_object[1])<180 and min(main_object[2])>-90 and min(other_object[2])>-90 and max(main_object[1])<90 and max(other_object[2])<90 and (max(main_object[1])-min(main_object[1]))<2 and (max(main_object[2])-min(main_object[2]))<2 and (max(other_object[1])-min(other_object[1]))<2 and (max(other_object[2])-min(other_object[2]))<2:
                    collisions = collision_detection(main_object,other_object)

                    #if not collisions:
                    #    print("No collisions detected")
                    if collisions:
                        for collision in collisions:
                            dm.alertCollision(main_object[0], other_object[0], collision)


        print("\n\nEnded collision detection\n\n")

        time.sleep(10) #make function to sleep for 10 seconds
