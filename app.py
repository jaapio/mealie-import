from flask import Flask, render_template, request, redirect, url_for
from recipe_scrapers import scrape_me
import requests
import asyncio
import json
import uuid
import os
from mealieapi import MealieClient

app = Flask(__name__)

# Define the Mealie API URL
MEALIE_API_URL = os.getenv('API_URL')
MEALIE_API_KEY = os.getenv('API_KEY')

def toIngredients(note):
    return {
      "title": None,
      "note": note,
      "unit": None,
      "food": None,
      "disableAmount": True,
      "quantity": 1,
      "referenceId": str(uuid.uuid4())
    }

def toInstruction(instruction):
    return {
      "title": "",
      "text": instruction,
      "ingredient_references": []
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]

        scraper = scrape_me(url, wild_mode=True);

        recipe = {
            'name': scraper.title(),
            'description': scraper.description(),
            'totalTime': scraper.total_time(),
            'recipeIngredient': [toIngredients(i) for i in scraper.ingredients()],
            'recipeInstructions': [toInstruction(i) for i in scraper.instructions_list()],
            'orgURL': url,
            'recipeYield': scraper.yields()
        }

        headers = {'Authorization': 'Bearer ' + MEALIE_API_KEY, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        # Post will just create a recipe, with a name. 
        post = requests.post(MEALIE_API_URL + '/api/recipes', data=json.dumps(recipe, indent=2), headers=headers)
        slug = json.loads(post.text);

        # Get the recipe, because the api patch does not work otherwise.
        recipeData = json.loads(requests.get(MEALIE_API_URL + '/api/recipes/' + slug, headers=headers).text);
        recipeData.update(recipe);
        response = requests.patch(MEALIE_API_URL + '/api/recipes/' + slug, data=json.dumps(recipeData, indent=2), headers=headers)

        #set the image
        requests.post(MEALIE_API_URL + '/api/recipes/' + slug + '/image', data=json.dumps({'url': scraper.image()}, indent=2), headers=headers)

        return render_template("index.html", response= response.status_code == 200 and 'Done' or response.text)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)