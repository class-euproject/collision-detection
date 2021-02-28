from cd.CD import collision_detection, transformObjectFromFile
from cd.fileBasedObjectManager import FileBasedObjectManager
import sys

def main():

    threshold_collision = int(sys.argv[3])
    tp_log = sys.argv[2]

    dm = FileBasedObjectManager(path=sys.argv[1],filename=tp_log)
    
    iterations = dm.getIterations()
    for iteration in iterations:

        #print("Frame: " + str(iteration))
        input_objects = dm.getIteration(iteration)
        
        for i1,x1 in enumerate(input_objects):     
            main_object = input_objects[i1]
            main_obj = transformObjectFromFile(main_object)
            other_objects = [x2 for i2,x2 in enumerate(input_objects) if i2!=i1]
            for other_object in other_objects:
                other_obj = transformObjectFromFile(other_object)
                collisions = collision_detection(main_obj,other_obj, threshold_collision)

                #if not collisions:
                #    print("No collisions detected")
                if collisions:
                    for collision in collisions:
                        dm.alertCollision(main_obj[0], other_obj[0], collision)
                        
                        raw_out = str(iteration) + " " + main_obj[0]+","+other_obj[0] + " " + str(collision[0])+","+str(collision[1])+","+str(collision[2])
                        dm.storeRawResult(raw_out)

 
    # store in a local file
    dm.createResultsFile()


if __name__ == '__main__':
    main()
