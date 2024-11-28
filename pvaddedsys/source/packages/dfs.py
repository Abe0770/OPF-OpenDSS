# pseudocode 
gen_bus_line_loss = {}
def dfs(gen_name, gen_bus_name, visited_dict, gen_bus_line_loss, adjacency_list, current_sum):
    visited_dict[gen_bus_name] = 1

    for key, val in adjacency_list.items():
        if int(key) == int(gen_bus_name):
            for key1, val1 in val.items():
                if visited_dict[key1] == 0: # Only explore unvisited nodes
                    visited_dict[key1] = 1
                    new_sum = current_sum + float(val1) # Update sum with current line loss
                    gen_bus_line_loss[key1] = {}
                    gen_bus_line_loss[key1][gen_name] = new_sum
                    dfs(gen_name, key1, visited_dict, gen_bus_line_loss, adjacency_list, new_sum)
                    visited_dict[key1] = 0 # Backtrack and mark unvisited for other paths

def merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in merged_dict and isinstance(merged_dict[key], dict) and isinstance(value, dict):
            merged_dict[key] = merge_dicts(merged_dict[key], value)
        else:
            merged_dict[key] = value
    return merged_dict

def adj_list(loss_file, Bus_set, gen_file_path, pd):
    with open(loss_file, 'r') as file:
        lines = file.readlines()

    adjacency_list = {}

    for line in lines:
      if line.startswith('"Line.'):
          # Extract node names and weight
          node1 = line.strip().split()[0].split('.')[1][:3]
          node2 = line.strip().split()[0].split('.')[1][3:6]
          weight = line.strip().split()[1][:7]

          if node1 not in adjacency_list:
              adjacency_list[node1] = {}
          adjacency_list[node1][node2] = weight
          if node2 not in adjacency_list:
              adjacency_list[node2] = {}
          adjacency_list[node2][node1] = weight
    visited_dict = {}
    
    merged_dict = {}
    gen_df = pd.read_csv(gen_file_path)
    for i in gen_df.values.tolist():
        for j in Bus_set:
            visited_dict[j] = 0
        gen_name = i[0]
        gen_bus_name = i[9]
        dfs(gen_name, gen_bus_name, visited_dict, gen_bus_line_loss, adjacency_list, 0)
        merged_dict = merge_dicts(merged_dict, gen_bus_line_loss)

    return merged_dict

'''
def dfs(gen_name, gen_bus_name, visited_dict, gen_bus_line_loss, adjacency_list, sum):
    visited_dict[gen_bus_name] = 1
    print(gen_bus_line_loss)
    #   (gen_bus_name)  

    for key, val in adjacency_list.items():
        if key == gen_bus_name:
            for key1, val1 in val.items():
                if not visited_dict[key1]:
                    sum = sum + float(val1)
                    # Initialize gen_bus_line_loss[key1] only once
                    if key1 not in gen_bus_line_loss:
                        gen_bus_line_loss[key1] = {}
                    gen_bus_line_loss[key1][gen_bus_name] = sum
                    dfs(gen_name, gen_bus_name, visited_dict, gen_bus_line_loss, adjacency_list, 0)
                    sum = sum - float(val1)

def adj_list(loss_file, Bus_set, gen_file_path, pd, gen_bus_line_loss):
    with open(loss_file, 'r') as file:
        lines = file.readlines()

    adjacency_list = {}
    
    for line in lines:
      if line.startswith('"Line.'):
          # Extract node names and weight
          node1 = line.strip().split()[0].split('.')[1][:3]
          node2 = line.strip().split()[0].split('.')[1][3:6]
          weight = line.strip().split()[1][:7]

          if node1 not in adjacency_list:
              adjacency_list[node1] = {}
          adjacency_list[node1][node2] = weight
          if node2 not in adjacency_list:
              adjacency_list[node2] = {}
          adjacency_list[node2][node1] = weight
    visited_dict = {}
    for i in Bus_set:
        visited_dict[i] = 0
    print(visited_dict)
    print(adjacency_list)

    gen_df = pd.read_csv(gen_file_path)
    for i in gen_df.values.tolist():
        gen_name = i[0]
        gen_bus_name = i[9]
        dfs(gen_name, gen_bus_name, visited_dict, gen_bus_line_loss, adjacency_list, 0)

    return gen_bus_line_loss

'''