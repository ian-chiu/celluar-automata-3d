class Rule:
    def __init__(
        self, name: str, format: str, initial_density=1.0, initial_radius=0.1
    ) -> None:
        self.name = name
        self.format = format
        self.initial_density = initial_density
        self.initial_radius = initial_radius

        tokens = format.split("/")
        self.survival = self._get_set_from_token(tokens[0])
        self.spawn = self._get_set_from_token(tokens[1])
        self.max_state = int(tokens[2])
        self.neighbor = tokens[3]

    def _get_set_from_token(self, token: str):
        result = set()
        values = token.split(",")
        for value in values:
            if "-" in value:
                start_value = int(value.split("-")[0])
                end_value = int(value.split("-")[1])
                for v in range(start_value, end_value + 1):
                    result.add(v)
            else:
                result.add(int(value))
        return result
