from model.common_genome_data import *
from model.model import *
from model.model_constants import INPUT_NETWORK_SIZE, OUTPUT_NETWORK_SIZE
from simulation.sim_constants import FITNESS_MULITPLIER_LC, HARD_DROP_COUNT_MULTIPLIER
from game.model_scripts.game_with_ai import TetrisGameWithAI
from game.constants import DEFAULT_SEED, FPS
from model.genome import InnovationDatabase
from misc.visualizers import visualize_phenotype, draw_diagrams
import numpy as np
import pygame
import sys
import time

class ExpSpecimen:
    def __init__(self, model:Model, fitness:int):
        self.fitness = fitness
        self.model = model

class Experiment:
    def __init__(self, iteration_count:int, population_size:int, tournament_size:int, common_rates:CommonRates):
        self.iteration_count = iteration_count
        self.population_size = population_size
        self.tournament_size = tournament_size
        self.common_rates = common_rates
        self.rng = np.random.default_rng()

    def tournament_selection(self, population):
        contenders = self.rng.choice(
            population, 
            size=self.tournament_size, 
            replace=False
        )
        
        # The winner is the one with the highest fitness
        winner = max(contenders, key=lambda x: x.fitness)
        return winner
        
    def __call__(self):
        # Initialize pygame
        pygame.init()
        
        # Set up the display
        #screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        #pygame.display.set_caption(TITLE)
        
        # Create a clock for controlling the frame rate
        clock = pygame.time.Clock()
        
        # Create a game instance
        #game = TetrisGame()
        #game = TetrisGameWithAI(seed=seed, ai_model=ai_model)
        corrected_size = self.population_size - 1
        
        population = [None] * corrected_size
        next_population = [None] * corrected_size
        common_innovation_db = InnovationDatabase(INPUT_NETWORK_SIZE + OUTPUT_NETWORK_SIZE)
        # create initial population
        for i in range(corrected_size):
            print(f'Creating new specimen.')
            model = Model.generate_network(input_size=INPUT_NETWORK_SIZE, output_size=OUTPUT_NETWORK_SIZE, common_rates=self.common_rates, innovation_db=common_innovation_db)
            spec = ExpSpecimen(model, 0)
            population[i] = spec
        
        current_iteration = 1
        best_specimen = population[0]
        
        fl_popSize = float(self.population_size)
        fitnessSumPerIt = 0.0
        runtimeSum_s_PerIt = 0.0
        clearedLinesPerIt = 0.0
        
        mean_fitnesses = []
        mean_runtime = []
        mean_clearedLines = []
        
        # main 'training' loop
        while (current_iteration <= self.iteration_count):
            print(f'Current iteration: {current_iteration}')
            # run test (headless) for each and set fitness
            
            fitnessSumPerIt = 0.0
            runtimeSum_s_PerIt = 0.0
            clearedLinesPerIt = 0.0
            for specimen in population:
                game = TetrisGameWithAI(seed=DEFAULT_SEED, ai_model=specimen.model)
                start = time.time() # will be in seconds I guess
                while (not game.game_over):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            game.handle_input(event.key)
                    game.update()
                    clock.tick(FPS)
                runtimeSum_s_PerIt += time.time() - start
                clearedLinesPerIt += game.lines_cleared
                specimen.fitness = game.score + (game.lines_cleared * FITNESS_MULITPLIER_LC) - (game.hard_drop_count * HARD_DROP_COUNT_MULTIPLIER)
                #specimen.fitness = game.score
                #print(f'Specimen finess: {specimen.fitness}')
                fitnessSumPerIt += specimen.fitness
                if (specimen.fitness > best_specimen.fitness):
                    best_specimen = specimen
            
            avg_fitness = fitnessSumPerIt / fl_popSize
            avg_time = runtimeSum_s_PerIt / fl_popSize
            avg_linesCleared = clearedLinesPerIt / fl_popSize
            mean_fitnesses.append(avg_fitness)
            mean_runtime.append(avg_time)
            mean_clearedLines.append(avg_linesCleared)
            
            # sort population by fitness (descending order)
            sorted_population = sorted(population, key=lambda x: x.fitness, reverse=True)

            # elitism
            next_population[0] = sorted_population[0]

            # tournament selection and crossover
            for i in range(1, corrected_size):
                parent1 = self.tournament_selection(sorted_population)

                # crossover
                if self.rng.random() < self.common_rates.crossover_rate:
                    parent2 = self.tournament_selection(sorted_population)
                    while parent2 == parent1:
                        parent2 = self.tournament_selection(sorted_population)

                    genome1 = parent1.model.genome
                    genome2 = parent2.model.genome
                    fitness1 = parent1.fitness
                    fitness2 = parent2.fitness

                    child_genome = genome1.crossover(genome2, fitness1, fitness2)
                else:
                    # if no crossover, just clone better parent - just clone the one selected
                    #if parent1.fitness >= parent2.fitness:
                    #    child_genome = parent1.model.genome.copy()
                    #else:
                    #    child_genome = parent2.model.genome.copy()
                    child_genome = parent1.model.genome.copy()

                child_model = Model(genome=child_genome, previous_network_fitness=0)
                next_population[i] = ExpSpecimen(child_model, 0)

            # mutation for each
            for specimen in next_population[1:]:
                if self.rng.random() < self.common_rates.node_addition_mutation_rate:
                    specimen.model.genome.mutation_add_node()
                if self.rng.random() < self.common_rates.connection_addition_mutation_rate:
                    specimen.model.genome.mutation_add_connection()
                if self.rng.random() < self.common_rates.weight_mutation_rate:
                    specimen.model.genome.mutation_change_random_weight()
                if self.rng.random() < self.common_rates.activation_mutation_rate:
                    specimen.model.genome.mutation_change_activation_function()
            
            # replace old population
            for i in range(corrected_size):
                population[i] = next_population[i]
            current_iteration += 1
        
        print(f'Best fitness is: {best_specimen.fitness}')
        draw_diagrams(mean_scores=mean_fitnesses, mean_runtimes=mean_runtime, mean_clearedLines=mean_clearedLines, common_rates=self.common_rates, fps_recordered=FPS)
        visualize_phenotype(best_specimen.model.genome)
        
    
    