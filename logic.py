cur_vals = []
cur_idxs = []
def read_signal(filepath, idxs, vals):
    """extracts the input from the filepath into idxs and vals (2 lists)"""
    text_input = []
    with open(filepath) as file:
        text_input = file.readlines()[2:]

    n = int(text_input[0].strip())
    text_input = text_input[1:]
    for i in range(n):
        c, d = text_input[i].strip().split()
        idxs.append(int(c))
        vals.append(int(d))

def sub_signal(idxs, vals):
    vals = [-1 * val for val in vals]
    return add_signal(idxs, vals)

def advance_signal(idxs, vals, k):
    for i in range(len(idxs)):
        idxs[i] = idxs[i] + k 


def delay_signal(idxs, vals, k):
    for i in range(len(idxs)):
            idxs[i] = idxs[i] - k 
            
def fold_signal(idxs, vals):
    for i in range(len(idxs)):
            idxs[i] = idxs[i] * -1 

def add_signal(idxs, vals):
    """
    Add the given signal (idxs, vals) into the global cur_idxs / cur_vals.
    This function MUTATES cur_idxs and cur_vals in-place so external modules
    that hold references to these lists see updates.
    """
    global cur_idxs, cur_vals

    # guard
    if not idxs or not vals:
        return

    # If no accumulated signal yet, extend the existing lists (mutate in-place)
    if len(cur_idxs) == 0:
        cur_idxs.extend(idxs)
        cur_vals.extend(vals)
        return

    # Merge two sorted index lists and sum overlapping samples
    i, j = 0, 0
    result_idxs = []
    result_vals = []

    while i < len(cur_idxs) and j < len(idxs):
        a = cur_idxs[i]
        b = idxs[j]
        if a < b:
            result_idxs.append(a)
            result_vals.append(cur_vals[i])
            i += 1
        elif a > b:
            result_idxs.append(b)
            result_vals.append(vals[j])
            j += 1
        else:  # equal index
            result_idxs.append(a)
            result_vals.append(cur_vals[i] + vals[j])
            i += 1
            j += 1

    # append remaining tail from cur
    while i < len(cur_idxs):
        result_idxs.append(cur_idxs[i])
        result_vals.append(cur_vals[i])
        i += 1

    # append remaining tail from new signal
    while j < len(idxs):
        result_idxs.append(idxs[j])
        result_vals.append(vals[j])
        j += 1

    # MUTATE the original lists so references remain valid
    cur_idxs[:] = result_idxs
    cur_vals[:] = result_vals

def multiply(vals, c):
    """Multiply given list of signal values in place."""
    for i in range(len(vals)):
        vals[i] *= c

    
            

def reposition_array(indices, values):
    
    paired = list(zip(indices, values))
    
    paired.sort(key=lambda x: x[0])
    
    ordered_values = [val for _, val in paired]
    return ordered_values



# signal1_path = "Signal1.txt"
# signal2_path = "Signal2.txt"
# idxs1 = []
# idxs2 = []
# vals1 = []
# vals2 = []

# result = []
# result_idx = []
# read_signal(signal1_path, idxs1, vals1)
# read_signal(signal2_path, idxs2, vals2)
# result, result_idx = add_signals(idxs1,vals1,idxs2, vals2)
# print (idxs1)
# print (vals1)
# print ()
# print (idxs2)
# print(vals2)
# print()
# print(result)
# print(result_idx)
# [-2, 3, 0, 1, 7, 8, 4, -2, 5, 5, 0, 2, 3]
# [-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]