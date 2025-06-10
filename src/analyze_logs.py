#!/usr/bin/env python3

import csv
import os
import argparse
from collections import Counter
import statistics

def analyze_csv_log(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found")
        return
    
    move_counts = Counter()
    scores = []
    game_times = []
    probabilities_data = []
    seed = None
    
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if seed is None and 'seed' in row:
                seed = row['seed']
            
            move_type = row['move_type']
            move_counts[move_type] += 1
            
            score = int(row['score'])
            scores.append(score)
            
            game_time = float(row['game_time'])
            game_times.append(game_time)
            
            chosen_prob = float(row['chosen_probability'])
            probabilities_data.append(chosen_prob)
    
    print(f"=== Analysis of {filepath} ===")
    if seed:
        print(f"Game seed: {seed}")
    print(f"Total moves: {sum(move_counts.values())}")
    print(f"Game duration: {max(game_times):.2f} seconds")
    print(f"Final score: {max(scores)}")
    print()
    
    print("Move distribution:")
    for move, count in move_counts.most_common():
        percentage = (count / sum(move_counts.values())) * 100
        print(f"  {move}: {count} ({percentage:.1f}%)")
    print()
    
    print("Probability statistics:")
    print(f"  Average chosen probability: {statistics.mean(probabilities_data):.4f}")
    print(f"  Min chosen probability: {min(probabilities_data):.4f}")
    print(f"  Max chosen probability: {max(probabilities_data):.4f}")
    print(f"  Median chosen probability: {statistics.median(probabilities_data):.4f}")
    print()

def list_log_files(directory="logs"):
    if not os.path.exists(directory):
        print(f"Logs directory '{directory}' not found")
        return []
    
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    csv_files.sort(reverse=True)
    
    return [os.path.join(directory, f) for f in csv_files]

def compare_seeds(log_directory="logs"):
    if not os.path.exists(log_directory):
        print(f"Error: Directory {log_directory} not found")
        return
    
    seed_data = {}
    
    for filename in os.listdir(log_directory):
        if filename.endswith('.csv') and 'seed' in filename:
            filepath = os.path.join(log_directory, filename)
            
            import re
            seed_match = re.search(r'seed\[(\d+)\]', filename)
            if not seed_match:
                continue
                
            seed = seed_match.group(1)
            
            move_counts = Counter()
            scores = []
            game_times = []
            
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    
                    for row in reader:
                        move_type = row['move_type']
                        move_counts[move_type] += 1
                        
                        score = int(row['score'])
                        scores.append(score)
                        
                        game_time = float(row['game_time'])
                        game_times.append(game_time)
                
                if scores and game_times:
                    seed_data[seed] = {
                        'final_score': max(scores),
                        'game_duration': max(game_times),
                        'total_moves': sum(move_counts.values()),
                        'filename': filename
                    }
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
    
    if not seed_data:
        print("No seed-based log files found for comparison")
        return
    
    print("=== Seed Performance Comparison ===")
    print(f"{'Seed':<8} {'Final Score':<12} {'Duration (s)':<12} {'Total Moves':<12} {'Score/Move':<12}")
    print("-" * 60)
    
    sorted_seeds = sorted(seed_data.items(), key=lambda x: x[1]['final_score'], reverse=True)
    
    for seed, data in sorted_seeds:
        score_per_move = data['final_score'] / data['total_moves'] if data['total_moves'] > 0 else 0
        print(f"{seed:<8} {data['final_score']:<12} {data['game_duration']:<12.2f} {data['total_moves']:<12} {score_per_move:<12.2f}")
    
    print(f"\nBest performing seed: {sorted_seeds[0][0]} (Score: {sorted_seeds[0][1]['final_score']})")
    print(f"Worst performing seed: {sorted_seeds[-1][0]} (Score: {sorted_seeds[-1][1]['final_score']})")

def main():
    parser = argparse.ArgumentParser(description='Analyze Tetris AI CSV logs')
    parser.add_argument('--file', '-f', type=str, help='Specific CSV file to analyze')
    parser.add_argument('--list', '-l', action='store_true', help='List all available log files')
    parser.add_argument('--latest', action='store_true', help='Analyze the latest log file')
    parser.add_argument('--compare', '-c', action='store_true', help='Compare performance across different seeds')
    
    args = parser.parse_args()
    
    if args.list:
        print("Available log files:")
        files = list_log_files()
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file}")
        return
    
    if args.compare:
        compare_seeds()
        return
    
    if args.latest:
        files = list_log_files()
        if files:
            analyze_csv_log(files[0])
        else:
            print("No log files found")
        return
    
    if args.file:
        analyze_csv_log(args.file)
        return
    
    files = list_log_files()
    if files:
        print("No specific file provided. Analyzing latest log file:")
        analyze_csv_log(files[0])
    else:
        print("No log files found. Run the game first to generate logs.")

if __name__ == "__main__":
    main()
