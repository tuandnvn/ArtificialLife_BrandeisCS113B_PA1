import poker_hand as ph
import util
from collections import defaultdict
import optparse

class Card_Score_Test ():
    def __init__ ( self ):
        pass

    def run ( self ):
        hands = []
        hands.append ( ph.Poker_Hand( [Card('3', 'Diamond') , Card('6', 'Heart') ,
                     Card('10', 'Heart') , Card('Q', 'Spade') ,
                          Card('K', 'Spade')] ) )
        hands.append ( ph.Poker_Hand( [Card('4', 'Spade') , Card('6', 'Club') ,
                     Card('6', 'Spade') , Card('6', 'Diamond') ,
                          Card('Q', 'Club')] ) )
        hands.append ( ph.Poker_Hand( [Card('5', 'Spade') , Card('5', 'Heart') ,
                     Card('6', 'Heart') , Card('J', 'Diamond') ,
                          Card('J', 'Heart')] ) )
        hands.append ( ph.Poker_Hand( [Card('8', 'Club') , Card('9', 'Heart') ,
                     Card('10', 'Heart') , Card('J', 'Club') ,
                          Card('Q', 'Spade')] ) )
        for hand in hands:
            print hand
            print hand.fitness_value ( util.plus_one, 'get_simple_score' )
        
class Test():
    def __init__ (self):
        self.population = ph.Population ( 50, wrapper_function = util.plus_one, threshold = 7 )

    def run ( self, params ):
        return self.population.run ( 100, **params )

"""
The following code is for testing
    Change the number_of_test 
"""
if __name__ == "__main__":
    parser = optparse.OptionParser(usage="%prog [OPTIONS]")
    parser.add_option('-n', '--size', default='1',
                      help='Number of tests')
    parser.add_option('-c', '--crossover', default='0.7',
                      help='Crossover rate')
    parser.add_option('-m', '--mutation', default='0.1',
                      help='Mutation rate')
    parser.add_option('-s', '--suitmutation', default='0.1',
                      help='Suit mutation rate')
    parser.add_option('-e', '--elitism', default='0.1',
                      help='Elitism rate')
    
    options, args = parser.parse_args()
    params = {}
    
    try:
        no_of_test = int(options.size)
        params['crossover'] = float(options.crossover)
        params['mutation'] = float(options.mutation)
        params['suit_mutation'] = float(options.suitmutation)
        params['elitism'] = float(options.elitism)
    
        best_hand_counter = defaultdict(int)
        for i in xrange(no_of_test):
            print '================================================================'
            print '=============================RUN '+ str(i) + '==============================='
            test = Test()
            best_hand = test.run(params)
            print '=============Best hand==============='
            print best_hand
            fitness_value = best_hand.fitness_value ( util.plus_one, 'get_simple_score' )
            print 'Fitness value :' + str(fitness_value)
            best_hand_counter[best_hand.hand_kind] += 1

        print '|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|'
        for hand_kind in best_hand_counter:
            print '|=|= Number of ' + hand_kind + ' : ' + str(best_hand_counter[hand_kind])
    except TypeError as e:
        print e
        
