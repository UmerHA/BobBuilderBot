# Bob, the BuilderBot
## 👷🏼‍♂️ LLM-Agent for autonomous Software Creation 🏗️

Bob the BuilderBot explores how we can use LLMs to create good software. It is still in very early development.
The goal is to create an agent that takes input from an average non-technical user and creates working software for the user.

Reasonable asks from Bob the BuilderBot could be:
- Give me a Tetris game I can play in the browser
- I want a website where I can track my weight
- For our neighborhood, we're building an item library, where you can borrow items instead of books. Can you give me a website where people can borrow items?

The goal is **not** to build highly complex, performant or security-critical systems.
Bob will never build software to control nuclear power plants or hospitals.

## Examples
todo

## Approach

Bob uses an agile development process. He aims to quickly develop an MVP, show it to the user and then improve.

Additionally, Bob tries to make educated assumptions instead of asking the user for every detail. Only when really necessary, does Bob ask clarifying questions.

Bob's phases of Software Creation are:
1. **Understand:** Translate user input into a detailed requirements list & ask clarifying questions
2. **Architect:** Decide on high-level architecture and tech stack
3. **Structure Code:** Decide which files we'll need, what they'll do and what the main functions are
4. **Structure Tests:** Decide how we'll test and what tests we'll have
5. **Write code:** Iteratively, write the code
6. **Write out tests:** Iteratively, write the tests and make sure they pass
7. **Deploy:** Deploy so user can see and interact with the project
8. **Improve:** Ask user for feedback, rinse and repeats

Theses phases only roughly correspond do traditional Software Engingeering phases, as I think that in the context of Sofware Creation via LLMs, it makes more sense to divide the process along LLM capabilites. I.e., each phase should be one action an LLM can do.

Each step is an LLM-call wrapped in a [SmartGPT workflow](https://youtu.be/wVzuvf9D9BU).

## Problems to solve
This is an incomplete list of what's to do:

1. Finish v0
- Handle when agents asks clarifying questions 
- Finish implementing all phases

2. Improve without gradient based techniques
- Use few-shot prompting (currently zero-shot)
- Use better method for LLM inference (e.g. [Reflexion](https://arxiv.org/abs/2303.11366), [Tree of Thought](https://arxiv.org/abs/2305.10601))

3. Improve with gradient based techniques
- Finetune?

4. General
- Add prioritization to requirements list (?)
- How are iterations 2+ different for the initial iteration


## How to use

**Step 1:** Let Bob build
```
from builderbot import BuilderBot
bob = BuilderBot("gpt-4")
task = "I want a website where I can track my weight"
bob.build(task)
```
Bob will create your project in the `output` folder.

**Step 2:** Deploy to replit

On [replit](replit.com/), log in, create a new repl and copy paste the code into it.
## How to contribute
todo


## Citation
todo

---
Twitter: [@UmerHAdil](https://twitter.com/UmerHAdil) - Feel free to reach out!
