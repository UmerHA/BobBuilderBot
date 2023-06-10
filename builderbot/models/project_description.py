from typing import List, Optional
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class UserQuestion(BaseModel):
    content: str = Field(description="a claryfing question to the user")

class Assumption(BaseModel):
    content: str = Field(description="an educated, explicit assumptions you made")

class Requirement(BaseModel):
    content: str = Field(description="a project requirement")

class ProjectDescription(BaseModel):
    user_goal: str = Field(description="the user's goal")
    requirements: List[Requirement] = Field(description="list of requirements that together define the project")
    assumptions: List[Assumption] = Field(description="list of educated, explicit assumptions you made")
    questions: Optional[List[UserQuestion]] = Field(description="list of clarifying questions to the user")

    def to_str(self) -> str:
        '''Represent project description as string, so it is easier to process by LLM'''

        result = "The user's goal is " + self.user_goal + "\n\n"

        result += "Therefore, the requirements are:\n"
        for req in self.requirements:
            result += "- " + req.content + "\n"
        result += "\n"

        result += "In this, I have made the following assumptions:\n"
        for assumption in self.assumptions:
            result += "- " + assumption.content + "\n"
        result += "\n"
        
        if self.questions:
            result += "I have these questions to the user::\n"
            for q in self.questions:
                result += "- " + q.content + "\n"
            result += "\n"            
        else:
            result += "I have no question to the user."

        return result

project_description_parser = PydanticOutputParser(pydantic_object=ProjectDescription)