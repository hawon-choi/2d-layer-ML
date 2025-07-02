import json, math, cv2, os

def find_points_on_edge(x_corner, y_corner, shape):

    # find points on the edge using internal section points

    x_edge, y_edge = [], []

    if len(x_corner) != len(y_corner):
        raise ValueError("x and y size are different.(find_points_on_edge)")
        
    indices = (range(len(x_corner)) if shape == "polygon" else range(1,  len(x_corner)))

    for i in indices :
        x1, y1 = x_corner[i-1], y_corner[i-1]
        x2, y2 = x_corner[i], y_corner[i]

        if x1 == x2: 
            for y in range(min(y1, y2), max(y1, y2)+1):
                x_edge.append(x1)
                y_edge.append(y)
                    
        else:
            cnt_points = max(abs(x2 - x1), abs(y2 - y1)) + 1
            x_points = [int(x1 + t * (x2 - x1) / cnt_points) for t in range(cnt_points)]
            y_points = [int(y1 + t * (y2 - y1) / cnt_points) for t in range(cnt_points)]
            
            x_edge.extend(x_points)
            y_edge.extend(y_points)
            
    return x_edge, y_edge

def find_points_in_normal_direction(x_edge, y_edge, normal_size, width, height, num_of_layer):
    
    # Find the points "normal_size" pixels away from the edge in the normal direction

    x_normal, y_normal = [], []

    if len(x_edge) != len(y_edge):
        raise ValueError("x and y size are different.(find_points_in_normal_direction)")
    
    indices = (range(len(x_edge)) if num_of_layer else range(1, len(x_edge)))

    for i in indices:
        x1, y1 = x_edge[i-1], y_edge[i-1]
        x2, y2 = x_edge[i], y_edge[i]

        # using the concept of normal vector
        x_vec, y_vec = x2 - x1, y2 - y1
        vector_size = math.sqrt(x_vec*x_vec + y_vec*y_vec)

        if vector_size == 0:
            continue

        x_normal_unit, y_normal_unit = (y1 - y2) / vector_size,  (x2 - x1) / vector_size
        
        x1_norm1, y1_norm1 = round(x1 + x_normal_unit * normal_size), round(y1 + y_normal_unit * normal_size)
        x1_norm2, y1_norm2 = round(x1 - x_normal_unit * normal_size), round(y1 - y_normal_unit * normal_size)

        if 0 <= x1_norm1 < width and 0 <= y1_norm1 < height:
            x_normal.append(x1_norm1)
            y_normal.append(y1_norm1)

        if 0 <= x1_norm2 < width and 0 <= y1_norm2 < height:
            x_normal.append(x1_norm2)
            y_normal.append(y1_norm2)   

    return x_normal, y_normal
     

def are_points_inside_polygon(x_points, y_points, polygon_x, polygon_y):
    
    # Check if a point (x, y) is inside a polygon defined by its vertices.

    n = len(polygon_x)
    IS_IN = []

    for i in range(len(x_points)):
        x, y = x_points[i], y_points[i]
        inside = False

        p1x, p1y = polygon_x[0], polygon_y[0]
        for j in range(1, n + 1):
            p2x, p2y = polygon_x[j % n], polygon_y[j % n]

            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
            p1x, p1y = p2x, p2y

        IS_IN.append(inside)

    return IS_IN

def extract_RGB_YIQ(image, x, y):

    # extract RGB from pixels and linearly convert to YIQ

    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    R, G, B, Y_, I, Q = [[] for _ in range(6)] 


    if len(x) != len(y):
        print("x and y size are different")
        return 
        
    else:
        for X, Y in zip(x, y):
            if 0 <= X < img.shape[1] and 0 <= Y < img.shape[0]:
                r, g, b = img[Y, X].tolist()
                R.append(r)
                G.append(g)
                B.append(b)

                y_ = round(0.299 * r + 0.587 * g + 0.114 * b, 4)
                i = round(0.596 * r - 0.275 * g - 0.321 * b, 4)
                q = round(0.212 * r - 0.523 * g + 0.311 * b, 4)

                Y_.append(y_)
                I.append(i)
                Q.append(q)

    return R, G, B, Y_, I, Q 

