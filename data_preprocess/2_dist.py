import json, cv2, math, os, numpy as np

def euclidean_dist_sq(x1, y1, x2, y2):
    return (x1 - x2)**2 + (y1 - y2)**2

def color_dist(x, y, z):
    return round(math.sqrt(x**2 + y**2 + z**2), 4) 

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
input_file_path = os.path.join(current_dir, "data", "json", "Graphene_pixel.json")

result_data = {'diff_data':[]}

with open(input_file_path, 'r') as file:
    raw = json.load(file)
    data = raw["pixel_data"]
    
    for index in range(len(data)):

        layer_data = data[index]["layer_data"]
        image_path = data[index]["file_name"]
        
        final_data = []

        # Search the subtrate (layer = 0)
        x_outer, y_outer, R_outer, G_outer, B_outer, Y_outer, I_outer, Q_outer = [],[],[],[],[],[],[],[]

        for i in range(len(layer_data)):
            if not layer_data[i]["layer"]: # layer : 0
                for j in range(len(layer_data[i]["pos"]["x"])):
                    x_outer.append(layer_data[i]["pos"]["x"][j])
                    y_outer.append(layer_data[i]["pos"]["y"][j])
                    R_outer.append(layer_data[i]["color"]["R"][j]) 
                    G_outer.append(layer_data[i]["color"]["G"][j])
                    B_outer.append(layer_data[i]["color"]["B"][j])
                    Y_outer.append(layer_data[i]["color"]["Y"][j])
                    I_outer.append(layer_data[i]["color"]["I"][j])
                    Q_outer.append(layer_data[i]["color"]["Q"][j])
                                
        # Compute the distance and find minimum, then save the difference of the value         
        for i in range(len(layer_data)):

            min_dist_array, min_dist_x_outer, min_dist_y_outer, R_diff, G_diff, B_diff, Y_diff, I_diff, Q_diff = [],[],[],[],[],[],[],[],[]                    

            if layer_data[i]["layer"]: # layer : 1~5, 10(thick)
                num_of_layer = layer_data[i]["layer"] 
                x = layer_data[i]["pos"]["x"] 
                y = layer_data[i]["pos"]["y"] 
                R = layer_data[i]["color"]["R"]
                G = layer_data[i]["color"]["G"]
                B = layer_data[i]["color"]["B"]
                Y = layer_data[i]["color"]["Y"]
                I = layer_data[i]["color"]["I"]
                Q = layer_data[i]["color"]["Q"]
                                    
                if len(x) != len(y):
                    print("Error: x != y")
                    break
                
                # compute the distance and find the outer pixel position with minimum distance 
                for k, (x_val, y_val) in enumerate(zip(x, y)):
                    x1, y1 = x_val, y_val

                    min_dist = float('inf')
                    min_idx = -1
                    
                    for l in range(len(x_outer)):
                        x2, y2 = x_outer[l], y_outer[l]
                        dist = euclidean_dist_sq(x1, y1, x2, y2)

                        if min_dist > dist:
                            min_dist = dist
                            min_idx = l
                        
                    # save the difference of R, G, B, Y, I, Q  
                    if 0 <= min_idx < len(x_outer):

                        min_dist_array.append(min_dist)
                        min_dist_x_outer.append(x_outer[min_idx])
                        min_dist_y_outer.append(y_outer[min_idx])
                        R_diff.append(R[k] - R_outer[min_idx])
                        G_diff.append(G[k] - G_outer[min_idx])
                        B_diff.append(B[k] - B_outer[min_idx])
                        Y_diff.append(round(Y[k] - Y_outer[min_idx],4))
                        I_diff.append(round(I[k] - I_outer[min_idx], 4))
                        Q_diff.append(round(Q[k] - Q_outer[min_idx], 4))
                

                # Remove points above 1 sigma, which are too far
                min_dist_np = np.array(min_dist_array)
                min_dist_avg = np.mean(min_dist_np)
                min_dist_std = np.std(min_dist_np)

                indices_to_keep = []

                for m in range(len(min_dist_array)):
                    if min_dist_array[m] <= min_dist_avg + 0.5 * min_dist_std and 0 <= m < len(min_dist_x_outer) and 0 <= m < len(x):
                        indices_to_keep.append(m)


                # Create new lists with values to keep
                x_new = [x[i] for i in indices_to_keep]
                y_new = [y[i] for i in indices_to_keep]
                min_dist_x_outer_new = [min_dist_x_outer[i] for i in indices_to_keep]
                min_dist_y_outer_new = [min_dist_y_outer[i] for i in indices_to_keep]
                R_diff_new = [R_diff[i] for i in indices_to_keep]
                G_diff_new = [G_diff[i] for i in indices_to_keep]
                B_diff_new = [B_diff[i] for i in indices_to_keep]
                Y_diff_new = [Y_diff[i] for i in indices_to_keep]
                I_diff_new = [I_diff[i] for i in indices_to_keep]
                Q_diff_new = [Q_diff[i] for i in indices_to_keep]


                RGB_dist = [color_dist(r,g,b) for r, g, b in zip(R_diff_new, G_diff_new, B_diff_new)]
                YIQ_dist = [color_dist(y_,i,q) for y_, i, q in zip(Y_diff_new, I_diff_new, Q_diff_new)]
                

                final_data.append({
                    "layer": num_of_layer,
                    "pos": {
                        "x": x,
                        "y": y,
                        "min_dist_x_outer": min_dist_x_outer,
                        "min_dist_y_outer": min_dist_y_outer
                    },
                    "color_diff": {
                        "RGB_dist": RGB_dist,
                        "YIQ_dist": YIQ_dist
                    }
                })

        result_data['diff_data'].append({
            "file_name": image_path,
            "layer_data": final_data
        })

    output_file_path = os.path.join(current_dir, "data", "json", "Graphene_dist.json")

    with open(output_file_path, 'w') as output_file:
        json.dump(result_data, output_file, separators=(',', ':'))