import random
import copy
import time
import numpy as np
import networkx as nx
import pandas as pd
from typing import List

from  sched_lib.algorithms.dag_utils import set_ranku, convert_to_virtual_entry_dag, convert_to_virtual_exit_dag
from  sched_lib.algorithms.genetic_algorithm import Chromosome, GeneticAlgorithm
from  sched_lib.processors.homogeneous.cluster import CluesteredProcessor
from .QLHEFT import QLHEFT
from  sched_lib.scheduler.list_scheduler import ListSchedulerToClusteredProcessor


class CQGAHEFT(GeneticAlgorithm):
    def __init__(
        self,
        dag: nx.DiGraph,
        num_of_population: int,
        max_population: int,
        mutation_ratio: float,
        alpha: float,
        gamma: float,
        processor: CluesteredProcessor
    ) -> None:
        super().__init__(dag.number_of_edges(), [0,1], num_of_population, max_population, mutation_ratio)
        self.G = copy.deepcopy(dag)
        self.alpha = alpha
        self.gamma = gamma
        self.P = copy.deepcopy(processor)
        self._correspond_gene_edge = {}
        for i in range(self.G.number_of_edges()):
            self._correspond_gene_edge[str(i)] = list(self.G.edges)[i]

    def _get_sched_list_from_chromosome(self, chromosome: Chromosome) -> List[int]:
        G = copy.deepcopy(self.G)
        for i, v in enumerate(chromosome.gene_list):
            if(v == 1):
                G.edges[self._correspond_gene_edge[str(i)]]['comm'] = int(G.edges[self._correspond_gene_edge[str(i)]]['comm'] * self.P.inout_ratio)

        qlheft = QLHEFT(G, self.alpha, self.gamma)
        qlheft.learn(50000)

        return qlheft.get_sched_list()

    def _calc_fitness(self) -> None:
        for chromosome in self.population:
            G = copy.deepcopy(self.G)
            P = copy.deepcopy(self.P)
            sched_list = self._get_sched_list_from_chromosome(chromosome)
            S = ListSchedulerToClusteredProcessor(G, P, sched_list)
            S.schedule()
            chromosome.fitness = S.get_makespan()
        self.print_population()

    def evolution(self) -> None:
        evolution_start_time = time.time()

        self._calc_fitness()
        for _ in range(self.max_population):
            offspring = self._elite_select(int(np.ceil(len(self.population) / 4)))

            # crossover
            children = []
            for i in range(int(np.ceil((len(self.population)-len(offspring)) / 2))):
                gene1 = random.choice(offspring)
                gene2 = random.choice(offspring)
                child1, child2 = self._single_point_crossover(gene1, gene2)
                children.append(child1)
                children.append(child2)  
            offspring += children

            self.population = offspring
            self._mutate()
            self._calc_fitness()
            
            # timeout
            if(time.time() - evolution_start_time > 14400):
                break

        self.duration = time.time() - evolution_start_time

    def get_sched_list(self) -> List[int]:
        sorted_population = sorted(self.population, key=lambda x: x.fitness)
        return self._get_sched_list_from_chromosome(sorted_population[0])

    def print_population(self) -> None:
        for i, chromosome in enumerate(self.population):
            print(f'chromosome {i}: {chromosome.fitness}')
        print('---------------------------------------')
