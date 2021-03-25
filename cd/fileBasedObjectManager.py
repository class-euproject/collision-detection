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

import json

class FileBasedObjectManager:

    results = {}
    output_path = ""
    raw_output = ""
    visual_output = ""

    def __init__(self, path='.', filename="results.txt"):

        self.output_path = path

        # read example data
        import json

        with open(path+'/'+filename) as json_file:
            self.results = json.load(json_file)

    def getIterations(self):
        return self.results.keys()

    def getIteration(self, it):
        return self.results[it]

    def alertCollision(self, v_main, v_other, col):
        print(f"----------------------------------------")
        print(f"WARNING!!! Possible collision detected")
        print(f"  v_main: {v_main} v_other: {v_other}")
        print(f"    x: {col[0]} y: {col[1]} t: {col[2]}")
        print(f"----------------------------------------")

    def storeRawResult(self, raw_out):
        self.raw_output = self.raw_output + raw_out + "\n"

    def storeVisualResult(self, visual_out):
        self.visual_output = self.visual_output + visual_out + "\n"
        
    def createResultsFile(self):
        with open(self.output_path + "/raw_results_CD.txt", "w") as raw_file:
            raw_file.write(self.raw_output)
        with open(self.output_path + "/visual_results_CD.txt", "w") as visual_file:
            visual_file.write(self.visual_output)

