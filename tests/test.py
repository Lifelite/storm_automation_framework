from storm_test.storm import Scenario, StormTest, test_case


class TestTheThing(StormTest):

    def __init__(self, test_data = None):
        self.preconditions = "The thing exists"
        self.postconditions = "The thing did the other thing"
        self.description = "The thing did the other thing"
        self.scenario = Scenario(
            given="The Automation Framework",
            when=self.preconditions,
            then=self.postconditions
        )

    def set_up(self):
        print("set up")

    def set_up_each(self):
        print("set up each")

    def tear_down_each(self):
        print("tear down each")

    @test_case
    def test_the_thing(self, test_data = None):
        print("they look I did a thing")

    @test_case
    def test_the_other_thing(self, test_data = None):
        print("they did the other thing")

        self.validate(f"Quick Test of {test_data}", True, "Sucks to suck")

    def tear_down(self):
        print("tear down")


if __name__ == "__main__":
    pass
