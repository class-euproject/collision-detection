from cd.CD import collision_detection

from cd.fileBasedObjectManager import FileBasedObjectManager

def main():

    dm = FileBasedObjectManager(path="data")
    
    iterations = dm.getIterations()
    for iteration in iterations:

        input_objects = dm.getIteration(iteration)

        main_object = input_objects[0]
        other_objects = input_objects[1:]

        for other_object in other_objects:
            collisions = collision_detection(main_object,other_object)

            #if not collisions:
            #    print("No collisions detected")
            if collisions:
                for collision in collisions:
                    dm.alertCollision(main_object["v_id"], other_object["v_id"], collision)


if __name__ == '__main__':
    main()
