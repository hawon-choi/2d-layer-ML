import json, copy, os


current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
input_file_path = os.path.join(current_dir, "data", "json", "Graphene_dist.json")

material = "Graphene"
substrate = "Gelpack"

with open(input_file_path, 'r') as file:
    raw_data = json.load(file)
    neighbor_data = raw_data["diff_data"]
    
    data = {
            "RGB_dist": [],
            "YIQ_dist": []
        }

    l1, l2, l3, l4, l5, l10 = copy.deepcopy(data), copy.deepcopy(data), copy.deepcopy(data), copy.deepcopy(data), copy.deepcopy(data), copy.deepcopy(data)

    for index in range(len(neighbor_data)):
        image_path = neighbor_data[index]["file_name"]
        layer_data = neighbor_data[index]["layer_data"]
        

        for l in range(len(layer_data)):

            layer = layer_data[l]["layer"]
            patch_data = layer_data[l]["color_diff"]

            RGB_dist = patch_data["RGB_dist"]
            YIQ_dist = patch_data["YIQ_dist"]


            if (len(RGB_dist) == len(YIQ_dist)):
                
                for i in range(len(RGB_dist)):
                    
                    if layer == 1:

                        l1["RGB_dist"].append(RGB_dist[i])
                        l1["YIQ_dist"].append(YIQ_dist[i])


                    elif layer == 2:
                        l2["RGB_dist"].append(RGB_dist[i])
                        l2["YIQ_dist"].append(YIQ_dist[i])

                    elif layer == 3:
                        l3["RGB_dist"].append(RGB_dist[i])
                        l3["YIQ_dist"].append(YIQ_dist[i])

                    elif layer == 4:
                        l4["RGB_dist"].append(RGB_dist[i])
                        l4["YIQ_dist"].append(YIQ_dist[i])

                    elif layer == 5:
                        l5["RGB_dist"].append(RGB_dist[i])
                        l5["YIQ_dist"].append(YIQ_dist[i])

                    elif layer == 10:
                        l10["RGB_dist"].append(RGB_dist[i])
                        l10["YIQ_dist"].append(YIQ_dist[i])
                    
                    else :
                        print("layer error")

            else: 
                print(f"length error! {image_path}, layer:{layer}")


    final_data = {
        "material": material,
        "substrate": substrate,
    "data": [
            {"layer": 1, "count": len(l1["RGB_dist"]), "dist": l1},
            {"layer": 2, "count": len(l2["RGB_dist"]), "dist": l2},
            {"layer": 3, "count": len(l3["RGB_dist"]), "dist": l3},
            {"layer": 4, "count": len(l4["RGB_dist"]), "dist": l4},
            {"layer": 5, "count": len(l5["RGB_dist"]), "dist": l5},
            {"layer": 10, "count": len(l10["RGB_dist"]), "dist": l10},
        ]
    }
    
    output_file_path = os.path.join(current_dir, "data", "json", "Graphene_merge.json")

    with open(output_file_path, 'w') as output_file:
        json.dump(final_data, output_file, separators=(',', ':'))