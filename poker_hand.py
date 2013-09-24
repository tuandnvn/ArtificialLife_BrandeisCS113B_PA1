import heapq
import bisect
import random
import math
import copy

class Card():
    """
    A class to store the structure of a normal poker card
    """
    '''
    I order the suits by the following rule:
    Heart = 3, Diamond = 2, Spade = 1, Club = 0
    Order of the kind:
    A,2,3,4,5,6,7,8,9,10,J,Q,K
    '''
    all_kinds = ['A','2','3',
                 '4','5','6',
                 '7','8','9',
                 '10','J','Q','K']
    all_suits = [ 'Club', 'Spade', 'Diamond', 'Heart']
    
    def __init__(self, kind, suit):
        """
        Constructor: 
            Each card has a kind and suit
        Parameters:
            kind: string
            suit: string
        """
        self.kind = kind
        self.suit = suit
        '''The card could be given a position if we order the whole desk'''
        self.pos = self.get_pos ()
        
    def get_pos ( self ):
        """
        Get a number for 0 to 51 for each card, based on the kind and suit.
        """
        '''
        all_kind_dict is a class variable to keep track of
        an one-to-one mapping between kinds and kind ranks
        '''
        if not 'all_kind_dict' in Card.__dict__:
            Card.all_kind_dict = {}
            for i in xrange(len(Card.all_kinds)):
                Card.all_kind_dict[Card.all_kinds[i]] = i
        '''
        all_suit_dict is a class variable to keep track of
        an one-to-one mapping between suits and suit ranks
        '''
        if not 'all_suit_dict' in Card.__dict__:
            Card.all_suit_dict = {}
            for i in xrange(len(Card.all_suits)):
                Card.all_suit_dict[Card.all_suits[i]] = i
                
        return Card.all_kind_dict[self.kind]*len(Card.all_suits) + Card.all_suit_dict[self.suit]

    @classmethod
    def random_suit ( cls ):
        return Card.all_suits[random.randint( 0, 3 )]
    
    @classmethod
    def get_card ( cls, pos ):
        """
        Class method: get a card given its position in an ordered desk
        Parameters:
            pos: integer (card's position in an ordered desk)
        """
        kind_value = int(math.floor(pos/len(Card.all_suits)))
        suit_value = int(pos % len(Card.all_suits))
        return cls( Card.all_kinds[kind_value], Card.all_suits[suit_value] )

    @classmethod
    def random_card ( cls ):
        """
        Class method: Random a card
        """
        kind = cls.all_kinds[random.randint ( 0, len(cls.all_kinds) - 1 )]
        suit = cls.all_suits[random.randint ( 0, len(cls.all_suits) - 1 )]
        return cls( kind , suit )
        
    def __str__( self ):
        return self.kind + ' ' + self.suit

