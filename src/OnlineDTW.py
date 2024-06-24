import numpy as np

class OnlineDTW:
    def __init__(self, known_seq, unknown_seq, c=200, max_run_count=3):
        self.known_seq = known_seq
        self.unknown_seq = unknown_seq
        self.t = 0  # current position in known sequence
        self.j = 0  # current position in unknown sequence
        self.previous = None
        self.c = c
        self.run_count = 0
        self.max_run_count = max_run_count
        self.D = np.ones((len(self.unknown_seq), len(self.known_seq))) * np.inf

        self.Both = 0
        self.Column = 1
        self.Row = 2
        self.path = []

    def d(self, i, j):
        # cosine distance - note ||u|| = ||v|| = 1
        u = self.unknown_seq[i]
        v = self.known_seq[j]
        return np.clip(1 - np.dot(u, v), 0, 1)
    
    def EvaluatePathCost(self, i, j):
        # Base Case
        if i == 0 and j == 0:
            self.D[i, j] = self.d(i, j)
            return
        
        # Recursive Case
        if j == 0:
            below = np.inf
        else:
            below = self.D[i, j-1] + self.d(i, j)

        if i == 0:
            left = np.inf
        else:
            left = self.D[i-1, j] + self.d(i, j)

        if i == 0 or j ==  0:
            diagonal = np.inf
        else:
            diagonal = self.D[i-1, j-1] + 2 * self.d(i, j)
        
        self.D[i, j] = np.min((below, left, diagonal))

    def GetInc(self, t, j):
        if t < self.c:
            return self.Both
        
        if self.run_count > self.max_run_count:
            if self.previous == self.Row:
                return self.Column
            else:
                return self.Row
            
        x1, y1 = t, np.argmin(self.D[t, :])
        x2, y2 = np.argmin(self.D[:, j]), j
        
        if self.D[x1, y1] <= self.D[x2, y2]:
            x, y = x1, y1
        else:
            x, y = x2, y2

        self.path.append((x, y))
        if x < t:
            return self.Column
        elif y < j:
            return self.Row
        else:
            return self.Both
    
    def run(self):
        self.EvaluatePathCost(self.t, self.j)
        while True:
            if self.GetInc(self.t, self.j) != self.Column:
                self.t = self.t + 1
                if self.t >= len(self.unknown_seq):
                    break
                for k in range(self.j - self.c + 1, self.j + 1, 1):
                    if k >= 0:
                        self.EvaluatePathCost(self.t, k)
            if self.GetInc(self.t, self.j) != self.Row:
                self.j = self.j + 1
                if self.j >= len(self.known_seq):
                    break
                for k in range(self.t - self.c + 1, self.t + 1, 1):
                    if k >= 0:
                        self.EvaluatePathCost(k, self.j)
            if self.GetInc(self.t, self.j) == self.previous:
                self.run_count = self.run_count + 1
            else:
                self.run_count = 1
            if self.GetInc(self.t, self.j) != self.Both:
                self.previous = self.GetInc(self.t, self.j)
                