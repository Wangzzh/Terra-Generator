import random
import sys
import math
import copy

import numpy as np
import matplotlib.pyplot as plt




def apply_drift(terrain, num_drifts=10, max_drift_segments=8):
	print("Apply drift to terrain...")
	height = len(terrain)
	width = len(terrain[0])
	max_segment_length = (height + width) / num_drifts / max_drift_segments * 5
	terrain = create_potential_map_and_drift(terrain, height, width, 
		num_drifts, max_drift_segments, max_segment_length, 100)


	# Modify potentials and drit
	return terrain


def calculate_vertices(potential_map, num_segments, max_segment_length):
	height = len(potential_map)
	width = len(potential_map[0])
	vertices = [np.array([random.randrange(height), random.randrange(width)])]
	displacement = random_vector(max_segment_length)
	for i in range(num_segments):
		last = vertices[-1]
		displacement = displacement + random_vector(max_segment_length * 0.5)
		new = last + displacement
		if new[0] <= 0:
			new[0] = 0
		elif new[0] >= len(potential_map) - 1:
			new[0] = len(potential_map) - 1
		vertices.append(new)
		displacement = new - last
	return vertices


def create_potential_map_and_drift(terrain, height, width, n=10, max_drift_segments=8, max_segment_length=10, iterations=30):
	print("Creating potential map...")
	potential_map = np.zeros([height, width])
	vertices_set = []
	for i in range(n):
		num_segments = random.randrange(max_drift_segments) + 3
		vertices = calculate_vertices(potential_map, num_segments, max_segment_length)
		vertices_set.append(vertices)
		potential_map = draw_vertices_on_potential(vertices, potential_map)
	solved_map = solve_potential(potential_map)
	terrain = terrain + solved_map
	for it in range(iterations):
		print("Drifting, time=%d" % it)
		potential_map = np.zeros([height, width])
		vertices_set = modify_vertices(vertices_set, potential_map, num_segments, max_segment_length, max_segment_length / 4)
		for vertices in vertices_set:
			potential_map = draw_vertices_on_potential(vertices, potential_map)
		solved_map = solve_potential(potential_map)
		terrain = terrain + solved_map

	return terrain


def draw_vertices_on_potential(vertices, potential_map):
	height = len(potential_map)
	width = len(potential_map[0])
	power = []
	if len(vertices) == 1:
		power = [1]
	else:
		for i in range(len(vertices) - 1):
			power.append( math.sin( math.pi * (i + 0.5) / (len(vertices) - 1) ) )

	invert = random.randrange(2)
	for i in range(len(power)):
		if invert == 1:
			power[i] = - power[i]
		power[i] = power[i] * random.uniform(0,2)


	for i in range(len(vertices) - 1):
		begin = vertices[i]
		end = vertices[i + 1]
		delta_h = end[0] - begin[0]
		delta_w = end[1] - begin[1]
		num_points = math.ceil(max(abs(delta_h), abs(delta_w)))
		for j in range(num_points + 1):
			l = 1 / num_points * j
			p = l * begin + (1 - l) * end
			potential_map[math.floor(p[0])][math.floor(p[1]) % width] = power[i]
	return potential_map


def generate_empty_terrain(height, width):
	return np.zeros([height, width])


def generate_terrain(height, width):
	print("Generating terrain %d*%d..." % (height, width))
	terrain = generate_empty_terrain(height, width)
	terrain = apply_drift(terrain)
	terrain = terrain - np.mean(terrain)
	terrain = terrain / np.std(terrain) * 1000 - 100

	terrain[0][0]=5000
	terrain[-1][-1]=-5000
	show_terrain(terrain)
	land = copy.deepcopy(terrain)
	land[land<0]=-5000
	show_terrain(land)



def modify_vertices(vertices_set, potential_map, num_segments, max_segment_length, displ):
	for i in range(len(vertices_set)):
		displacement = random_vector(displ)
		r = random.randrange(8)
		for j in range(len(vertices_set[i])):
			v_displ = displacement + random_vector(displ / 4)
			vertices_set[i][j] = vertices_set[i][j] + v_displ
			if vertices_set[i][j][0] <= 0:
				vertices_set[i][j][0] = 0
			elif vertices_set[i][j][0] >= height - 1:
				vertices_set[i][j][0] = height - 0.01
	for i in range(len(vertices_set)):
		r = random.randrange(15)
		if r == 0:
			vertices_set[i] = calculate_vertices(potential_map, num_segments, max_segment_length)
	return vertices_set


def random_direction():
	theta = random.uniform(0, 2 * math.pi)
	return np.array([math.cos(theta), math.sin(theta)])


def random_vector(max_length):
	r = random_direction()
	l = random.uniform(0, max_length)
	return r * l


def show_terrain(terrain):
	plt.matshow(terrain, cmap="terrain")
	plt.colorbar()
	plt.show()


def solve_potential(potential):
	mask = potential != 0
	height = len(potential)
	width = len(potential[0])
	iterations = math.ceil((height + width) / 5)
	new_potential = potential

	for it in range(iterations):
		for h in range(height):
			for w in range(width):
				if mask[h][w] == False:
					neighbours = []
					if h != 0:
						neighbours.append(potential[h-1][w])
					if h != height - 1:
						neighbours.append(potential[h+1][w])
					neighbours.append(potential[h][(w+1)%width])
					neighbours.append(potential[h][(w-1)%width])
					s = 0
					for neighbour in neighbours:
						s += neighbour
					new_potential[h][w] = s / len(neighbours)
				else:
					new_potential[h][w] = potential[h][w]
		potential = new_potential
	return potential



if __name__ == "__main__":
	print(sys.argv)
	if len(sys.argv) <= 2:
		height = int(input('Enter height of the terrain: '))
		width = int(input('Enter width of the terrain: '))
	else:
		height = int(sys.argv[1])
		width = int(sys.argv[2])
	generate_terrain(height, width)