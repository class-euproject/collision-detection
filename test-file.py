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

from cd.CD import collision_detection, transformObjectFromFile
from cd.fileBasedObjectManager import FileBasedObjectManager
import sys

def main():

    threshold_collision = float(sys.argv[3])
    tp_log = sys.argv[2]

    dm = FileBasedObjectManager(path=sys.argv[1],filename=tp_log)
    
    iterations = dm.getIterations()
    col_cnt = 0
    it = 0
    for iteration in iterations:
        #print("Frame: " + str(iteration))
        input_objects = dm.getIteration(iteration)
        #print(type(input_objects))
        
        for i1,x1 in enumerate(input_objects):     
            main_object = input_objects[i1]
            main_obj = transformObjectFromFile(main_object)

            if(main_obj[0][0] == 0):
                continue
            #print(type(main_obj))
            # if not (main_obj[4] == 20939_211 | main_obj[4] == 20939_213 | main_obj[4] == 20939_269 | main_obj[4] == 20939_132 | main_obj[4] == 20939_315):
            #     continue
            other_objects = [x2 for i2,x2 in enumerate(input_objects) if i2!=i1]
            for other_object in other_objects:
                other_obj = transformObjectFromFile(other_object)
                if(other_obj[0][0] == 0):
                    continue
                # if not (other_obj[4] == 20939_211 | other_obj[4] == 20939_213 | other_obj[4] == 20939_269 | other_obj[4] == 20939_132 | other_obj[4] == 20939_315):
                #     continue 
                collisions = collision_detection(main_obj,other_obj, threshold_collision)

                #if not collisions:
                #    print("No collisions detected")
                if collisions:
                    for collision in collisions:
                        col_cnt = col_cnt+1
                        #print("Collisions found: ", col_cnt, end="\r")
                        #dm.alertCollision(main_obj[4], other_obj[4], collision)
                        
                        raw_out = str(iteration) + " " + main_obj[4]+","+other_obj[4] + " " + str(collision[0])+","+str(collision[1])+","+str(collision[2])
                        dm.storeRawResult(raw_out)

                        visual_out = main_obj[4]+" "+other_obj[4]+ " [(" + str(collision[0])+","+str(collision[1])+","+str(collision[2])+")] ["+','.join(str(e) for e in main_obj[0])+"] ["+','.join(str(e) for e in main_obj[1])+"] ["+','.join(str(e) for e in main_obj[2])+"] ["+','.join(str(e) for e in other_obj[0])+"] ["+','.join(str(e) for e in other_obj[1])+"] ["+','.join(str(e) for e in other_obj[2])+"] "+str(int(main_obj[2][0])/1000-1)
                        dm.storeVisualResult(visual_out)

        print('Processing: %.2f' %(100*it/len(iterations)), end="\r")
        it = it+1

    # store in a local fileW
    dm.createResultsFile()
    

if __name__ == '__main__':
    main()
