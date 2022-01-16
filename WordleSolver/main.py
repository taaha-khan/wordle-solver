from collections import defaultdict
import string

letters = string.ascii_lowercase
valid_words = set([line.rstrip('\n') for line in open('5_letter_words.txt')])

def rank_words(words, get_scores = False):

	freq = defaultdict(int)

	for word in words:
		for letter in word:
			freq[letter] += 1

	lowest = min(freq.values())
	for letter in letters:
		freq[letter] /= lowest

	scores = defaultdict(float)
	for word in words:
		for letter in set(word):
			scores[word] += freq[letter]

	sort = list(sorted(scores, key = scores.get, reverse = True))
	if get_scores: return sort, scores
	return sort

ranked = rank_words(valid_words)
print(f'Recomended start word: {ranked[0]}\n')

guessed = set()

data = {letter: {'confirmed': set(), 'incorrect': set(), 'possible': True} for letter in letters}

while True:

	input_word = input('Enter word: ')
	output_scores = input('Enter scores in order as (y/n/m): ')

	assert(len(output_scores) == len(input_word) == 5)
	assert(input_word in valid_words)
	assert(len([let for let in output_scores if let not in 'ynm']) == 0)

	guessed.add(input_word)
	possible_solutions = []

	for i, letter in enumerate(input_word):
		score = output_scores[i]

		if score == 'n':
			data[letter]['possible'] = False

		elif score == 'm':
			data[letter]['incorrect'].add(i)

		elif score == 'y':
			data[letter]['confirmed'].add(i)
		
	for word in valid_words:
		# Check if word fits all criteria

		if word in guessed:
			continue

		possible = True

		for i, letter in enumerate(word):
			if not data[letter]['possible']:
				possible = False
				break

			elif i in data[letter]['incorrect']:
				possible = False
				break

			for let in letters:
				found = (len(data[let]['incorrect']) > 0)
				if found and let not in word:
					possible = False
					break
				if not possible: break

		if possible:

			ye = True
			for letter in letters:
				confirmed = data[letter]['confirmed']
				for index in confirmed:
					if word[index] != letter:
						ye = False
						break
				if not ye: break

			if ye:
				possible_solutions.append(word) 
	
	if len(possible_solutions) == 0:
		print(f'!ERROR FOUND NO VALID SOLUTIONS!')
		exit()

	sorted_solutions, scores = rank_words(possible_solutions, get_scores = True)

	sol = f'\n{len(sorted_solutions)} valid solutions'
	print(sol + '\n' + ('-' * (len(sol) - 1)))
	for i in range(min(len(sorted_solutions), 15)):
		word = sorted_solutions[i]
		rank = (str(i + 1) + '.').ljust(3)
		print(f'{rank} {word} | {scores[word]}')
	print(f'RECOMENDED WORD: {sorted_solutions[0]}\n')
