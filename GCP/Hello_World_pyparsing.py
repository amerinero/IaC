# ejemplo en Python 2.x
from pyparsing import Word, alphas

greet = Word( alphas ) + "," + Word( alphas ) + "!"
greeting = greet.parseString( "Una2palabra, World!" )
print greeting
