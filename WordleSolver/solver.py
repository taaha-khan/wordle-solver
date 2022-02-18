
from collections import defaultdict
import numpy as np
import itertools
import string
import math
import json

class Solver:

	def __init__(self, valid_answers, valid_guesses):

		self.valid_answers = valid_answers
		self.valid_guesses = valid_guesses

		self.possible_solutions = list(self.valid_answers.copy())

		self.letters = string.ascii_lowercase
		self.len = len(list(self.valid_answers)[0])

		self.info = [{'confirmed': None, 'incorrect': set()} for _ in range(self.len)]
		self.invalid_letters = set()
		self.valid_letters = set()

		self.history = []
	
	def update(self, guess, result):

		self.history.append((guess, result))
		if guess in self.possible_solutions:
			self.possible_solutions.remove(guess)

		for i, letter in enumerate(guess):
			score = result[i]

			if score == 'y':
				self.valid_letters.add(letter)
				self.info[i]['confirmed'] = letter
		
			elif score == 'n':
				if letter not in self.valid_letters:
					self.invalid_letters.add(letter)

			elif score == 'm':
				self.valid_letters.add(letter)
				self.info[i]['incorrect'].add(letter)
			
		for n in range(len(self.possible_solutions) - 1, -1, -1):
			# Check if word fits all criteria
			word = self.possible_solutions[n]

			used_letters = set(word)

			# Word uses letters that are invalid
			if (used_letters & self.invalid_letters):
				self.possible_solutions.pop(n)
				continue

			# Does not use letters that are confirmed valid
			elif (used_letters & self.valid_letters) != self.valid_letters:
				self.possible_solutions.pop(n)
				continue

			for i, letter in enumerate(word):
				
				# This index did not use the confirmed letter
				if None != self.info[i]['confirmed'] != letter:
					self.possible_solutions.pop(n)
					break

				# This letter cannot be guessed here
				elif letter in self.info[i]['incorrect']:
					self.possible_solutions.pop(n)
					break

		return self.possible_solutions

	def get_result(self, guess, target):
		result = ''
		for i, letter in enumerate(guess):
			if letter not in target:
				result += 'n'
			elif letter in target:
				target = target.replace(letter, '_', 1)
				if target[i] == letter:
					result += 'y'
				else:
					result += 'm'
		return result

	def print_dict(self, data):
		for key in data:
			print(f'{key}: {data[key]}')

	def search_tree(self, solutions):
		best_scores = {}
		
		_, _, groups = self.rank_solutions_v3(solutions, get_groups = True)
		for result in groups.keys():
			next_group = groups[result]
			_, scores = self.rank_solutions_v3(next_group)
			score = np.mean(list(scores.values()))
			for n in next_group:
				best_scores[n] = score
			# print(f'{result}: {len(next_group)} = {score}')

		sort_2 = list(sorted(solutions, key = best_scores.get, reverse = True))
		return (sort_2, best_scores)

	def rank_solutions_v4(self, solutions, get_groups = False):

		solutions = list(solutions)
		if len(solutions) == 1:
			return (solutions, {solutions[0]: 0.0})

		scores = {}

		for i, target in enumerate(self.valid_guesses):

			groups = defaultdict(list)
			for word in solutions:
				result = self.get_result(word, target)
				groups[result].append(word)

			information = 0.0
			for pattern in groups.keys():
				prob = len(groups[pattern]) / len(solutions)
				information += prob * -math.log2(prob)

			valid_probability = 0.0
			if target in set(solutions):
				valid_probability = 1 / len(solutions)

			scores[target] = information + valid_probability

		sort = list(sorted(scores, key = scores.get, reverse = True))
		if get_groups: 
			return (sort, scores, groups)
		return (sort, scores)

	def rank_solutions_v3(self, solutions, get_groups = False):

		solutions = list(solutions)
		if len(solutions) == 1:
			return (solutions, {solutions[0]: 0.0})

		scores = {}
		all_groups = defaultdict(list)

		for i, target in enumerate(solutions):

			solutions.pop(i)

			groups = defaultdict(list)
			for word in solutions:
				result = self.get_result(word, target)
				groups[result].append(word)
				all_groups[result].append(word)

			solutions.insert(i, target)

			information = 0.0
			for pattern in groups.keys():
				prob = len(groups[pattern]) / len(solutions)
				information += prob * -math.log2(prob)

			scores[target] = information
			# all_groups.update(dict(groups))

		sort = list(sorted(scores, key = scores.get, reverse = True))
		if get_groups: 
			return (sort, scores, all_groups)
		return (sort, scores)

	def rank_solutions_v2(self, solutions):

		solutions = list(solutions)
		if len(solutions) == 1:
			return (solutions, {solutions[0]: float('inf')})

		scores = {}

		for i, target in enumerate(solutions):

			solutions.pop(i)

			groups = defaultdict(int)
			for word in solutions:
				result = self.get_result(word, target)
				groups[result] += 1

			solutions.insert(i, target)

			sections = list(groups.values())
			scores[target] = -(np.mean(sections) + max(sections) / 1e5)

		sort = list(sorted(scores, key = scores.get, reverse = True))
		return (sort, scores)
		
	def run_until_found(self, target, heuristic, start = 'salet'):

		line = ''

		guesses = 0
		while True:
			guesses += 1

			if guesses == 1:
				guess = start
				if target == start:
					return 1
			else:
				solutions = self.update(guess, result)
				sorted_solutions, scores = heuristic(solutions)
				# best_guesses = [word for word in sorted_solutions if scores[word] == min(scores.values())]
				# if target in best_guesses:
				# 	return guesses
				# guess = sorted(best_guesses)[0]
				guess = sorted_solutions[0]

			line += ',' + guess

			# if guess == target:
			# 	fopen = open('data/output.txt', 'a')
			# 	fopen.write(line[1:] + '\n')
			# 	fopen.close()
			# 	return guesses

			result = self.get_result(guess, target)
