
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

def add_signals(idxs1, vals1, idxs2, vals2):
    i = 0
    j = 0
    result = []
    start = min(idxs1[0], idxs2[0])
    end = max(idxs1[-1], idxs2[-1])
    resultIdxs = list(range(start, end+1))
    i = 0 
    j = 0
    while i <= len(idxs2) and j <= len(idxs1):
        if idxs1[i] < idxs2[j]:
            result.append(vals1[i])
            i+=1
        elif idxs1[i] > idxs2[j]:
            result.append(vals2[j])
            j+=1
        else:
            result.append(vals1[i]+vals2[j])
            i+=1
            j+=1
    
    result.extend(vals1[i:])
    result.extend(vals2[j:])
    return result, resultIdxs
    
            

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