from model.common_genome_data import *
from model.model import *
from model.model_constants import INPUT_NETWORK_SIZE, OUTPUT_NETWORK_SIZE
from simulation.sim_constants import (FITNESS_MULITPLIER_LC, HARD_DROP_COUNT_PENALTY_MULTIPLIER, 
                                      LIFETIME_VALUE_MULTIPLIER, ALMOST_CLEARED_LINES_MULTIPLIER, 
                                      HEIGHT_PENALTY_MULTIPLIER, GAME_OVER_PENALTY, POSITIONING_BONUS_MULTIPLIER)
from game.model_scripts.game_with_ai import TetrisGameWithAI
from game.constants import DEFAULT_SEED, FPS, ALMOST_COMPLETE_LINES_BLOCK_COUNT
from model.genome import InnovationDatabase
from misc.visualizers import visualize_phenotype, draw_diagrams
import numpy as np
import pygame
import sys
import time
from collections import deque

class ExpSpecimen:
    def __init__(self, model:Model, fitness:int):
        self.fitness = fitness
        self.model = model

class Experiment:
    def __init__(self, iteration_count:int, population_size:int, tournament_size:int, elite_size_percent:float, enable_pruning:bool, prune_percent: float, stagnation_mean_percent: float, common_rates:CommonRates):
        self.iteration_count = iteration_count
        self.population_size = population_size
        self.tournament_size = tournament_size
        self.common_rates = common_rates
        self.elite_size_percent = elite_size_percent
        self.enable_pruning = enable_pruning
        self.prune_percent = prune_percent
        self.stagnation_threshold = stagnation_mean_percent
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
        best_fitness_ever = 0
        best_specimen = population[0]
        
        fl_popSize = float(self.population_size)
        fitnessSumPerIt = 0.0
        runtimeSum_s_PerIt = 0.0
        clearedLinesPerIt = 0.0
        
        (max_lines_cleared, iteration_for_lines) = (0, 0)
        
        mean_fitnesses = []
        mean_runtime = []
        mean_clearedLines = []
        mean_hard_drop_percent = []
        
        # previous pruning
        previous_avg = deque()
        
        # main 'training' loop
        while (current_iteration <= self.iteration_count):
            print(f'Current iteration: {current_iteration}')
            #print(f'Best specimen was {best_specimen.fitness}')
            # run test (headless) for each and set fitness
            
            fitnessSumPerIt = 0.0
            runtimeSum_s_PerIt = 0.0
            clearedLinesPerIt = 0.0
            hard_drops = 0
            moves = 0
            max_move_count = 1000
            current_pop = 1
            for specimen in population:
                #print(f'Specimen {current_pop}')
                current_pop += 1
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
                    if game.move_count >= max_move_count:
                        print('Time is up')
                        break
                runtime = time.time() - start
                runtimeSum_s_PerIt += runtime
                #print(f'This game ran for: {runtime} with {game.move_count} moves.')
                clearedLinesPerIt += game.lines_cleared
                almost_cleared = game.board.get_almost_complete_lines(ALMOST_COMPLETE_LINES_BLOCK_COUNT).count(1)
                avg_height = game.final_average_board_height
                specimen.fitness =  self._calculate_fitness(game.score, game.lines_cleared, game.move_count, game.hard_drop_count, 
                                                            almost_cleared_lines_count=almost_cleared, average_board_height=avg_height, is_game_over=game.game_over)
                   
                #print(f'Game score: {game.score}. Fitness: {specimen.fitness}.')
                #specimen.fitness = game.score
                #print(f'Specimen finess: {specimen.fitness}')
                fitnessSumPerIt += specimen.fitness
                
                if max_lines_cleared < game.lines_cleared:
                    max_lines_cleared = game.lines_cleared
                    iteration_for_lines = current_iteration
                
                hard_drops += game.hard_drop_count
                moves += game.move_count
                if (specimen.fitness > best_fitness_ever):
                    best_fitness_ever = specimen.fitness
                    best_specimen = specimen
                    print(f'Best specimen changed fitness to: {best_specimen.fitness}')
            
            avg_fitness = fitnessSumPerIt / fl_popSize
            move_count_percent = hard_drops / float(moves)
            mean_hard_drop_percent.append(move_count_percent)
            avg_time = runtimeSum_s_PerIt / fl_popSize
            avg_linesCleared = clearedLinesPerIt / fl_popSize
            mean_fitnesses.append(avg_fitness)
            print(f'Mean fitness: {avg_fitness}, iteration: {current_iteration}')
            print(f'Mean moves per game: {moves / fl_popSize}, iteration: {current_iteration}')
            mean_runtime.append(avg_time)
            mean_clearedLines.append(avg_linesCleared)
                        
            # overwrite diagrams per iteration
            draw_diagrams(generations=self.iteration_count,mean_scores=mean_fitnesses, mean_runtimes=mean_runtime, mean_clearedLines=mean_clearedLines, 
                          best_fitness=best_specimen.fitness, pop_size=self.population_size, common_rates=self.common_rates, 
                          fps_recordered=FPS, max_lines=max_lines_cleared, iteration_lines=iteration_for_lines)
            
            # sort population by fitness (descending order)
            sorted_population = sorted(population, key=lambda x: x.fitness, reverse=True)
            
            #if self.enable_pruning:
            #    if len(previous_avg) >= 5:
            #        previous_avg.popleft()
            #    
            #    previous_avg.append(avg_fitness)
            #    #variance = sum([pow((avg_fitness - previous), 2) for previous in previous_avg]) / len(previous_avg)
            #    
            #    #if len(previous_avg) >= 5:
            #    #    mean_of_means = sum(previous_avg) / len(previous_avg)
            #    #    coefficient_of_variation = (variance ** 0.5) / max(mean_of_means, 1)
            #    #
            #    #    if coefficient_of_variation < self.stagnation_threshold:
            #    #        print('Hell yeah we prunin')
            #    #        population_for_pruning_size = self.population_size * self.prune_percent
            #    #        for i in range(self.population_size - population_for_pruning_size, self.population_size):
            #    #            new_model = Model.generate_network(INPUT_NETWORK_SIZE, OUTPUT_NETWORK_SIZE, self.common_rates, common_innovation_db)
            #    #            population[i] = ExpSpecimen(new_model, 0)
            #    if len(previous_avg) >= 5:
            #        mean_of_means = sum(previous_avg) / len(previous_avg)
            #        if mean_of_means + self.stagnation_threshold * avg_fitness > avg_fitness:
            #            population_for_pruning_size = int(self.population_size * self.prune_percent)
            #            print('Hell yeah we prunin')
            #            for i in range(self.population_size - population_for_pruning_size, self.population_size - 1):
            #                new_model = Model.generate_network(INPUT_NETWORK_SIZE, OUTPUT_NETWORK_SIZE, self.common_rates, common_innovation_db)
            #                sorted_population[i] = ExpSpecimen(new_model, 0)
            #                previous_avg.clear()
            
            
            if sorted_population[0].fitness > best_specimen.fitness:
                best_specimen = population[0]
                
            next_population = [None] * corrected_size

            # elitism
            elite_size = int(self.elite_size_percent * self.population_size)
            for i in range(0, elite_size):
                next_population[i] = self._copy_specimen(sorted_population[i])                
                        
            
            # tournament selection and crossover
            for i in range(elite_size, corrected_size):
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

            # mutation for each except elitism
            for specimen in next_population[elite_size:]:
                self._apply_mutations(specimen)
            
            # replace old population
            population = next_population
            current_iteration += 1
        
        print(f'Best fitness is: {best_specimen.fitness}')
        print(f'Mean hard drop percent of moves: {sum(mean_hard_drop_percent)/self.iteration_count}')
        draw_diagrams(generations=self.iteration_count,
                      mean_scores=mean_fitnesses, mean_runtimes=mean_runtime, mean_clearedLines=mean_clearedLines, 
                      best_fitness=best_specimen.fitness, pop_size=self.population_size, common_rates=self.common_rates, 
                      fps_recordered=FPS, max_lines=max_lines_cleared, iteration_lines=iteration_for_lines)
        #visualize_phenotype(best_specimen.model.genome)
        
    def _calculate_fitness(self, score, lines_cleared, moves_count, hard_drop_count, almost_cleared_lines_count, average_board_height, is_game_over):
        base = score + (lines_cleared * FITNESS_MULITPLIER_LC)
        efficiency_bonus = 0.0 # score / max(1, moves_count)
        lifetime_bonus = 0.0 #moves_count * LIFETIME_VALUE_MULTIPLIER
        life_bonus = 0.0
        if moves_count > 50:
            life_bonus += 10.0
        if moves_count > 100:
            life_bonus += 60.0
        if moves_count > 200:
            life_bonus += 150
        #    print(f'Life bonus: {life_bonus} at: {moves_count}')
        
        #lifetime_bonus = moves_count * LIFETIME_VALUE_MULTIPLIER
        almost_cleared_lines_bonus = almost_cleared_lines_count * ALMOST_CLEARED_LINES_MULTIPLIER
        hard_drop_penalty = hard_drop_count * HARD_DROP_COUNT_PENALTY_MULTIPLIER
        board_height_penalty = average_board_height * HEIGHT_PENALTY_MULTIPLIER
        positioning_bonus = (moves_count - hard_drop_count) * POSITIONING_BONUS_MULTIPLIER
        
        #if float((moves_count - hard_drop_count)/moves_count) <= 0.55:
        #    positioning_bonus += 30.0
        #print(f'Board height penalty is: {board_height_penalty}')
        game_over_penalty = GAME_OVER_PENALTY if is_game_over else 0.0
        return base + efficiency_bonus + positioning_bonus + lifetime_bonus + almost_cleared_lines_bonus + life_bonus - board_height_penalty - hard_drop_penalty - game_over_penalty
    
    def _apply_mutations(self, specimen):
        if self.rng.random() < self.common_rates.node_addition_mutation_rate:
            specimen.model.genome.mutation_add_node()
        if self.rng.random() < self.common_rates.connection_addition_mutation_rate:
            specimen.model.genome.mutation_add_connection()
        if self.rng.random() < self.common_rates.weight_mutation_rate:
            specimen.model.genome.mutation_change_random_weight()
        if self.rng.random() < self.common_rates.activation_mutation_rate:
            specimen.model.genome.mutation_change_activation_function()
        if self.rng.random() < self.common_rates.connection_change_mutation_rate:
            specimen.model.genome.mutation_change_connection()
            
    def _copy_specimen(self, specimen):
        copied_genome = specimen.model.genome.copy()
        copied_model = Model(genome=copied_genome, previous_network_fitness=specimen.fitness)
        return ExpSpecimen(copied_model, specimen.fitness)