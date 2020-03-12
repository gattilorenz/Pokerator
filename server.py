from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints
from twisted.web.server import NOT_DONE_YET


from NameEvaluation import evaluation_name
from PokedexEntryBuilder import build_description
from QuestionHandling import ask_questions
from Wordblender import blend_a_word
from DescriptionEvaluation import check_description_is_novel

import html	
from xml.etree.ElementTree import ElementTree
import os

import fnmatch
import time
import cgi
import json

import pdb



class Generation(Resource):
	isLeaf = True
	
	def generate_Pokemon(self, request):

		returndict =	{

		}
		try:
			print('Started generating name and desc')
			print(self.answersList)
			#pdb.set_trace()
			blended_words, w1, w2 = blend_a_word(self.answersList)
			pokemon = evaluation_name(blended_words)
			print('Name chosen: '+pokemon)
			for retry in range(1,3):
				description = build_description([w1, w2], pokemon)
				print('generated desc number '+str(retry))				
				if check_description_is_novel(description):
					print('novel description!')
					break
				print('discareded 1 desc')
			name = pokemon.upper()
			returndict['name'] = name
			returndict['description'] = description
			print(description)
			returndict["STATUS"] = "OK"			
		except Exception as err:
			print("Error generating pokemon")
			print(type(err))
			print(err.args)
			print(err)
			returndict["STATUS"] = "ERROR"			
		print('encoding response and returning it...')
		request.write(json.dumps(returndict).encode('utf-8'))
		request.finish()
		print('response returned')
		return
				
	def render_POST(self, request):
		jsonAnswers = request.content.read().decode("utf-8")
		answers = json.loads(jsonAnswers)
		self.answersList = list(answers.values()) #I HATE PYTHON
		reactor.callLater(0, self.generate_Pokemon, request)
		return NOT_DONE_YET
		
		
root = File('./WebServer')
generation = Generation()
root.putChild(b"generate", generation)


factory = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8000)
endpoint.listen(factory)
print("Pokerator server listening on port 8000")
reactor.run()
