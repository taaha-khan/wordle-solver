# Solver for https://www.powerlanguage.co.uk/wordle/

import sys
sys.dont_write_bytecode = True

from collections import defaultdict
import numpy as np
import time

from solver import Solver

VALID_ANSWERS = set([line.rstrip('\n') for line in open('data/valid_answers.txt')])
VALID_GUESSES = set([line.rstrip('\n') for line in open('data/valid_guesses.txt')])

solver = Solver(VALID_ANSWERS, VALID_GUESSES)

def test_algorithm(heuristic):

	n_guesses = []
	times = []
	dist = defaultdict(int)
	over = []

	run = 0

	for target in VALID_ANSWERS:
		
		solver = Solver(VALID_ANSWERS, VALID_GUESSES)
		start = time.perf_counter()
		guesses = solver.run_until_found(target, heuristic, start = 'salet')
		times.append(time.perf_counter() - start)
		n_guesses.append(guesses)
		dist[guesses] += 1
		if guesses > 6: over.append(target)

		run += 1
		print(f'{run} / {len(VALID_ANSWERS)}: {[dist[i] for i in range(1, max(n_guesses) + 1)]}')

	print(f'Heuristic | Avg Guesses: {round(np.mean(n_guesses), 3)} | Max Guesses: {max(n_guesses)} | Avg time: {round(np.mean(times), 3)} sec')
	print(f'Distribution: {[dist[i] for i in range(1, max(n_guesses) + 1)]} | Incomplete: {over}')

def main():

	print(f'Recomended start word: salet\n')

	while True:

		guess = input('Enter word: ').lower()
		result = input('Enter (y/n/m): ').lower()

		solutions = solver.update(guess, result)
		sorted_solutions, scores = solver.rank_solutions(solutions)

		best_guesses = [word.upper() for word in solutions if scores[word] == min(scores.values())]

		sol = f'\n{len(sorted_solutions)} valid solutions'
		print(sol + '\n' + ('-' * (len(sol) - 1)))
		for i in range(min(len(sorted_solutions), 15)):
			word = sorted_solutions[i]
			rank = (str(i + 1) + '.').ljust(3)
			print(f'{rank} {word.upper()} | {round(scores[word], 3)}')
		print(f'Recomended word(s): {best_guesses}\n')

		if len(solutions) == 1:
			break
		
if __name__ == '__main__':
	main()
	# test_algorithm(solver.rank_solutions)
	# test_algorithm(solver.rank_solutions_old)