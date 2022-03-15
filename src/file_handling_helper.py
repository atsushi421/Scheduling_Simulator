import networkx as nx
import os

from exceptions import UnimplementedError


def read_dag(dag_file_path: str) -> nx.DiGraph:
    _, ext = os.path.splitext(os.path.basename(dag_file_path))

    if(ext == '.tgff'):
        # Get "type" & "exec_time" of "@PE 5"
        type_cost = []
        read_flag = 0
        info_flag = 0
        f = open(dag_file_path, 'r')
        for line in f:
            if(line == '\n'):
                continue
            line_list = line.split()
            if(len(line_list) >= 2):
                if(line_list[0] == '@PE' and line_list[1] == '5'):
                    read_flag = 1
                if(line_list[1] == 'type' and line_list[2] == 'exec_time'):
                    info_flag = 1
                    continue
                if(read_flag == 1 and info_flag == 1):
                    type_cost.append(int(float(line_list[1])))
            elif(line_list[0] == '}'):
                read_flag = 0
                info_flag = 0
        f.close()

        # Create DAG
        G = nx.DiGraph()
        f = open(dag_file_path, 'r')
        for line in f:
            if(line == "\n"):
                continue
            line_list = line.split()

            # Add node
            if(line_list[0] == 'TASK'):
                G.add_node(G.number_of_nodes(), exec=type_cost[int(line_list[3])])

            # Add edge
            if(line_list[0] == 'ARC'):
                source = int(line_list[3][3:])
                target = int(line_list[5][3:])
                G.add_edge(source, target, comm=type_cost[int(line_list[7])])
        f.close()

        return G



    if(ext == '.yaml'):
        pass  # TODO
    if(ext == '.json'):
        pass  # TODO
    if(ext == '.dot'):
        pass  # TODO

    raise UnimplementedError('')
