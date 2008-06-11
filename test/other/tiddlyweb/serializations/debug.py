
"""
External serialization for testing remote module loading.
"""

from tiddlyweb.serializations import SerializationInterface

class Serialization(SerializationInterface):

    def list_recipes(self, recipes):
        print recipes

    def list_bags(self, bags):
        print bags

    def recipe_as(self, recipe):
        print "r_as: %s" % recipe

    def as_recipe(self, recipe, input):
        print "as_r: %s" % input

    def bag_as(self, bag):
        print "b_as: %s" % bag

    def as_bag(self, bag, input):
        print "as_b: %s" % input

    def tiddler_as(self, tiddler):
        print "t_as: %s" % tiddler

    def as_tiddler(self, tiddler, input):
        print "as_t: %s" % input
