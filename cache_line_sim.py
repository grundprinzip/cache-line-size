# Variables for the size of the L1 data cache
CACHE_LINE_SIZE = 64
L1_SET_SIZE = 64
L1_ASSOC = 8
L1_SIZE = CACHE_LINE_SIZE * L1_SET_SIZE * L1_ASSOC

class LRUMap(object):
    """
    This class is a very simple implementation of a LRU list,
    the keys are counted and if the total number of buckets is reached
    it will be replaced
    """
    def __init__(self, buckets):
        self.buckets = buckets
        self.lru = [] 

    def add(self, value):
        
        if value in self.lru:
            del self.lru[self.lru.index(value)]
            self.lru.append(value)
        else:
            if len(self.lru) < self.buckets:
                self.lru.append(value)
            else:
                del self.lru[0]
                self.lru.append(value)

    def full(self):
        return len(self.lru) == self.buckets
    
    def size(self):
        return len(self.lru)

    def last(self):
        return self.lru[0]

    def __len__(self):
        return len(self.lru)

    def __str__(self):
        return "<class:LRU %s>" % str(self.lru)


def load(offset, amount):
    return range(offset, offset + amount)

def possible_locations_for_address(address):
    offset = int(address / L1_SET_SIZE) % L1_SET_SIZE
    return range( offset * L1_ASSOC, offset * L1_ASSOC + L1_ASSOC)

def set_for_address(address):
    offset = int(address / L1_SET_SIZE) % L1_SET_SIZE
    return offset 

def col_address_for(col, row, max_col, max_row, width):
    """Map an position in the matrix to a cols store"""
    return col * max_row * width + row * width


def simulate_eviction(rows, cols, address_mapper, width=4):
    """
    We have an array of size rows x cols filled with data type of width.
    Now we assume that the memory positions are set to the associated 
    cache lines using the associativity. 

    Example
    0x000 -> 0,1,2,3,4,5,6,7
    0x001 -> 8,9,10,11,12,13,14,15
    0x002 -> 16,17,18,19,20,21,22,23
    0x003 -> 24,25,26,27,28,29,30,31
    0x004 -> 32,33,34,35,36,37,38,39
    0x005 -> 40,41,42,43,44,45,46,47
    0x007 -> 48,...
    0x008 -> 56,...

    """
    hit = 0
    miss = 0
    evict = 0


    # Prepare the L1 cache
    cache_lines = []
    line_lru = []
    for i in range(L1_SIZE):
        cache_lines.append([])

    for i in range(L1_SET_SIZE):
        line_lru.append(LRUMap(L1_ASSOC))
    
    for r in range(rows):
        for c in range(cols):
            # For all rows and all cols iterate
            # and calculate
            address = address_mapper(c,r,cols, rows, width)
            
            locations = possible_locations_for_address(address)

            set_number = set_for_address(address)
           
            lru = line_lru[set_number]
            
            #print "(%d,%d @ %d)" % (c,r,address)

            # check if we find that address in one of our cache lines
            # that map to that address
            flag = False
            for l in locations: 
                for w in range(width):
                    if address+w in cache_lines[l]:
                        flag = True
                        break
                if flag:
                    # If we found it we have to push this line in our
                    # LRU list
                    #print "hit"
                    hit += 1
                    lru.add(l)
                    break

            if not flag:
                #print "Miss"
                
                # if we have a miss, than check which cache line
                # to remove and replace
                #print lru
                if not lru.full():
                    miss += 1
                    cache_line_number = locations[lru.size()]    
                    lru.add(cache_line_number)
                else:
                    #print "Evict"
                    evict += 1
                    cache_line_number = lru.last()
                    lru.add(cache_line_number)

                #print cache_line_number
                cache_lines[cache_line_number] = load(address, CACHE_LINE_SIZE)

    #print cache_lines
    #print "(%d, %d, %d)" % (hit, miss, evict)
    return (hit, miss, evict)

if __name__ == "__main__":
    # Simulate the eviction with 10000 rows, 20 columns
    # and the column address strategy
    rows = 10000
    for x in range(1,40):
        res = simulate_eviction(rows, x, col_address_for)
        print x, float(res[2] / float(x))


