from cd.CD import collision_detection, transformObjectFromFile
from cd.fileBasedObjectManager import FileBasedObjectManager

def main():

    dm = FileBasedObjectManager(path="data")
    
    iterations = dm.getIterations()
    for iteration in iterations:

        input_objects = dm.getIteration(iteration)

        main_object = input_objects[0]
        main_obj = transformObjectFromFile(main_object)
        other_objects = input_objects[1:]

        for other_object in other_objects:
            other_obj = transformObjectFromFile(other_object)
            collisions = collision_detection(main_obj,other_obj)

            #if not collisions:
            #    print("No collisions detected")
            if collisions:
                for collision in collisions:
                    dm.alertCollision(main_obj[0], other_obj[0], collision)


if __name__ == '__main__':
    main()
