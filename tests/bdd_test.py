from storm_test.storm_bdd import StormBehaviorDrivenTest, given, when, then, can_fail


class BDDTest(StormBehaviorDrivenTest):

    @given
    def set_up(self, test_data):
        print("set up")
        return test_data

    @given
    def set_up_each(self, test_data):
        print("set up each")
        return test_data

    @then
    def tear_down_each(self, test_data):
        print("tear down each")
        return test_data

    @can_fail
    @then
    def test_the_thing(self, test_data = None):
        print("they look I did a thing")
        if test_data:
            return True
        else:
            return False


    @then
    def test_the_other_thing(self, test_data = None):
        print("they did the other thing")

        return self.validate(f"Quick Test of {test_data}", True, "Sucks to suck")

    @when
    def tear_down(self, test_data):
        print("tear down")


if __name__ == "__main__":
    pass
