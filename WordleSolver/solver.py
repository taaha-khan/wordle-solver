
from collections import defaultdict
import numpy as np
import itertools
import string

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
				if target[i] == letter:
					result += 'y'
				else:
					result += 'm'
		return result

	def rank_solutions(self, solutions):

		solutions = list(solutions)
		if len(solutions) == 1: return (solutions, {solutions[0]: 0.0})

		scores = {}

		for i, target in enumerate(solutions):

			solutions.pop(i)

			groups = defaultdict(int)
			for word in solutions:
				result = self.get_result(word, target)
				groups[result] += 1
			scores[target] = np.mean(list(groups.values()))

			solutions.insert(i, target)

			# score
			# ynnnn: 10
			# ynnny: 2
			# yyynn: 1
			# 

		sort = list(sorted(scores, key = scores.get))
		return (sort, scores)
		
	def rank_solutions_old(self, words):

		freq = defaultdict(int)
		location = defaultdict(int)

		for word in self.valid_answers:
			for i, letter in enumerate(word):
				freq[letter] += 1
				location[(i, letter)] += 1

		scores = defaultdict(float)
		for word in words:
			completed = set()
			for i, letter in enumerate(word):
				if letter not in completed: scores[word] -= freq[letter]
				scores[word] -= location[(i, letter)] * 0.5
				completed.add(letter)

		sort = list(sorted(scores, key = scores.get))
		return (sort, scores)

	def run_until_found(self, target, heuristic, start = 'salet'):

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
				best_guesses = [word for word in solutions if scores[word] == min(scores.values())]
				if target in best_guesses:
					return guesses
				guess = sorted(best_guesses)[0]

			result = self.get_result(guess, target)
