import json

class FileBasedObjectManager:

    results = {}

    def __init__(self, path='.'):
        # read example data
        import json

        with open(path+'/data.txt') as json_file:
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

