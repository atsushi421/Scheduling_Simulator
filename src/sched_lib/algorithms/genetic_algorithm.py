import random
import time
from typing import List, Tuple
from abc import ABCMeta, abstractmethod


class Chromosome:
    def __init__(self, length: int, gene_options: List[int]):
        self.fitness = -1
        self.gene_list = [random.choice(gene_options) for _ in range(length)]


class GeneticAlgorithm(metaclass=ABCMeta):
    def __init__(
        self,
        chromosome_length: int,
        gene_options: List[int],
        num_of_population: int,
        max_population: int,
        mutation_ratio: float,
    ) -> None:
        self.chromosome_length = chromosome_length
        self.gene_options = gene_options
        self.max_population = max_population
        self.mutation_ratio = mutation_ratio
        self.population = [Chromosome(self.chromosome_length, gene_options) for _ in range(num_of_population)]
        self.duration = None

    @abstractmethod
    def _calc_fitness(self):
        pass

    @abstractmethod
    def evolution(self):
        pass

    def _elite_select(self, num_of_selections: int) -> List[int]:
        elite = sorted(self.population, key=lambda x: x.fitness)
        return elite[:num_of_selections]

    def _single_point_crossover(self, gene1: Chromosome, gene2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        gene1_after_cross = Chromosome(self.chromosome_length, self.gene_options)
        gene2_after_cross = Chromosome(self.chromosome_length, self.gene_options)

        cross_point = random.randint(0, self.chromosome_length)
        gene1_after_cross.gene_list = gene1.gene_list[cross_point:] + gene2.gene_list[:cross_point]
        gene2_after_cross.gene_list = gene2.gene_list[cross_point:] + gene1.gene_list[:cross_point]

        return gene1_after_cross, gene2_after_cross

    def _mutate(self) -> None:
        for chromosome in self.population:
            for gene in chromosome.gene_list:
                if(random.random() < self.mutation_ratio):
                    gene = random.choice(self.gene_options)
