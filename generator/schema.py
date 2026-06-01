# generator/schema.py
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """One input/output pair for testing the student's code."""
    args: list = Field(description="Arguments to pass to the function")
    expected: object = Field(description="Expected return value")


class Exercise(BaseModel):
    """A programming exercise generated for a given topic."""
    id: str
    topic: str
    statement: str = Field(description="What the student needs to do")
    function_name: str = Field(description="Name of the function to implement")
    reference_solution: str = Field(description="A correct Python solution")
    tests: list[TestCase]