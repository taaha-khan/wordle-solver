# Solver for https://www.powerlanguage.co.uk/wordle/

import sys
sys.dont_write_bytecode = True

from tqdm import tqdm
import progress.bar as Bar
import concurrent.futures as processor

from collections import defaultdict
import numpy as np
import time

from solver import Solver

VALID_ANSWERS = [line.rstrip('\n') for line in open('data/valid_answers.txt')]
VALID_GUESSES = set([line.rstrip('\n') for line in open('data/valid_guesses.txt')])

solver = Solver(VALID_ANSWERS, VALID_GUESSES)

def run_simulation(heuristic, target):
	solver = Solver(VALID_ANSWERS, VALID_GUESSES)
	start = time.perf_counter()
	guesses = solver.run_until_found(target, heuristic, start = 'salet')
	data = {
		'target': target,
		'guesses': guesses,
		'time': time.perf_counter() - start
	}
	print(data)
	return data

def test_algorithm_mp(heuristic):

	dist = defaultdict(int)
	guesses = []
	times = []
	over = []

	# Multiprocessing simulations
	with processor.ProcessPoolExecutor() as executor:

		# Saving data
		outputs = []
		simulations = []

		for target in VALID_ANSWERS:
			simulations.append(executor.submit(run_simulation, heuristic, target))

		bar = Bar.IncrementalBar('Processing', max = len(VALID_ANSWERS))
		for simulation in processor.as_completed(simulations):
			bar.next()

			output = simulation.result()
			outputs.append(output)

			n_guesses = output['guesses']
			guesses.append(n_guesses)
			dist[n_guesses] += 1	

			if n_guesses > 6:
				over.append(output['target'])

			times.append(output['time'])
		
		bar.finish()

	print(f'Heuristic | Avg Guesses: {round(np.mean(guesses), 3)} | Max Guesses: {max(guesses)} | Avg time: {round(np.mean(times), 3)} sec')
	print(f'Distribution: {[dist[i] for i in range(1, max(guesses) + 1)]} | Incomplete: {over}')

def main():

	print(f'Recomended start word: tares\n')

	# sorted_solutions, scores = solver.rank_solutions_v3(VALID_GUESSES)
	# fout = open('data/ranked_words.txt', 'w')
	# for word in sorted_solutions:
	# 	# print(f'{word}: {scores[word]}')
	# 	fout.write(f'{word}: {scores[word]}\n')
	# fout.close()

	while True:

		guess = input('Enter word: ').lower()
		result = input('Enter (y/n/m): ').lower()

		solutions = solver.update(guess, result)
		sorted_solutions, scores = solver.rank_solutions_v3(solutions)
		# sorted_solutions, scores = solver.search_tree(solutions)

		best_guesses = [word.upper() for word in sorted_solutions if scores[word] == max(scores.values())]

		sol = f'\n{len(sorted_solutions)} valid solutions'
		print(sol + '\n' + ('-' * (len(sol) - 1)))
		for i in range(min(len(sorted_solutions), 15)):
			word = sorted_solutions[i]
			rank = (str(i + 1) + '.').ljust(3)
			# print(f'{rank} {word.upper()} | {scores[word]}')
			print(f'{rank} {word.upper()} | {round(scores[word], 2)}')
		print(f'Recomended word(s): {best_guesses}\n')
		print(f'Valid Solutions: {[word.upper() for word in solutions]}\n')

		if len(solutions) == 1:
			break

if __name__ == '__main__':
	main()
	# test_algorithm_mp(solver.rank_solutions_v3)