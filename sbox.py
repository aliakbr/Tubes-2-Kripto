import numpy as np

class SBox():
    def __init__(self, plainbit):
        self.plainbit = plainbit
        self.boxbit = None
                
        l_plainbit = [int(x) for x in plainbit]
        self.boxbit = np.asarray(l_plainbit)
        self.boxbit = np.reshape(self.boxbit, (8, 8))
        
    def box_to_1d(self):
        return np.reshape(self.boxbit, 64)
    
    def box_to_list(self):
        return self.box_to_1d().tolist()
    
    def rotatebox(self, d4, d3, d2, d1):
        b4, b3, b2, b1 = self.unravel_box()
        b3.reverse()
        b1.reverse()
        
        for _ in range(d4):
            b4 = twist(b4)
        for _ in range(d3):
            b3 = twist(b3)
        for _ in range(d2):
            b2 = twist(b2)
        for _ in range(d1):
            b1 = twist(b1)
            
        self.boxbit = self.ensemble(b4, b3, b2, b1)
    
    def rotatebox_inv(self, d4, d3, d2, d1):
        b4, b3, b2, b1 = self.unravel_box()
        b4.reverse()
        b2.reverse()
        
        for _ in range(d4):
            b4 = twist(b4)
        for _ in range(d3):
            b3 = twist(b3)
        for _ in range(d2):
            b2 = twist(b2)
        for _ in range(d1):
            b1 = twist(b1)
            
        self.boxbit = self.ensemble(b4, b3, b2, b1)
        
    def unravel_box(self):
        b4 = unravel(self.boxbit, 4)
        b3 = unravel(self.boxbit, 3)
        b2 = unravel(self.boxbit, 2)
        b1 = unravel(self.boxbit, 1)
        
        return b4, b3, b2, b1
    
    def ensemble(self, b4, b3, b2, b1):
        b = []
        b.extend(b4[:8])
        b.extend([b4[-1]] + b3[:6] + [b4[8]])
        b.extend([b4[-2]] + [b3[-1]] + b2[:4] + [b3[6]] + [b4[9]])
        b.extend([b4[-3]] + [b3[-2]] + [b2[-1]] + b1[:2] + [b2[4]] + [b3[7]] +[b4[10]])
        b.extend([b4[-4]] + [b3[-3]] + [b2[-2]] + b1[::-1][:2] + [b2[5]] + [b3[8]] +[b4[11]])
        b.extend([b4[-5]] + [b3[-4]] + b2[::-1][2:6] + [b3[9]] +[b4[12]])
        b.extend([b4[-6]] + b3[::-1][4:10] + [b4[13]])
        b.extend(b4[::-1][6:14])
        
        return np.reshape(np.asarray(b), (8,8))
    
def twist(thread):
    return thread[1:] + [thread[0]]

def unravel(boxbit, d):
    d_f = 4 - d
    
    b = []
    b.extend(boxbit[d_f][d_f:(8-d_f)].tolist())
    for i in range((d_f+1),(7-d_f)):
        b.extend(boxbit[i][7-d_f])
    b.extend(boxbit[7-d_f][d_f:(8-d_f)].tolist()[::-1])
    for i in range((6-d_f),d_f,-1):
        b.extend(boxbit[i][d_f])
    
    return b