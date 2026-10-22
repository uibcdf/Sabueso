from sabueso._private.argdigest._shared import refuse


def digest_question(question, caller=None):
    if isinstance(question, str) and question.strip():
        return question
    raise refuse(
        "question", question, caller, "expected a nonempty registered question key"
    )
