
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

def reposition_array(indices, values):
    
    paired = list(zip(indices, values))
    
    paired.sort(key=lambda x: x[0])
    
    ordered_values = [val for _, val in paired]
    return ordered_values



# filepath = "Signal2.txt"
# a = []
# b = []
# extract_input(filepath, a, b)
# result = reposition_array(a, b)
# print(a)
# print(b)
# print (result)
