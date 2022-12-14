# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to Pokedex, you can search the details of original Pokemon here. Try searching for a Pokemon! or say help if you need help!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class PokemonDetailsIntentHandler(AbstractRequestHandler):
    """Handler for Pokemon Details Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PokemonDetails")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Parsing slot value
        slots = handler_input.request_envelope.request.intent.slots
        pokemon = slots['pokemon'].value
        pokemon = pokemon.lower()
        
        # Fetching data from Pokemon API
        pokemon_api = "https://pokeapi.co/api/v2/pokemon/" + pokemon
        response = requests.get(pokemon_api)
        data = response.json()
        
        pokemon_name = data["name"]
        pokemon_api = data["species"]["url"]
        response = requests.get(pokemon_api)
        data_species = response.json()
        
        # Filtering the description of Pokemon
        temp = data_species["flavor_text_entries"][0]["flavor_text"]
        temp = temp.replace("\n"," ")
        temp = temp.replace("\u000c"," ")
        pokemon_description = temp
        
        # Storing the Pokemon type
        pokemon_type = data["types"][0]["type"]["name"]
        
        # Finding the abilities of the Pokemon
        pokemon_abilities = []
        count = 0
        
        try:
            while(count < 2):
                pokemon_abilities.append(data["abilities"][count]["ability"]["name"])
                count += 1
            
        except:
            count = 1
        
        # Finding the evolution of Pokemon
        pokemon_evolution = data_species["evolves_from_species"]
        pokemon_api = data_species["evolution_chain"]["url"]
        response = requests.get(pokemon_api)
        data_species = response.json()
        
        try:
            if(pokemon_evolution == None):
                pokemon_evolution = data_species["chain"]["evolves_to"][0]["species"]["name"]
            else:
                pokemon_evolution = data_species["chain"]["evolves_to"][0]["evolves_to"][0]["species"]["name"]
                if (pokemon_evolution == pokemon_name):
                    pokemon_evolution = False
        except:
            pokemon_evolution = False
            
        # Formatting the Output
        pokemon_name = pokemon_name.capitalize()
        if(pokemon_evolution != False):
            pokemon_evolution = pokemon_evolution.capitalize()
        
        # Creating the final speech output for Alexa
        speak_output = pokemon_name + ". " + " It is a " + pokemon_type + " Pokemon. " + pokemon_description
        
        if(count == 2):
            speak_output = speak_output + " It has " + str(count) + " abilities " + pokemon_abilities[0] + " and " + pokemon_abilities[1]
        else:
            speak_output = speak_output + " It has " + str(count) + " ability " + pokemon_abilities[0]
            
        if(pokemon_evolution == False):
            speak_output = speak_output + ". It is fully evolved"
        else:
            speak_output = speak_output + ". It evolves to " + pokemon_evolution
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say the name of Pokemon to look for it's details! For example try saying 'Search Charmander'"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Thankyou for using Pokedex! Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say help if you need help to search for Pokemon details."
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PokemonDetailsIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()