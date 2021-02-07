import json

class FileBasedObjectManager:

    results = {}
    output_path = ""
    raw_output = ""

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
        
    def createResultsFile(self):
        with open(self.output_path + "/raw_results_CD.txt", "w") as raw_file:
            raw_file.write(self.raw_output)