def write_data(NUM_OF_LAYER, x, y, R, G, B, Y, I, Q):
    
    # organize data to save JSON file

    return {
        'layer' : NUM_OF_LAYER,
        'pos': {
            'x': x,
            'y': y
        },
        'color':{
            'R': R,
            'G': G,
            'B': B,
            'Y': Y,
            'I': I,
            'Q': Q
        }
    }



# file and directory path 
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
input_file_path = os.path.join(current_dir, "data", "json", "Graphene.json")
image_dir = os.path.join(current_dir, "data\images")

with open(input_file_path, 'r') as file:
    data = json.load(file)

    final_data = {'pixel_data': []}

    for file_name, image_data in data.items(): # key, value
        layer_data = []
    
        image_name = image_data["filename"]
        image_path = os.path.join(current_dir, "data", "images", image_name)
        image = cv2.imread(image_path)

        height, width, channels = image.shape # 1200, 1600, 3  
        normal_size = 5    
        region = image_data['regions']

        for i in range(len(region)):

            x_corner = region[i]["shape_attributes"]["all_points_x"]
            y_corner = region[i]["shape_attributes"]["all_points_y"]
            shape = region[i]["shape_attributes"]["name"]

            NUM_OF_LAYER = -1 
            layer = region[i]["region_attributes"]["layer"]

            for l, num in layer.items():
                if num : 
                    if l == "mono":
                        NUM_OF_LAYER = 1 
                    elif l == "bi":
                        NUM_OF_LAYER = 2 
                    elif l == "tri":
                        NUM_OF_LAYER = 3 
                    elif l == "quad":
                        NUM_OF_LAYER = 4
                    elif l == "penta":
                        NUM_OF_LAYER = 5
                    elif l == "thick":
                        NUM_OF_LAYER = 10
                    elif l == "flake":
                        NUM_OF_LAYER = 0
                else :
                    NUM_OF_LAYER = -1 

                x_edge, y_edge = find_points_on_edge(x_corner, y_corner, shape)
                x_normal, y_normal = find_points_in_normal_direction(x_edge, y_edge, normal_size, width, height, NUM_OF_LAYER)
                IS_IN = are_points_inside_polygon(x_normal, y_normal, x_corner, y_corner) # in: True, out: False
                R, G, B, Y_, I, Q = extract_RGB_YIQ(image, x_normal, y_normal)

                x_IN, y_IN, x_OUT, y_OUT, R_IN, G_IN, B_IN, R_OUT, G_OUT, B_OUT, Y_IN, I_IN, Q_IN, Y_OUT, I_OUT, Q_OUT = [[] for _ in range(16)]

                for x, y, r, g, b, y_, i, q, is_in in zip(x_normal, y_normal, R, G, B, Y_, I, Q, IS_IN):

                    if is_in: # get flake pixel
                        x_IN.append(x)
                        y_IN.append(y)
                        R_IN.append(r)
                        G_IN.append(g)
                        B_IN.append(b)
                        Y_IN.append(y_)
                        I_IN.append(i)
                        Q_IN.append(q)

                    else: # get substrate pixel
                        x_OUT.append(x)
                        y_OUT.append(y)
                        R_OUT.append(r)
                        G_OUT.append(g)
                        B_OUT.append(b)
                        Y_OUT.append(y_)
                        I_OUT.append(i)
                        Q_OUT.append(q)

                data = {}

                if NUM_OF_LAYER < 0 : 
                    continue
                
                elif NUM_OF_LAYER > 0 :
                    data = write_data(NUM_OF_LAYER, x_IN, y_IN, R_IN, G_IN, B_IN, Y_IN, I_IN, Q_IN)

                elif NUM_OF_LAYER == 0 :
                    data = write_data(NUM_OF_LAYER, x_OUT, y_OUT, R_OUT, G_OUT, B_OUT, Y_OUT, I_OUT, Q_OUT)

                layer_data.append(data)
                

        final_data["pixel_data"].append({
            'file_name' : image_name,
            'layer_data': layer_data
        })

    output_file_path = os.path.join(current_dir, "data", "json", "Graphene_pixel.json")
    
    # Save final data to a new JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(final_data, output_file, separators=(',', ':'))                            