class Rule:
    def __init__(
            self,
            format: str,
            initial_density = 1.0,
            initial_radius = 0.1
            ) -> None:
        tokens = format.split('/')
        self.survival = {int(v) for v in tokens[0].split(',')}
        self.spawn = {int(v) for v in tokens[1].split(',')}
        self.max_state = int(tokens[2])
        self.neighbor = tokens[3]
        self.initial_density = initial_density
        self.initial_radius = initial_radius

if __name__ == "__main__":
    r445m = Rule('4/4/5/M')
    print(r445m.survival, r445m.spawn, r445m.max_state, r445m.neighbor)
