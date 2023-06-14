"""Functions for counting the number of tokens in a message or string."""
from __future__ import annotations

import json
from typing import List

import tiktoken

from autogpt.llm.base import Message
from autogpt.logs import logger

FUNCTIONS_TOKEN_COST = 500  # ballpark estimate, no need to be exact for now.


def count_message_tokens(
    messages: List[Message], model: str = "gpt-3.5-turbo-16k-0613"
) -> int:
    """
    Returns the number of tokens used by a list of messages.

    Args:
        messages (list): A list of messages, each of which is a dictionary
            containing the role and content of the message.
        model (str): The name of the model to use for tokenization.
            Defaults to "gpt-3.5-turbo-16k-0613".

    Returns:
        int: The number of tokens used by the list of messages.
    """
    # TODO: Will tiktoken eventually have this?
    if model == "gpt-4-0613":
        encoding_model = "gpt-3.5-turbo"
    else:
        encoding_model = "gpt-4"

    try:
        encoding = tiktoken.encoding_for_model(encoding_model)
    except KeyError:
        logger.warn("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if model.startswith("gpt-3.5"):
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model.startswith("gpt-4"):
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}.\n"
            " See https://github.com/openai/openai-python/blob/main/chatml.md for"
            " information on how messages are converted to tokens."
        )

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.raw().items():
            # FIXME? Use json dumped version of function call dict for guesstimation
            if type(value) is not str:
                value = json.dumps(value)

            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def count_string_tokens(string: str, model_name: str) -> int:
    """
    Returns the number of tokens in a text string.

    Args:
        string (str): The text string.
        model_name (str): The name of the encoding to use. (e.g., "gpt-3.5-turbo-16k-0613")

    Returns:
        int: The number of tokens in the text string.
    """
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(string))