class Poker_Hand():
    """
    A class to store the structure of a normal poker hand
    with 5 cards (In reality, people could play with 7 cards as well)
    """
    def __init__(self, cards):
        """
        Constructor: Create a poker hands of 5 cards
        Parameters:
            cards: list of Card objects
        """
        if len(cards) != 5:
            raise Exception('Poker hands is not valid: A poker hand must have 5 cards!')
        self.cards = cards
        '''
        basic_repr is the 52 bits representation of the hand
        card_pos is the concise representation of the hand (sorted)
        card_kinds is the kind of all the cards (sorted)
        card_suits is the suit of all the cards (sorted in the same order with card_pos)
        '''
        self.basic_repr, self.card_pos = self.make_repr_from_cards ( cards , '52_bits')
        self.card_pos = sorted(self.card_pos)
        self.card_kinds = [int(t/4) for t in self.card_pos]
        self.card_suits = [t % 4 for t in self.card_pos]
        
    def fitness_value ( self, wrapper_function, fitness_type ):
        """
        Get the fitness value given a wrapper function and a fitness type
            wrapper_function is an external function that make further calculation on the fitness
            fitness_type could be some calculation inherent to the poker hierarchy
        
        Parameters:
            wrapper_function: a function with both input and output are an integer
            fitness_type: string 
        """
        return wrapper_function(getattr( self, fitness_type )())

    @property
    def hand_kind( self ):
        if not hasattr(self, '_hand_kind'):
            score = self.get_simple_score ()
        kind_strings = ['Highest card', 'A pair', 'Two pair', 'Three of a kind',
                        'Straight', 'Flush', 'Full house', 'Straight flush',
                        'Four of a kind', 'Royal Straight Flush' ]
        return kind_strings[score]
        
    @classmethod
    def generate_poker_hand ( cls, repr_52_bits ):
        """
        Class method: Generate a poker hand given it 52 bits representation
        
        Parameters:
            repr_52_bits: An array of '0' or '1'
        """
        cards = []
        for i in xrange(52):
            if repr_52_bits[i] == '1':
                cards.append( Card.get_card(i) )
                if len(cards) > 5:
                    raise Exception(' This 52 bits representation is illegitimate ')
        return cls( cards )

    @classmethod
    def random_poker_hand ( cls ):
        """
        Class method: Generate a poker hand randomly
        
        Parameters:
            repr_52_bits: An array of '0' or '1'
        """
        card_count = 0
        repr_52_bits = ['0'] * 52
        while ( card_count < 5 ):
            new_card = Card.random_card()
            if ( repr_52_bits[new_card.get_pos()] == '0' ):
                repr_52_bits[new_card.get_pos()] = '1'
                card_count += 1
        
        return cls.generate_poker_hand ( repr_52_bits )
            

    def get_simple_score ( self ):
        """
        A simple score given to a hand based on how powerful it is 
        The score would be simply integer values corresponding to different
        type of hand.
            Royal flush = 9
            Four of a kind = 8
            Straight Flush = 7
            Full House = 6
            Flush = 5
            Straight = 4
            Three of a kind = 3
            Two Pair = 2
            Pair = 1
            No-pair = 0
        """
        
        if 'simple_score' in self.__dict__:
            return self.simple_score

        pair_flag = 0
        triple_flag = False
        quartet_flag = False
        flush_flag = False
        straigh_flag = False
        royal_straight_flag = False
        
        kinds = self.get_same_kinds()
        for kind in kinds:
            if kinds[kind] == 2:
                pair_flag += 1
            if kinds[kind] == 3:
                triple_flag = True
            if kinds[kind] == 4:
                quartet_flag = True
                break
        ''' Two pairs '''
        if pair_flag == 2:
            self.simple_score = 2
            return 2
        ''' Four of a kind '''
        if quartet_flag:
            self.simple_score = 8
            return 8
        
        ''' Pair or full house '''
        if pair_flag == 1:
            if triple_flag:
                self.simple_score = 6
                return 6
            self.simple_score = 1
            return 1
        
        ''' Three of a kind '''
        if triple_flag:
            self.simple_score = 3
            return 3

        if self.is_straight():
            straigh_flag = True
            if type(self.is_straight()) == tuple:
                royal_straight_flag = True

        if self.is_flush():
            flush_flag = True

        if royal_straight_flag and flush_flag:
            self.simple_score = 9
            return 9

        if straigh_flag:
            if flush_flag:
                self.simple_score = 7
                return 7
            self.simple_score = 4
            return 4

        if flush_flag:
            self.simple_score = 5
            return 5
        self.simple_score = 0
        return 0
        
    def get_same_kinds( self ):
        """
        Get a auxillary variable for the hand 
        Example: 3 Heart, 3 Spade, 4 Club, 4 Heart, 4 Spade
        would have same_kinds = { 2:1 , 3:1 }
        """
        if 'same_kinds' in self.__dict__:
            return self.same_kinds
        self.same_kinds = {}

        for kind in self.card_kinds:
            if kind in self.same_kinds:
                self.same_kinds[kind] += 1
            else:
                self.same_kinds[kind] = 1
        return self.same_kinds

    def is_straight ( self ):
        """
        Check if the hand is straight or not
        """
        '''
        Check for the last four cards to see if they straight
        '''
        for i in xrange(3):
            if self.card_kinds[i+2] - self.card_kinds[i+1] != 1:
                return False
        ''' 10 and A '''
        if self.card_kinds[1] - self.card_kinds[0] == 9 :
            return ( True, True )
        ''' Other cases '''
        if self.card_kinds[1] - self.card_kinds[0] == 1 :
            return True
        return False
    

    def is_flush ( self ):
        """
        Check if the hand is straight or not
        """
        for i in xrange(4):
            if self.card_suits[i + 1] != self.card_suits[i]:
                return False
        return True
            

    def make_repr_from_cards ( self, cards, repr_type ):
        """
        From cards, get binary string to represent the hand
        cards: List of Cards
        repr_type:
            - 52_bits
        """
        '''
        A bit string of 52 0's with 5 1's indication the 5 cards by position
        
        '''
        card_pos = []
        if repr_type == '52_bits':
            string = ['0']*52
            for card in cards:
                pos = card.get_pos()
                if string[pos] == '0':
                    string[pos] = '1'
                    card_pos.append(pos)
                else:
                    raise Exception('Poker hands is not valid: Cards of the same value')
            return ( string , card_pos )

    def __str__( self ):
        return ' , '.join([str(card) for card in self.cards])

    
    """--------------------------------------------------------------------------------------"""
    """---------------------This section is for mutation and crossover-----------------------"""
    @classmethod
    def mutate ( cls, poker_hand ):
        """
        Mutate a poker hand
        Parameters:
            poker_hand: A Poker_Hand object
        """
        basic_repr = copy.copy( poker_hand.basic_repr )
        '''Random a card to be replaced'''
        selected_card = random.randint( 0 , 4 )
        
        basic_repr[poker_hand.card_pos[selected_card]] = '0'

        new_card = random.randint( 0 , 51 )
        while basic_repr[new_card] == '1':
            new_card = random.randint( 0 , 51 )
        basic_repr[new_card] = '1'
        return cls.generate_poker_hand( basic_repr )

    @classmethod
    def suit_mutate ( cls, poker_hand ):
        """
        Mutate a poker hand in the following way:
        Randomly select a subset of the poker hand and then change
        the suit of all cards in the subset into the same suit
        Parameters:
            poker_hand: A Poker_Hand object
        """
        new_cards = []
        '''Random inclusion of a card for suit mutation'''
        mutated_suit_hand = copy.deepcopy( poker_hand )
        mutation_kinds = []

        done_mutate = False

        counter = 0
        while (not done_mutate) and counter < 5:
            def random_subset ( no ):
                t = set()
                while (len(t) != no):
                    t.add( random.randint ( 0, no - 1 ) )
                return t

            no_of_subset_element = random.randint ( 3, 5 ) 
            subset_index = random_subset ( no_of_subset_element )
            for i in xrange(5):
                included = i in subset_index
                if included == 0:
                    new_cards.append (copy.deepcopy( poker_hand.cards[i]))
                else:
                    mutation_kinds.append ( poker_hand.cards[i].kind )

            suit = Card.random_suit()
            for kind in  mutation_kinds:
                new_cards.append( Card( kind, suit ))

            try:
                counter += 1
                mutated_suit_hand = Poker_Hand(new_cards)
                done_mutate = True
            except Exception:
                pass

        return mutated_suit_hand

    @classmethod
    def crossover ( cls, poker_hand_1, poker_hand_2 ):
        """
        Crossover two poker hands to create two offsprings
        Parameters:
            poker_hand_1: A Poker_Hand object
            poker_hand_2: A Poker_Hand object
        """
        selected_pos = random.randint( 1 , 4 )
        try:
            child_1 = cls(poker_hand_1.card_pos[:selected_pos] + poker_hand_2.card_pos[selected_pos:])
            child_2 = cls(poker_hand_2.card_pos[:selected_pos] + poker_hand_1.card_pos[selected_pos:])
            return [child_1, child_2]
        except Exception:
            return []

