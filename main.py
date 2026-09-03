from graph.workflow import build_workflow

app = build_workflow()

state = {
    "user_question": "Why does my hair look dry?",
    "image_path": "images/hair.jpg",
    "user_context": {
        "heat_styling": "frequent",
        "chemical_treatment": "no"
    }
}

result = app.invoke(state)
print(result)
