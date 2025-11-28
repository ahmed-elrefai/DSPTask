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

def moving_average(vals, window_size):
    """Compute moving average of signal values.
    
    Args:
        vals: list of signal values
        window_size: number of points to average over
    
    Returns:
        list of moving average values (same length as input)
    """
    if window_size <= 0 or window_size > len(vals):
        raise ValueError("Window size must be positive and <= signal length")
    
    result = []
    for i in range(len(vals)):
        start = max(0, i - window_size + 1)
        end = i + 1
        avg = sum(vals[start:end]) / (end - start)
        result.append(avg)
    
    return result

def convolve_signals(signal1_vals, signal2_vals):    
    if not signal1_vals or not signal2_vals:
        raise ValueError("Both signals must be non-empty")
    
    N = len(signal1_vals)
    M = len(signal2_vals)
    result_len = N + M - 1
    result = [0.0] * result_len
    
    for n in range(result_len):
        for k in range(max(0, n - M + 1), min(n + 1, N)):
            result[n] += signal1_vals[k] * signal2_vals[n - k]
    
    indices = list(range(result_len))
    return result, indices

def dft(vals, inverse=False):
    """"Calculate Fourier Transform of the signal"""
    import cmath
    f = []
    N = len(vals)
    for k in range(N):
        f_k = 0
        for n in range(N):
            phase = (2*cmath.pi*k*n) / N 
            phase = phase if inverse else -1 * phase
            f_k += vals[n]*cmath.rect(1,phase) 
        if inverse:
            f_k = round((1 / N) * f_k.real)
        f.append(f_k)
    return f



def first_derivative(vals):
    """Return first derivative y(n) = x(n) - x(n-1)."""
    if len(vals) < 2:
        raise ValueError("Signal must have at least 2 samples for first derivative")
    return [vals[i] - vals[i-1] for i in range(1, len(vals))]

def second_derivative(vals):
    """Return second derivative y(n) = x(n+1) - 2*x(n) + x(n-1)."""
    if len(vals) < 3:
        raise ValueError("Signal must have at least 3 samples for second derivative")
    return [vals[i+1] - 2*vals[i] + vals[i-1] for i in range(1, len(vals)-1)]

# Keep existing (older) inplace-naming functions for compatibility if needed,
# but prefer the return-style API above in GUI.
def first_dervative(idxs, vals):
    """Legacy: inplace mutation (kept for compatibility)."""
    global cur_idxs, cur_vals
    new_idxs = []
    new_vals = []
    for i in range(1, len(cur_idxs)):
        new_idxs.append(cur_idxs[i])
        new_vals.append(cur_vals[i] - cur_vals[i-1])
    cur_idxs = new_idxs
    cur_vals = new_vals

def second_dervative(idxs, vals):
    """Legacy: inplace mutation (kept for compatibility)."""
    global cur_idxs, cur_vals
    new_idxs = []
    new_vals = []
    for i in range(0, len(cur_idxs)-1):
        new_idxs.append(cur_idxs[i])
        new_vals.append(cur_vals[i+1] - 2*cur_vals[i] + cur_vals[i-1])
    cur_idxs = new_idxs
    cur_vals = new_vals

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

    
def quantize(vals, bits):
    """Quantize given list of signal values in place."""
    levels = 2 ** bits
    min_val = min(vals)
    max_val = max(vals)
    delta = (max_val - min_val) / levels

    def quantize_error(original_vals, quantized_vals):
        """Calculate quantization error between original and quantized values."""
        error = []
        for o, q in zip(original_vals, quantized_vals):
            error.append(o - q)
        return error

    for i in range(len(vals)):
        q_level = round((vals[i] - min_val) / delta)
        vals[i] = min_val + q_level * delta
    

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
