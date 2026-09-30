import random
import math
import heapq

class Board:
    directions = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

    def __init__(self):
        self.rows = 10
        self.columns = 10
        self.start = (self.rows - 1, self.columns - 1)
        self.goal = (0, 0)

        self.make_graph()

        self.player = [self.start, 0, [self.start]]
        self.agents = self._create_agents()



    # Graph ================================================================
    def _neighbours(self, row, col):
        for d_row, d_col in self.directions.values():
            r = row + d_row
            c = col + d_col
            if 0 <= r < self.rows and 0 <= c < self.columns:
                yield (r, c)

    def make_graph(self):
        self.graph = {}
        self.edge_cost = {}
        for r in range(self.rows):
            for c in range(self.columns):
                node = (r, c)
                self.graph[node] = {}
                for neighbor in self._neighbours(r, c):
                    key = (min(node, neighbor), max(node, neighbor))
                    if key not in self.edge_cost:
                        self.edge_cost[key] = random.randint(1, 50)
                    self.graph[node][neighbor] = self.edge_cost[key]

    def edge_weight(self, a, b):
        return self.edge_cost.get((min(a, b), max(a, b)), math.inf)



    # Player ================================================================
    def move_player(self, direction):
        pos = self.player[0]
        d_row = self.directions[direction][0]
        d_col = self.directions[direction][1]
        new_pos = (pos[0] + d_row, pos[1] + d_col)
        if 0 <= new_pos[0] < self.rows and 0 <= new_pos[1] < self.columns:
            self.player[1] += self.edge_weight(pos, new_pos)
            self.player[0] = new_pos
            self.player[2].append(new_pos)
            return True
        return False

    def player_at_goal(self):
        return self.player[0] == self.goal



    # Agents ================================================================
    def advance_agents(self):
        for agent in self.agents:
            plan = agent["plan"]
            try:
                index = plan.index(agent["pos"])
            except ValueError:
                index = 0
            if index + 1 < len(plan):
                next_Node = plan[index + 1]
                agent["cost"] += self.edge_weight(agent["pos"], next_Node)
                agent["pos"] = next_Node
                agent["path"].append(next_Node)

    def agents_at_goal(self):
        return [a for a in self.agents if a["pos"] == self.goal]

    def all_finished(self):
        return self.player_at_goal() and all(a["pos"] == self.goal for a in self.agents)

    def results(self):
        entries = [("You", self.player[1])]
        for a in self.agents:
            entries.append((a["name"], a["cost"]))
        return sorted(entries, key=lambda x: x[1])



    # MakeAgents ================================================================
    def _create_agents(self):
        agents = []
        warm_population = self._warm_up(size=60, sa_iter=1200)

        agents.append({"name": "Greedy", "pos": self.start, "cost": 0, "path": [self.start], "algo": "greedy", "plan": self._greedy_plan(), "image": "greedy_dot"})

        sa_settings = [(400.0, 0.5, 10000, self._random_path), (150.0, 0.5, 10000, self._cheapest_neighbour_path)]
        sa_plans = []
        for i, (T_start, T_end, iters, seed_fn) in enumerate(sa_settings):
            plan = self._sa_plan(iterations=iters, Temp_start=T_start, Temp_end=T_end, seed=seed_fn())
            sa_plans.append(plan)
            agents.append({"name": f"SA-{i+1}", "pos": self.start, "cost": 0, "path": [self.start], "algo": "sa", "plan": plan, "image": "sa_dot"})

        agents.append({"name": "GA-1", "pos": self.start, "cost": 0, "path": [self.start], "algo": "ga", "plan": self._ga_plan(warm_population + sa_plans), "image": "ga_dot"})
        agents.append({"name": "A*-1", "pos": self.start, "cost": 0, "path": [self.start], "algo": "astar", "plan": self._astar(), "image": "astar_dot"})
        return agents



    # Pathing ================================================================
    
    
    # Move toward the goal using Manhattan distance
    # Break ties with edge cost
    def _greedy_plan(self):
        path = [self.start]
        visited = {self.start}
        node = self.start
        while node != self.goal:
            neighbors = [n for n in self._neighbours(*node) if n not in visited]
            if not neighbors:
                break
            node = min(neighbors, key=lambda n: (abs(n[0] - self.goal[0]) + abs(n[1] - self.goal[1]), self.edge_weight(node, n)))
            visited.add(node)
            path.append(node)
        return path



    # Picks the cheapest immediate option
    #Used as a more stable starting path for SA
    def _cheapest_neighbour_path(self):
        path = [self.start]
        visited = {self.start}
        node = self.start
        while node != self.goal:
            neighbors = [(self.edge_weight(node, n), n) for n in self._neighbours(*node) if n not in visited]
            if not neighbors:
                for prev in reversed(path[:-1]):
                    backtrack_list = [(self.edge_weight(prev, n), n) for n in self._neighbours(*prev) if n not in visited]
                    if backtrack_list:
                        node = min(backtrack_list)[1]
                        visited.add(node)
                        path.append(node)
                        break
                else:
                    break
            else:
                node = min(neighbors)[1]
                visited.add(node)
                path.append(node)
        return path


    # Picks randomly
    # Used to seed SA && population diversity for Genetic
    def _random_path(self):
        path = [self.start]
        visited = {self.start}
        node = self.start
        while node != self.goal:
            neighbors = [n for n in self._neighbours(*node) if n not in visited]
            if not neighbors:
                for prev in reversed(path[:-1]):
                    backtrackOptions = [n for n in self._neighbours(*prev) if n not in visited]
                    if backtrackOptions:
                        node = random.choice(backtrackOptions)
                        visited.add(node)
                        path.append(node)
                        break
                else:
                    break
            else:
                node = random.choice(neighbors)
                visited.add(node)
                path.append(node)
        return path



    ## Rebuilds a path between two nodes
    # simulated annealing and genetic use this to modify paths
    def _partial_random(self, startpoint, endpoint):
        path = [startpoint]
        visited = {startpoint}
        node = startpoint
        for _ in range(self.rows * self.columns * 2):
            if node == endpoint:
                break
            neighbors = list(self._neighbours(*node))
            if not neighbors:
                break
            weights = [1.0 / (abs(n[0] - endpoint[0]) + abs(n[1] - endpoint[1]) + 1) for n in neighbors]
            total = sum(weights)
            node = random.choices(neighbors, weights=[weight / total for weight in weights])[0]
            if node not in visited:
                visited.add(node)
                path.append(node)
        # If we failed to reach point, do the rest with greedy
        # prevent teleporting
        if path[-1] != endpoint:
            current = path[-1]
            fallbackVisited = set(path)
            while current != endpoint:
                neighbors = [n for n in self._neighbours(*current) if n not in fallbackVisited]
                if not neighbors:
                    neighbors = list(self._neighbours(*current))
                    if not neighbors:
                        break
                current = min(neighbors, key=lambda n: abs(n[0] - endpoint[0]) + abs(n[1] - endpoint[1]))
                fallbackVisited.add(current)
                path.append(current)
        return path

    def _path_cost(self, path):
        return sum(self.edge_weight(path[i], path[i + 1]) for i in range(len(path) - 1))


        # Accepts worse solutions with random probability (avoid local minima)
    # High temp = tons of exploration; cool down over time to hopefully converge
    def _sa_plan(self, iterations=3000, Temp_start=200.0, Temp_end=0.5, seed=None):
        current = seed[:] if seed is not None else self._random_path()
        best = current[:]
        best_c = self._path_cost(best)
        temp = Temp_start
        for _ in range(iterations):
            temp = max(temp * 0.997, Temp_end)
            if len(current) < 4:
                candidate = self._random_path()
            else:
                i = random.randint(0, len(current) - 2)
                j = random.randint(i + 1, len(current) - 1)
                candidate = current[:i] + self._partial_random(current[i], current[j]) + current[j + 1:]
            c_cost = self._path_cost(candidate)
            if c_cost == math.inf: #reject teleportation; return to monkey
                continue
            difference = c_cost - self._path_cost(current)

            # Accepts worse solutions with random probability
            if difference < 0 or random.random() < math.exp(-difference / max(temp, 1e-9)):
                current = candidate
                if c_cost < best_c:
                    best = candidate[:]
                    best_c = c_cost
        return best




    # Evolves a mutating population of paths over many generations
    # Keeps better solutions and combines them
    # Uses SA-generated paths for seeds and the SA mutation function
    def _ga_plan(self, seed_pool, population_size=30, generations=80):
        population = [p[:] for p in seed_pool]
        while len(population) < population_size:
            population.append(self._random_path())
        population = population[:population_size]

        def fitness(p): return self._path_cost(p)
        def tournament(k=4): return min(random.sample(population, k), key=fitness)

        for gen in range(generations):
            elite = sorted(population, key=fitness)[:2]
            new_pop = [e[:] for e in elite]
            mutation_r = 0.4 * (1 - gen / generations) + 0.1
            while len(new_pop) < population_size:
                child = self._cross(tournament(), tournament())
                if random.random() < mutation_r:
                    child = self._sa_mutate(child)
                new_pop.append(child)
            population = new_pop

        return min(population, key=fitness)

    def _cross(self, parent1, parent2):
        common = (set(parent1) & set(parent2)) - {self.start}
        if not common:
            return parent1[:]
        pivot = random.choice(list(common))
        return parent1[:parent1.index(pivot)] + parent2[parent2.index(pivot):]

    def _sa_mutate(self, path):
        if len(path) < 4:
            return path
        i = random.randint(0, len(path) - 2)
        j = random.randint(i + 1, len(path) - 1)
        return path[:i] + self._partial_random(path[i], path[j]) + path[j + 1:]


    #runs simulated annealing many times to make good starting paths for genetic algo
    def _warm_up(self, size=60, sa_iter=1200):
        pool = []
        for i in range(size):
            temp = 50.0 + (i / size) * 350.0
            pool.append(self._sa_plan(iterations=sa_iter, Temp_start=temp, Temp_end=0.5, seed=None))
        return pool
    


    # A*: cost so far + heuristic cost to goal (Manhattan)
    def _astar(self):
        def h(node):
            return abs(node[0] - self.goal[0]) + abs(node[1] - self.goal[1])

        frontier = []
        heapq.heappush(frontier, (h(self.start), self.start))
        cost_so_far = {self.start: 0}
        previous = {self.start: None}

        while frontier:
            current_priority, current_node = heapq.heappop(frontier)
            if current_node == self.goal:
                break
            for neighbor, edge_cost in self.graph[current_node].items():
                new_cost = cost_so_far[current_node] + edge_cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + h(neighbor)
                    heapq.heappush(frontier, (priority, neighbor))
                    previous[neighbor] = current_node

        path = []
        node = self.goal
        while node is not None:
            path.append(node)
            node = previous.get(node)
        path.reverse()
        return path