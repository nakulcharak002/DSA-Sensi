import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.gateway import get_langchain_llm
from app.prompts.metadata_prompt import METADATA_PROMPT
from app.schemas.problem_metadata import ProblemMetadata

llm = get_langchain_llm(feature="metadata")


def extract_metadata(
    problem_statement: str,
) -> ProblemMetadata:
    """
    Extract metadata from a DSA problem statement.
    """

    response = llm.invoke(
        [
            SystemMessage(content=METADATA_PROMPT),
            HumanMessage(content=problem_statement),
        ]
    )

    text = response.content.strip()

    text = re.sub(r"^```json", "", text)
    text = re.sub(r"```$", "", text)

    data = json.loads(text)

    return ProblemMetadata.model_validate(data)