class Population():
    """
    A class to handle a population of poker hands
    """
    def __init__ ( self, no_of_individual, **kwargs ):
        """
        Constructor: Create a population of poker hands
        Parameters:
            no_of_individual: int (population size)
            **kwargs: will recognize wrapper_function and threshold
                wrapper_function: an external function to further process the fitness score
                threshold: a threshold to remove the high-fitness cards at the beginning
        """
        self.wrapper_function = kwargs['wrapper_function']
        self.threshold = self.wrapper_function ( kwargs['threshold'] )
        self.no_of_individual = no_of_individual
        self.population = []
        self.total_score = 0
        self.current_gen = 0

        while (len(self.population) != no_of_individual):
            new_poker_hand = Poker_Hand.random_poker_hand ()
            fitness_score = new_poker_hand.fitness_value( self.wrapper_function, 'get_simple_score')
            if  fitness_score > self.threshold:
                continue
            self.total_score += fitness_score
            
            heapq.heappush(self.population, ( fitness_score, new_poker_hand ))

        self.proportional_struct = self.get_proportional_struct()
##        self.print_representation()
    
        
    def print_representation ( self ):
        """
        Print out the average fitness of the population and its highest scored individual
        """
        largest = heapq.nlargest( 1 , self.population )[0]
        print '-----------------------------------------------------------------------------'
        print 'Generation ' + str( self.current_gen)
        print 'Average fitness :' + str(float( self.total_score)/ self.no_of_individual)
        print 'Highest fitness :' + str(largest[0])
        print 'The corresponding poker hand : ' + str(largest[1])

    def get_proportional_struct( self ):
        """
        An array storing the accumulating score of individual,
        to help randomly generate candidates for next generation
        """
        left = 0
        left_list = [0]
        
        for i in xrange( self.no_of_individual - 1 ):
            left_list.append( self.population[i][0] + left_list[-1] )
        
        return left_list
        
    def next_generation ( self , **kwargs):
        """
        Generate a generation
        Parameters:
            **kwargs:
                crossover: crossover rate ( 0 < crossover < 1 )
                mutation: mutation rate ( 0 < mutation < 1 )
                suit_mutation: suit mutation rate ( 0 < suit_mutation < 1 )
                elitism: elitism rate ( 0 < elitism < 1 )
                crossover + mutation + crossover = 1
        """
        cross_rate = kwargs['crossover']
        mutate_rate = kwargs['mutation']
        suit_mutate_rate = kwargs['suit_mutation']
        elite_rate = kwargs['elitism']

        sum_rate = 0
        for keyword in kwargs:
            sum_rate += kwargs[keyword]
        if math.fabs( sum_rate - 1 ) > 0.001:
            raise Exception (' The rate need to sum up to 1 ')
        
        next_gen_population = []
        

        '''
        Generate a random value to decide what kind of method
        to generate a pair of children for next generation
        '''
        while ( len(next_gen_population) < self.no_of_individual ):
            type_rand_val = random.random()
            if type_rand_val < cross_rate:
                gen_type = 0
            elif type_rand_val < cross_rate + mutate_rate:
                gen_type = 1
            elif type_rand_val < cross_rate + mutate_rate + suit_mutate_rate:
                gen_type = 2
            else:
                gen_type = 3

            rand_val = random.randint( 1, self.total_score )
            p_1 = self.population[ bisect.bisect_left ( self.proportional_struct, rand_val ) - 1 ][1]
            if gen_type == 0:
                '''Cross the parents here'''
                rand_val = random.randint( 0, self.total_score - 1)
                p_2 = self.population[ bisect.bisect ( self.proportional_struct, rand_val ) - 1 ][1]
                children = Poker_Hand.crossover ( p_1, p_2 )
                for child in children:
                    next_gen_population.append( child )
            elif gen_type == 1:
                'Mutation here'''
                child = Poker_Hand.mutate ( p_1 )
            
                next_gen_population.append( child )
            elif gen_type == 2:
                '''Suit mutation here'''
                child = Poker_Hand.suit_mutate ( p_1 )
                next_gen_population.append( child )
            else:
                '''Elitism'''
                next_gen_population.append( p_1 )

        if len(next_gen_population) > self.no_of_individual:
            discard_pos = random.randint( 0, next_gen_population - 1 )
            del next_gen_population[ discard_pos ]

        ''' Replace current population with the generated population '''
        self.population = []
        self.total_score = 0

        is_good = False
        best_score = 0
        best_hand = None
        
        for i in xrange( self.no_of_individual ):
            poker_hand = next_gen_population[i]
            fitness_score = poker_hand.fitness_value( self.wrapper_function, 'get_simple_score')
            if  fitness_score > self.threshold:
##                print 'Find a good poker hand: ' + str(poker_hand)
                is_good = True

            if fitness_score > best_score:
                best_hand = poker_hand
                best_score = fitness_score
            try:
                self.total_score += fitness_score
            except TypeError:
                print poker_hand
            
            heapq.heappush(self.population, ( fitness_score, poker_hand ))
        
        self.proportional_struct = self.get_proportional_struct()
        self.current_gen += 1
        self.print_representation()

        
        return is_good, best_hand

    def run ( self, no_of_loop, **kwargs ):
        best_hand = None
        for i in xrange( no_of_loop ):
            is_good, best_hand = self.next_generation ( **kwargs )
            if is_good:
                return best_hand
        return best_hand
